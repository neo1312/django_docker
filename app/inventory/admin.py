from django.contrib import admin
from .models import Product, ProductVariant, Brand
from .models import InventoryItem, StatusChangeLog

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity', 'last_updated',)
    list_editable = ('price', 'quantity')
    search_fields = ('name',)
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'

    @admin.display(description='Last Updated')
    def last_updated(self, obj):
        return obj.updated_at.strftime("%Y-%m-%d %H:%M")


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product','brand','stock','barcode')
    list_filter = ('is_active', 'product')
    search_fields = ('product__name',)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)



@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('id','product_variant', 'sequential_id', 'current_status', 'location_in_warehouse')
    list_filter = ('current_status', 'supplier')
    search_fields = ('product_variant__name', 'sequential_id')
    readonly_fields = ('status_changed','sequential_id')

@admin.register(StatusChangeLog)
class StatusChangeLogAdmin(admin.ModelAdmin):
    list_display = ('inventory_item', 'old_status', 'new_status', 'change_date','changed_by')
    list_filter = ('new_status',)
    search_fields = ('inventory_item__product_variant__name',)

