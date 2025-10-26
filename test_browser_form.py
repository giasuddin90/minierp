#!/usr/bin/env python
"""
Test script to simulate browser form submission
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/home/giasudin/PycharmProjects/djangoerp/miniErp')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from datetime import date

from sales.models import SalesOrder, SalesOrderItem
from stock.models import Product, ProductCategory, ProductBrand, Stock


def test_browser_form_simulation():
    """Simulate browser form submission with realistic data"""
    
    # Create test client
    client = Client()
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'password': 'testpass123'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    
    # Force login the user
    client.force_login(user)
    
    # Get or create test data
    category, _ = ProductCategory.objects.get_or_create(
        name='Test Category',
        defaults={'is_active': True}
    )
    
    brand, _ = ProductBrand.objects.get_or_create(
        name='Test Brand',
        defaults={'is_active': True}
    )
    
    product, _ = Product.objects.get_or_create(
        name='Test Product',
        defaults={
            'unit_type': 'pcs',
            'selling_price': Decimal('100.00'),
            'category': category,
            'brand': brand,
            'is_active': True
        }
    )
    
    stock, _ = Stock.objects.get_or_create(
        product=product,
        defaults={
            'quantity': Decimal('100.00'),
            'unit_cost': Decimal('50.00')
        }
    )
    
    print("✅ Test data ready")
    
    # Test 1: GET request to see the form
    print("\n📝 Testing GET request...")
    response = client.get(reverse('sales:instant_sales'))
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print("   ❌ Form failed to load")
        return False
    
    print("   ✅ Form loads successfully")
    
    # Test 2: POST request with realistic browser data
    print("\n📤 Testing POST request with realistic data...")
    
    # Simulate what a browser would send
    form_data = {
        'customer_name': 'John Doe',
        'order_date': '2025-10-26',
        'notes': 'Walk-in customer',
        'sales_type': 'instant',
        
        # Formset management form (exactly as browser would send)
        'items-TOTAL_FORMS': '1',
        'items-INITIAL_FORMS': '0',
        'items-MIN_NUM_FORMS': '0',
        'items-MAX_NUM_FORMS': '1000',
        
        # Formset data (exactly as browser would send)
        'items-0-product': str(product.id),
        'items-0-quantity': '3',
        'items-0-unit_price': '100.00',
        'items-0-total_price': '300.00',
        'items-0-DELETE': '',
    }
    
    print(f"   Form data: {form_data}")
    
    response = client.post(reverse('sales:instant_sales'), data=form_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 302:
        print("   ✅ Form submission successful (redirected)")
        
        # Check if order was created
        orders = SalesOrder.objects.filter(sales_type='instant')
        print(f"   Instant orders count: {orders.count()}")
        
        if orders.exists():
            order = orders.first()
            print(f"   ✅ Order created: {order.order_number}")
            print(f"   Customer: {order.customer_name}")
            print(f"   Total: ৳{order.total_amount}")
            print(f"   Items: {order.items.count()}")
            
            # Check items
            for item in order.items.all():
                print(f"     - {item.product.name}: {item.quantity} x ৳{item.unit_price} = ৳{item.total_price}")
            
            return True
        else:
            print("   ❌ No order created")
            return False
    else:
        print("   ❌ Form submission failed")
        print(f"   Response content: {response.content.decode()[:1000]}")
        
        # Check for form errors
        if hasattr(response, 'context') and response.context:
            form = response.context.get('form')
            formset = response.context.get('formset')
            
            if form and form.errors:
                print(f"   Form errors: {form.errors}")
            
            if formset and formset.errors:
                print(f"   Formset errors: {formset.errors}")
        
        return False


if __name__ == '__main__':
    print("🌐 Testing Browser Form Simulation...")
    print("=" * 50)
    
    success = test_browser_form_simulation()
    
    print("=" * 50)
    if success:
        print("🎉 Browser form simulation PASSED!")
        print("✅ The form should work in the browser!")
    else:
        print("💥 Browser form simulation FAILED!")
        print("❌ There might be an issue with the form!")
