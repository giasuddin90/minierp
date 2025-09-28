from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import random

from accounting.models import BankAccount, BankTransaction, Loan, LoanTransaction, TrialBalance
from customers.models import Customer, CustomerLedger, CustomerCommission, CustomerCommitment
from suppliers.models import Supplier, SupplierLedger, SupplierCommission
from stock.models import Warehouse, ProductCategory, Product, Stock, StockMovement, StockAlert
from sales.models import SalesOrder, SalesOrderItem, SalesInvoice, SalesInvoiceItem, SalesReturn, SalesReturnItem, SalesPayment
from purchases.models import PurchaseOrder, PurchaseOrderItem, GoodsReceipt, GoodsReceiptItem, PurchaseInvoice, PurchaseInvoiceItem, PurchaseReturn, PurchaseReturnItem, PurchasePayment


class Command(BaseCommand):
    help = 'Upload demo data for testing the Building Materials ERP system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting demo data upload...'))
        
        # Clear existing demo data first
        self.clear_existing_data()
        
        # Create demo data
        self.create_bank_accounts()
        self.create_warehouses()
        self.create_product_categories()
        self.create_products()
        self.create_customers()
        self.create_suppliers()
        self.create_stock_data()
        self.create_sales_data()
        self.create_purchase_data()
        self.create_trial_balance_data()
        
        self.stdout.write(self.style.SUCCESS('Demo data upload completed successfully!'))
        self.stdout.write(self.style.SUCCESS('You can now test the full software functionality.'))

    def clear_existing_data(self):
        """Clear existing demo data"""
        self.stdout.write('Clearing existing demo data...')
        
        # Clear in reverse order to avoid foreign key constraints
        SalesPayment.objects.all().delete()
        SalesReturnItem.objects.all().delete()
        SalesReturn.objects.all().delete()
        SalesInvoiceItem.objects.all().delete()
        SalesInvoice.objects.all().delete()
        SalesOrderItem.objects.all().delete()
        SalesOrder.objects.all().delete()
        
        PurchasePayment.objects.all().delete()
        PurchaseReturnItem.objects.all().delete()
        PurchaseReturn.objects.all().delete()
        PurchaseInvoiceItem.objects.all().delete()
        PurchaseInvoice.objects.all().delete()
        GoodsReceiptItem.objects.all().delete()
        GoodsReceipt.objects.all().delete()
        PurchaseOrderItem.objects.all().delete()
        PurchaseOrder.objects.all().delete()
        
        StockMovement.objects.all().delete()
        StockAlert.objects.all().delete()
        Stock.objects.all().delete()
        Product.objects.all().delete()
        ProductCategory.objects.all().delete()
        Warehouse.objects.all().delete()
        
        CustomerCommitment.objects.all().delete()
        CustomerCommission.objects.all().delete()
        CustomerLedger.objects.all().delete()
        Customer.objects.all().delete()
        
        SupplierCommission.objects.all().delete()
        SupplierLedger.objects.all().delete()
        Supplier.objects.all().delete()
        
        LoanTransaction.objects.all().delete()
        Loan.objects.all().delete()
        BankTransaction.objects.all().delete()
        BankAccount.objects.all().delete()
        TrialBalance.objects.all().delete()

    def create_bank_accounts(self):
        """Create bank accounts and transactions"""
        self.stdout.write('Creating bank accounts...')
        
        # Bank accounts
        banks = [
            {'name': 'Main Business Account', 'bank_name': 'Dutch-Bangla Bank', 'account_number': '1234567890', 'opening_balance': 500000},
            {'name': 'Savings Account', 'bank_name': 'BRAC Bank', 'account_number': '9876543210', 'opening_balance': 200000},
            {'name': 'Loan Account', 'bank_name': 'Islami Bank', 'account_number': '5555555555', 'opening_balance': 0},
        ]
        
        for bank_data in banks:
            bank, created = BankAccount.objects.get_or_create(
                name=bank_data['name'],
                defaults={
                    'bank_name': bank_data['bank_name'],
                    'account_number': bank_data['account_number'],
                    'opening_balance': bank_data['opening_balance'],
                    'current_balance': bank_data['opening_balance'],
                    'is_active': True
                }
            )
            
            # Create some bank transactions
            for i in range(5):
                BankTransaction.objects.get_or_create(
                    bank_account=bank,
                    transaction_type=random.choice(['deposit', 'withdrawal']),
                    amount=Decimal(random.randint(10000, 100000)),
                    description=f"Demo transaction {i+1}",
                    transaction_date=timezone.now() - timedelta(days=random.randint(1, 30)),
                    created_by=User.objects.first()
                )

    def create_warehouses(self):
        """Create warehouses"""
        self.stdout.write('Creating warehouses...')
        
        warehouses = [
            {'name': 'Main Warehouse', 'location': 'Dhaka, Bangladesh'},
            {'name': 'Chittagong Branch', 'location': 'Chittagong, Bangladesh'},
            {'name': 'Sylhet Branch', 'location': 'Sylhet, Bangladesh'},
        ]
        
        for warehouse_data in warehouses:
            Warehouse.objects.get_or_create(
                name=warehouse_data['name'],
                defaults={'location': warehouse_data['location'], 'is_active': True}
            )

    def create_product_categories(self):
        """Create product categories"""
        self.stdout.write('Creating product categories...')
        
        categories = [
            {'name': 'Cement', 'description': 'Various types of cement products'},
            {'name': 'Steel Rod', 'description': 'Steel reinforcement bars'},
            {'name': 'Tiles', 'description': 'Floor and wall tiles'},
            {'name': 'Paint', 'description': 'Interior and exterior paints'},
            {'name': 'Hardware', 'description': 'Nails, screws, and other hardware items'},
        ]
        
        for category_data in categories:
            ProductCategory.objects.get_or_create(
                name=category_data['name'],
                defaults={'description': category_data['description'], 'is_active': True}
            )

    def create_products(self):
        """Create products"""
        self.stdout.write('Creating products...')
        
        products = [
            # Cement products
            {'name': 'Lafarge Cement 50kg', 'category': 'Cement', 'brand': 'Lafarge', 'unit_type': 'bag', 'unit_name': 'Bag', 'cost_price': 450, 'selling_price': 500, 'min_stock_level': 100},
            {'name': 'Holcim Cement 50kg', 'category': 'Cement', 'brand': 'Holcim', 'unit_type': 'bag', 'unit_name': 'Bag', 'cost_price': 440, 'selling_price': 490, 'min_stock_level': 100},
            {'name': 'Crown Cement 50kg', 'category': 'Cement', 'brand': 'Crown', 'unit_type': 'bag', 'unit_name': 'Bag', 'cost_price': 430, 'selling_price': 480, 'min_stock_level': 100},
            
            # Steel products
            {'name': 'Steel Rod 12mm', 'category': 'Steel Rod', 'brand': 'BSRM', 'unit_type': 'kg', 'unit_name': 'KG', 'cost_price': 85, 'selling_price': 95, 'min_stock_level': 1000},
            {'name': 'Steel Rod 16mm', 'category': 'Steel Rod', 'brand': 'BSRM', 'unit_type': 'kg', 'unit_name': 'KG', 'cost_price': 85, 'selling_price': 95, 'min_stock_level': 1000},
            {'name': 'Steel Rod 20mm', 'category': 'Steel Rod', 'brand': 'BSRM', 'unit_type': 'kg', 'unit_name': 'KG', 'cost_price': 85, 'selling_price': 95, 'min_stock_level': 1000},
            
            # Tiles
            {'name': 'Ceramic Floor Tile 2x2', 'category': 'Tiles', 'brand': 'Rongpong', 'unit_type': 'sqft', 'unit_name': 'Sq Ft', 'cost_price': 45, 'selling_price': 55, 'min_stock_level': 500},
            {'name': 'Wall Tile 1x1', 'category': 'Tiles', 'brand': 'Rongpong', 'unit_type': 'sqft', 'unit_name': 'Sq Ft', 'cost_price': 35, 'selling_price': 45, 'min_stock_level': 500},
            
            # Paint
            {'name': 'Interior Paint 1L', 'category': 'Paint', 'brand': 'Berger', 'unit_type': 'liter', 'unit_name': 'Liter', 'cost_price': 250, 'selling_price': 300, 'min_stock_level': 50},
            {'name': 'Exterior Paint 1L', 'category': 'Paint', 'brand': 'Berger', 'unit_type': 'liter', 'unit_name': 'Liter', 'cost_price': 300, 'selling_price': 350, 'min_stock_level': 50},
            
            # Hardware
            {'name': 'Nails 2 inch', 'category': 'Hardware', 'brand': 'Generic', 'unit_type': 'kg', 'unit_name': 'KG', 'cost_price': 80, 'selling_price': 100, 'min_stock_level': 50},
            {'name': 'Screws 3 inch', 'category': 'Hardware', 'brand': 'Generic', 'unit_type': 'pcs', 'unit_name': 'Pieces', 'cost_price': 2, 'selling_price': 3, 'min_stock_level': 1000},
        ]
        
        for product_data in products:
            category = ProductCategory.objects.get(name=product_data['category'])
            Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'category': category,
                    'brand': product_data['brand'],
                    'unit_type': product_data['unit_type'],
                    'unit_name': product_data['unit_name'],
                    'cost_price': product_data['cost_price'],
                    'selling_price': product_data['selling_price'],
                    'min_stock_level': product_data['min_stock_level'],
                    'is_active': True
                }
            )

    def create_customers(self):
        """Create customers"""
        self.stdout.write('Creating customers...')
        
        customers = [
            # Retail customers
            {'name': 'Abdul Rahman', 'customer_type': 'retail', 'phone': '01712345678', 'address': 'Dhanmondi, Dhaka', 'credit_limit': 50000},
            {'name': 'Fatima Begum', 'customer_type': 'retail', 'phone': '01723456789', 'address': 'Gulshan, Dhaka', 'credit_limit': 30000},
            {'name': 'Mohammad Ali', 'customer_type': 'retail', 'phone': '01734567890', 'address': 'Uttara, Dhaka', 'credit_limit': 40000},
            
            # Wholesale customers
            {'name': 'Rahman Construction Ltd', 'customer_type': 'wholesale', 'phone': '01745678901', 'address': 'Tejgaon, Dhaka', 'credit_limit': 500000},
            {'name': 'Ali Builders', 'customer_type': 'wholesale', 'phone': '01756789012', 'address': 'Banani, Dhaka', 'credit_limit': 300000},
            {'name': 'Hasan Developers', 'customer_type': 'wholesale', 'phone': '01767890123', 'address': 'Dhanmondi, Dhaka', 'credit_limit': 400000},
        ]
        
        for customer_data in customers:
            customer, created = Customer.objects.get_or_create(
                name=customer_data['name'],
                defaults={
                    'customer_type': customer_data['customer_type'],
                    'phone': customer_data['phone'],
                    'address': customer_data['address'],
                    'credit_limit': customer_data['credit_limit'],
                    'opening_balance': 0,
                    'current_balance': 0,
                    'is_active': True
                }
            )
            
            # Create customer commissions
            if customer.customer_type == 'wholesale':
                CustomerCommission.objects.get_or_create(
                    customer=customer,
                    commission_rate=Decimal('2.5'),
                    is_per_party=True,
                    effective_from=timezone.now().date(),
                    is_active=True
                )

    def create_suppliers(self):
        """Create suppliers"""
        self.stdout.write('Creating suppliers...')
        
        suppliers = [
            {'name': 'Lafarge Bangladesh Ltd', 'phone': '01778901234', 'address': 'Tejgaon, Dhaka', 'contact_person': 'Mr. Karim'},
            {'name': 'BSRM Steel Ltd', 'phone': '01789012345', 'address': 'Chittagong', 'contact_person': 'Mr. Rahman'},
            {'name': 'Rongpong Ceramics', 'phone': '01790123456', 'address': 'Narayanganj', 'contact_person': 'Mr. Ahmed'},
            {'name': 'Berger Paints Bangladesh', 'phone': '01701234567', 'address': 'Dhaka', 'contact_person': 'Mr. Hasan'},
            {'name': 'Hardware Supply Co', 'phone': '01712345098', 'address': 'Old Dhaka', 'contact_person': 'Mr. Ali'},
        ]
        
        for supplier_data in suppliers:
            supplier, created = Supplier.objects.get_or_create(
                name=supplier_data['name'],
                defaults={
                    'contact_person': supplier_data['contact_person'],
                    'phone': supplier_data['phone'],
                    'address': supplier_data['address'],
                    'opening_balance': 0,
                    'current_balance': 0,
                    'is_active': True
                }
            )

    def create_stock_data(self):
        """Create stock data"""
        self.stdout.write('Creating stock data...')
        
        warehouses = Warehouse.objects.all()
        products = Product.objects.all()
        
        for warehouse in warehouses:
            for product in products:
                # Create stock entry
                stock, created = Stock.objects.get_or_create(
                    product=product,
                    warehouse=warehouse,
                    defaults={
                        'quantity': random.randint(50, 500),
                        'unit_cost': product.cost_price
                    }
                )
                
                # Create stock movements
                for i in range(3):
                    StockMovement.objects.get_or_create(
                        product=product,
                        warehouse=warehouse,
                        movement_type='inward',
                        quantity=random.randint(10, 100),
                        unit_cost=product.cost_price,
                        movement_date=timezone.now() - timedelta(days=random.randint(1, 30)),
                        created_by=User.objects.first(),
                        reference=f"INV-{random.randint(1000, 9999)}"
                    )

    def create_sales_data(self):
        """Create sales data"""
        self.stdout.write('Creating sales data...')
        
        customers = Customer.objects.all()
        products = Product.objects.all()
        warehouses = Warehouse.objects.all()
        
        # Create sales orders
        for i in range(10):
            customer = random.choice(customers)
            order = SalesOrder.objects.create(
                order_number=f"SO-{1000 + i}",
                customer=customer,
                order_date=timezone.now().date() - timedelta(days=random.randint(1, 30)),
                delivery_date=timezone.now().date() - timedelta(days=random.randint(1, 15)),
                status=random.choice(['confirmed', 'delivered']),
                total_amount=0,
                created_by=User.objects.first()
            )
            
            # Create order items
            total_amount = 0
            for j in range(random.randint(1, 5)):
                product = random.choice(products)
                quantity = random.randint(1, 20)
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
            
                # Create sales invoice if order is delivered
            if order.status == 'delivered':
                payment_type = random.choice(['cash', 'credit'])
                labor_charges = total_amount * Decimal('0.05') if customer.customer_type == 'retail' else 0
                invoice_total = total_amount + labor_charges
                
                invoice = SalesInvoice.objects.create(
                    invoice_number=f"INV-{1000 + i}",
                    customer=customer,
                    sales_order=order,
                    invoice_date=order.delivery_date,
                    payment_type=payment_type,
                    subtotal=total_amount,
                    labor_charges=labor_charges,
                    total_amount=invoice_total,
                    paid_amount=invoice_total if payment_type == 'cash' else 0,
                    due_amount=0 if payment_type == 'cash' else invoice_total,
                    created_by=User.objects.first()
                )
                
                # Create invoice items
                for item in order.items.all():
                    warehouse = random.choice(warehouses)
                    SalesInvoiceItem.objects.create(
                        sales_invoice=invoice,
                        product=item.product,
                        warehouse=warehouse,
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                        total_price=item.total_price
                    )
                
                # Create payment if cash sale
                if invoice.payment_type == 'cash':
                    SalesPayment.objects.create(
                        sales_invoice=invoice,
                        payment_date=invoice.invoice_date,
                        payment_method='cash',
                        amount=invoice.total_amount,
                        created_by=User.objects.first()
                    )

    def create_purchase_data(self):
        """Create purchase data"""
        self.stdout.write('Creating purchase data...')
        
        suppliers = Supplier.objects.all()
        products = Product.objects.all()
        warehouses = Warehouse.objects.all()
        
        # Create purchase orders
        for i in range(8):
            supplier = random.choice(suppliers)
            order = PurchaseOrder.objects.create(
                order_number=f"PO-{1000 + i}",
                supplier=supplier,
                order_date=timezone.now().date() - timedelta(days=random.randint(1, 30)),
                expected_date=timezone.now().date() - timedelta(days=random.randint(1, 15)),
                status=random.choice(['sent', 'received']),
                total_amount=0,
                created_by=User.objects.first()
            )
            
            # Create order items
            total_amount = 0
            for j in range(random.randint(1, 4)):
                product = random.choice(products)
                quantity = random.randint(10, 100)
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
            
            # Create goods receipt if order is received
            if order.status == 'received':
                receipt = GoodsReceipt.objects.create(
                    receipt_number=f"GR-{1000 + i}",
                    purchase_order=order,
                    receipt_date=order.expected_date,
                    status='received',
                    total_amount=total_amount,
                    created_by=User.objects.first()
                )
                
                # Create receipt items
                for item in order.items.all():
                    warehouse = random.choice(warehouses)
                    GoodsReceiptItem.objects.create(
                        goods_receipt=receipt,
                        product=item.product,
                        warehouse=warehouse,
                        quantity=item.quantity,
                        unit_cost=item.unit_price,
                        total_cost=item.total_price
                    )
                
                # Create purchase invoice
                invoice = PurchaseInvoice.objects.create(
                    invoice_number=f"PINV-{1000 + i}",
                    supplier=supplier,
                    purchase_order=order,
                    goods_receipt=receipt,
                    invoice_date=receipt.receipt_date,
                    payment_type=random.choice(['cash', 'credit']),
                    subtotal=total_amount,
                    total_amount=total_amount,
                    paid_amount=total_amount if random.choice([True, False]) else 0,
                    due_amount=0 if total_amount == 0 else total_amount,
                    created_by=User.objects.first()
                )
                
                # Create invoice items
                for item in receipt.items.all():
                    PurchaseInvoiceItem.objects.create(
                        purchase_invoice=invoice,
                        product=item.product,
                        warehouse=item.warehouse,
                        quantity=item.quantity,
                        unit_cost=item.unit_cost,
                        total_cost=item.total_cost
                    )

    def create_trial_balance_data(self):
        """Create trial balance data"""
        self.stdout.write('Creating trial balance data...')
        
        # Create trial balance for today
        today = timezone.now().date()
        TrialBalance.objects.get_or_create(
            date=today,
            defaults={
                'opening_balance': 500000,
                'cash_inflows': 150000,
                'cash_outflows': 100000,
                'closing_balance': 550000,
                'is_balanced': True
            }
        )
