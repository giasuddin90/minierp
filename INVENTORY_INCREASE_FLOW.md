# How Inventory Increases After Purchase

## Overview
In your simplified ERP system, inventory increases automatically when goods are received from a purchase order. Here's the complete flow:

## Step-by-Step Process

### 1. **Create Purchase Order** 📝
```
Status: purchase-order
├── Select Supplier
├── Add Products & Quantities
├── Set Unit Prices
└── Save Order
```

**Example:**
- Product: "Laptop" 
- Quantity: 10 units
- Unit Price: $800 each
- Total: $8,000

### 2. **Receive Goods** 📦
When goods arrive from supplier:
```
Status: purchase-order → goods-received
├── Add Invoice ID from supplier
├── Call receive_goods() method
└── Inventory automatically updates
```

### 3. **Automatic Inventory Update** ⬆️
The `receive_goods()` method triggers:

```python
def receive_goods(self, user=None):
    if self.status != 'goods-received':
        self.status = 'goods-received'
        self.save()
        
        # For each item in the order
        for item in self.items.all():
            Stock.update_stock(
                product=item.product,
                quantity_change=item.quantity,  # +10 laptops
                unit_cost=item.unit_price,     # $800 each
                movement_type='inward',         # INCREASE stock
                reference=f"PO-{self.order_number}",
                description=f"Purchase order receipt - {self.supplier.name}",
                user=user
            )
```

## Inventory Update Logic

### **Stock.update_stock() Method:**
```python
@classmethod
def update_stock(cls, product, quantity_change, unit_cost=None, movement_type='inward', reference='', description='', user=None):
    with transaction.atomic():
        # Get or create stock record
        stock, created = cls.objects.get_or_create(
            product=product,
            defaults={'quantity': 0, 'unit_cost': unit_cost or 0}
        )
        
        # INCREASE quantity for 'inward' movement
        if movement_type == 'inward':
            stock.quantity += quantity_change  # 0 + 10 = 10 laptops
        
        # Update unit cost
        if unit_cost is not None:
            stock.unit_cost = unit_cost  # $800 per laptop
        
        stock.save()
        
        # Check for low stock alerts
        if stock.quantity <= product.min_stock_level:
            # Create alert if stock is low
```

## Real Example

### **Before Purchase:**
```
Product: Laptop
Current Stock: 5 units
Unit Cost: $750
Total Value: $3,750
```

### **Purchase Order:**
```
Order: PO-ABC123
Supplier: TechCorp
Items: 10 Laptops @ $800 each
Total: $8,000
Status: purchase-order
```

### **After Receiving Goods:**
```
Product: Laptop
Updated Stock: 15 units (5 + 10)
New Unit Cost: $800 (updated from $750)
Total Value: $12,000 (15 × $800)
Status: goods-received
```

## Key Features

### ✅ **Automatic Updates**
- No manual inventory entry needed
- Stock increases automatically when goods received
- Unit costs update to latest purchase price

### ✅ **Transaction Safety**
- Uses database transactions
- All-or-nothing updates
- Prevents partial updates

### ✅ **Audit Trail**
- Reference to purchase order
- Description with supplier name
- User tracking
- Timestamp recording

### ✅ **Low Stock Alerts**
- Automatically checks if stock falls below minimum
- Creates alerts for reordering
- Helps prevent stockouts

## Database Changes

### **Stock Table Update:**
```sql
UPDATE stock_stock 
SET quantity = quantity + 10,
    unit_cost = 800.00
WHERE product_id = 123;
```

### **New Stock Movement Record:**
```sql
INSERT INTO stock_movement (
    product_id, quantity, movement_type, 
    reference, description, created_by
) VALUES (
    123, 10, 'inward', 
    'PO-ABC123', 'Purchase order receipt - TechCorp', 1
);
```

## Benefits of This System

1. **Accuracy** - No manual data entry errors
2. **Speed** - Instant inventory updates
3. **Traceability** - Full audit trail
4. **Automation** - Reduces manual work
5. **Consistency** - Standardized process

## Summary

When you receive goods from a purchase order:
1. **Status changes** to `goods-received`
2. **Stock quantities increase** automatically
3. **Unit costs update** to latest purchase price
4. **Low stock alerts** are checked
5. **Audit trail** is created

This ensures your inventory is always accurate and up-to-date! 📊
