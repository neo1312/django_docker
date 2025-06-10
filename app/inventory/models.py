from django.db import models
from core.models  import TimeStampedModel

class Brand(TimeStampedModel):
    name = models.CharField(max_length=225, unique=True)
    def __str__(self):
        return self.name

class Product(TimeStampedModel):
    UNIT_CHOICES = [
            ('grams' 'Grams'),
            ('kilograms', 'Kilograms'),
            ('units', 'Units'),
            ('meters','Meters')
            ]
    name = models.CharField(max_length=100)
    min_stock = models.PositiveIntegerField(default=0)
    max_stock = models.PositiveIntegerField(default=0)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_bulk = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (${self.price})"

class ProductVariant(TimeStampedModel):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    barcode = models.CharField(max_length=50, unique=True)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.brand.name if self.brand else 'No Brand'}"
