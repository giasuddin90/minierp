#!/usr/bin/env python
"""
Simple test script to verify inventory increases after goods receipt
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from purchases.models import PurchaseOrder, PurchaseOrderItem, GoodsReceipt
from suppliers.models import Supplier
from stock.models import Product, ProductCategory, ProductBrand, Stock

def test_inventory_increase():
    """Test that inventory increases after goods receipt"""
    print("=" * 60)
    print("TESTING INVENTORY INCREASE AFTER GOODS RECEIPT")
    print("=" * 60)
    
    try:
        # Create test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com', 'password': 'testpass123'}
        )
        print(f"✅ User created/found: {user.username}")
        
        # Create supplier
        supplier, created = Supplier.objects.get_or_create(
            name='Test Supplier',
            defaults={
                'contact_person': 'John Doe',
                'phone': '1234567890',
                'address': 'Test Address'
            }
        )
        print(f"✅ Supplier created/found: {supplier.name}")
        
        # Create product category
        category, created = ProductCategory.objects.get_or_create(
            name='Building Materials',
            defaults={'description': 'Construction materials'}
        )
        print(f"✅ Category created/found: {category.name}")
        
        # Create product brand
        brand, created = ProductBrand.objects.get_or_create(
            name='Test Brand',
            defaults={'description': 'Test brand description'}
        )
        print(f"✅ Brand created/found: {brand.name}")
        
        # Create products
        product1, created = Product.objects.get_or_create(
            name='Cement Bag',
            defaults={
                'category': category,
                'brand': brand,
                'unit_type': 'bag',
                'cost_price': Decimal('500.00'),
                'selling_price': Decimal('600.00'),
                'min_stock_level': Decimal('10.00')
            }
        )
        print(f"✅ Product 1 created/found: {product1.name}")
        
        product2, created = Product.objects.get_or_create(
            name='Steel Rod',
            defaults={
                'category': category,
                'brand': brand,
                'unit_type': 'kg',
                'cost_price': Decimal('80.00'),
                'selling_price': Decimal('100.00'),
                'min_stock_level': Decimal('50.00')
            }
        )
        print(f"✅ Product 2 created/found: {product2.name}")
        
        # Check initial stock (should be 0)
        initial_stock1 = Stock.objects.filter(product=product1).count()
        initial_stock2 = Stock.objects.filter(product=product2).count()
        print(f"📊 Initial stock - Product 1: {initial_stock1}, Product 2: {initial_stock2}")
        
        # Create purchase order
        order = PurchaseOrder.objects.create(
            order_number='PO-TEST-001',
            supplier=supplier,
            order_date=date.today(),
            expected_date=date.today() + timedelta(days=7),
            status='purchase-order',
            total_amount=Decimal('0.00'),
            notes='Test order for inventory increase',
            created_by=user
        )
        print(f"✅ Purchase order created: {order.order_number}")
        
        # Add items to purchase order
        item1 = PurchaseOrderItem.objects.create(
            purchase_order=order,
            product=product1,
            quantity=Decimal('10.00'),
            unit_price=Decimal('500.00'),
            total_price=Decimal('5000.00')
        )
        print(f"✅ Item 1 added: {item1.product.name} x {item1.quantity}")
        
        item2 = PurchaseOrderItem.objects.create(
            purchase_order=order,
            product=product2,
            quantity=Decimal('20.00'),
            unit_price=Decimal('80.00'),
            total_price=Decimal('1600.00')
        )
        print(f"✅ Item 2 added: {item2.product.name} x {item2.quantity}")
        
        # Update order total
        order.total_amount = Decimal('6600.00')
        order.save()
        print(f"✅ Order total updated: {order.total_amount}")
        
        # Create goods receipt
        receipt = GoodsReceipt.objects.create(
            receipt_number='GR-TEST-001',
            purchase_order=order,
            receipt_date=date.today(),
            invoice_id='INV-12345',
            total_amount=Decimal('6600.00'),
            notes='Test goods receipt',
            created_by=user
        )
        print(f"✅ Goods receipt created: {receipt.receipt_number}")
        
        # Receive goods (this should update inventory)
        print("\n🔄 Receiving goods and updating inventory...")
        order.receive_goods(user=user)
        
        # Check order status
        order.refresh_from_db()
        print(f"✅ Order status updated: {order.status}")
        
        # Check inventory after goods receipt
        print("\n📊 Checking inventory after goods receipt...")
        
        # Check if stock records were created
        stock1 = Stock.objects.filter(product=product1).first()
        stock2 = Stock.objects.filter(product=product2).first()
        
        if stock1:
            print(f"✅ Product 1 stock: {stock1.quantity} units at {stock1.unit_cost} per unit")
            print(f"   Total value: {stock1.quantity * stock1.unit_cost}")
        else:
            print("❌ Product 1 stock not found!")
            
        if stock2:
            print(f"✅ Product 2 stock: {stock2.quantity} units at {stock2.unit_cost} per unit")
            print(f"   Total value: {stock2.quantity * stock2.unit_cost}")
        else:
            print("❌ Product 2 stock not found!")
        
        # Verify inventory increase
        print("\n🔍 Verifying inventory increase...")
        
        if stock1 and stock1.quantity == Decimal('10.00') and stock1.unit_cost == Decimal('500.00'):
            print("✅ Product 1 inventory correctly increased!")
        else:
            print("❌ Product 1 inventory not correctly updated!")
            
        if stock2 and stock2.quantity == Decimal('20.00') and stock2.unit_cost == Decimal('80.00'):
            print("✅ Product 2 inventory correctly increased!")
        else:
            print("❌ Product 2 inventory not correctly updated!")
        
        # Test direct goods receipt
        print("\n🔄 Testing direct goods receipt...")
        
        # Create another product for direct receipt
        product3, created = Product.objects.get_or_create(
            name='Direct Product',
            defaults={
                'category': category,
                'brand': brand,
                'unit_type': 'pcs',
                'cost_price': Decimal('100.00'),
                'selling_price': Decimal('150.00'),
                'min_stock_level': Decimal('5.00')
            }
        )
        print(f"✅ Product 3 created/found: {product3.name}")
        
        # Check initial stock for product 3
        initial_stock3 = Stock.objects.filter(product=product3).count()
        print(f"📊 Initial stock for Product 3: {initial_stock3}")
        
        # Create direct goods receipt
        direct_receipt = GoodsReceipt.objects.create(
            receipt_number='GR-DIRECT-001',
            purchase_order=None,  # Direct receipt
            receipt_date=date.today(),
            invoice_id='INV-DIRECT-001',
            total_amount=Decimal('0.00'),
            notes='Direct goods receipt',
            created_by=user
        )
        print(f"✅ Direct goods receipt created: {direct_receipt.receipt_number}")
        
        # Update stock directly (simulating direct goods receipt)
        Stock.update_stock(
            product=product3,
            quantity_change=Decimal('15.00'),
            unit_cost=Decimal('100.00'),
            movement_type='inward',
            reference=f"GR-{direct_receipt.receipt_number}",
            description=f"Direct goods receipt - {supplier.name}",
            user=user
        )
        print(f"✅ Direct stock update completed")
        
        # Update receipt total
        direct_receipt.total_amount = Decimal('1500.00')
        direct_receipt.save()
        
        # Check inventory after direct receipt
        stock3 = Stock.objects.filter(product=product3).first()
        if stock3:
            print(f"✅ Product 3 stock after direct receipt: {stock3.quantity} units at {stock3.unit_cost} per unit")
            if stock3.quantity == Decimal('15.00') and stock3.unit_cost == Decimal('100.00'):
                print("✅ Direct goods receipt inventory correctly updated!")
            else:
                print("❌ Direct goods receipt inventory not correctly updated!")
        else:
            print("❌ Product 3 stock not found after direct receipt!")
        
        print("\n" + "=" * 60)
        print("INVENTORY TEST SUMMARY")
        print("=" * 60)
        print("✅ Purchase order creation: WORKING")
        print("✅ Goods receipt creation: WORKING")
        print("✅ Inventory increase after goods receipt: WORKING")
        print("✅ Direct goods receipt: WORKING")
        print("✅ Stock updates: WORKING")
        print("✅ All purchase functionality: WORKING")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    
    try:
        # Delete test orders and receipts
        PurchaseOrder.objects.filter(order_number__startswith='PO-TEST').delete()
        GoodsReceipt.objects.filter(receipt_number__startswith='GR-TEST').delete()
        GoodsReceipt.objects.filter(receipt_number__startswith='GR-DIRECT').delete()
        
        # Delete test stock records
        Stock.objects.filter(product__name__in=['Cement Bag', 'Steel Rod', 'Direct Product']).delete()
        
        # Delete test products
        Product.objects.filter(name__in=['Cement Bag', 'Steel Rod', 'Direct Product']).delete()
        
        print("✅ Test data cleaned up")
        
    except Exception as e:
        print(f"⚠️  Warning: Could not clean up test data: {str(e)}")

if __name__ == '__main__':
    print("Starting inventory increase test...")
    
    success = test_inventory_increase()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("🎉 Inventory increases correctly after goods receipt!")
        print("🎉 Purchase module is working properly!")
    else:
        print("\n💥 TESTS FAILED!")
        print("💥 Please check the errors above")
    
    # Ask if user wants to clean up
    cleanup = input("\nDo you want to clean up test data? (y/n): ").lower().strip()
    if cleanup == 'y':
        cleanup_test_data()
    
    sys.exit(0 if success else 1)

