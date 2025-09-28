from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    # Purchase Orders
    path('orders/', views.PurchaseOrderListView.as_view(), name='order_list'),
    path('orders/create/', views.PurchaseOrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/', views.PurchaseOrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/edit/', views.PurchaseOrderUpdateView.as_view(), name='order_edit'),
    path('orders/<int:pk>/delete/', views.PurchaseOrderDeleteView.as_view(), name='order_delete'),
    
    # Goods Receipts
    path('receipts/', views.GoodsReceiptListView.as_view(), name='receipt_list'),
    path('receipts/create/', views.GoodsReceiptCreateView.as_view(), name='receipt_create'),
    path('receipts/<int:pk>/', views.GoodsReceiptDetailView.as_view(), name='receipt_detail'),
    path('receipts/<int:pk>/edit/', views.GoodsReceiptUpdateView.as_view(), name='receipt_edit'),
    path('receipts/<int:pk>/delete/', views.GoodsReceiptDeleteView.as_view(), name='receipt_delete'),
    
    # Purchase Invoices
    path('invoices/', views.PurchaseInvoiceListView.as_view(), name='invoice_list'),
    path('invoices/create/', views.PurchaseInvoiceCreateView.as_view(), name='invoice_create'),
    path('invoices/<int:pk>/', views.PurchaseInvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<int:pk>/edit/', views.PurchaseInvoiceUpdateView.as_view(), name='invoice_edit'),
    path('invoices/<int:pk>/delete/', views.PurchaseInvoiceDeleteView.as_view(), name='invoice_delete'),
    
    # Purchase Returns
    path('returns/', views.PurchaseReturnListView.as_view(), name='return_list'),
    path('returns/create/', views.PurchaseReturnCreateView.as_view(), name='return_create'),
    path('returns/<int:pk>/', views.PurchaseReturnDetailView.as_view(), name='return_detail'),
    path('returns/<int:pk>/edit/', views.PurchaseReturnUpdateView.as_view(), name='return_edit'),
    path('returns/<int:pk>/delete/', views.PurchaseReturnDeleteView.as_view(), name='return_delete'),
    
    # Purchase Payments
    path('payments/', views.PurchasePaymentListView.as_view(), name='payment_list'),
    path('payments/create/', views.PurchasePaymentCreateView.as_view(), name='payment_create'),
    path('payments/<int:pk>/edit/', views.PurchasePaymentUpdateView.as_view(), name='payment_edit'),
    path('payments/<int:pk>/delete/', views.PurchasePaymentDeleteView.as_view(), name='payment_delete'),
    
    # Reports
    path('reports/daily/', views.PurchaseDailyReportView.as_view(), name='purchase_daily_report'),
    path('reports/monthly/', views.PurchaseMonthlyReportView.as_view(), name='purchase_monthly_report'),
    path('reports/supplier/', views.PurchaseSupplierReportView.as_view(), name='purchase_supplier_report'),
]
