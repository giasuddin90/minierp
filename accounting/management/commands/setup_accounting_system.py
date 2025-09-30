from django.core.management.base import BaseCommand
from django.utils import timezone
from accounting.models import (
    AccountCategory, Account, ExpenseCategory, IncomeCategory, 
    Expense, Income, BankAccount
)
from decimal import Decimal
import random
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Set up complete accounting system with chart of accounts and sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing accounting data before setup',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing accounting data...')
            Expense.objects.all().delete()
            Income.objects.all().delete()
            Account.objects.all().delete()
            AccountCategory.objects.all().delete()
            ExpenseCategory.objects.all().delete()
            IncomeCategory.objects.all().delete()

        # Create Account Categories
        self.create_account_categories()
        
        # Create Chart of Accounts
        self.create_chart_of_accounts()
        
        # Create Expense Categories
        self.create_expense_categories()
        
        # Create Income Categories
        self.create_income_categories()
        
        # Create Sample Expenses
        self.create_sample_expenses()
        
        # Create Sample Income
        self.create_sample_income()
        
        self.stdout.write(
            self.style.SUCCESS('Accounting system setup completed successfully!')
        )

    def create_account_categories(self):
        """Create account categories"""
        categories = [
            ('Assets', 'asset'),
            ('Liabilities', 'liability'),
            ('Equity', 'equity'),
            ('Income', 'income'),
            ('Expenses', 'expense'),
        ]
        
        for name, account_type in categories:
            category, created = AccountCategory.objects.get_or_create(
                name=name,
                defaults={'account_type': account_type}
            )
            if created:
                self.stdout.write(f'Created account category: {name}')

    def create_chart_of_accounts(self):
        """Create chart of accounts"""
        # Get categories
        asset_cat = AccountCategory.objects.get(name='Assets')
        liability_cat = AccountCategory.objects.get(name='Liabilities')
        equity_cat = AccountCategory.objects.get(name='Equity')
        income_cat = AccountCategory.objects.get(name='Income')
        expense_cat = AccountCategory.objects.get(name='Expenses')
        
        accounts = [
            # Assets
            ('1000', 'Cash in Hand', asset_cat, None),
            ('1100', 'Bank Accounts', asset_cat, None),
            ('1200', 'Accounts Receivable', asset_cat, None),
            ('1300', 'Inventory', asset_cat, None),
            ('1400', 'Fixed Assets', asset_cat, None),
            
            # Liabilities
            ('2000', 'Accounts Payable', liability_cat, None),
            ('2100', 'Loans Payable', liability_cat, None),
            ('2200', 'Accrued Expenses', liability_cat, None),
            
            # Equity
            ('3000', 'Owner\'s Equity', equity_cat, None),
            ('3100', 'Retained Earnings', equity_cat, None),
            
            # Income
            ('4000', 'Sales Revenue', income_cat, None),
            ('4100', 'Service Revenue', income_cat, None),
            ('4200', 'Other Income', income_cat, None),
            
            # Expenses
            ('5000', 'Cost of Goods Sold', expense_cat, None),
            ('5100', 'Operating Expenses', expense_cat, None),
            ('5200', 'Administrative Expenses', expense_cat, None),
            ('5300', 'Financial Expenses', expense_cat, None),
        ]
        
        for code, name, category, parent in accounts:
            account, created = Account.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'category': category,
                    'parent_account': parent
                }
            )
            if created:
                self.stdout.write(f'Created account: {code} - {name}')

    def create_expense_categories(self):
        """Create expense categories"""
        categories = [
            'House Rent',
            'Office Rent',
            'Utilities (Electricity)',
            'Utilities (Water)',
            'Utilities (Gas)',
            'Internet & Phone',
            'Office Supplies',
            'Marketing & Advertising',
            'Transportation',
            'Meals & Entertainment',
            'Professional Services',
            'Insurance',
            'Maintenance & Repairs',
            'Bank Charges',
            'Interest Expense',
            'Other Operating Expenses',
        ]
        
        for name in categories:
            category, created = ExpenseCategory.objects.get_or_create(name=name)
            if created:
                self.stdout.write(f'Created expense category: {name}')

    def create_income_categories(self):
        """Create income categories"""
        categories = [
            'Sales Revenue',
            'Service Revenue',
            'Interest Income',
            'Rental Income',
            'Investment Income',
            'Other Income',
        ]
        
        for name in categories:
            category, created = IncomeCategory.objects.get_or_create(name=name)
            if created:
                self.stdout.write(f'Created income category: {name}')

    def create_sample_expenses(self):
        """Create sample expenses"""
        expense_categories = ExpenseCategory.objects.all()
        bank_accounts = BankAccount.objects.filter(is_active=True)
        
        if not expense_categories.exists():
            self.stdout.write('No expense categories found. Creating sample expenses skipped.')
            return
        
        if not bank_accounts.exists():
            self.stdout.write('No bank accounts found. Creating sample expenses skipped.')
            return
        
        # Sample expenses for the last 30 days
        for i in range(20):
            category = random.choice(expense_categories)
            amount = Decimal(str(random.uniform(500, 50000)))
            bank_account = random.choice(bank_accounts) if random.choice([True, False]) else None
            
            # Random date in last 30 days
            days_ago = random.randint(1, 30)
            expense_date = timezone.now().date() - timedelta(days=days_ago)
            
            Expense.objects.create(
                expense_category=category,
                amount=amount,
                description=f"Sample expense for {category.name}",
                payment_method=random.choice(['cash', 'bank', 'check', 'card']),
                bank_account=bank_account,
                expense_date=expense_date,
                reference=f"EXP-{i+1:03d}",
            )
        
        self.stdout.write('Created 20 sample expenses')

    def create_sample_income(self):
        """Create sample income"""
        income_categories = IncomeCategory.objects.all()
        bank_accounts = BankAccount.objects.filter(is_active=True)
        
        if not income_categories.exists():
            self.stdout.write('No income categories found. Creating sample income skipped.')
            return
        
        if not bank_accounts.exists():
            self.stdout.write('No bank accounts found. Creating sample income skipped.')
            return
        
        # Sample income for the last 30 days
        for i in range(15):
            category = random.choice(income_categories)
            amount = Decimal(str(random.uniform(1000, 100000)))
            bank_account = random.choice(bank_accounts) if random.choice([True, False]) else None
            
            # Random date in last 30 days
            days_ago = random.randint(1, 30)
            income_date = timezone.now().date() - timedelta(days=days_ago)
            
            Income.objects.create(
                income_category=category,
                amount=amount,
                description=f"Sample income from {category.name}",
                payment_method=random.choice(['cash', 'bank', 'check', 'card']),
                bank_account=bank_account,
                income_date=income_date,
                reference=f"INC-{i+1:03d}",
            )
        
        self.stdout.write('Created 15 sample income records')
