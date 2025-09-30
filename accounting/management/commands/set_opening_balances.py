from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from accounting.models import (
    Account, AccountCategory, JournalEntry, JournalEntryLine
)
from django.utils import timezone
from datetime import date


class Command(BaseCommand):
    help = 'Sets up opening balances for all accounts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Opening balance date (YYYY-MM-DD)',
            default=timezone.now().date().strftime('%Y-%m-%d')
        )

    def handle(self, *args, **options):
        opening_date = options['date']
        self.stdout.write(f'Setting up opening balances for {opening_date}...')
        
        # Create opening balance journal entry
        self.create_opening_balance_entry(opening_date)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created opening balance entries!')
        )

    def create_opening_balance_entry(self, opening_date):
        """Create opening balance journal entry"""
        try:
            with transaction.atomic():
                # Create opening balance journal entry
                journal_entry = JournalEntry.objects.create(
                    entry_number=f"OB-{opening_date.replace('-', '')}",
                    entry_date=opening_date,
                    description="Opening Balance Entry",
                    reference="Opening Balance",
                    is_balanced=True
                )
                
                # Define opening balances for different account types
                opening_balances = {
                    # Assets
                    'Cash in Hand': Decimal('50000.00'),
                    'Bank Account': Decimal('200000.00'),
                    'Accounts Receivable': Decimal('75000.00'),
                    'Inventory': Decimal('150000.00'),
                    'Equipment': Decimal('100000.00'),
                    'Furniture': Decimal('25000.00'),
                    
                    # Liabilities
                    'Accounts Payable': Decimal('45000.00'),
                    'Bank Loan': Decimal('100000.00'),
                    'Accrued Expenses': Decimal('5000.00'),
                    
                    # Equity
                    'Owner Capital': Decimal('300000.00'),
                    'Retained Earnings': Decimal('50000.00'),
                    
                    # Income
                    'Sales Revenue': Decimal('0.00'),
                    'Service Revenue': Decimal('0.00'),
                    
                    # Expenses
                    'Purchase Expenses': Decimal('0.00'),
                    'Operating Expenses': Decimal('0.00'),
                    'Administrative Expenses': Decimal('0.00'),
                }
                
                total_debits = Decimal('0')
                total_credits = Decimal('0')
                
                for account_name, balance in opening_balances.items():
                    account = self.get_or_create_account(account_name)
                    
                    if balance > 0:
                        if account.category.account_type in ['asset', 'expense']:
                            # Debit for assets and expenses
                            JournalEntryLine.objects.create(
                                journal_entry=journal_entry,
                                account=account,
                                description=f"Opening balance for {account_name}",
                                debit_amount=balance,
                                credit_amount=Decimal('0')
                            )
                            total_debits += balance
                        else:
                            # Credit for liabilities, equity, and income
                            JournalEntryLine.objects.create(
                                journal_entry=journal_entry,
                                account=account,
                                description=f"Opening balance for {account_name}",
                                debit_amount=Decimal('0'),
                                credit_amount=balance
                            )
                            total_credits += balance
                
                # Update journal entry totals
                journal_entry.total_debit = total_debits
                journal_entry.total_credit = total_credits
                journal_entry.is_balanced = abs(total_debits - total_credits) < Decimal('0.01')
                journal_entry.save()
                
                self.stdout.write(f'Created opening balance entry: {journal_entry.entry_number}')
                self.stdout.write(f'Total Debits: ৳{total_debits}')
                self.stdout.write(f'Total Credits: ৳{total_credits}')
                self.stdout.write(f'Balanced: {journal_entry.is_balanced}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating opening balance entry: {str(e)}')
            )

    def get_or_create_account(self, name):
        """Get or create account with specified name"""
        try:
            account = Account.objects.get(name=name)
            return account
        except Account.DoesNotExist:
            # Determine account type based on name
            if name in ['Cash in Hand', 'Bank Account', 'Accounts Receivable', 'Inventory', 'Equipment', 'Furniture']:
                account_type = 'asset'
            elif name in ['Accounts Payable', 'Bank Loan', 'Accrued Expenses']:
                account_type = 'liability'
            elif name in ['Owner Capital', 'Retained Earnings']:
                account_type = 'equity'
            elif name in ['Sales Revenue', 'Service Revenue']:
                account_type = 'income'
            else:
                account_type = 'expense'
            
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
