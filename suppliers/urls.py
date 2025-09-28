from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [
    # Supplier Management
    path('', views.SupplierListView.as_view(), name='supplier_list'),
    path('create/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('<int:pk>/', views.SupplierDetailView.as_view(), name='supplier_detail'),
    path('<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier_edit'),
    path('<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),
    
    # Supplier Ledger
    path('<int:supplier_id>/ledger/', views.SupplierLedgerListView.as_view(), name='supplier_ledger_list'),
    path('<int:supplier_id>/ledger/create/', views.SupplierLedgerCreateView.as_view(), name='supplier_ledger_create'),
    
    # Supplier Commission
    path('<int:supplier_id>/commissions/', views.SupplierCommissionListView.as_view(), name='supplier_commission_list'),
    path('<int:supplier_id>/commissions/create/', views.SupplierCommissionCreateView.as_view(), name='supplier_commission_create'),
]
