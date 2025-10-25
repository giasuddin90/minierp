"""
Comprehensive Test Suite for Purchase Module
Tests all functionality including inventory updates after goods receipt
"""

from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from datetime import date, timedelta
import json

from .models import PurchaseOrder, PurchaseOrderItem, GoodsReceipt
from suppliers.models import Supplier
from stock.models import Product, ProductCategory, ProductBrand, Stock, StockAlert


class PurchaseOrderModelTest(TestCase):
    """Test cases for PurchaseOrder model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create supplier
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            contact_person='John Doe',
            phone='1234567890',
            address='Test Address'
        )
        
        # Create product category and brand
        self.category = ProductCategory.objects.create(
            name='Building Materials',
            description='Construction materials'
        )
        
        self.brand = ProductBrand.objects.create(
            name='Test Brand',
            description='Test brand description'
        )
        
        # Create products
        self.product1 = Product.objects.create(
            name='Cement Bag',
            category=self.category,
            brand=self.brand,
            unit_type='bag',
            cost_price=Decimal('500.00'),
            selling_price=Decimal('600.00'),
            min_stock_level=Decimal('10.00')
        )
        
        self.product2 = Product.objects.create(
            name='Steel Rod',
            category=self.category,
            brand=self.brand,
            unit_type='kg',
            cost_price=Decimal('80.00'),
            selling_price=Decimal('100.00'),
            min_stock_level=Decimal('50.00')
        )
    
    def test_purchase_order_creation(self):
        """Test creating a purchase order"""
        order = PurchaseOrder.objects.create(
            order_number='PO-TEST-001',
            supplier=self.supplier,
            order_date=date.today(),
            expected_date=date.today() + timedelta(days=7),
            status='purchase-order',
            total_amount=Decimal('1000.00'),
            notes='Test order',
            created_by=self.user
        )
        
        self.assertEqual(str(order), f"PO-{order.order_number} - {self.supplier.name}")
        self.assertEqual(order.supplier, self.supplier)
        self.assertEqual(order.status, 'purchase-order')
        self.assertEqual(order.total_amount, Decimal('1000.00'))
        self.assertEqual(order.created_by, self.user)
    
    def test_purchase_order_with_items(self):
        """Test creating a purchase order with items"""
        order = PurchaseOrder.objects.create(
            order_number='PO-TEST-002',
            supplier=self.supplier,
            order_date=date.today(),
            expected_date=date.today() + timedelta(days=7),
            status='purchase-order',
            total_amount=Decimal('0.00'),
            created_by=self.user
        )
        
        # Add items
        item1 = PurchaseOrderItem.objects.create(
            purchase_order=order,
            product=self.product1,
            quantity=Decimal('10.00'),
            unit_price=Decimal('500.00'),
            total_price=Decimal('5000.00')
        )
        
        item2 = PurchaseOrderItem.objects.create(
            purchase_order=order,
            product=self.product2,
            quantity=Decimal('20.00'),
            unit_price=Decimal('80.00'),
            total_price=Decimal('1600.00')
        )
        
        # Update total
        total = sum(item.total_price for item in order.items.all())
        order.total_amount = total
        order.save()
        
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.total_amount, Decimal('6600.00'))
        self.assertEqual(str(item1), f"{order.order_number} - {self.product1.name}")
        self.assertEqual(str(item2), f"{order.order_number} - {self.product2.name}")
    
    def test_purchase_order_receive_goods(self):
        """Test receiving goods and updating inventory"""
        # Create order with items
        order = PurchaseOrder.objects.create(
            order_number='PO-TEST-003',
            supplier=self.supplier,
            order_date=date.today(),
            expected_date=date.today() + timedelta(days=7),
            status='purchase-order',
            total_amount=Decimal('0.00'),
            created_by=self.user
        )
        
        # Add items
        PurchaseOrderItem.objects.create(
            purchase_order=order,
            product=self.product1,
            quantity=Decimal('10.00'),
            unit_price=Decimal('500.00'),
            total_price=Decimal('5000.00')
        )
        
        PurchaseOrderItem.objects.create(
            purchase_order=order,
            product=self.product2,
            quantity=Decimal('20.00'),
            unit_price=Decimal('80.00'),
            total_price=Decimal('1600.00')
        )
        
        # Check initial stock (should be 0)
        self.assertEqual(Stock.objects.filter(product=self.product1).count(), 0)
        self.assertEqual(Stock.objects.filter(product=self.product2).count(), 0)
        
        # Receive goods
        order.receive_goods(user=self.user)
        
        # Check order status
        order.refresh_from_db()
        self.assertEqual(order.status, 'goods-received')
        
        # Check if stock was updated
        stock1 = Stock.objects.get(product=self.product1)
        stock2 = Stock.objects.get(product=self.product2)
        
        self.assertEqual(stock1.quantity, Decimal('10.00'))
        self.assertEqual(stock1.unit_cost, Decimal('500.00'))
        self.assertEqual(stock2.quantity, Decimal('20.00'))
        self.assertEqual(stock2.unit_cost, Decimal('80.00'))
    
    def test_purchase_order_cancel(self):
        """Test canceling a purchase order"""
        order = PurchaseOrder.objects.create(
            order_number='PO-TEST-004',
            supplier=self.supplier,
            order_date=date.today(),
            expected_date=date.today() + timedelta(days=7),
            status='purchase-order',
            total_amount=Decimal('1000.00'),
            created_by=self.user
        )
        
        # Cancel order
        order.cancel_order(user=self.user)
        
        # Check status
        order.refresh_from_db()
        self.assertEqual(order.status, 'canceled')
    
    def test_purchase_order_status_choices(self):
        """Test purchase order status choices"""
        order = PurchaseOrder.objects.create(
            order_number='PO-TEST-005',
            supplier=self.supplier,
            order_date=date.today(),
            expected_date=date.today() + timedelta(days=7),
            status='purchase-order',
            total_amount=Decimal('1000.00'),
            created_by=self.user
        )
        
        # Test status choices
        status_choices = [choice[0] for choice in PurchaseOrder.ORDER_STATUS]
        self.assertIn('purchase-order', status_choices)
        self.assertIn('goods-received', status_choices)
        self.assertIn('canceled', status_choices)


class GoodsReceiptModelTest(TestCase):
    """Test cases for GoodsReceipt model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            contact_person='John Doe',
            phone='1234567890',
            address='Test Address'
        )
        
        self.category = ProductCategory.objects.create(
            name='Building Materials',
            description='Construction materials'
        )
        
        self.brand = ProductBrand.objects.create(
            name='Test Brand',
            description='Test brand description'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            brand=self.brand,
            unit_type='pcs',
            cost_price=Decimal('100.00'),
            selling_price=Decimal('150.00'),
            min_stock_level=Decimal('10.00')
        )
        
        self.purchase_order = PurchaseOrder.objects.create(
            order_number='PO-TEST-001',
            supplier=self.supplier,
            order_date=date.today(),
            expected_date=date.today() + timedelta(days=7),
            status='purchase-order',
            total_amount=Decimal('1000.00'),
            created_by=self.user
        )
    
    def test_goods_receipt_creation(self):
        """Test creating a goods receipt"""
        receipt = GoodsReceipt.objects.create(
            receipt_number='GR-TEST-001',
            purchase_order=self.purchase_order,
            receipt_date=date.today(),
            invoice_id='INV-12345',
            total_amount=Decimal('1000.00'),
            notes='Test receipt',
            created_by=self.user
        )
        
        self.assertEqual(str(receipt), f"GR-{receipt.receipt_number} - {self.purchase_order.supplier.name}")
        self.assertEqual(receipt.purchase_order, self.purchase_order)
        self.assertEqual(receipt.invoice_id, 'INV-12345')
        self.assertEqual(receipt.total_amount, Decimal('1000.00'))
        self.assertEqual(receipt.created_by, self.user)
    
    def test_goods_receipt_without_purchase_order(self):
        """Test creating a goods receipt without purchase order"""
        receipt = GoodsReceipt.objects.create(
            receipt_number='GR-TEST-002',
            purchase_order=None,
            receipt_date=date.today(),
            invoice_id='INV-67890',
            total_amount=Decimal('500.00'),
            notes='Direct receipt',
            created_by=self.user
        )
        
        self.assertEqual(receipt.purchase_order, None)
        self.assertEqual(receipt.invoice_id, 'INV-67890')
        self.assertEqual(receipt.total_amount, Decimal('500.00'))


