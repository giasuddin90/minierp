from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'stock'

def stock_redirect(request):
    return redirect('stock:product_list')

urlpatterns = [
    # Default redirect to products
    path('', stock_redirect, name='stock_home'),
    
    # Product Management
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('products/<int:pk>/adjust-stock/', views.stock_adjustment, name='stock_adjustment'),
    
    # Category Management
    path('categories/', views.ProductCategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.ProductCategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.ProductCategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.ProductCategoryDeleteView.as_view(), name='category_delete'),
    
    # Brand Management
    path('brands/', views.ProductBrandListView.as_view(), name='brand_list'),
    path('brands/create/', views.ProductBrandCreateView.as_view(), name='brand_create'),
    path('brands/<int:pk>/edit/', views.ProductBrandUpdateView.as_view(), name='brand_edit'),
    path('brands/<int:pk>/delete/', views.ProductBrandDeleteView.as_view(), name='brand_delete'),
    
    # UnitType Management
    path('unit-types/', views.UnitTypeListView.as_view(), name='unittype_list'),
    path('unit-types/create/', views.UnitTypeCreateView.as_view(), name='unittype_create'),
    path('unit-types/<int:pk>/edit/', views.UnitTypeUpdateView.as_view(), name='unittype_edit'),
    path('unit-types/<int:pk>/delete/', views.UnitTypeDeleteView.as_view(), name='unittype_delete'),
    
    # Stock Management
    path('stock/', views.StockListView.as_view(), name='stock_list'),
    path('stock/<int:pk>/', views.StockDetailView.as_view(), name='stock_detail'),
    path('stock/<int:pk>/edit/', views.StockUpdateView.as_view(), name='stock_edit'),
    
    # Stock Alerts
    path('alerts/', views.StockAlertListView.as_view(), name='alert_list'),
    
    # Reports
    path('reports/stock/', views.StockReportView.as_view(), name='stock_report'),
    path('reports/valuation/', views.StockValuationReportView.as_view(), name='stock_valuation_report'),
    
    # Inventory Dashboard
    path('dashboard/', views.InventoryDashboardView.as_view(), name='inventory_dashboard'),
]
