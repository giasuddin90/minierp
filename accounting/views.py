from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction, models
from django.utils import timezone
from django.http import JsonResponse
from decimal import Decimal
from .models import (
    BankAccount, BankTransaction, Loan, LoanTransaction, TrialBalance,
    AccountCategory, Account, ExpenseCategory, IncomeCategory, 
    Expense, Income, JournalEntry, JournalEntryLine
)


class BankAccountListView(ListView):
    model = BankAccount
    template_name = 'accounting/bank_list.html'
    context_object_name = 'banks'


class BankAccountDetailView(DetailView):
    model = BankAccount
    template_name = 'accounting/bank_detail.html'


class BankAccountCreateView(CreateView):
    model = BankAccount
    template_name = 'accounting/bank_form.html'
    fields = '__all__'
    success_url = reverse_lazy('accounting:bank_list')


class BankAccountUpdateView(UpdateView):
    model = BankAccount
    template_name = 'accounting/bank_form.html'
    fields = '__all__'
    success_url = reverse_lazy('accounting:bank_list')


class BankAccountDeleteView(DeleteView):
    model = BankAccount
    template_name = 'accounting/bank_confirm_delete.html'
    success_url = reverse_lazy('accounting:bank_list')


class BankTransactionListView(ListView):
    model = BankTransaction
    template_name = 'accounting/bank_transaction_list.html'
    context_object_name = 'transactions'


class BankTransactionCreateView(CreateView):
    model = BankTransaction
    template_name = 'accounting/bank_transaction_form.html'
    fields = '__all__'
    success_url = reverse_lazy('accounting:bank_list')


class LoanListView(ListView):
    model = Loan
    template_name = 'accounting/loan_list.html'
    context_object_name = 'loans'


class LoanDetailView(DetailView):
    model = Loan
    template_name = 'accounting/loan_detail.html'


class LoanCreateView(CreateView):
    model = Loan
    template_name = 'accounting/loan_form.html'
    fields = ['deal_number', 'bank_account', 'principal_amount', 'interest_rate', 'loan_date', 'maturity_date', 'status']
    success_url = reverse_lazy('accounting:loan_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banks'] = BankAccount.objects.filter(is_active=True)
        return context


class LoanUpdateView(UpdateView):
    model = Loan
    template_name = 'accounting/loan_form.html'
    fields = ['deal_number', 'bank_account', 'principal_amount', 'interest_rate', 'loan_date', 'maturity_date', 'status']
    success_url = reverse_lazy('accounting:loan_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banks'] = BankAccount.objects.filter(is_active=True)
        return context


class LoanDeleteView(DeleteView):
    model = Loan
    template_name = 'accounting/loan_confirm_delete.html'
    success_url = reverse_lazy('accounting:loan_list')


class TrialBalanceListView(ListView):
    model = TrialBalance
    template_name = 'accounting/trial_balance_list.html'
    context_object_name = 'trial_balances'


class TrialBalanceDetailView(DetailView):
    model = TrialBalance
    template_name = 'accounting/trial_balance_detail.html'


class TrialBalanceCreateView(CreateView):
    model = TrialBalance
    template_name = 'accounting/trial_balance_form.html'
    fields = '__all__'
    success_url = reverse_lazy('accounting:trial_balance_list')


class TrialBalanceUpdateView(UpdateView):
    model = TrialBalance
    template_name = 'accounting/trial_balance_form.html'
    fields = '__all__'
    success_url = reverse_lazy('accounting:trial_balance_list')


class TrialBalanceDeleteView(DeleteView):
    model = TrialBalance
    template_name = 'accounting/trial_balance_confirm_delete.html'
    success_url = reverse_lazy('accounting:trial_balance_list')


class DailyReportView(ListView):
    model = BankTransaction
    template_name = 'accounting/daily_report.html'
    context_object_name = 'reports'
    
    def get_queryset(self):
        from django.utils import timezone
        today = timezone.now().date()
        return BankTransaction.objects.filter(transaction_date=today)


class MonthlyReportView(ListView):
    model = BankTransaction
    template_name = 'accounting/monthly_report.html'
    context_object_name = 'reports'
    
    def get_queryset(self):
        from django.utils import timezone
        from datetime import datetime
        now = timezone.now()
        return BankTransaction.objects.filter(
            transaction_date__year=now.year,
            transaction_date__month=now.month
        )


class BankReportView(ListView):
    model = BankAccount
    template_name = 'accounting/bank_report.html'
    context_object_name = 'reports'