class PurchaseOrderViewTest(TestCase):
    """Test cases for PurchaseOrder views"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            contact_person='John Doe',
            phone='1234567890',
            address='Test Address'
        )
        
        self.category = ProductCategory.objects.create(
            name='Building Materials',
            description='Construction materials'
        )
        
        self.brand = ProductBrand.objects.create(
            name='Test Brand',
            description='Test brand description'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            brand=self.brand,
            unit_type='pcs',
            cost_price=Decimal('100.00'),
            selling_price=Decimal('150.00'),
            min_stock_level=Decimal('10.00')
        )
        
        self.client = Client()
        self.client.force_login(self.user)
    
    def test_purchase_order_list_view(self):
        """Test purchase order list view"""
        # Create test orders
        PurchaseOrder.objects.create(
            order_number='PO-TEST-001',
            supplier=self.supplier,
            order_date=date.today(),
            expected_date=date.today() + timedelta(days=7),
            status='purchase-order',
            total_amount=Decimal('1000.00'),
            created_by=self.user
        )
        
        response = self.client.get(reverse('purchases:order_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PO-TEST-001')
        self.assertContains(response, 'Test Supplier')
    
    def test_purchase_order_create_view_get(self):
        """Test purchase order create view GET request"""
        response = self.client.get(reverse('purchases:order_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New Purchase Order')
        self.assertContains(response, 'Test Supplier')
        self.assertContains(response, 'Test Product')
    
    def test_purchase_order_create_view_post_success(self):
        """Test successful purchase order creation"""
        data = {
            'supplier': self.supplier.id,
            'order_date': date.today().strftime('%Y-%m-%d'),
            'expected_date': (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'status': 'purchase-order',
            'notes': 'Test order',
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '1',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-product': self.product.id,
            'form-0-quantity': '10',
            'form-0-unit_price': '100.00',
            'form-0-total_price': '1000.00',
        }
        
        response = self.client.post(reverse('purchases:order_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        
        # Check if order was created
        order = PurchaseOrder.objects.get(supplier=self.supplier)
        self.assertEqual(order.notes, 'Test order')
        self.assertEqual(order.created_by, self.user)
        self.assertTrue(order.order_number.startswith('PO-'))
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total_amount, Decimal('1000.00'))
    
    def test_purchase_order_create_with_multiple_products(self):
        """Test purchase order creation with multiple products"""
        # Create another product
        product2 = Product.objects.create(
            name='Test Product 2',
            category=self.category,
            brand=self.brand,
            unit_type='kg',
            cost_price=Decimal('50.00'),
            selling_price=Decimal('75.00'),
            min_stock_level=Decimal('5.00')
        )
        
        data = {
            'supplier': self.supplier.id,
            'order_date': date.today().strftime('%Y-%m-%d'),
            'expected_date': (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'status': 'purchase-order',
            'notes': 'Test order with multiple products',
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '1',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-product': self.product.id,
            'form-0-quantity': '10',
            'form-0-unit_price': '100.00',
            'form-0-total_price': '1000.00',
            'form-1-product': product2.id,
            'form-1-quantity': '5',
            'form-1-unit_price': '50.00',
            'form-1-total_price': '250.00',
        }
        
        response = self.client.post(reverse('purchases:order_create'), data)
        self.assertEqual(response.status_code, 302)
        
        # Check if order and items were created
        order = PurchaseOrder.objects.get(supplier=self.supplier)
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.total_amount, Decimal('1250.00'))  # 1000 + 250
    
    def test_purchase_order_detail_view(self):
        """Test purchase order detail view"""
        order = PurchaseOrder.objects.create(
            order_number='PO-TEST-001',
            supplier=self.supplier,
            order_date=date.today(),
            expected_date=date.today() + timedelta(days=7),
            status='purchase-order',
            total_amount=Decimal('1000.00'),
            created_by=self.user
        )
        
        response = self.client.get(reverse('purchases:order_detail', kwargs={'pk': order.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PO-TEST-001')
        self.assertContains(response, 'Test Supplier')
    
    def test_purchase_order_update_view(self):
        """Test purchase order update view"""
        order = PurchaseOrder.objects.create(
            order_number='PO-TEST-001',
            supplier=self.supplier,
            order_date=date.today(),
            expected_date=date.today() + timedelta(days=7),
            status='purchase-order',
            total_amount=Decimal('1000.00'),
            created_by=self.user
        )
        
        # Test GET request
        response = self.client.get(reverse('purchases:order_edit', kwargs={'pk': order.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Test POST request
        data = {
            'supplier': self.supplier.id,
            'order_date': date.today().strftime('%Y-%m-%d'),
            'expected_date': (date.today() + timedelta(days=10)).strftime('%Y-%m-%d'),
            'status': 'goods-received',
            'notes': 'Updated test order',
            'form-TOTAL_FORMS': '0',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '1',
            'form-MAX_NUM_FORMS': '1000',
        }
        
        response = self.client.post(reverse('purchases:order_edit', kwargs={'pk': order.pk}), data)
        self.assertEqual(response.status_code, 302)
        
        # Check if order was updated
        order.refresh_from_db()
        self.assertEqual(order.status, 'goods-received')
        self.assertEqual(order.notes, 'Updated test order')
    
    def test_purchase_order_delete_view(self):
        """Test purchase order delete view"""
        order = PurchaseOrder.objects.create(
            order_number='PO-TEST-001',
            supplier=self.supplier,
            order_date=date.today(),
            expected_date=date.today() + timedelta(days=7),
            status='purchase-order',
            total_amount=Decimal('1000.00'),
            created_by=self.user
        )
        
        # Test GET request (confirmation page)
        response = self.client.get(reverse('purchases:order_delete', kwargs={'pk': order.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Test POST request (actual deletion)
        response = self.client.post(reverse('purchases:order_delete', kwargs={'pk': order.pk}))
        self.assertEqual(response.status_code, 302)
        
        # Check if order was deleted
        self.assertFalse(PurchaseOrder.objects.filter(pk=order.pk).exists())


class GoodsReceiptViewTest(TestCase):
    """Test cases for GoodsReceipt views"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            contact_person='John Doe',
            phone='1234567890',
            address='Test Address'
        )
        
        self.category = ProductCategory.objects.create(
            name='Building Materials',
            description='Construction materials'
        )
        
        self.brand = ProductBrand.objects.create(
            name='Test Brand',
            description='Test brand description'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            brand=self.brand,
            unit_type='pcs',
            cost_price=Decimal('100.00'),
            selling_price=Decimal('150.00'),
            min_stock_level=Decimal('10.00')
        )
        
        self.purchase_order = PurchaseOrder.objects.create(
            order_number='PO-TEST-001',
            supplier=self.supplier,
            order_date=date.today(),
            expected_date=date.today() + timedelta(days=7),
            status='purchase-order',
            total_amount=Decimal('1000.00'),
            created_by=self.user
        )
        
        self.client = Client()
        self.client.force_login(self.user)
    
    def test_goods_receipt_list_view(self):
        """Test goods receipt list view"""
        # Create test receipt
        GoodsReceipt.objects.create(
            receipt_number='GR-TEST-001',
            purchase_order=self.purchase_order,
            receipt_date=date.today(),
            invoice_id='INV-12345',
            total_amount=Decimal('1000.00'),
            created_by=self.user
        )
        
        response = self.client.get(reverse('purchases:receipt_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'GR-TEST-001')
    
    def test_goods_receipt_create_view_get(self):
        """Test goods receipt create view GET request"""
        response = self.client.get(reverse('purchases:receipt_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New Goods Receipt')
    
    def test_goods_receipt_create_view_post_success(self):
        """Test successful goods receipt creation"""
        data = {
            'purchase_order': self.purchase_order.id,
            'receipt_date': date.today().strftime('%Y-%m-%d'),
            'invoice_id': 'INV-12345',
            'notes': 'Test receipt',
        }
        
        response = self.client.post(reverse('purchases:receipt_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        
        # Check if receipt was created
        receipt = GoodsReceipt.objects.get(purchase_order=self.purchase_order)
        self.assertEqual(receipt.invoice_id, 'INV-12345')
        self.assertEqual(receipt.created_by, self.user)
        self.assertTrue(receipt.receipt_number.startswith('GR-'))
        
        # Check if purchase order status was updated
        self.purchase_order.refresh_from_db()
        self.assertEqual(self.purchase_order.status, 'goods-received')
    
    def test_direct_goods_receipt_create_view(self):
        """Test direct goods receipt creation without purchase order"""
        data = {
            'supplier': self.supplier.id,
            'receipt_date': date.today().strftime('%Y-%m-%d'),
            'invoice_id': 'INV-DIRECT-001',
            'notes': 'Direct receipt',
            'products[]': [str(self.product.id)],
            'quantities[]': ['10'],
            'unit_costs[]': ['100.00'],
        }
        
        response = self.client.post(reverse('purchases:direct_receipt_create'), data)
        self.assertEqual(response.status_code, 302)
        
        # Check if receipt was created
        receipt = GoodsReceipt.objects.get(invoice_id='INV-DIRECT-001')
        self.assertEqual(receipt.purchase_order, None)
        self.assertEqual(receipt.total_amount, Decimal('1000.00'))
        
        # Check if stock was updated
        stock = Stock.objects.get(product=self.product)
        self.assertEqual(stock.quantity, Decimal('10.00'))
        self.assertEqual(stock.unit_cost, Decimal('100.00'))


class PurchaseOrderIntegrationTest(TransactionTestCase):
    """Integration test cases for complete purchase order workflow"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            contact_person='John Doe',
            phone='1234567890',
            address='Test Address'
        )
        
        self.category = ProductCategory.objects.create(
            name='Building Materials',
            description='Construction materials'
        )
        
        self.brand = ProductBrand.objects.create(
            name='Test Brand',
            description='Test brand description'
        )
        
        self.product1 = Product.objects.create(
            name='Cement Bag',
            category=self.category,
            brand=self.brand,
            unit_type='bag',
            cost_price=Decimal('500.00'),
            selling_price=Decimal('600.00'),
            min_stock_level=Decimal('10.00')
        )
        
        self.product2 = Product.objects.create(
            name='Steel Rod',
            category=self.category,
            brand=self.brand,
            unit_type='kg',
            cost_price=Decimal('80.00'),
            selling_price=Decimal('100.00'),
            min_stock_level=Decimal('50.00')
        )
        
        self.client = Client()
        self.client.force_login(self.user)
    
    def test_complete_purchase_order_workflow(self):
        """Test complete purchase order workflow from creation to receiving"""
        # Step 1: Create purchase order
        data = {
            'supplier': self.supplier.id,
            'order_date': date.today().strftime('%Y-%m-%d'),
            'expected_date': (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'status': 'purchase-order',
            'notes': 'Complete workflow test',
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '1',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-product': self.product1.id,
            'form-0-quantity': '20',
            'form-0-unit_price': '500.00',
            'form-0-total_price': '10000.00',
            'form-1-product': self.product2.id,
            'form-1-quantity': '50',
            'form-1-unit_price': '80.00',
            'form-1-total_price': '4000.00',
        }
        
        response = self.client.post(reverse('purchases:order_create'), data)
        self.assertEqual(response.status_code, 302)
        
        # Step 2: Verify order was created
        order = PurchaseOrder.objects.get(supplier=self.supplier)
        self.assertEqual(order.status, 'purchase-order')
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.total_amount, Decimal('14000.00'))
        
        # Step 3: Check initial stock (should be 0)
        self.assertEqual(Stock.objects.filter(product=self.product1).count(), 0)
        self.assertEqual(Stock.objects.filter(product=self.product2).count(), 0)
        
        # Step 4: Create goods receipt
        receipt_data = {
            'purchase_order': order.id,
            'receipt_date': date.today().strftime('%Y-%m-%d'),
            'invoice_id': 'INV-12345',
            'notes': 'Goods received',
        }
        
        response = self.client.post(reverse('purchases:receipt_create'), receipt_data)
        self.assertEqual(response.status_code, 302)
        
        # Step 5: Verify order status and stock update
        order.refresh_from_db()
        self.assertEqual(order.status, 'goods-received')
        
        # Check stock was updated
        stock1 = Stock.objects.get(product=self.product1)
        stock2 = Stock.objects.get(product=self.product2)
        
        self.assertEqual(stock1.quantity, Decimal('20.00'))
        self.assertEqual(stock1.unit_cost, Decimal('500.00'))
        self.assertEqual(stock2.quantity, Decimal('50.00'))
        self.assertEqual(stock2.unit_cost, Decimal('80.00'))
        
        # Check receipt was created
        receipt = GoodsReceipt.objects.get(purchase_order=order)
        self.assertEqual(receipt.invoice_id, 'INV-12345')
        self.assertEqual(receipt.total_amount, Decimal('14000.00'))
    
    def test_direct_goods_receipt_workflow(self):
        """Test direct goods receipt workflow without purchase order"""
        # Check initial stock
        self.assertEqual(Stock.objects.filter(product=self.product1).count(), 0)
        
        # Create direct goods receipt
        data = {
            'supplier': self.supplier.id,
            'receipt_date': date.today().strftime('%Y-%m-%d'),
            'invoice_id': 'INV-DIRECT-001',
            'notes': 'Direct receipt',
            'products[]': [str(self.product1.id), str(self.product2.id)],
            'quantities[]': ['15', '25'],
            'unit_costs[]': ['500.00', '80.00'],
        }
        
        response = self.client.post(reverse('purchases:direct_receipt_create'), data)
        self.assertEqual(response.status_code, 302)
        
        # Check if receipt was created
        receipt = GoodsReceipt.objects.get(invoice_id='INV-DIRECT-001')
        self.assertEqual(receipt.purchase_order, None)
        self.assertEqual(receipt.total_amount, Decimal('9500.00'))  # 15*500 + 25*80
        
        # Check if stock was updated
        stock1 = Stock.objects.get(product=self.product1)
        stock2 = Stock.objects.get(product=self.product2)
        
        self.assertEqual(stock1.quantity, Decimal('15.00'))
        self.assertEqual(stock1.unit_cost, Decimal('500.00'))
        self.assertEqual(stock2.quantity, Decimal('25.00'))
        self.assertEqual(stock2.unit_cost, Decimal('80.00'))
    
    def test_inventory_increase_after_goods_receipt(self):
        """Test that inventory increases correctly after goods receipt"""
        # Create purchase order with items
        order = PurchaseOrder.objects.create(
            order_number='PO-TEST-001',
            supplier=self.supplier,
            order_date=date.today(),
            expected_date=date.today() + timedelta(days=7),
            status='purchase-order',
            total_amount=Decimal('0.00'),
            created_by=self.user
        )
        
        # Add items to order
        PurchaseOrderItem.objects.create(
            purchase_order=order,
            product=self.product1,
            quantity=Decimal('10.00'),
            unit_price=Decimal('500.00'),
            total_price=Decimal('5000.00')
        )
        
        PurchaseOrderItem.objects.create(
            purchase_order=order,
            product=self.product2,
            quantity=Decimal('20.00'),
            unit_price=Decimal('80.00'),
            total_price=Decimal('1600.00')
        )
        
        # Update order total
        order.total_amount = Decimal('6600.00')
        order.save()
        
        # Verify initial stock is 0
        self.assertEqual(Stock.objects.filter(product=self.product1).count(), 0)
        self.assertEqual(Stock.objects.filter(product=self.product2).count(), 0)
        
        # Create goods receipt
        receipt_data = {
            'purchase_order': order.id,
            'receipt_date': date.today().strftime('%Y-%m-%d'),
            'invoice_id': 'INV-12345',
            'notes': 'Goods received',
        }
        
        response = self.client.post(reverse('purchases:receipt_create'), receipt_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify inventory increased
        stock1 = Stock.objects.get(product=self.product1)
        stock2 = Stock.objects.get(product=self.product2)
        
        self.assertEqual(stock1.quantity, Decimal('10.00'))
        self.assertEqual(stock1.unit_cost, Decimal('500.00'))
        self.assertEqual(stock2.quantity, Decimal('20.00'))
        self.assertEqual(stock2.unit_cost, Decimal('80.00'))
        
        # Verify order status changed
        order.refresh_from_db()
        self.assertEqual(order.status, 'goods-received')
        
        # Verify receipt was created
        receipt = GoodsReceipt.objects.get(purchase_order=order)
        self.assertEqual(receipt.invoice_id, 'INV-12345')
        self.assertEqual(receipt.total_amount, Decimal('6600.00'))


class PurchaseOrderFormTest(TestCase):
    """Test cases for purchase order forms"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            contact_person='John Doe',
            phone='1234567890',
            address='Test Address'
        )
        
        self.category = ProductCategory.objects.create(
            name='Building Materials',
            description='Construction materials'
        )
        
        self.brand = ProductBrand.objects.create(
            name='Test Brand',
            description='Test brand description'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            brand=self.brand,
            unit_type='pcs',
            cost_price=Decimal('100.00'),
            selling_price=Decimal('150.00'),
            min_stock_level=Decimal('10.00')
        )
    
    def test_purchase_order_form_valid_data(self):
        """Test purchase order form with valid data"""
        from .forms import PurchaseOrderForm
        
        data = {
            'supplier': self.supplier.id,
            'order_date': date.today(),
            'expected_date': date.today() + timedelta(days=7),
            'status': 'purchase-order',
            'notes': 'Test order',
        }
        
        form = PurchaseOrderForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_purchase_order_form_invalid_data(self):
        """Test purchase order form with invalid data"""
        from .forms import PurchaseOrderForm
        
        data = {
            'supplier': self.supplier.id,
            'order_date': 'invalid-date',
            'expected_date': date.today() + timedelta(days=7),
            'status': 'purchase-order',
            'notes': 'Test order',
        }
        
        form = PurchaseOrderForm(data=data)
        self.assertFalse(form.is_valid())
    
    def test_purchase_order_item_form_valid_data(self):
        """Test purchase order item form with valid data"""
        from .forms import PurchaseOrderItemForm
        
        data = {
            'product': self.product.id,
            'quantity': '10',
            'unit_price': '100.00',
            'total_price': '1000.00',
        }
        
        form = PurchaseOrderItemForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_purchase_order_item_form_invalid_quantity(self):
        """Test purchase order item form with invalid quantity"""
        from .forms import PurchaseOrderItemForm
        
        data = {
            'product': self.product.id,
            'quantity': '0',  # Invalid: quantity must be > 0
            'unit_price': '100.00',
            'total_price': '0.00',
        }
        
        form = PurchaseOrderItemForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)
    
    def test_purchase_order_item_form_invalid_unit_price(self):
        """Test purchase order item form with invalid unit price"""
        from .forms import PurchaseOrderItemForm
        
        data = {
            'product': self.product.id,
            'quantity': '10',
            'unit_price': '0.00',  # Invalid: unit price must be > 0
            'total_price': '0.00',
        }
        
        form = PurchaseOrderItemForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('unit_price', form.errors)


class PurchaseOrderAuthenticationTest(TestCase):
    """Test cases for purchase order authentication requirements"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
    
    def test_purchase_order_list_requires_authentication(self):
        """Test that purchase order list view requires authentication"""
        response = self.client.get(reverse('purchases:order_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_purchase_order_create_requires_authentication(self):
        """Test that purchase order create view requires authentication"""
        response = self.client.get(reverse('purchases:order_create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_goods_receipt_list_requires_authentication(self):
        """Test that goods receipt list view requires authentication"""
        response = self.client.get(reverse('purchases:receipt_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_goods_receipt_create_requires_authentication(self):
        """Test that goods receipt create view requires authentication"""
        response = self.client.get(reverse('purchases:receipt_create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login


class PurchaseOrderReportTest(TestCase):
    """Test cases for purchase order reports"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            contact_person='John Doe',
            phone='1234567890',
            address='Test Address'
        )
        
        self.client = Client()
        self.client.force_login(self.user)
    
    def test_purchase_daily_report_view(self):
        """Test purchase daily report view"""
        # Create test orders for today
        PurchaseOrder.objects.create(
            order_number='PO-TEST-001',
            supplier=self.supplier,
            order_date=date.today(),
            expected_date=date.today() + timedelta(days=7),
            status='purchase-order',
            total_amount=Decimal('1000.00'),
            created_by=self.user
        )
        
        response = self.client.get(reverse('purchases:purchase_daily_report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PO-TEST-001')
    
    def test_purchase_monthly_report_view(self):
        """Test purchase monthly report view"""
        # Create test orders for this month
        PurchaseOrder.objects.create(
            order_number='PO-TEST-001',
            supplier=self.supplier,
            order_date=date.today(),
            expected_date=date.today() + timedelta(days=7),
            status='purchase-order',
            total_amount=Decimal('1000.00'),
            created_by=self.user
        )
        
        response = self.client.get(reverse('purchases:purchase_monthly_report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PO-TEST-001')
    
    def test_purchase_supplier_report_view(self):
        """Test purchase supplier report view"""
        # Create test orders
        PurchaseOrder.objects.create(
            order_number='PO-TEST-001',
            supplier=self.supplier,
            order_date=date.today(),
            expected_date=date.today() + timedelta(days=7),
            status='purchase-order',
            total_amount=Decimal('1000.00'),
            created_by=self.user
        )
        
        response = self.client.get(reverse('purchases:purchase_supplier_report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PO-TEST-001')
        self.assertContains(response, 'Test Supplier')


if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['purchases.test_comprehensive'])

