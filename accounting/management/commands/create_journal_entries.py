from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from accounting.models import (
    Account, AccountCategory, JournalEntry, JournalEntryLine,
    BankAccount, BankTransaction
)
from purchases.models import PurchasePayment, PurchaseInvoice
from sales.models import SalesPayment, SalesInvoice
from suppliers.models import SupplierLedger
from customers.models import CustomerLedger
from django.utils import timezone
from datetime import date


class Command(BaseCommand):
    help = 'Creates journal entries for supplier payments and customer payments'

    def handle(self, *args, **options):
        self.stdout.write('Creating journal entries for payments...')
        
        # Create journal entries for supplier payments
        self.create_supplier_payment_journals()
        
        # Create journal entries for customer payments
        self.create_customer_payment_journals()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created journal entries for all payments!')
        )

    def create_supplier_payment_journals(self):
        """Create journal entries for supplier payments"""
        self.stdout.write('Creating journal entries for supplier payments...')
        
        # Get or create accounts
        accounts_payable = self.get_or_create_account('Accounts Payable', 'liability')
        cash_account = self.get_or_create_account('Cash in Hand', 'asset')
        bank_account = self.get_or_create_account('Bank Account', 'asset')
        
        supplier_payments = PurchasePayment.objects.filter(
            created_at__date=timezone.now().date()
        )
        
        for payment in supplier_payments:
            try:
                with transaction.atomic():
                    # Create journal entry
                    journal_entry = JournalEntry.objects.create(
                        entry_number=f"SP-{payment.id}-{timezone.now().strftime('%Y%m%d')}",
                        entry_date=payment.payment_date,
                        description=f"Supplier payment for {payment.purchase_invoice.invoice_number}",
                        reference=payment.reference,
                        created_by=payment.created_by
                    )
                    
                    # Determine debit account based on payment method
                    if payment.payment_method == 'cash':
                        debit_account = cash_account
                    else:
                        debit_account = bank_account
                    
                    # Create debit line (Payment made)
                    JournalEntryLine.objects.create(
                        journal_entry=journal_entry,
                        account=debit_account,
                        description=f"Payment to {payment.purchase_invoice.supplier.name}",
                        debit_amount=payment.amount,
                        credit_amount=Decimal('0')
                    )
                    
                    # Create credit line (Accounts Payable reduced)
                    JournalEntryLine.objects.create(
                        journal_entry=journal_entry,
                        account=accounts_payable,
                        description=f"Payment to {payment.purchase_invoice.supplier.name}",
                        debit_amount=Decimal('0'),
                        credit_amount=payment.amount
                    )
                    
                    # Update journal entry totals
                    journal_entry.total_debit = payment.amount
                    journal_entry.total_credit = payment.amount
                    journal_entry.is_balanced = True
                    journal_entry.save()
                    
                    # Create bank transaction if payment method is bank transfer
                    if payment.payment_method == 'bank_transfer' and payment.bank_account:
                        BankTransaction.objects.create(
                            bank_account=payment.bank_account,
                            transaction_type='withdrawal',
                            amount=payment.amount,
                            description=f"Payment to {payment.purchase_invoice.supplier.name}",
                            reference=payment.reference,
                            transaction_date=payment.payment_date,
                            created_by=payment.created_by
                        )
                    
                    self.stdout.write(f'Created journal entry for supplier payment: {payment.id}')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating journal entry for supplier payment {payment.id}: {str(e)}')
                )

    def create_customer_payment_journals(self):
        """Create journal entries for customer payments"""
        self.stdout.write('Creating journal entries for customer payments...')
        
        # Get or create accounts
        accounts_receivable = self.get_or_create_account('Accounts Receivable', 'asset')
        cash_account = self.get_or_create_account('Cash in Hand', 'asset')
        bank_account = self.get_or_create_account('Bank Account', 'asset')
        sales_revenue = self.get_or_create_account('Sales Revenue', 'income')
        
        customer_payments = SalesPayment.objects.filter(
            created_at__date=timezone.now().date()
        )
        
        for payment in customer_payments:
            try:
                with transaction.atomic():
                    # Create journal entry
                    journal_entry = JournalEntry.objects.create(
                        entry_number=f"CP-{payment.id}-{timezone.now().strftime('%Y%m%d')}",
                        entry_date=payment.payment_date,
                        description=f"Customer payment for {payment.sales_invoice.invoice_number}",
                        reference=payment.reference,
                        created_by=payment.created_by
                    )
                    
                    # Determine credit account based on payment method
                    if payment.payment_method == 'cash':
                        credit_account = cash_account
                    else:
                        credit_account = bank_account
                    
                    # Create debit line (Cash/Bank received)
                    JournalEntryLine.objects.create(
                        journal_entry=journal_entry,
                        account=credit_account,
                        description=f"Payment from {payment.sales_invoice.customer.name}",
                        debit_amount=payment.amount,
                        credit_amount=Decimal('0')
                    )
                    
                    # Create credit line (Accounts Receivable reduced)
                    JournalEntryLine.objects.create(
                        journal_entry=journal_entry,
                        account=accounts_receivable,
                        description=f"Payment from {payment.sales_invoice.customer.name}",
                        debit_amount=Decimal('0'),
                        credit_amount=payment.amount
                    )
                    
                    # Update journal entry totals
                    journal_entry.total_debit = payment.amount
                    journal_entry.total_credit = payment.amount
                    journal_entry.is_balanced = True
                    journal_entry.save()
                    
                    # Create bank transaction if payment method is bank transfer
                    if payment.payment_method == 'bank_transfer' and payment.bank_account:
                        BankTransaction.objects.create(
                            bank_account=payment.bank_account,
                            transaction_type='deposit',
                            amount=payment.amount,
                            description=f"Payment from {payment.sales_invoice.customer.name}",
                            reference=payment.reference,
                            transaction_date=payment.payment_date,
                            created_by=payment.created_by
                        )
                    
                    self.stdout.write(f'Created journal entry for customer payment: {payment.id}')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating journal entry for customer payment {payment.id}: {str(e)}')
                )

    def get_or_create_account(self, name, account_type):
        """Get or create account with specified name and type"""
        try:
            # Try to find existing account
            account = Account.objects.get(name=name)
            return account
        except Account.DoesNotExist:
            # Create account category if it doesn't exist
            category, created = AccountCategory.objects.get_or_create(
                name=f"{account_type.title()} Category",
                account_type=account_type
            )
            
            # Create account
            account = Account.objects.create(
                code=f"{account_type.upper()}{Account.objects.count() + 1:04d}",
                name=name,
                category=category
            )
            
            self.stdout.write(f'Created account: {name}')
            return account
