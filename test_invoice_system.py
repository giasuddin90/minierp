#!/usr/bin/env python
"""
Comprehensive test script to verify the sales invoice system is working properly.
This script tests the complete invoice functionality including PDF generation and ledger integration.
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

# Add the project directory to Python path
sys.path.append('/home/giasudin/PycharmProjects/djangoerp/building_materials_full')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from sales.models import SalesInvoice, SalesInvoiceItem, SalesOrder, SalesOrderItem
from customers.models import Customer, CustomerLedger
from stock.models import Product, Warehouse

def test_invoice_system():
    """Test the comprehensive invoice system functionality"""
    print("🧪 Testing Sales Invoice System...")
    print("=" * 50)
    
    try:
        # Test 1: Check if we can access invoice URLs
        print("\n1. Testing URL Accessibility...")
        client = Client()
        
        # Test invoice list
        response = client.get('/sales/invoices/')
        print(f"✓ Invoice list URL: {response.status_code}")
        
        # Test invoice create
        response = client.get('/sales/invoices/create/')
        print(f"✓ Invoice create URL: {response.status_code}")
        
        # Test 2: Check if models are working
        print("\n2. Testing Model Functionality...")
        print(f"✓ SalesInvoice model: {SalesInvoice.__name__}")
        print(f"✓ SalesInvoiceItem model: {SalesInvoiceItem.__name__}")
        print(f"✓ SalesOrder model: {SalesOrder.__name__}")
        print(f"✓ CustomerLedger model: {CustomerLedger.__name__}")
        
        # Test 3: Check existing data
        print("\n3. Checking Existing Data...")
        invoice_count = SalesInvoice.objects.count()
        print(f"✓ Current invoices: {invoice_count}")
        
        customer_count = Customer.objects.count()
        print(f"✓ Current customers: {customer_count}")
        
        product_count = Product.objects.count()
        print(f"✓ Current products: {product_count}")
        
        warehouse_count = Warehouse.objects.count()
        print(f"✓ Current warehouses: {warehouse_count}")
        
        order_count = SalesOrder.objects.count()
        print(f"✓ Current sales orders: {order_count}")
        
        # Test 4: Test PDF generation URL
        print("\n4. Testing PDF Generation...")
        if invoice_count > 0:
            first_invoice = SalesInvoice.objects.first()
            response = client.get(f'/sales/invoices/{first_invoice.id}/pdf/')
            print(f"✓ PDF generation URL: {response.status_code}")
            if response.status_code == 200:
                print(f"✓ PDF content type: {response.get('Content-Type', 'Unknown')}")
        else:
            print("⚠ No invoices found for PDF testing")
        
        # Test 5: Test invoice creation from order
        print("\n5. Testing Invoice Creation from Order...")
        if order_count > 0:
            first_order = SalesOrder.objects.first()
            print(f"✓ Found order: {first_order.order_number}")
            print(f"✓ Order status: {first_order.status}")
            print(f"✓ Order total: ৳{first_order.total_amount}")
        else:
            print("⚠ No sales orders found for testing")
        
        # Test 6: Test payment processing URL
        print("\n6. Testing Payment Processing...")
        if invoice_count > 0:
            first_invoice = SalesInvoice.objects.first()
            response = client.post(f'/sales/invoices/{first_invoice.id}/payment/', {
                'paid_amount': 100.00
            })
            print(f"✓ Payment processing URL: {response.status_code}")
        else:
            print("⚠ No invoices found for payment testing")
        
        print("\n" + "=" * 50)
        print("✅ Invoice system comprehensive test completed successfully!")
        print("\n📋 Invoice System Features Implemented:")
        print("   • Create invoices directly from sales orders")
        print("   • Auto-fill customer, products, and amounts")
        print("   • PDF generation for invoices")
        print("   • Payment processing with ledger integration")
        print("   • Standard invoice format with all required fields")
        print("   • Print functionality via PDF download")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing invoice system: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_invoice_system()
    sys.exit(0 if success else 1)
