from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from suppliers.models import Supplier
from stock.models import Product, Warehouse


class PurchaseOrder(models.Model):
    ORDER_STATUS = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    order_date = models.DateField()
    expected_date = models.DateField()
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='draft')
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PO-{self.order_number} - {self.supplier.name}"

    def receive_goods(self, user=None):
        """Receive goods and update inventory"""
        from stock.models import Stock
        
        if self.status != 'received':
            self.status = 'received'
            self.save()
            
            # Update inventory for each item
            for item in self.items.all():
                # Increase stock (inward movement)
                Stock.update_stock(
                    product=item.product,
                    warehouse=item.warehouse,
                    quantity_change=item.quantity,
                    unit_cost=item.unit_price,
                    movement_type='inward',
                    reference=f"PO-{self.order_number}",
                    description=f"Purchase order receipt - {self.supplier.name}",
                    user=user
                )

    class Meta:
        verbose_name = "Purchase Order"
        verbose_name_plural = "Purchase Orders"


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.purchase_order.order_number} - {self.product.name}"

    class Meta:
        verbose_name = "Purchase Order Item"
        verbose_name_plural = "Purchase Order Items"


class GoodsReceipt(models.Model):
    RECEIPT_STATUS = [
        ('draft', 'Draft'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]
    
    receipt_number = models.CharField(max_length=50, unique=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    receipt_date = models.DateField()
    status = models.CharField(max_length=20, choices=RECEIPT_STATUS, default='draft')
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"GR-{self.receipt_number} - {self.purchase_order.supplier.name}"

    class Meta:
        verbose_name = "Goods Receipt"
        verbose_name_plural = "Goods Receipts"


class GoodsReceiptItem(models.Model):
    goods_receipt = models.ForeignKey(GoodsReceipt, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.goods_receipt.receipt_number} - {self.product.name}"

    class Meta:
        verbose_name = "Goods Receipt Item"
        verbose_name_plural = "Goods Receipt Items"


class PurchaseInvoice(models.Model):
    PAYMENT_TYPES = [
        ('cash', 'Cash'),
        ('credit', 'Credit'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True)
    goods_receipt = models.ForeignKey(GoodsReceipt, on_delete=models.SET_NULL, null=True, blank=True)
    invoice_date = models.DateField()
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    due_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PINV-{self.invoice_number} - {self.supplier.name}"

    class Meta:
        verbose_name = "Purchase Invoice"
        verbose_name_plural = "Purchase Invoices"


class PurchaseInvoiceItem(models.Model):
    purchase_invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.purchase_invoice.invoice_number} - {self.product.name}"

    class Meta:
        verbose_name = "Purchase Invoice Item"
        verbose_name_plural = "Purchase Invoice Items"


class PurchaseReturn(models.Model):
    RETURN_STATUS = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
    ]
    
    return_number = models.CharField(max_length=50, unique=True)
    purchase_invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.CASCADE)
    return_date = models.DateField()
    status = models.CharField(max_length=20, choices=RETURN_STATUS, default='draft')
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    reason = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PRET-{self.return_number} - {self.purchase_invoice.supplier.name}"

    class Meta:
        verbose_name = "Purchase Return"
        verbose_name_plural = "Purchase Returns"


class PurchaseReturnItem(models.Model):
    purchase_return = models.ForeignKey(PurchaseReturn, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.purchase_return.return_number} - {self.product.name}"

    class Meta:
        verbose_name = "Purchase Return Item"
        verbose_name_plural = "Purchase Return Items"


class PurchasePayment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('other', 'Other'),
    ]
    
    purchase_invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.CASCADE)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.purchase_invoice.invoice_number} - {self.amount}"

    class Meta:
        verbose_name = "Purchase Payment"
        verbose_name_plural = "Purchase Payments"
