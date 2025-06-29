from django.db import models
from core.models  import TimeStampedModel
from django.core.validators import MinValueValidator
from decimal import Decimal
from srm.models import Supplier
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Brand(TimeStampedModel):
    name = models.CharField(max_length=225, unique=True)
    def __str__(self):
        return self.name

class Product(TimeStampedModel):
    UNIT_CHOICES = [
            ('grams', 'Grams'),
            ('kilograms', 'Kilograms'),
            ('units', 'Units'),
            ('meters','Meters')
            ]
    name = models.CharField(max_length=100)
    min_stock = models.PositiveIntegerField(default=0)
    max_stock = models.PositiveIntegerField(default=0)
    quantity = models.IntegerField(default=0,validators=[MinValueValidator(0)])
    price = models.DecimalField(max_digits=10, decimal_places=2,validators=[MinValueValidator(Decimal("0.00"))])
    is_bulk = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} (${self.price:.2f})"

    @property
    def total_stock(self):
        return self.variants.aggregate(total=models.Sum('stock'))['total'] or 0

class ProductVariant(TimeStampedModel):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    barcode = models.CharField(max_length=50, unique=True)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.brand.name if self.brand else 'No Brand'}"


class InventoryItem(models.Model):
    STATUS_CHOICES = [
        ('ordered', 'Ordered'),
        ('received', 'Received in Warehouse'),
        ('quality_check', 'Quality Check'),
        ('ready_for_sale', 'Ready for Sale'),
        ('reserved', 'Reserved'),
        ('sold', 'Sold'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),
        ('discarded', 'Discarded'),
    ]

    STATUS_TRANSITION_RULES = {
        'ordered': ['received', 'discarded'],
        'received': ['quality_check', 'returned', 'discarded'],
        'quality_check': ['ready_for_sale', 'returned', 'discarded'],
        'ready_for_sale': ['reserved', 'returned', 'discarded'],
        'reserved': ['sold', 'ready_for_sale'],
        'sold': ['shipped', 'returned'],
        'shipped': ['delivered', 'returned'],
        'delivered': ['returned'],
        'returned': ['ready_for_sale', 'discarded'],
        'discarded': []
    }

    # Basic Information
    id = models.AutoField(primary_key=True) 
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="inventory_items")
    sequential_id = models.PositiveIntegerField()
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Financial Information
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_applied = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    # Status Tracking
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ordered')
    status_changed = models.DateTimeField(auto_now=True)
    
    # Timeline Dates
    date_ordered = models.DateTimeField(default=now)
    date_received = models.DateTimeField(null=True, blank=True)
    date_quality_check = models.DateTimeField(null=True, blank=True)
    date_ready_for_sale = models.DateTimeField(null=True, blank=True)
    date_reserved = models.DateTimeField(null=True, blank=True)
    date_sold = models.DateTimeField(null=True, blank=True)
    date_shipped = models.DateTimeField(null=True, blank=True)
    date_delivered = models.DateTimeField(null=True, blank=True)
    date_returned = models.DateTimeField(null=True, blank=True)
    date_discarded = models.DateTimeField(null=True, blank=True)
    
    # Additional Tracking Information
    purchase_order_reference = models.CharField(max_length=100, blank=True, null=True)
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    shipping_carrier = models.CharField(max_length=100, blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    location_in_warehouse = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Quality Control
    quality_check_passed = models.BooleanField(null=True, blank=True)
    quality_check_notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('product_variant', 'sequential_id')
        ordering = ['-status_changed']
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"
        indexes = [
            models.Index(fields=['current_status']),
            models.Index(fields=['status_changed']),
        ]

    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only for new instances
            last_id = InventoryItem.objects.filter(
                product_variant=self.product_variant
            ).aggregate(models.Max('sequential_id'))['sequential_id__max'] or 0
            self.sequential_id = last_id + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return (f"{self.product_variant.product.name} - "
                f"{self.product_variant.brand.name if self.product_variant.brand else 'No Brand'} - "
                f"ID: {self.sequential_id} - Status: {self.get_current_status_display()}")

    def clean(self):
        """Validate that dates make sense in sequence"""
        if self.date_received and self.date_ordered and self.date_received < self.date_ordered:
            raise ValidationError("Received date cannot be before ordered date")
        
        if self.date_sold and self.date_ready_for_sale and self.date_sold < self.date_ready_for_sale:
            raise ValidationError("Sold date cannot be before ready for sale date")

    def validate_status_transition(self, new_status):
        """Validate if status transition is allowed"""
        if new_status not in dict(self.STATUS_CHOICES):
            raise ValidationError(f"Invalid status: {new_status}")
        
        if new_status not in self.STATUS_TRANSITION_RULES.get(self.current_status, []):
            raise ValidationError(
                f"Cannot change status from {self.current_status} to {new_status}"
            )

    def update_status(self, new_status, user=None, notes=None, commit=True):
        """
        Enhanced status update with logging and validation
        """
        self.validate_status_transition(new_status)
        
        old_status = self.current_status
        self.current_status = new_status
        
        # Set the corresponding date field if it exists
        status_date_field = f"date_{new_status}"
        if hasattr(self, status_date_field) and getattr(self, status_date_field) is None:
            setattr(self, status_date_field, now())
        
        if commit:
            self.save()
            # Create log entry
            StatusChangeLog.objects.create(
                inventory_item=self,
                old_status=old_status,
                new_status=new_status,
                changed_by=user,
                notes=notes
            )

    @property
    def is_available_for_sale(self):
        """Check if item is available for sale"""
        return self.current_status == 'ready_for_sale'

    @property
    def is_in_stock(self):
        """Check if item is in stock (available or reserved)"""
        return self.current_status in ['ready_for_sale', 'reserved']

    @property
    def is_shipped(self):
        """Check if item has been shipped"""
        return self.current_status in ['shipped', 'delivered']

    def get_time_in_status(self):
        """Returns timedelta of how long in current status"""
        date_field = getattr(self, f"date_{self.current_status}")
        if date_field:
            return now() - date_field
        return None

    def get_status_history(self):
        """
        Returns a list of all status changes with their dates
        with proper status display names
        """
        history = []
        status_dict = dict(self.STATUS_CHOICES)
        
        for status, _ in self.STATUS_CHOICES:
            date = getattr(self, f"date_{status}", None)
            if date:
                history.append({
                    'status': status,
                    'status_display': status_dict.get(status, status),
                    'date': date
                })
        return sorted(history, key=lambda x: x['date'])

    def calculate_profit(self):
        """
        Calculate profit considering discount and tax
        Rounded to 2 decimal places
        """
        if not self.sale_price or not self.purchase_price:
            return 0
            
        subtotal = self.sale_price * (1 - self.discount_applied/100)
        taxed_amount = subtotal * (1 + self.tax_rate/100)
        return round(taxed_amount - self.purchase_price, 2)

    def get_current_location(self):
        """
        Determine current location based on status
        """
        if self.current_status in ['ordered', 'received', 'quality_check']:
            return "Warehouse - Incoming"
        elif self.current_status == 'ready_for_sale':
            return self.location_in_warehouse or "Warehouse - Storage"
        elif self.current_status in ['reserved', 'sold']:
            return "Warehouse - Picking Area"
        elif self.current_status in ['shipped', 'delivered']:
            return f"In Transit ({self.shipping_carrier or 'Unknown Carrier'})"
        else:
            return "Unknown"


class StatusChangeLog(models.Model):
    """Log of all status changes for inventory items"""
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='status_logs')
    old_status = models.CharField(max_length=20, choices=InventoryItem.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=InventoryItem.STATUS_CHOICES)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    change_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-change_date']
        verbose_name = "Status Change Log"
        verbose_name_plural = "Status Change Logs"

    def __str__(self):
        return f"{self.inventory_item} - {self.old_status} → {self.new_status}"
