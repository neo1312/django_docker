# srm/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from ..models import Supplier
from .handlers import recalculate_supplier_score

@receiver(post_save, sender=Supplier)
def on_supplier_saved(sender, instance, **kwargs):
    recalculate_supplier_score(sender, instance, **kwargs)

@receiver(post_delete, sender=Supplier)
def on_supplier_deleted(sender, instance, **kwargs):
    recalculate_supplier_score(sender, instance, **kwargs)
