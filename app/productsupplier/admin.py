from django.contrib import admin
from .models import SupplierProduct,SupplierProductScore

@admin.register(SupplierProduct)
class SupplierProductAdmin(admin.ModelAdmin):
    list_display = ('get_product_name', 'supplier', 'cost', 'min_order_quantity', 'is_active', 'updated_at')
    list_filter = ('is_active', 'supplier', 'min_order_quantity')
    search_fields = ('product_variant__product__name', 'supplier__name')
    list_editable = ('cost', 'is_active')
    raw_id_fields = ('product_variant',)  # Useful if you have many variants
    ordering = ('product_variant__product__name',)
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_product_name(self, obj):
        return obj.product_variant.product.name
    get_product_name.short_description = 'Product Name'
    get_product_name.admin_order_field = 'product_variant__product__name'


@admin.register(SupplierProductScore)
class SupplierProductScoreAdmin(admin.ModelAdmin):
    # Only use fields that exist in SupplierProductScore model
    list_display = (
        'supplier_product',  # ForeignKey to SupplierProduct
        'cost_score',
        'quantity_score', 
        'overall_score'
    )
    
    readonly_fields = (
        'cost_score',
        'quantity_score',
        'overall_score'
    )