# Enhanced Loan Management Views
class LoanTransactionListView(ListView):
    model = LoanTransaction
    template_name = 'accounting/loan_transaction_list.html'
    context_object_name = 'transactions'
    
    def get_queryset(self):
        loan_id = self.kwargs.get('loan_id')
        return LoanTransaction.objects.filter(loan_id=loan_id).order_by('-transaction_date')


class LoanTransactionCreateView(CreateView):
    model = LoanTransaction
    template_name = 'accounting/loan_transaction_form.html'
    fields = ['transaction_type', 'amount', 'description', 'transaction_date']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loan_id = self.kwargs.get('loan_id')
        context['loan'] = get_object_or_404(Loan, id=loan_id)
        return context
    
    def form_valid(self, form):
        loan_id = self.kwargs.get('loan_id')
        loan = get_object_or_404(Loan, id=loan_id)
        form.instance.loan = loan
        form.instance.created_by = self.request.user
        
        # Process the loan payment
        with transaction.atomic():
            # Save the transaction
            response = super().form_valid(form)
            
            # Update loan totals
            if form.instance.transaction_type == 'principal_payment':
                loan.total_principal_paid += form.instance.amount
            elif form.instance.transaction_type == 'interest_payment':
                loan.total_interest_paid += form.instance.amount
            
            # Check if loan is fully paid
            if loan.outstanding_amount <= 0:
                loan.status = 'closed'
            
            loan.save()
            
            # Create corresponding bank transaction
            BankTransaction.objects.create(
                bank_account=loan.bank_account,
                transaction_type='withdrawal',
                amount=form.instance.amount,
                description=f"Loan Payment - {form.instance.get_transaction_type_display()} for {loan.deal_number}",
                reference=f"LOAN-{loan.deal_number}-{form.instance.id}",
                transaction_date=form.instance.transaction_date,
                created_by=self.request.user
            )
            
            messages.success(self.request, f'Loan payment of ৳{form.instance.amount} processed successfully!')
            
        return response
    
    def get_success_url(self):
        loan_id = self.kwargs.get('loan_id')
        return reverse_lazy('accounting:loan_detail', kwargs={'pk': loan_id})


def process_loan_payment(request, loan_id):
    """Process loan payment with automatic calculations"""
    loan = get_object_or_404(Loan, id=loan_id)
    
    if request.method == 'POST':
        payment_amount = Decimal(request.POST.get('payment_amount', 0))
        payment_type = request.POST.get('payment_type', 'principal_payment')
        description = request.POST.get('description', '')
        
        if payment_amount <= 0:
            messages.error(request, 'Payment amount must be greater than zero.')
            return redirect('accounting:loan_detail', pk=loan_id)
        
        with transaction.atomic():
            # Create loan transaction
            loan_transaction = LoanTransaction.objects.create(
                loan=loan,
                transaction_type=payment_type,
                amount=payment_amount,
                description=description,
                transaction_date=timezone.now(),
                created_by=request.user
            )
            
            # Update loan totals
            if payment_type == 'principal_payment':
                loan.total_principal_paid += payment_amount
            elif payment_type == 'interest_payment':
                loan.total_interest_paid += payment_amount
            
            # Check if loan is fully paid
            if loan.outstanding_amount <= 0:
                loan.status = 'closed'
                messages.success(request, f'Loan {loan.deal_number} has been fully paid and closed!')
            else:
                messages.success(request, f'Payment of ৳{payment_amount} processed successfully!')
            
            loan.save()
            
            # Create corresponding bank transaction
            BankTransaction.objects.create(
                bank_account=loan.bank_account,
                transaction_type='withdrawal',
                amount=payment_amount,
                description=f"Loan Payment - {loan_transaction.get_transaction_type_display()} for {loan.deal_number}",
                reference=f"LOAN-{loan.deal_number}-{loan_transaction.id}",
                transaction_date=loan_transaction.transaction_date,
                created_by=request.user
            )
    
    return redirect('accounting:loan_detail', pk=loan_id)


def calculate_loan_interest(request, loan_id):
    """Calculate interest for a loan"""
    loan = get_object_or_404(Loan, id=loan_id)
    
    # Simple interest calculation
    days_elapsed = (timezone.now().date() - loan.loan_date).days
    daily_rate = loan.interest_rate / 365 / 100
    interest_amount = loan.outstanding_amount * daily_rate * days_elapsed
    
    return JsonResponse({
        'outstanding_amount': float(loan.outstanding_amount),
        'interest_rate': float(loan.interest_rate),
        'days_elapsed': days_elapsed,
        'interest_amount': float(interest_amount),
        'total_due': float(loan.outstanding_amount + interest_amount)
    })


