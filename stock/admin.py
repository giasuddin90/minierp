from django.contrib import admin
from .models import ProductCategory, ProductBrand, Product, Stock, StockAlert


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProductBrand)
class ProductBrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']




@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'brand', 'unit_type', 'cost_price', 'selling_price', 'is_active']
    list_filter = ['category', 'brand', 'unit_type', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'category__name', 'brand__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'unit_cost', 'total_value']
    list_filter = ['last_updated']
    search_fields = ['product__name']
    readonly_fields = ['last_updated']




@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ['product', 'current_quantity', 'min_quantity', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['product__name']
    readonly_fields = ['created_at']
