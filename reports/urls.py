from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Enhanced Reports with Time Range Filtering
    path('sales-enhanced/', views.SalesReportEnhancedView.as_view(), name='sales_report_enhanced'),
    path('inventory-enhanced/', views.InventoryReportEnhancedView.as_view(), name='inventory_report_enhanced'),
    path('top-products/', views.TopSellingProductsReportView.as_view(), name='top_selling_products'),
    path('top-customers/', views.TopSellingCustomersReportView.as_view(), name='top_selling_customers'),
    path('accounts-receivable/', views.AccountsReceivableReportView.as_view(), name='accounts_receivable'),
    
    # CSV Download URLs
    path('download/sales-csv/', views.download_sales_report_csv, name='download_sales_csv'),
    path('download/inventory-csv/', views.download_inventory_report_csv, name='download_inventory_csv'),
    path('download/top-products-csv/', views.download_top_products_csv, name='download_top_products_csv'),
    path('download/top-customers-csv/', views.download_top_customers_csv, name='download_top_customers_csv'),
    path('download/receivables-csv/', views.download_receivables_csv, name='download_receivables_csv'),
]
