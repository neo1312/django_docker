from django.test import TestCase
from inventory.models import Brand

class BrandTest(TestCase):
    def test_create_brand(self):
        brand = Brand.objects.create(name="nike")
        self.assertEqual(brand.name, "nike")
        self.assertIsNotNone(brand.created_at)
        self.assertTrue(brand.is_active)

    def test_str_representation(self):
        brand = Brand.objects.create(name="Adidas")
        self.assertEqual(str(brand), "Adidas")


