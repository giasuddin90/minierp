from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Dashboard
    path('', views.ReportDashboardView.as_view(), name='dashboard'),
    
    # Financial Reports
    path('financial/', views.FinancialReportView.as_view(), name='financial_report'),
    
    # Inventory Reports
    path('inventory/', views.InventoryReportView.as_view(), name='inventory_report'),
    
    # Sales Reports
    path('sales/', views.SalesReportView.as_view(), name='sales_report'),
    
    # Purchase Reports
    path('purchase/', views.PurchaseReportView.as_view(), name='purchase_report'),
    
    # Customer Reports
    path('customer/', views.CustomerReportView.as_view(), name='customer_report'),
    
    # Supplier Reports
    path('supplier/', views.SupplierReportView.as_view(), name='supplier_report'),
    
    # Report Templates
    path('templates/', views.ReportTemplateListView.as_view(), name='template_list'),
    path('templates/create/', views.ReportTemplateCreateView.as_view(), name='template_create'),
    path('templates/<int:pk>/edit/', views.ReportTemplateUpdateView.as_view(), name='template_edit'),
    path('templates/<int:pk>/delete/', views.ReportTemplateDeleteView.as_view(), name='template_delete'),
    
    # Report Logs
    path('logs/', views.ReportLogListView.as_view(), name='log_list'),
    
    # Generate Reports
    path('generate/<str:report_type>/', views.generate_report, name='generate_report'),
]
