from django.test import TestCase
from srm.models import Supplier

class SupplierModelsTest(TestCase):

    def test_create_supplier(self):
        supplier = Supplier.objects.create(
                name="Test Supplier",
                reliability_score=8.5,
                credit_score=7.0,
                cost_delivery_score=9.0
                )
        self.assertEqual(supplier.name,"Test Supplier")
        self.assertEqual(supplier.reliability_score,8.5)
        self.assertEqual(supplier.credit_score,7.0)
        self.assertEqual(supplier.cost_delivery_score,9.0)


