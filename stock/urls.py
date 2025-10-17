from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    
    # Product Management
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    
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
