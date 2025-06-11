from django.db import models

class CreatedUpdatedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['created_at']

class IsActiveModel(models.Model):
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

class TimeStampedModel(CreatedUpdatedModel, IsActiveModel):
    class Meta:
        abstract = True

