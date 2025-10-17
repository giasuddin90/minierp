from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'sales'

def sales_redirect(request):
    return redirect('sales:order_list')

urlpatterns = [
    # Default redirect to orders
    path('', sales_redirect, name='sales_home'),
    
    # Sales Orders
    path('orders/', views.SalesOrderListView.as_view(), name='order_list'),
    path('orders/create/', views.SalesOrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/', views.SalesOrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/edit/', views.SalesOrderUpdateView.as_view(), name='order_edit'),
    path('orders/<int:pk>/delete/', views.SalesOrderDeleteView.as_view(), name='order_delete'),
    
    # Sales Invoices
    path('invoices/', views.SalesInvoiceListView.as_view(), name='invoice_list'),
    path('invoices/create/', views.SalesInvoiceCreateView.as_view(), name='invoice_create'),
    path('invoices/<int:pk>/', views.SalesInvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<int:pk>/edit/', views.SalesInvoiceUpdateView.as_view(), name='invoice_edit'),
    path('invoices/<int:pk>/delete/', views.SalesInvoiceDeleteView.as_view(), name='invoice_delete'),
    
    # Sales Returns
    path('returns/', views.SalesReturnListView.as_view(), name='return_list'),
    path('returns/create/', views.SalesReturnCreateView.as_view(), name='return_create'),
    path('returns/<int:pk>/', views.SalesReturnDetailView.as_view(), name='return_detail'),
    path('returns/<int:pk>/edit/', views.SalesReturnUpdateView.as_view(), name='return_edit'),
    path('returns/<int:pk>/delete/', views.SalesReturnDeleteView.as_view(), name='return_delete'),
    
    # Sales Payments
    path('payments/', views.SalesPaymentListView.as_view(), name='payment_list'),
    path('payments/create/', views.SalesPaymentCreateView.as_view(), name='payment_create'),
    path('payments/<int:pk>/edit/', views.SalesPaymentUpdateView.as_view(), name='payment_edit'),
    path('payments/<int:pk>/delete/', views.SalesPaymentDeleteView.as_view(), name='payment_delete'),
    
    # Reports
    path('reports/daily/', views.SalesDailyReportView.as_view(), name='sales_daily_report'),
    path('reports/monthly/', views.SalesMonthlyReportView.as_view(), name='sales_monthly_report'),
    path('reports/customer/', views.SalesCustomerReportView.as_view(), name='sales_customer_report'),
    
    # Invoice from Order
    path('orders/<int:order_id>/create-invoice/', views.create_invoice_from_order, name='create_invoice_from_order'),
    
    # PDF and Payment
    path('invoices/<int:invoice_id>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    path('invoices/<int:invoice_id>/payment/', views.process_invoice_payment, name='process_invoice_payment'),
]
