from django.db import models
from ../core.models.base  import TimeStampedModel

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
