from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    # Customer Management
    path('', views.CustomerListView.as_view(), name='customer_list'),
    path('create/', views.CustomerCreateView.as_view(), name='customer_create'),
    path('<int:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),
    path('<int:pk>/edit/', views.CustomerUpdateView.as_view(), name='customer_edit'),
    path('<int:pk>/delete/', views.CustomerDeleteView.as_view(), name='customer_delete'),
    
    # Customer Ledger
    path('<int:pk>/ledger/', views.CustomerLedgerDetailView.as_view(), name='customer_ledger_detail'),
    path('<int:customer_id>/ledger/create/', views.CustomerLedgerCreateView.as_view(), name='customer_ledger_create'),
    path('<int:pk>/opening-balance/', views.set_opening_balance, name='customer_opening_balance'),
    
    # Customer Commission
    path('<int:customer_id>/commissions/', views.CustomerCommissionListView.as_view(), name='customer_commission_list'),
    path('<int:customer_id>/commissions/create/', views.CustomerCommissionCreateView.as_view(), name='customer_commission_create'),
    
    # Customer Commitments
    path('<int:customer_id>/commitments/', views.CustomerCommitmentListView.as_view(), name='customer_commitment_list'),
    path('<int:customer_id>/commitments/create/', views.CustomerCommitmentCreateView.as_view(), name='customer_commitment_create'),
    
    # General views (without customer_id)
    path('ledger/', views.CustomerLedgerListView.as_view(), name='ledger_list'),
    path('ledger/create/', views.CustomerLedgerCreateView.as_view(), name='ledger_create'),
    path('commission/', views.CustomerCommissionListView.as_view(), name='commission_list'),
    path('commission/create/', views.CustomerCommissionCreateView.as_view(), name='commission_create'),
    path('commitment/', views.CustomerCommitmentListView.as_view(), name='commitment_list'),
    path('commitment/create/', views.CustomerCommitmentCreateView.as_view(), name='commitment_create'),
]
