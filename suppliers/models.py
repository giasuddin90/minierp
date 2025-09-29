from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    terms = models.TextField(blank=True)
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def set_opening_balance(self, amount, user=None):
        """Set opening balance and create ledger entry"""
        self.opening_balance = amount
        self.current_balance = amount
        self.save()
        
        # Create opening balance ledger entry
        SupplierLedger.objects.create(
            supplier=self,
            transaction_type='opening_balance',
            amount=amount,
            description=f"Opening balance set to ৳{amount}",
            reference="OPENING",
            transaction_date=timezone.now(),
            created_by=user
        )

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"


class SupplierLedger(models.Model):
    TRANSACTION_TYPES = [
        ('opening_balance', 'Opening Balance'),
        ('purchase', 'Purchase'),
        ('return', 'Return'),
        ('payment', 'Payment'),
        ('adjustment', 'Adjustment'),
        ('commission', 'Commission'),
    ]
    
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    reference = models.CharField(max_length=100, blank=True)
    transaction_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.supplier.name} - {self.transaction_type} - {self.amount}"

    class Meta:
        verbose_name = "Supplier Ledger"
        verbose_name_plural = "Supplier Ledgers"


class SupplierCommission(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)
    is_per_transaction = models.BooleanField(default=False)
    is_per_party = models.BooleanField(default=True)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.supplier.name} - {self.commission_rate}%"

    class Meta:
        verbose_name = "Supplier Commission"
        verbose_name_plural = "Supplier Commissions"
