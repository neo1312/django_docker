from django.test import TestCase
from django.test import SimpleTestCase
from inventory.models import Product, Brand, ProductVariant, InventoryItem
from srm.models import Supplier 
from django.urls import reverse, resolve
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth.models import User 

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

class ProductTimeStampedModelTest(TestCase):
    def test_timestamps_and_is_active_exist(self):
        # Crear un producto de prueba
        product = Product.objects.create(
            name="Producto Test",
            min_stock=1,
            max_stock=10,
            quantity=5,
            price=Decimal("20.00"),
            is_bulk=False,
            is_active=True
        )

        # Comprobar que los campos existan y tengan valores válidos
        self.assertIsNotNone(product.created_at)
        self.assertIsNotNone(product.updated_at)
        self.assertTrue(product.is_active)

    def test_updated_at_changes_on_save(self):
        product = Product.objects.create(
            name="Producto Test 2",
            min_stock=1,
            max_stock=10,
            quantity=5,
            price=Decimal("30.00"),
            is_bulk=False,
            is_active=True
        )

        original_updated_at = product.updated_at

        import time
        time.sleep(1)  # Esperar 1 segundo para notar el cambio en la fecha

        product.name = "Producto Test Modificado"
        product.save()

        self.assertNotEqual(product.updated_at, original_updated_at)

class ProductListViewTest(TestCase):
    def test_product_list_view_return_200(self):
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code,200)
    def test_product_list_view_shows_products(self):
        Product.objects.create(name="Martillo",price=1)
        Product.objects.create(name="Clavos",price=2)

        response = self.client.get(reverse('product_list'))
        self.assertContains(response, "Martillo")
        self.assertContains(response, "Clavos")

    def test_product_list_view_filters_by_name(self):

        Product.objects.create(name="Martillo",price=1)
        Product.objects.create(name="Clavos",price=2)
        response = self.client.get(reverse('product_list'), {'q': 'martillo'})
        self.assertContains(response, "Martillo")
        self.assertNotContains(response, "Clavos")
    def test_product_list_view_filters_by_barcode(self):
        product = Product.objects.create(name="Taladro",price=4)
        ProductVariant.objects.create(product=product, barcode="123ABC")

        response = self.client.get(reverse('product_list'), {'q': '123ABC'})
        self.assertContains(response, "Taladro") 
    def test_htmx_request_renders_table_template(self):
        Product.objects.create(name="Lijadora",price=1)

        response = self.client.get(
            reverse('product_list'),
            HTTP_HX_REQUEST='true'
        )
        self.assertTemplateUsed(response, 'table.html')

class InventoryItemCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.supplier = Supplier.objects.create(name="BLG")
        self.product= Product.objects.create(name="pala",price="40") 
        self.product_variant = ProductVariant.objects.create(
                product = self.product,
                barcode = 1234
                )
    def test_create_inventory_item(self):
        """Test creating a basic inventory item"""
        item = InventoryItem.objects.create(
            product_variant=self.product_variant,
            sequential_id=1,
            supplier=self.supplier,
            purchase_price=899.99,
            sale_price=999.99,
            current_status='ordered'
        )
        
        self.assertEqual(item.sequential_id, 1)  # Check warehouse ID
        self.assertEqual(item.purchase_price, 899.99)  # Verify cost
        self.assertEqual(item.current_status, 'ordered')  # Verify status
    
    def test_status_transitions(self):
        """Test updating status and automatic date setting"""
        item = InventoryItem.objects.create(
            product_variant=self.product_variant,
            sequential_id=2,
            purchase_price=899.99,
            current_status='ordered'
        )
        
        # Test initial state
        self.assertIsNotNone(item.date_ordered)
        self.assertIsNone(item.date_received)
        
        # Move to received status
        item.update_status('received')
        item.refresh_from_db()
        
        self.assertEqual(item.current_status, 'received')
        self.assertIsNotNone(item.date_received)
        self.assertTrue(item.date_received > item.date_ordered)

    def test_date_validation(self):
        """Test that dates must follow logical sequence"""
        item = InventoryItem(
            product_variant=self.product_variant,
            sequential_id=3,
            purchase_price=899.99,
            current_status='received',
            date_ordered=timezone.now(),
            date_received=timezone.now() - timezone.timedelta(days=1)  # Received BEFORE ordered!
        )
        
        with self.assertRaises(ValidationError):
            item.full_clean()  # This should fail our warehouse rules

    def test_profit_calculation(self):
        """Test profit calculation with discount and tax"""
        item = InventoryItem.objects.create(
            product_variant=self.product_variant,
            sequential_id=4,
            purchase_price=900,
            sale_price=1000,
            discount_applied=10.0,  # 10% discount
            tax_rate=8.0,  # 8% tax
            current_status='ready_for_sale'
        )
        
        # Expected calculation:
        # 1000 - 10% = 900
        # 900 + 8% tax = 972
        # Profit = 972 - 900 = 72
        self.assertEqual(item.calculate_profit(), 72)
    

    def test_location_logic(self):
        """Test location determination based on status"""
        # Test ready_for_sale with location
        item1 = InventoryItem(
            product_variant=self.product_variant,
            sequential_id=5,
            current_status='ready_for_sale',
            location_in_warehouse="Shelf A12"
        )
        self.assertEqual(item1.get_current_location(), "Shelf A12")
        
        # Test shipped status
        item2 = InventoryItem(
            product_variant=self.product_variant,
            sequential_id=6,
            current_status='shipped',
            shipping_carrier="FedEx"
        )
        self.assertIn("FedEx", item3.get_current_location())
    
    def test_location_logic(self):
        """Test location determination based on status"""
        # Test ready_for_sale with location
        item1 = InventoryItem(
            product_variant=self.product_variant,
            sequential_id=5,
            current_status='ready_for_sale',
            location_in_warehouse="Shelf A12"
        )
        self.assertEqual(item1.get_current_location(), "Shelf A12")
        
        # Test shipped status
        item2 = InventoryItem(
            product_variant=self.product_variant,
            sequential_id=6,
            current_status='shipped',
            shipping_carrier="FedEx"
        )
        self.assertIn("FedEx", item2.get_current_location())


    def test_status_history(self):
        """Test getting complete status history with display names"""
        item = InventoryItem.objects.create(
            product_variant=self.product_variant,
            sequential_id=8,
            purchase_price=899.99,
            current_status='ordered'
        )
        
        # Update through several statuses
        item.update_status('received')
        item.update_status('quality_check')
        
        history = item.get_status_history()
        
        # Should have 3 statuses now
        self.assertEqual(len(history), 3)
        
        # Verify display names are correct
        status_display_map = {
            'ordered': 'Ordered',
            'received': 'Received in Warehouse',
            'quality_check': 'Quality Check'
        }
        
        for entry in history:
            self.assertEqual(entry['status_display'], status_display_map[entry['status']])
        
        # Verify dates are in order
        self.assertTrue(history[0]['date'] <= history[1]['date'] <= history[2]['date'])
    
    def test_valid_status_transition(self):
        item = InventoryItem.objects.create(
            product_variant=self.product_variant,
            sequential_id=1,
            current_status='ordered',
            purchase_price=10
        )
        item.update_status('received', user=self.user)
        self.assertEqual(item.current_status, 'received')
    
    def test_invalid_status_transition(self):
        item = InventoryItem.objects.create(
            product_variant=self.product_variant,
            sequential_id=2,
            current_status='ordered',
            purchase_price="1"
        )
        with self.assertRaises(ValidationError):
            item.update_status('shipped')  # Can't go from ordered to shipped

    def test_status_log_creation(self):
        item = InventoryItem.objects.create(
            product_variant=self.product_variant,
            sequential_id=3,
            current_status='ordered',
            purchase_price="1"
        )
        item.update_status('received', user=self.user, notes="Initial receiving")
        logs = item.status_logs.all()
        self.assertEqual(logs.count(), 1)
        self.assertEqual(logs[0].old_status, 'ordered')
        self.assertEqual(logs[0].new_status, 'received')
   
    def test_availability_checks(self):
        item = InventoryItem.objects.create(
            product_variant=self.product_variant,
            sequential_id=4,
            current_status='ready_for_sale',
            purchase_price=1
        )
        self.assertTrue(item.is_available_for_sale)
        self.assertTrue(item.is_in_stock)
        self.assertFalse(item.is_shipped)

