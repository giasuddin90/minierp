from django.core.management.base import BaseCommand
from django.utils import timezone
from accounting.models import BankAccount, Loan, LoanTransaction
from decimal import Decimal
import random
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Add sample loans and loan transactions to the system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing loans before adding new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing loans...')
            Loan.objects.all().delete()
            LoanTransaction.objects.all().delete()

        # Get available bank accounts
        bank_accounts = BankAccount.objects.filter(is_active=True)
        if not bank_accounts.exists():
            self.stdout.write(
                self.style.ERROR('No active bank accounts found. Please run "add_sample_banks" first.')
            )
            return

        # Sample loans data
        loans_data = [
            {
                'deal_number': 'LOAN-001-2024',
                'principal_amount': Decimal('500000.00'),
                'interest_rate': Decimal('12.00'),
                'loan_date': timezone.now().date() - timedelta(days=90),
                'maturity_date': timezone.now().date() + timedelta(days=270),
                'status': 'active',
            },
            {
                'deal_number': 'LOAN-002-2024',
                'principal_amount': Decimal('750000.00'),
                'interest_rate': Decimal('10.50'),
                'loan_date': timezone.now().date() - timedelta(days=60),
                'maturity_date': timezone.now().date() + timedelta(days=300),
                'status': 'active',
            },
            {
                'deal_number': 'LOAN-003-2024',
                'principal_amount': Decimal('300000.00'),
                'interest_rate': Decimal('15.00'),
                'loan_date': timezone.now().date() - timedelta(days=30),
                'maturity_date': timezone.now().date() + timedelta(days=180),
                'status': 'active',
            },
            {
                'deal_number': 'LOAN-004-2024',
                'principal_amount': Decimal('1000000.00'),
                'interest_rate': Decimal('9.75'),
                'loan_date': timezone.now().date() - timedelta(days=120),
                'maturity_date': timezone.now().date() + timedelta(days=240),
                'status': 'active',
            },
            {
                'deal_number': 'LOAN-005-2024',
                'principal_amount': Decimal('250000.00'),
                'interest_rate': Decimal('11.25'),
                'loan_date': timezone.now().date() - timedelta(days=15),
                'maturity_date': timezone.now().date() + timedelta(days=345),
                'status': 'active',
            },
        ]

        created_loans = []
        
        for i, loan_data in enumerate(loans_data):
            # Assign random bank account
            bank_account = random.choice(bank_accounts)
            
            loan, created = Loan.objects.get_or_create(
                deal_number=loan_data['deal_number'],
                defaults={
                    **loan_data,
                    'bank_account': bank_account,
                }
            )
            
            if created:
                created_loans.append(loan)
                self.stdout.write(
                    self.style.SUCCESS(f'Created loan: {loan.deal_number} - ৳{loan.principal_amount} ({bank_account.name})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Loan already exists: {loan.deal_number}')
                )

        # Add sample loan transactions for each loan
        self.add_sample_loan_transactions(created_loans)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully processed {len(created_loans)} loans')
        )

    def add_sample_loan_transactions(self, loans):
        """Add sample loan transactions for the created loans"""
        transaction_types = ['principal_payment', 'interest_payment', 'penalty']
        descriptions = [
            'Monthly principal payment',
            'Interest payment',
            'Additional principal payment',
            'Late payment penalty',
            'Early payment bonus',
            'Quarterly interest payment',
            'Annual principal payment',
            'Emergency payment',
            'Partial payment',
            'Final payment',
        ]

        for loan in loans:
            # Add 3-8 random transactions for each loan
            num_transactions = random.randint(3, 8)
            
            for i in range(num_transactions):
                transaction_type = random.choice(transaction_types)
                
                # Calculate appropriate amount based on transaction type
                if transaction_type == 'principal_payment':
                    # Principal payment should not exceed outstanding amount
                    max_amount = loan.principal_amount - loan.total_principal_paid
                    amount = Decimal(str(random.uniform(10000, min(50000, float(max_amount)))))
                elif transaction_type == 'interest_payment':
                    # Interest payment based on outstanding amount and rate
                    outstanding = loan.principal_amount - loan.total_principal_paid
                    monthly_rate = loan.interest_rate / 12 / 100
                    amount = Decimal(str(random.uniform(1000, float(outstanding * monthly_rate * 2))))
                else:  # penalty
                    amount = Decimal(str(random.uniform(500, 5000)))
                
                # Ensure amount doesn't exceed outstanding for principal payments
                if transaction_type == 'principal_payment':
                    amount = min(amount, loan.principal_amount - loan.total_principal_paid)
                
                if amount > 0:
                    description = random.choice(descriptions)
                    
                    # Create transaction date (spread over loan period)
                    days_ago = random.randint(1, (timezone.now().date() - loan.loan_date).days)
                    transaction_date = timezone.now() - timedelta(days=days_ago)
                    
                    LoanTransaction.objects.create(
                        loan=loan,
                        transaction_type=transaction_type,
                        amount=amount,
                        description=f"{description} - Transaction {i+1}",
                        transaction_date=transaction_date,
                    )
                    
                    # Update loan totals
                    if transaction_type == 'principal_payment':
                        loan.total_principal_paid += amount
                    elif transaction_type == 'interest_payment':
                        loan.total_interest_paid += amount
                    
                    loan.save()

        self.stdout.write(
            self.style.SUCCESS(f'Added sample loan transactions for {len(loans)} loans')
        )
