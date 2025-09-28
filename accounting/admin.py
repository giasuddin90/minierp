from django.contrib import admin
from .models import BankAccount, BankTransaction, Loan, LoanTransaction, TrialBalance


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'bank_name', 'account_number', 'current_balance', 'is_active']
    list_filter = ['is_active', 'bank_name', 'created_at']
    search_fields = ['name', 'bank_name', 'account_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BankTransaction)
class BankTransactionAdmin(admin.ModelAdmin):
    list_display = ['bank_account', 'transaction_type', 'amount', 'transaction_date', 'created_by']
    list_filter = ['transaction_type', 'transaction_date', 'created_at']
    search_fields = ['bank_account__name', 'description', 'reference']
    readonly_fields = ['created_at']


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['deal_number', 'bank_account', 'principal_amount', 'status', 'outstanding_amount']
    list_filter = ['status', 'loan_date', 'created_at']
    search_fields = ['deal_number', 'bank_account__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LoanTransaction)
class LoanTransactionAdmin(admin.ModelAdmin):
    list_display = ['loan', 'transaction_type', 'amount', 'transaction_date', 'created_by']
    list_filter = ['transaction_type', 'transaction_date', 'created_at']
    search_fields = ['loan__deal_number', 'description']
    readonly_fields = ['created_at']


@admin.register(TrialBalance)
class TrialBalanceAdmin(admin.ModelAdmin):
    list_display = ['date', 'opening_balance', 'cash_inflows', 'cash_outflows', 'closing_balance', 'is_balanced']
    list_filter = ['date', 'is_balanced', 'created_at']
    search_fields = ['date']
    readonly_fields = ['created_at']
