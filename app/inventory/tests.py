from django.test import TestCase
from django.test import SimpleTestCase
from inventory.models import Product, Brand, ProductVariant
from django.urls import reverse, resolve
from django.core.exceptions import ValidationError

class BrandTest(TestCase):
    def test_create_brand(self):
        brand = Brand.objects.create(name="nike")
        self.assertEqual(brand.name, "nike")
        self.assertIsNotNone(brand.created_at)
        self.assertTrue(brand.is_active)

    def test_str_representation(self):
        brand = Brand.objects.create(name="Adidas")
        self.assertEqual(str(brand), "Adidas")

class ProductModeltest(TestCase):
    def setUp(self):
        self.product1 = Product.objects.create(
                name = 'pico',
                min_stock = '1',
                max_stock = '5',
                quantity = 1,
                price = 10.00,
                is_bulk = False,
                is_active = True
                )
    def test_product_str_representation(self):
        self.assertEqual(str(self.product1), "pico ($10.00)")

    def test_field_defaults(self):
        product = Product.objects.create(
            name='Martillo',
            price=15
        )
        self.assertEqual(product.min_stock, 0)
        self.assertEqual(product.max_stock, 0)
        self.assertEqual(product.quantity, 0)
        self.assertTrue(product.is_active)
        self.assertFalse(product.is_bulk)
    
    def test_price_cannot_be_negative(self):
        product = Product(
            name='Producto Inválido',
            price=-5.00,
            quantity=10,
        )
        with self.assertRaises(ValidationError):
            product.full_clean()  # Esto ejecuta los validadores manualmente

    def test_quantity_cannot_be_negative(self):
        product = Product(
            name='Producto Inválido',
            price=5.00,
            quantity=-10,
        )
        with self.assertRaises(ValidationError):
            product.full_clean()

class ProductVariantModelTest(TestCase):

    def setUp(self):
        self.product = Product.objects.create(name="Taladro",price=199.99)
        self.brand = Brand.objects.create(name="Makita")

    def test_str_with_brand(self):
        variant = ProductVariant.objects.create(
            product=self.product,
            brand=self.brand,
            barcode="123456789",
            stock=10
        )
        self.assertEqual(str(variant), "Taladro - Makita")

    def test_str_without_brand(self):
        variant = ProductVariant.objects.create(
            product=self.product,
            brand=None,
            barcode="987654321",
            stock=5
        )
        self.assertEqual(str(variant), "Taladro - No Brand")
