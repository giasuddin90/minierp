from django.core.management.base import BaseCommand
from django.utils import timezone
from accounting.models import BankAccount, BankTransaction
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Add sample banks and initial transactions to the system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing banks before adding new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing banks...')
            BankAccount.objects.all().delete()
            BankTransaction.objects.all().delete()

        # Sample banks data
        banks_data = [
            {
                'name': 'Main Business Account',
                'account_number': 'ACC-001-2024',
                'bank_name': 'City Bank Limited',
                'branch': 'Dhanmondi Branch',
                'opening_balance': Decimal('500000.00'),
                'current_balance': Decimal('500000.00'),
            },
            {
                'name': 'Operating Account',
                'account_number': 'ACC-002-2024',
                'bank_name': 'Dutch-Bangla Bank Limited',
                'branch': 'Gulshan Branch',
                'opening_balance': Decimal('250000.00'),
                'current_balance': Decimal('250000.00'),
            },
            {
                'name': 'Savings Account',
                'account_number': 'ACC-003-2024',
                'bank_name': 'Islami Bank Bangladesh Limited',
                'branch': 'Uttara Branch',
                'opening_balance': Decimal('100000.00'),
                'current_balance': Decimal('100000.00'),
            },
            {
                'name': 'Investment Account',
                'account_number': 'ACC-004-2024',
                'bank_name': 'BRAC Bank Limited',
                'branch': 'Banani Branch',
                'opening_balance': Decimal('750000.00'),
                'current_balance': Decimal('750000.00'),
            },
            {
                'name': 'Emergency Fund',
                'account_number': 'ACC-005-2024',
                'bank_name': 'Eastern Bank Limited',
                'branch': 'Motijheel Branch',
                'opening_balance': Decimal('200000.00'),
                'current_balance': Decimal('200000.00'),
            },
        ]

        created_banks = []
        
        for bank_data in banks_data:
            bank, created = BankAccount.objects.get_or_create(
                account_number=bank_data['account_number'],
                defaults=bank_data
            )
            
            if created:
                created_banks.append(bank)
                self.stdout.write(
                    self.style.SUCCESS(f'Created bank: {bank.name} - {bank.bank_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Bank already exists: {bank.name} - {bank.bank_name}')
                )

        # Add sample transactions for each bank
        self.add_sample_transactions(created_banks)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully processed {len(created_banks)} banks')
        )

    def add_sample_transactions(self, banks):
        """Add sample transactions for the created banks"""
        transaction_types = ['deposit', 'withdrawal', 'transfer_in', 'transfer_out']
        descriptions = [
            'Initial deposit',
            'Business income',
            'Customer payment',
            'Supplier payment',
            'Office rent',
            'Utility bill payment',
            'Salary payment',
            'Equipment purchase',
            'Marketing expense',
            'Insurance payment',
            'Tax payment',
            'Investment return',
            'Loan disbursement',
            'Interest earned',
            'Service charge',
        ]

        for bank in banks:
            # Add 5-10 random transactions for each bank
            num_transactions = random.randint(5, 10)
            
            for i in range(num_transactions):
                transaction_type = random.choice(transaction_types)
                amount = Decimal(str(random.uniform(1000, 50000))).quantize(Decimal('0.01'))
                description = random.choice(descriptions)
                
                # Adjust amount based on transaction type
                if transaction_type in ['withdrawal', 'transfer_out']:
                    amount = -amount
                
                BankTransaction.objects.create(
                    bank_account=bank,
                    transaction_type=transaction_type,
                    amount=abs(amount),
                    description=f"{description} - Transaction {i+1}",
                    reference=f"REF-{bank.account_number}-{i+1:03d}",
                    transaction_date=timezone.now(),
                )
                
                # Update bank balance
                bank.current_balance += amount
                bank.save()

        self.stdout.write(
            self.style.SUCCESS(f'Added sample transactions for {len(banks)} banks')
        )
