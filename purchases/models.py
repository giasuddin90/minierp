from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from suppliers.models import Supplier
from stock.models import Product


class PurchaseOrder(models.Model):
    ORDER_STATUS = [
        ('purchase-order', 'Purchase Order'),
        ('goods-received', 'Goods Received'),
        ('canceled', 'Canceled'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    order_date = models.DateField()
    expected_date = models.DateField()
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='purchase-order')
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
        
        if self.status != 'goods-received':
            self.status = 'goods-received'
            self.save()
            
            # Update inventory for each item
            for item in self.items.all():
                # Increase stock (inward movement)
                Stock.update_stock(
                    product=item.product,
                    quantity_change=item.quantity,
                    unit_cost=item.unit_price,
                    movement_type='inward',
                    reference=f"PO-{self.order_number}",
                    description=f"Purchase order receipt - {self.supplier.name}",
                    user=user
                )
    
    def cancel_order(self, user=None):
        """Cancel the purchase order"""
        if self.status == 'purchase-order':
            self.status = 'canceled'
            self.save()

    class Meta:
        verbose_name = "Purchase Order"
        verbose_name_plural = "Purchase Orders"


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.purchase_order.order_number} - {self.product.name}"

    class Meta:
        verbose_name = "Purchase Order Item"
        verbose_name_plural = "Purchase Order Items"


class GoodsReceipt(models.Model):
    receipt_number = models.CharField(max_length=50, unique=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, null=True, blank=True)
    receipt_date = models.DateField()
    invoice_id = models.CharField(max_length=100, blank=True, help_text="Invoice ID from supplier when goods are received")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.purchase_order:
            return f"GR-{self.receipt_number} - {self.purchase_order.supplier.name}"
        else:
            return f"GR-{self.receipt_number} - Direct Receipt"

    class Meta:
        verbose_name = "Goods Receipt"
        verbose_name_plural = "Goods Receipts"
