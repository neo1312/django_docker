from django.contrib import admin
from .models import Product, ProductVariant

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity', 'last_updated')
    list_editable = ('price', 'quantity')
    search_fields = ('name',)
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'

    @admin.display(description='Last Updated')
    def last_updated(self, obj):
        return obj.updated_at.strftime("%Y-%m-%d %H:%M")


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product','brand','stock')
    list_filter = ('is_active', 'product')
    search_fields = ('product__name',)
