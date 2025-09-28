from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Customer(models.Model):
    CUSTOMER_TYPES = [
        ('retail', 'Retail'),
        ('wholesale', 'Wholesale'),
    ]
    
    name = models.CharField(max_length=200)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPES)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.customer_type})"

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"


class CustomerLedger(models.Model):
    TRANSACTION_TYPES = [
        ('sale', 'Sale'),
        ('return', 'Return'),
        ('payment', 'Payment'),
        ('adjustment', 'Adjustment'),
        ('commission', 'Commission'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    reference = models.CharField(max_length=100, blank=True)
    transaction_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} - {self.transaction_type} - {self.amount}"

    class Meta:
        verbose_name = "Customer Ledger"
        verbose_name_plural = "Customer Ledgers"


class CustomerCommission(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)
    is_per_transaction = models.BooleanField(default=False)
    is_per_party = models.BooleanField(default=True)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} - {self.commission_rate}%"

    class Meta:
        verbose_name = "Customer Commission"
        verbose_name_plural = "Customer Commissions"


class CustomerCommitment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    commitment_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    is_reminded = models.BooleanField(default=False)
    is_fulfilled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} - {self.commitment_date} - {self.amount}"

    class Meta:
        verbose_name = "Customer Commitment"
        verbose_name_plural = "Customer Commitments"
