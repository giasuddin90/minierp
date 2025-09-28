from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import BankAccount, BankTransaction, Loan, LoanTransaction, TrialBalance


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
    fields = '__all__'
    success_url = reverse_lazy('accounting:loan_list')


class LoanUpdateView(UpdateView):
    model = Loan
    template_name = 'accounting/loan_form.html'
    fields = '__all__'
    success_url = reverse_lazy('accounting:loan_list')


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
