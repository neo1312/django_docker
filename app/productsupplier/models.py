from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.validators import MinValueValidator
from decimal import Decimal
from inventory.models import ProductVariant
from srm.models import Supplier

class SupplierProduct(models.Model):
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="supplier_products",
        verbose_name="Product Variant"
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="supplied_product_variants"
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Cost per unit from supplier"
    )
    min_order_quantity= models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['product_variant', 'supplier']
        ordering = ['product_variant__product__name', 'supplier__name']
        verbose_name = "Supplier Product"
        verbose_name_plural = "Supplier Products"

    def __str__(self):
        return f"{self.product_variant.product.name} - {self.supplier.name} (${self.cost}/{self.min_order_quantity})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        SupplierProductScore.calculate_scores_for_product(self.product_variant.product)

class SupplierProductScore(models.Model):
    supplier_product = models.OneToOneField(
        SupplierProduct,
        on_delete=models.CASCADE,
        related_name="score"
    )
    cost_score = models.FloatField(default=0.0)  # Lower cost → higher score (1-5)
    quantity_score = models.FloatField(default=0.0)  # Lower MOQ → higher score (1-5)
    overall_score = models.FloatField(default=0.0)  # 70% cost + 30% quantity

    @classmethod
    def calculate_scores_for_product(cls, product):
        # Get all products (active and inactive)
        all_products = SupplierProduct.objects.filter(
            product_variant__product=product
        ).select_related('supplier')
        
        if not all_products.exists():
            cls.objects.filter(supplier_product__product_variant__product=product).delete()
            return

        # Only consider active products for min/max calculations
        active_products = all_products.filter(is_active=True)
        
        # Handle cases where all products are inactive
        if not active_products.exists():
            for sp in all_products:
                cls.objects.update_or_create(
                    supplier_product=sp,
                    defaults={
                        'cost_score': 0.0,
                        'quantity_score': 0.0,
                        'overall_score': 0.0
                    }
                )
            return

        # Calculate min/max only from active products
        costs = [float(p.cost) for p in active_products]
        quantities = [p.min_order_quantity for p in active_products]
        
        min_cost, max_cost = min(costs), max(costs)
        min_qty, max_qty = min(quantities), max(quantities)

        for sp in all_products:
            if not sp.is_active:
                # Set all scores to 0 for inactive products
                cls.objects.update_or_create(
                    supplier_product=sp,
                    defaults={
                        'cost_score': 0.0,
                        'quantity_score': 0.0,
                        'overall_score': 0.0
                    }
                )
                continue
                
            # Proceed with normal calculation for active products
            score, created = cls.objects.get_or_create(supplier_product=sp)
            
            # Cost score (5 = cheapest, 1 = most expensive)
            if max_cost == min_cost:
                score.cost_score = 5.0
            else:
                cost_normalized = (float(sp.cost) - min_cost) / (max_cost - min_cost)
                score.cost_score = round(5.0 - (4.0 * cost_normalized), 2)
            
            # Quantity score (5 = lowest MOQ, 1 = highest MOQ)
            if max_qty == min_qty:
                score.quantity_score = 5.0
            else:
                qty_normalized = (sp.min_order_quantity - min_qty) / (max_qty - min_qty)
                score.quantity_score = round(5.0 - (4.0 * qty_normalized), 2)
            
            # Overall score (90% cost, 10% quantity)
            score.overall_score = round(
                (score.cost_score * 0.9) + (score.quantity_score * 0.1),
                2
            )
            score.save()

# Signals
@receiver(post_save, sender=SupplierProduct)
def update_scores(sender, instance, **kwargs):
    """Update scores when SupplierProduct is saved"""
    SupplierProductScore.calculate_scores_for_product(instance.product_variant.product)

@receiver(post_delete, sender=SupplierProduct)
def rescore_on_delete(sender, instance, **kwargs):
    """Update scores when SupplierProduct is deleted"""
    SupplierProductScore.calculate_scores_for_product(instance.product_variant.product)

@receiver(post_save, sender=Supplier)
def update_supplier_scores(sender, instance, **kwargs):
    """Update all scores when Supplier changes"""
    for sp in instance.supplied_product_variants.all():
        SupplierProductScore.calculate_scores_for_product(sp.product_variant.product)
