from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Warehouse"
        verbose_name_plural = "Warehouses"


class Product(models.Model):
    UNIT_TYPES = [
        ('bag', 'Bag'),
        ('bundle', 'Bundle'),
        ('pcs', 'Pieces'),
        ('kg', 'Kilogram'),
        ('sqft', 'Square Feet'),
        ('liter', 'Liter'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPES)
    unit_name = models.CharField(max_length=50)
    brand = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    cost_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    min_stock_level = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.brand})"

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"


class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name} - {self.quantity}"

    @property
    def total_value(self):
        return self.quantity * self.unit_cost

    @classmethod
    def update_stock(cls, product, warehouse, quantity_change, unit_cost=None, movement_type='adjustment', reference='', description='', user=None):
        """Update stock quantity and create movement record"""
        from django.db import transaction
        
        with transaction.atomic():
            # Get or create stock record
            stock, created = cls.objects.get_or_create(
                product=product,
                warehouse=warehouse,
                defaults={'quantity': 0, 'unit_cost': unit_cost or 0}
            )
            
            # Update quantity
            if movement_type == 'inward':
                stock.quantity += quantity_change
            elif movement_type == 'outward':
                stock.quantity -= quantity_change
            else:  # adjustment
                stock.quantity = quantity_change
            
            # Update unit cost if provided
            if unit_cost is not None:
                stock.unit_cost = unit_cost
            
            stock.save()
            
            # Create movement record
            StockMovement.objects.create(
                product=product,
                warehouse=warehouse,
                movement_type=movement_type,
                quantity=abs(quantity_change),
                unit_cost=unit_cost or stock.unit_cost,
                reference=reference,
                description=description,
                movement_date=timezone.now(),
                created_by=user
            )
            
            # Check for low stock alert
            if stock.quantity <= product.min_stock_level:
                StockAlert.objects.get_or_create(
                    product=product,
                    warehouse=warehouse,
                    defaults={
                        'current_quantity': stock.quantity,
                        'min_quantity': product.min_stock_level,
                        'is_active': True
                    }
                )
            
            return stock

    class Meta:
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"
        unique_together = ['product', 'warehouse']


class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('inward', 'Inward'),
        ('outward', 'Outward'),
        ('transfer', 'Transfer'),
        ('adjustment', 'Adjustment'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    movement_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.movement_type} - {self.quantity}"

    class Meta:
        verbose_name = "Stock Movement"
        verbose_name_plural = "Stock Movements"


class StockAlert(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    current_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    min_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Low Stock Alert - {self.product.name}"

    class Meta:
        verbose_name = "Stock Alert"
        verbose_name_plural = "Stock Alerts"
