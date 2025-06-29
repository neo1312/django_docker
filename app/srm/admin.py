from django.contrib import admin
from .models import Supplier  # Import your Supplier model

@admin.register(Supplier)  # This decorator registers the model
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'reliability_score', 'credit_score', 'cost_delivery_score')  # Fields to display in list view
    search_fields = ('name',)  # Add search capability
    list_filter = ('reliability_score',)  # Add filters
    ordering = ('name',)  # Default ordering
