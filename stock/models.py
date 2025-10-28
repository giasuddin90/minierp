from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class ProductCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"
        ordering = ['name']


class ProductBrand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product Brand"
        verbose_name_plural = "Product Brands"
        ordering = ['name']


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
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    brand = models.ForeignKey(ProductBrand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPES)
    description = models.TextField(blank=True)
    cost_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    min_stock_level = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.brand})"
    
    def get_total_quantity(self):
        """Get total quantity across all warehouses"""
        try:
            return sum(stock.quantity for stock in self.stock_set.all())
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error calculating total quantity for product {self.id}: {e}")
            return Decimal('0')
    
    def get_total_stock_value(self):
        """Get total stock value across all warehouses"""
        try:
            total_value = Decimal('0')
            for stock in self.stock_set.all():
                total_value += stock.quantity * self.selling_price
            return total_value
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error calculating total stock value for product {self.id}: {e}")
            return Decimal('0')

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['brand']),
            models.Index(fields=['is_active']),
            models.Index(fields=['selling_price']),
        ]


class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    @property
    def total_value(self):
        return self.quantity * self.unit_cost

    @classmethod
    def update_stock(cls, product, quantity_change, unit_cost=None, movement_type='adjustment', reference='', description='', user=None):
        """Update stock quantity"""
        from django.db import transaction
        
        with transaction.atomic():
            # Get or create stock record
            stock, created = cls.objects.get_or_create(
                product=product,
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
            
            # Check for low stock alert
            if stock.quantity <= product.min_stock_level:
                StockAlert.objects.get_or_create(
                    product=product,
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




class StockAlert(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    current_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    min_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Low Stock Alert - {self.product.name}"

    class Meta:
        verbose_name = "Stock Alert"
        verbose_name_plural = "Stock Alerts"
