from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from customers.models import Customer
from stock.models import Product, Warehouse


class SalesOrder(models.Model):
    ORDER_STATUS = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateField()
    delivery_date = models.DateField()
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='draft')
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SO-{self.order_number} - {self.customer.name}"

    class Meta:
        verbose_name = "Sales Order"
        verbose_name_plural = "Sales Orders"


class SalesOrderItem(models.Model):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.sales_order.order_number} - {self.product.name}"

    class Meta:
        verbose_name = "Sales Order Item"
        verbose_name_plural = "Sales Order Items"


class SalesInvoice(models.Model):
    PAYMENT_TYPES = [
        ('cash', 'Cash'),
        ('credit', 'Credit'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.SET_NULL, null=True, blank=True)
    invoice_date = models.DateField()
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    labor_charges = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    due_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    is_sms_sent = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"INV-{self.invoice_number} - {self.customer.name}"

    class Meta:
        verbose_name = "Sales Invoice"
        verbose_name_plural = "Sales Invoices"


class SalesInvoiceItem(models.Model):
    sales_invoice = models.ForeignKey(SalesInvoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.sales_invoice.invoice_number} - {self.product.name}"

    class Meta:
        verbose_name = "Sales Invoice Item"
        verbose_name_plural = "Sales Invoice Items"


class SalesReturn(models.Model):
    RETURN_STATUS = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
    ]
    
    return_number = models.CharField(max_length=50, unique=True)
    sales_invoice = models.ForeignKey(SalesInvoice, on_delete=models.CASCADE)
    return_date = models.DateField()
    status = models.CharField(max_length=20, choices=RETURN_STATUS, default='draft')
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    reason = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RET-{self.return_number} - {self.sales_invoice.customer.name}"

    class Meta:
        verbose_name = "Sales Return"
        verbose_name_plural = "Sales Returns"


class SalesReturnItem(models.Model):
    sales_return = models.ForeignKey(SalesReturn, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.sales_return.return_number} - {self.product.name}"

    class Meta:
        verbose_name = "Sales Return Item"
        verbose_name_plural = "Sales Return Items"


class SalesPayment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('other', 'Other'),
    ]
    
    sales_invoice = models.ForeignKey(SalesInvoice, on_delete=models.CASCADE)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sales_invoice.invoice_number} - {self.amount}"

    class Meta:
        verbose_name = "Sales Payment"
        verbose_name_plural = "Sales Payments"
