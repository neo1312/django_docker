from django.db import models
from core.models import TimeStampedModel
from django.core.validators import MinValueValidator,MaxValueValidator
from decimal import Decimal

class Supplier(TimeStampedModel):
    name = models.CharField(max_length=255)
    credit_days= models.IntegerField(default=0,validators=[MinValueValidator(0)])
    delivery_cost= models.FloatField(default=0.0,validators=[MinValueValidator(0)])
    reliability_score = models.FloatField(default=1.0,validators=[MinValueValidator(1),MaxValueValidator(5)])
    credit_score = models.FloatField(default=1.0,validators=[MinValueValidator(1),MaxValueValidator(5)])
    cost_delivery_score= models.FloatField(default=1.0,validators=[MinValueValidator(1),MaxValueValidator(5)])
    overall_score= models.FloatField(default=0.0,validators=[MinValueValidator(1),MaxValueValidator(5)])

    class Meta:
        app_label = 'srm'

    def __str__(self):
        return self.name
