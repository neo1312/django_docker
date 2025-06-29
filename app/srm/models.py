from django.db import models
from core.models import TimeStampedModel

class Supplier(TimeStampedModel):
    name = models.CharField(max_length=255)
    reliability_score = models.FloatField(default=0.0)
    credit_score = models.FloatField(default=0.0)
    cost_delivery_score= models.FloatField(default=0.0)
    class Meta:
        app_label = 'srm'

    def __str__(self):
        return self.name
