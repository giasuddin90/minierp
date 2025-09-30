from django.urls import path
from . import views

app_name = 'accounting'

urlpatterns = [
    # Bank Management
    path('banks/', views.BankAccountListView.as_view(), name='bank_list'),
    path('banks/create/', views.BankAccountCreateView.as_view(), name='bank_create'),
    path('banks/<int:pk>/', views.BankAccountDetailView.as_view(), name='bank_detail'),
    path('banks/<int:pk>/edit/', views.BankAccountUpdateView.as_view(), name='bank_edit'),
    path('banks/<int:pk>/delete/', views.BankAccountDeleteView.as_view(), name='bank_delete'),
    
    # Bank Transactions
    path('banks/<int:bank_id>/transactions/', views.BankTransactionListView.as_view(), name='bank_transaction_list'),
    path('banks/<int:bank_id>/transactions/create/', views.BankTransactionCreateView.as_view(), name='bank_transaction_create'),
    
    # Loan Management
    path('loans/', views.LoanListView.as_view(), name='loan_list'),
    path('loans/create/', views.LoanCreateView.as_view(), name='loan_create'),
    path('loans/<int:pk>/', views.LoanDetailView.as_view(), name='loan_detail'),
    path('loans/<int:pk>/edit/', views.LoanUpdateView.as_view(), name='loan_edit'),
    path('loans/<int:pk>/delete/', views.LoanDeleteView.as_view(), name='loan_delete'),
    
    # Trial Balance
    path('trial-balance/', views.TrialBalanceListView.as_view(), name='trial_balance_list'),
    path('trial-balance/create/', views.TrialBalanceCreateView.as_view(), name='trial_balance_create'),
    path('trial-balance/<int:pk>/', views.TrialBalanceDetailView.as_view(), name='trial_balance_detail'),
    path('trial-balance/<int:pk>/edit/', views.TrialBalanceUpdateView.as_view(), name='trial_balance_edit'),
    path('trial-balance/<int:pk>/delete/', views.TrialBalanceDeleteView.as_view(), name='trial_balance_delete'),
    
    # Reports
    path('reports/daily/', views.DailyReportView.as_view(), name='daily_report'),
    path('reports/monthly/', views.MonthlyReportView.as_view(), name='monthly_report'),
    path('reports/bank/', views.BankReportView.as_view(), name='bank_report'),
    
    # Enhanced Loan Management
    path('loans/<int:loan_id>/transactions/', views.LoanTransactionListView.as_view(), name='loan_transaction_list'),
    path('loans/<int:loan_id>/transactions/create/', views.LoanTransactionCreateView.as_view(), name='loan_transaction_create'),
    path('loans/<int:loan_id>/payment/', views.process_loan_payment, name='process_loan_payment'),
    path('loans/<int:loan_id>/calculate-interest/', views.calculate_loan_interest, name='calculate_loan_interest'),
    
    # Banking Dashboard
    path('dashboard/', views.BankingDashboardView.as_view(), name='banking_dashboard'),
    
    # Expense Management
    path('expenses/', views.ExpenseListView.as_view(), name='expense_list'),
    path('expenses/create/', views.ExpenseCreateView.as_view(), name='expense_create'),
    path('expenses/<int:pk>/edit/', views.ExpenseUpdateView.as_view(), name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.ExpenseDeleteView.as_view(), name='expense_delete'),
    
    # Income Management
    path('income/', views.IncomeListView.as_view(), name='income_list'),
    path('income/create/', views.IncomeCreateView.as_view(), name='income_create'),
    path('income/<int:pk>/edit/', views.IncomeUpdateView.as_view(), name='income_edit'),
    path('income/<int:pk>/delete/', views.IncomeDeleteView.as_view(), name='income_delete'),
    
    # Chart of Accounts
    path('accounts/', views.AccountListView.as_view(), name='account_list'),
    path('accounts/create/', views.AccountCreateView.as_view(), name='account_create'),
    path('accounts/<int:pk>/edit/', views.AccountUpdateView.as_view(), name='account_edit'),
    
    # Enhanced Trial Balance
    path('trial-balance/enhanced/', views.EnhancedTrialBalanceView.as_view(), name='enhanced_trial_balance'),
    path('daily-summary/', views.DailyFinancialSummaryView.as_view(), name='daily_financial_summary'),
]