class BankingDashboardView(ListView):
    """Comprehensive banking dashboard"""
    model = BankAccount
    template_name = 'accounting/banking_dashboard.html'
    context_object_name = 'banks'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate total balances
        total_balance = BankAccount.objects.aggregate(
            total=models.Sum('current_balance')
        )['total'] or Decimal('0')
        
        # Get active loans
        active_loans = Loan.objects.filter(status='active')
        total_loan_amount = active_loans.aggregate(
            total=models.Sum('principal_amount')
        )['total'] or Decimal('0')
        
        total_loan_paid = active_loans.aggregate(
            total=models.Sum('total_principal_paid')
        )['total'] or Decimal('0')
        
        outstanding_loans = total_loan_amount - total_loan_paid
        
        # Recent transactions
        recent_transactions = BankTransaction.objects.select_related(
            'bank_account'
        ).order_by('-transaction_date')[:10]
        
        # Recent loan transactions
        recent_loan_transactions = LoanTransaction.objects.select_related(
            'loan', 'loan__bank_account'
        ).order_by('-transaction_date')[:10]
        
        # Monthly transaction summary
        from datetime import datetime, timedelta
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_deposits = BankTransaction.objects.filter(
            transaction_type='deposit',
            transaction_date__gte=month_start
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        
        monthly_withdrawals = BankTransaction.objects.filter(
            transaction_type='withdrawal',
            transaction_date__gte=month_start
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        
        context.update({
            'total_balance': total_balance,
            'active_loans_count': active_loans.count(),
            'total_loan_amount': total_loan_amount,
            'outstanding_loans': outstanding_loans,
            'recent_transactions': recent_transactions,
            'recent_loan_transactions': recent_loan_transactions,
            'monthly_deposits': monthly_deposits,
            'monthly_withdrawals': monthly_withdrawals,
            'net_monthly_flow': monthly_deposits - monthly_withdrawals,
        })
        
        return context


# Expense Management Views
class ExpenseListView(ListView):
    model = Expense
    template_name = 'accounting/expense_list.html'
    context_object_name = 'expenses'
    paginate_by = 20
    
    def get_queryset(self):
        return Expense.objects.select_related('expense_category', 'bank_account', 'created_by').order_by('-expense_date')


class ExpenseCreateView(CreateView):
    model = Expense
    template_name = 'accounting/expense_form.html'
    fields = ['expense_category', 'amount', 'description', 'payment_method', 'bank_account', 'expense_date', 'reference']
    success_url = reverse_lazy('accounting:expense_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expense_categories'] = ExpenseCategory.objects.filter(is_active=True)
        context['bank_accounts'] = BankAccount.objects.filter(is_active=True)
        return context
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ExpenseUpdateView(UpdateView):
    model = Expense
    template_name = 'accounting/expense_form.html'
    fields = ['expense_category', 'amount', 'description', 'payment_method', 'bank_account', 'expense_date', 'reference']
    success_url = reverse_lazy('accounting:expense_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expense_categories'] = ExpenseCategory.objects.filter(is_active=True)
        context['bank_accounts'] = BankAccount.objects.filter(is_active=True)
        return context


class ExpenseDeleteView(DeleteView):
    model = Expense
    template_name = 'accounting/expense_confirm_delete.html'
    success_url = reverse_lazy('accounting:expense_list')


# Income Management Views
class IncomeListView(ListView):
    model = Income
    template_name = 'accounting/income_list.html'
    context_object_name = 'incomes'
    paginate_by = 20
    
    def get_queryset(self):
        return Income.objects.select_related('income_category', 'bank_account', 'created_by').order_by('-income_date')


class IncomeCreateView(CreateView):
    model = Income
    template_name = 'accounting/income_form.html'
    fields = ['income_category', 'amount', 'description', 'payment_method', 'bank_account', 'income_date', 'reference']
    success_url = reverse_lazy('accounting:income_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['income_categories'] = IncomeCategory.objects.filter(is_active=True)
        context['bank_accounts'] = BankAccount.objects.filter(is_active=True)
        return context
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class IncomeUpdateView(UpdateView):
    model = Income
    template_name = 'accounting/income_form.html'
    fields = ['income_category', 'amount', 'description', 'payment_method', 'bank_account', 'income_date', 'reference']
    success_url = reverse_lazy('accounting:income_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['income_categories'] = IncomeCategory.objects.filter(is_active=True)
        context['bank_accounts'] = BankAccount.objects.filter(is_active=True)
        return context


class IncomeDeleteView(DeleteView):
    model = Income
    template_name = 'accounting/income_confirm_delete.html'
    success_url = reverse_lazy('accounting:income_list')


# Chart of Accounts Views
class AccountListView(ListView):
    model = Account
    template_name = 'accounting/account_list.html'
    context_object_name = 'accounts'
    
    def get_queryset(self):
        return Account.objects.select_related('category', 'parent_account').order_by('code')


class AccountCreateView(CreateView):
    model = Account
    template_name = 'accounting/account_form.html'
    fields = ['code', 'name', 'category', 'parent_account', 'is_active']
    success_url = reverse_lazy('accounting:account_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['account_categories'] = AccountCategory.objects.filter(is_active=True)
        context['parent_accounts'] = Account.objects.filter(is_active=True)
        return context


class AccountUpdateView(UpdateView):
    model = Account
    template_name = 'accounting/account_form.html'
    fields = ['code', 'name', 'category', 'parent_account', 'is_active']
    success_url = reverse_lazy('accounting:account_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['account_categories'] = AccountCategory.objects.filter(is_active=True)
        context['parent_accounts'] = Account.objects.filter(is_active=True)
        return context


# Enhanced Trial Balance View
class EnhancedTrialBalanceView(ListView):
    model = TrialBalance
    template_name = 'accounting/enhanced_trial_balance.html'
    context_object_name = 'trial_balances'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all transactions for today
        today = timezone.now().date()
        
        # Bank transactions
        bank_transactions = BankTransaction.objects.filter(
            transaction_date__date=today
        ).select_related('bank_account')
        
        # Expenses
        expenses = Expense.objects.filter(expense_date=today).select_related('expense_category')
        
        # Income
        incomes = Income.objects.filter(income_date=today).select_related('income_category')
        
        # Calculate totals
        total_bank_debits = sum(t.amount for t in bank_transactions if t.transaction_type in ['deposit', 'transfer_in'])
        total_bank_credits = sum(t.amount for t in bank_transactions if t.transaction_type in ['withdrawal', 'transfer_out'])
        
        total_expenses = sum(e.amount for e in expenses)
        total_income = sum(i.amount for i in incomes)
        
        # Calculate trial balance
        total_debits = total_bank_credits + total_expenses
        total_credits = total_bank_debits + total_income
        
        # Check if balanced
        is_balanced = abs(total_debits - total_credits) < Decimal('0.01')
        
        context.update({
            'today': today,
            'bank_transactions': bank_transactions,
            'expenses': expenses,
            'incomes': incomes,
            'total_bank_debits': total_bank_debits,
            'total_bank_credits': total_bank_credits,
            'total_expenses': total_expenses,
            'total_income': total_income,
            'total_debits': total_debits,
            'total_credits': total_credits,
            'is_balanced': is_balanced,
            'difference': total_debits - total_credits,
        })
        
        return context


# Daily Financial Summary
class DailyFinancialSummaryView(ListView):
    model = Expense
    template_name = 'accounting/daily_financial_summary.html'
    context_object_name = 'expenses'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get today's date
        today = timezone.now().date()
        
        # Get all transactions for today
        bank_transactions = BankTransaction.objects.filter(transaction_date__date=today)
        expenses = Expense.objects.filter(expense_date=today)
        incomes = Income.objects.filter(income_date=today)
        
        # Calculate totals
        total_bank_inflow = sum(t.amount for t in bank_transactions if t.transaction_type in ['deposit', 'transfer_in'])
        total_bank_outflow = sum(t.amount for t in bank_transactions if t.transaction_type in ['withdrawal', 'transfer_out'])
        total_expenses = sum(e.amount for e in expenses)
        total_income = sum(i.amount for i in incomes)
        
        # Net cash flow
        net_cash_flow = (total_bank_inflow + total_income) - (total_bank_outflow + total_expenses)
        
        # Category-wise breakdown
        expense_by_category = {}
        for expense in expenses:
            category = expense.expense_category.name
            if category not in expense_by_category:
                expense_by_category[category] = 0
            expense_by_category[category] += expense.amount
        
        income_by_category = {}
        for income in incomes:
            category = income.income_category.name
            if category not in income_by_category:
                income_by_category[category] = 0
            income_by_category[category] += income.amount
        
        context.update({
            'today': today,
            'bank_transactions': bank_transactions,
            'incomes': incomes,
            'total_bank_inflow': total_bank_inflow,
            'total_bank_outflow': total_bank_outflow,
            'total_expenses': total_expenses,
            'total_income': total_income,
            'net_cash_flow': net_cash_flow,
            'expense_by_category': expense_by_category,
            'income_by_category': income_by_category,
        })
        
        return context
