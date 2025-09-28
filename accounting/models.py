from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class BankAccount(models.Model):
    name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100, blank=True)
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.bank_name}"

    class Meta:
        verbose_name = "Bank Account"
        verbose_name_plural = "Bank Accounts"


class BankTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
    ]
    
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    reference = models.CharField(max_length=100, blank=True)
    transaction_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"

    class Meta:
        verbose_name = "Bank Transaction"
        verbose_name_plural = "Bank Transactions"


class Loan(models.Model):
    LOAN_STATUS = [
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]
    
    deal_number = models.CharField(max_length=50, unique=True)
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    principal_amount = models.DecimalField(max_digits=15, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    loan_date = models.DateField()
    maturity_date = models.DateField()
    status = models.CharField(max_length=20, choices=LOAN_STATUS, default='active')
    total_interest_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_principal_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Loan {self.deal_number} - {self.principal_amount}"

    @property
    def outstanding_amount(self):
        return self.principal_amount - self.total_principal_paid

    class Meta:
        verbose_name = "Loan"
        verbose_name_plural = "Loans"


class LoanTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('interest_payment', 'Interest Payment'),
        ('principal_payment', 'Principal Payment'),
        ('penalty', 'Penalty'),
    ]
    
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    transaction_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.loan.deal_number} - {self.transaction_type} - {self.amount}"

    class Meta:
        verbose_name = "Loan Transaction"
        verbose_name_plural = "Loan Transactions"


class TrialBalance(models.Model):
    date = models.DateField()
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cash_inflows = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cash_outflows = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    closing_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_balanced = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trial Balance - {self.date}"

    class Meta:
        verbose_name = "Trial Balance"
        verbose_name_plural = "Trial Balances"
        unique_together = ['date']
