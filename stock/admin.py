from django.contrib import admin
from .models import Product, Stock, StockMovement, StockAlert




@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'unit_type', 'cost_price', 'selling_price', 'is_active']
    list_filter = ['unit_type', 'is_active', 'created_at']
    search_fields = ['name', 'brand', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'unit_cost', 'total_value']
    list_filter = ['last_updated']
    search_fields = ['product__name']
    readonly_fields = ['last_updated']


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'movement_date', 'created_by']
    list_filter = ['movement_type', 'movement_date', 'created_at']
    search_fields = ['product__name', 'reference', 'description']
    readonly_fields = ['created_at']


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['product', 'current_quantity', 'min_quantity', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['product__name']
    readonly_fields = ['created_at']
