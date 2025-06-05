from django.contrib import admin
from .models import Product

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
