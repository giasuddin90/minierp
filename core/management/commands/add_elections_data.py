from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
import random

from customers.models import Customer, CustomerLedger, CustomerCommitment
from suppliers.models import Supplier, SupplierLedger
from stock.models import Product, ProductCategory, ProductBrand, UnitType
from sales.models import SalesOrder, SalesOrderItem
from purchases.models import PurchaseOrder, PurchaseOrderItem


class Command(BaseCommand):
    help = 'Add elections business related data to the ERP system'

    def handle(self, *args, **options):
        self.stdout.write('Creating elections business data...')
        
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@elections.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('✓ Created admin user (username: admin, password: admin123)')
        
        # Create unit types
        self.create_unit_types()
        
        # Create product categories
        self.create_product_categories()
        
        # Create product brands
        self.create_product_brands()
        
        # Create demo customers (election-related)
        self.create_elections_customers(admin_user)
        
        # Create demo suppliers (election-related)
        self.create_elections_suppliers(admin_user)
        
        # Create demo products (election materials)
        self.create_elections_products()
        
        # Create purchase orders to build inventory
        self.create_purchase_orders(admin_user)
        
        # Create sales orders
        self.create_sales_orders(admin_user)
        
        self.stdout.write(
            self.style.SUCCESS('✓ Elections business data created successfully!')
        )
        self.stdout.write('Login credentials:')
        self.stdout.write('Username: admin')
        self.stdout.write('Password: admin123')

    def create_unit_types(self):
        """Create unit types for elections products"""
        units = [
            {'name': 'Piece', 'code': 'pcs', 'description': 'Individual pieces'},
            {'name': 'Box', 'code': 'box', 'description': 'Box of items'},
            {'name': 'Pack', 'code': 'pack', 'description': 'Pack of items'},
            {'name': 'Set', 'code': 'set', 'description': 'Set of items'},
            {'name': 'Roll', 'code': 'roll', 'description': 'Roll of material'},
            {'name': 'Sheet', 'code': 'sheet', 'description': 'Single sheet'},
            {'name': 'Bottle', 'code': 'bottle', 'description': 'Bottle container'},
        ]
        
        for unit in units:
            UnitType.objects.get_or_create(
                code=unit['code'],
                defaults={
                    'name': unit['name'],
                    'description': unit['description']
                }
            )
        self.stdout.write('✓ Created unit types')

    def create_product_categories(self):
        """Create product categories for elections"""
        categories = [
            'Ballot Papers',
            'Voting Equipment',
            'Campaign Materials',
            'Polling Station Supplies',
            'Security Materials',
            'Stationery & Office Supplies',
        ]
        
        for cat_name in categories:
            ProductCategory.objects.get_or_create(
                name=cat_name,
                defaults={'is_active': True}
            )
        self.stdout.write('✓ Created product categories')

    def create_product_brands(self):
        """Create product brands"""
        brands = [
            'ElectionPro',
            'VoteSecure',
            'PollMaster',
            'BallotTech',
            'CampaignPlus',
        ]
        
        for brand_name in brands:
            ProductBrand.objects.get_or_create(
                name=brand_name,
                defaults={'is_active': True}
            )
        self.stdout.write('✓ Created product brands')

    def create_elections_customers(self, user):
        """Create elections-related customers"""
        customers_data = [
            {
                'name': 'Dhaka City Corporation',
                'customer_type': 'wholesale',
                'contact_person': 'Mohammad Rahman',
                'phone': '+880-2-12345678',
                'address': 'Nagor Bhaban, Dhaka',
                'opening_balance': Decimal('50000.00')
            },
            {
                'name': 'Chittagong City Corporation',
                'customer_type': 'wholesale',
                'contact_person': 'Abdul Karim',
                'phone': '+880-31-2345678',
                'address': 'Anderkilla, Chittagong',
                'opening_balance': Decimal('35000.00')
            },
            {
                'name': 'Sylhet City Corporation',
                'customer_type': 'wholesale',
                'contact_person': 'Fatema Begum',
                'phone': '+880-821-3456789',
                'address': 'Sylhet Sadar, Sylhet',
                'opening_balance': Decimal('25000.00')
            },
            {
                'name': 'Rajshahi City Corporation',
                'customer_type': 'wholesale',
                'contact_person': 'Hasan Ali',
                'phone': '+880-721-4567890',
                'address': 'Rajshahi Sadar, Rajshahi',
                'opening_balance': Decimal('30000.00')
            },
            {
                'name': 'Election Commission Regional Office',
                'customer_type': 'wholesale',
                'contact_person': 'Nurul Islam',
                'phone': '+880-2-98765432',
                'address': 'Agargaon, Dhaka',
                'opening_balance': Decimal('100000.00')
            },
        ]
        
        for data in customers_data:
            customer, created = Customer.objects.get_or_create(
                name=data['name'],
                defaults={
                    'customer_type': data['customer_type'],
                    'contact_person': data['contact_person'],
                    'phone': data['phone'],
                    'address': data['address'],
                    'opening_balance': data['opening_balance'],
                    'current_balance': data['opening_balance'],
                    'is_active': True
                }
            )
            
            if created:
                # Create opening balance ledger entry
                CustomerLedger.objects.create(
                    customer=customer,
                    transaction_type='opening_balance',
                    amount=data['opening_balance'],
                    description='Opening Balance',
                    transaction_date=timezone.now() - timedelta(days=30),
                    created_by=user
                )
        
        self.stdout.write('✓ Created elections customers')

    def create_elections_suppliers(self, user):
        """Create elections-related suppliers"""
        suppliers_data = [
            {
                'name': 'Ballot Paper Manufacturing Ltd',
                'contact_person': 'Ahmed Hossain',
                'phone': '+880-2-11111111',
                'address': 'Tejgaon Industrial Area, Dhaka',
                'opening_balance': Decimal('-15000.00')
            },
            {
                'name': 'Voting Equipment Solutions',
                'contact_person': 'Sultana Khatun',
                'phone': '+880-2-22222222',
                'address': 'Gulshan, Dhaka',
                'opening_balance': Decimal('-20000.00')
            },
            {
                'name': 'Security Materials Co',
                'contact_person': 'Rashid Mia',
                'phone': '+880-2-33333333',
                'address': 'Dhanmondi, Dhaka',
                'opening_balance': Decimal('-10000.00')
            },
            {
                'name': 'Printing & Stationery House',
                'contact_person': 'Farida Begum',
                'phone': '+880-2-44444444',
                'address': 'Motijheel, Dhaka',
                'opening_balance': Decimal('-8000.00')
            },
        ]
        
        for data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=data['name'],
                defaults={
                    'contact_person': data['contact_person'],
                    'phone': data['phone'],
                    'address': data['address'],
                    'opening_balance': data['opening_balance'],
                    'current_balance': data['opening_balance'],
                    'is_active': True
                }
            )
            
            if created:
                # Create opening balance ledger entry
                SupplierLedger.objects.create(
                    supplier=supplier,
                    transaction_type='opening_balance',
                    amount=abs(data['opening_balance']),
                    description='Opening Balance',
                    transaction_date=timezone.now() - timedelta(days=30),
                    created_by=user
                )
        
        self.stdout.write('✓ Created elections suppliers')

    def create_elections_products(self):
        """Create elections-related products"""
        category_ballot = ProductCategory.objects.get(name='Ballot Papers')
        category_voting = ProductCategory.objects.get(name='Voting Equipment')
        category_campaign = ProductCategory.objects.get(name='Campaign Materials')
        category_polling = ProductCategory.objects.get(name='Polling Station Supplies')
        category_security = ProductCategory.objects.get(name='Security Materials')
        category_stationery = ProductCategory.objects.get(name='Stationery & Office Supplies')
        
        brand_electionpro = ProductBrand.objects.get(name='ElectionPro')
        brand_votesecure = ProductBrand.objects.get(name='VoteSecure')
        brand_pollmaster = ProductBrand.objects.get(name='PollMaster')
        
        products_data = [
            # Ballot Papers
            {
                'name': 'Ballot Paper - National Election',
                'category': category_ballot,
                'brand': brand_electionpro,
                'unit_code': 'pcs',
                'cost_price': Decimal('2.50'),
                'selling_price': Decimal('4.00'),
                'min_stock_level': Decimal('10000.00'),
            },
            {
                'name': 'Ballot Paper - Local Election',
                'category': category_ballot,
                'brand': brand_electionpro,
                'unit_code': 'pcs',
                'cost_price': Decimal('2.00'),
                'selling_price': Decimal('3.50'),
                'min_stock_level': Decimal('8000.00'),
            },
            {
                'name': 'Ballot Paper - Presidium Election',
                'category': category_ballot,
                'brand': brand_electionpro,
                'unit_code': 'pcs',
                'cost_price': Decimal('1.80'),
                'selling_price': Decimal('3.00'),
                'min_stock_level': Decimal('5000.00'),
            },
            # Voting Equipment
            {
                'name': 'Ballot Box - Transparent',
                'category': category_voting,
                'brand': brand_votesecure,
                'unit_code': 'pcs',
                'cost_price': Decimal('500.00'),
                'selling_price': Decimal('750.00'),
                'min_stock_level': Decimal('100.00'),
            },
            {
                'name': 'Voting Booth - Standard',
                'category': category_voting,
                'brand': brand_pollmaster,
                'unit_code': 'pcs',
                'cost_price': Decimal('1200.00'),
                'selling_price': Decimal('1800.00'),
                'min_stock_level': Decimal('50.00'),
            },
            {
                'name': 'Electronic Voting Machine',
                'category': category_voting,
                'brand': brand_votesecure,
                'unit_code': 'pcs',
                'cost_price': Decimal('15000.00'),
                'selling_price': Decimal('22000.00'),
                'min_stock_level': Decimal('10.00'),
            },
            # Campaign Materials
            {
                'name': 'Campaign Poster - Large',
                'category': category_campaign,
                'brand': brand_electionpro,
                'unit_code': 'pcs',
                'cost_price': Decimal('25.00'),
                'selling_price': Decimal('40.00'),
                'min_stock_level': Decimal('500.00'),
            },
            {
                'name': 'Campaign Banner',
                'category': category_campaign,
                'brand': brand_electionpro,
                'unit_code': 'pcs',
                'cost_price': Decimal('150.00'),
                'selling_price': Decimal('250.00'),
                'min_stock_level': Decimal('200.00'),
            },
            {
                'name': 'Election Pamphlet',
                'category': category_campaign,
                'brand': brand_electionpro,
                'unit_code': 'pack',
                'cost_price': Decimal('80.00'),
                'selling_price': Decimal('120.00'),
                'min_stock_level': Decimal('100.00'),
            },
            # Polling Station Supplies
            {
                'name': 'Polling Station Sign Board',
                'category': category_polling,
                'brand': brand_pollmaster,
                'unit_code': 'pcs',
                'cost_price': Decimal('300.00'),
                'selling_price': Decimal('450.00'),
                'min_stock_level': Decimal('150.00'),
            },
            {
                'name': 'Voter List Folder',
                'category': category_polling,
                'brand': brand_pollmaster,
                'unit_code': 'pcs',
                'cost_price': Decimal('50.00'),
                'selling_price': Decimal('75.00'),
                'min_stock_level': Decimal('300.00'),
            },
            {
                'name': 'Polling Station Table',
                'category': category_polling,
                'brand': brand_pollmaster,
                'unit_code': 'pcs',
                'cost_price': Decimal('800.00'),
                'selling_price': Decimal('1200.00'),
                'min_stock_level': Decimal('80.00'),
            },
            # Security Materials
            {
                'name': 'Security Seal - Tamper Proof',
                'category': category_security,
                'brand': brand_votesecure,
                'unit_code': 'pack',
                'cost_price': Decimal('200.00'),
                'selling_price': Decimal('300.00'),
                'min_stock_level': Decimal('100.00'),
            },
            {
                'name': 'Security Ink - Indelible',
                'category': category_security,
                'brand': brand_votesecure,
                'unit_code': 'bottle',
                'cost_price': Decimal('150.00'),
                'selling_price': Decimal('250.00'),
                'min_stock_level': Decimal('200.00'),
            },
            # Stationery
            {
                'name': 'Election Result Form',
                'category': category_stationery,
                'brand': brand_electionpro,
                'unit_code': 'pack',
                'cost_price': Decimal('120.00'),
                'selling_price': Decimal('180.00'),
                'min_stock_level': Decimal('150.00'),
            },
            {
                'name': 'Voter Registration Form',
                'category': category_stationery,
                'brand': brand_electionpro,
                'unit_code': 'pack',
                'cost_price': Decimal('100.00'),
                'selling_price': Decimal('150.00'),
                'min_stock_level': Decimal('200.00'),
            },
        ]
        
        for data in products_data:
            # Get unit type by code
            unit_type = UnitType.objects.get(code=data.get('unit_code', 'pcs'))
            Product.objects.get_or_create(
                name=data['name'],
                defaults={
                    'category': data['category'],
                    'brand': data['brand'],
                    'unit_type': unit_type,
                    'cost_price': data['cost_price'],
                    'selling_price': data['selling_price'],
                    'min_stock_level': data['min_stock_level'],
                    'is_active': True
                }
            )
        
        self.stdout.write('✓ Created elections products')

    def create_purchase_orders(self, user):
        """Create purchase orders to build inventory"""
        suppliers = Supplier.objects.all()
        products = Product.objects.all()
        
        if not suppliers.exists() or not products.exists():
            return
        
        # Create purchase orders with status='goods-received' to build inventory
        for i in range(8):
            supplier = random.choice(list(suppliers))
            order_date = timezone.now() - timedelta(days=random.randint(1, 25))
            
            order = PurchaseOrder.objects.create(
                order_number=f'PO-ELEC-{i+1:04d}',
                supplier=supplier,
                order_date=order_date,
                expected_date=order_date + timedelta(days=3),
                status='goods-received',  # This will add to inventory
                total_amount=Decimal('0.00'),
                created_by=user
            )
            
            # Add items to order
            num_items = random.randint(2, 5)
            selected_products = random.sample(list(products), min(num_items, products.count()))
            total_amount = Decimal('0.00')
            
            for product in selected_products:
                # Larger quantities for elections products
                if 'ballot' in product.name.lower():
                    quantity = Decimal(str(random.randint(5000, 20000)))
                elif 'ballot box' in product.name.lower() or 'voting booth' in product.name.lower():
                    quantity = Decimal(str(random.randint(50, 200)))
                elif 'electronic' in product.name.lower():
                    quantity = Decimal(str(random.randint(5, 20)))
                else:
                    quantity = Decimal(str(random.randint(100, 1000)))
                
                unit_price = product.cost_price
                total_price = quantity * unit_price
                
                PurchaseOrderItem.objects.create(
                    purchase_order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price
                )
                
                total_amount += total_price
            
            order.total_amount = total_amount
            order.save()
        
        self.stdout.write('✓ Created purchase orders (inventory built)')

    def create_sales_orders(self, user):
        """Create sales orders for elections"""
        customers = Customer.objects.all()
        products = Product.objects.all()
        
        if not customers.exists() or not products.exists():
            return
        
        # Create sales orders with status='delivered'
        for i in range(12):
            customer = random.choice(list(customers))
            order_date = timezone.now() - timedelta(days=random.randint(1, 20))
            
            order = SalesOrder.objects.create(
                order_number=f'SO-ELEC-{i+1:04d}',
                customer=customer,
                order_date=order_date,
                delivery_date=order_date + timedelta(days=2),
                status='delivered',  # This will reduce inventory
                sales_type='regular',
                total_amount=Decimal('0.00'),
                created_by=user
            )
            
            # Add items to order
            num_items = random.randint(2, 4)
            selected_products = random.sample(list(products), min(num_items, products.count()))
            total_amount = Decimal('0.00')
            
            for product in selected_products:
                # Realistic quantities for elections sales
                if 'ballot' in product.name.lower():
                    quantity = Decimal(str(random.randint(1000, 10000)))
                elif 'ballot box' in product.name.lower() or 'voting booth' in product.name.lower():
                    quantity = Decimal(str(random.randint(10, 50)))
                elif 'electronic' in product.name.lower():
                    quantity = Decimal(str(random.randint(1, 5)))
                else:
                    quantity = Decimal(str(random.randint(50, 500)))
                
                unit_price = product.selling_price
                total_price = quantity * unit_price
                
                SalesOrderItem.objects.create(
                    sales_order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price
                )
                
                total_amount += total_price
            
            order.total_amount = total_amount
            order.save()
        
        self.stdout.write('✓ Created sales orders')

