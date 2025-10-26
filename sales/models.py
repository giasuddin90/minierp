from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from customers.models import Customer
from stock.models import Product


class SalesOrder(models.Model):
    ORDER_STATUS = [
        ('order', 'Order'),
        ('delivered', 'Delivered'),
        ('cancel', 'Cancel'),
    ]
    
    SALES_TYPE = [
        ('regular', 'Regular Sale'),
        ('instant', 'Instant Sale'),
    ]
    
    order_number = models.CharField(max_length=50, unique=True)
    sales_type = models.CharField(max_length=20, choices=SALES_TYPE, default='regular')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    customer_name = models.CharField(max_length=100, blank=True, help_text="For instant sales when no customer is selected")
    order_date = models.DateField()
    delivery_date = models.DateField(null=True, blank=True, help_text="Not required for instant sales")
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='order')
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        customer_name = self.customer.name if self.customer else self.customer_name or "Anonymous"
        return f"SO-{self.order_number} - {customer_name}"

    def mark_delivered(self, user=None):
        """Mark order as delivered and update inventory"""
        from stock.models import Stock
        
        if self.status == 'order':
            self.status = 'delivered'
            self.save()
            
            # Update inventory for each item
            customer_name = self.customer.name if self.customer else self.customer_name or "Anonymous"
            for item in self.items.all():
                # Reduce stock (outward movement)
                Stock.update_stock(
                    product=item.product,
                    quantity_change=item.quantity,
                    unit_cost=item.unit_price,
                    movement_type='outward',
                    reference=f"SO-{self.order_number}",
                    description=f"Sales order delivered - {customer_name}",
                    user=user
                )
    
    def cancel_order(self, user=None):
        """Cancel the order"""
        if self.status in ['order', 'delivered']:
            was_delivered = self.status == 'delivered'
            self.status = 'cancel'
            self.save()
            
            # If order was delivered, restore inventory
            if was_delivered:
                from stock.models import Stock
                customer_name = self.customer.name if self.customer else self.customer_name or "Anonymous"
                for item in self.items.all():
                    # Restore stock (inward movement)
                    Stock.update_stock(
                        product=item.product,
                        quantity_change=item.quantity,
                        unit_cost=item.unit_price,
                        movement_type='inward',
                        reference=f"SO-{self.order_number}",
                        description=f"Sales order cancelled - {customer_name}",
                        user=user
                    )

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


