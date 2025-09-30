from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
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


# Account Categories
class AccountCategory(models.Model):
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=[
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('income', 'Income'),
        ('expense', 'Expense'),
    ])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"

    class Meta:
        verbose_name = "Account Category"
        verbose_name_plural = "Account Categories"


# Chart of Accounts
class Account(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(AccountCategory, on_delete=models.CASCADE)
    parent_account = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"


# Expense Categories
class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Expense Category"
        verbose_name_plural = "Expense Categories"


# Income Categories
class IncomeCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Income Category"
        verbose_name_plural = "Income Categories"


# Expenses
class Expense(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('check', 'Check'),
        ('card', 'Credit/Debit Card'),
    ]
    
    expense_category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    bank_account = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, null=True, blank=True)
    expense_date = models.DateField()
    reference = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.expense_category.name} - ৳{self.amount}"

    class Meta:
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"


# Income
class Income(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('check', 'Check'),
        ('card', 'Credit/Debit Card'),
    ]
    
    income_category = models.ForeignKey(IncomeCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    bank_account = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, null=True, blank=True)
    income_date = models.DateField()
    reference = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.income_category.name} - ৳{self.amount}"

    class Meta:
        verbose_name = "Income"
        verbose_name_plural = "Income"


# Journal Entries
class JournalEntry(models.Model):
    entry_number = models.CharField(max_length=50, unique=True)
    entry_date = models.DateField()
    description = models.TextField()
    reference = models.CharField(max_length=100, blank=True)
    total_debit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_balanced = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"JE-{self.entry_number} - {self.entry_date}"

    class Meta:
        verbose_name = "Journal Entry"
        verbose_name_plural = "Journal Entries"


# Journal Entry Lines
class JournalEntryLine(models.Model):
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='lines')
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    description = models.TextField()
    debit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.account.name} - Dr: ৳{self.debit_amount} Cr: ৳{self.credit_amount}"

    class Meta:
        verbose_name = "Journal Entry Line"
        verbose_name_plural = "Journal Entry Lines"


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
