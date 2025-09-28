from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Customer, CustomerLedger, CustomerCommission, CustomerCommitment


class CustomerListView(ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'


class CustomerDetailView(DetailView):
    model = Customer
    template_name = 'customers/customer_detail.html'


class CustomerCreateView(CreateView):
    model = Customer
    template_name = 'customers/customer_form.html'
    fields = '__all__'
    success_url = reverse_lazy('customers:customer_list')


class CustomerUpdateView(UpdateView):
    model = Customer
    template_name = 'customers/customer_form.html'
    fields = '__all__'
    success_url = reverse_lazy('customers:customer_list')


class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'customers/customer_confirm_delete.html'
    success_url = reverse_lazy('customers:customer_list')


class CustomerLedgerListView(ListView):
    model = CustomerLedger
    template_name = 'customers/customer_ledger_list.html'
    context_object_name = 'ledger_entries'


class CustomerLedgerCreateView(CreateView):
    model = CustomerLedger
    template_name = 'customers/customer_ledger_form.html'
    fields = '__all__'
    success_url = reverse_lazy('customers:customer_list')


class CustomerCommissionListView(ListView):
    model = CustomerCommission
    template_name = 'customers/customer_commission_list.html'
    context_object_name = 'commissions'


class CustomerCommissionCreateView(CreateView):
    model = CustomerCommission
    template_name = 'customers/customer_commission_form.html'
    fields = '__all__'
    success_url = reverse_lazy('customers:customer_list')


class CustomerCommitmentListView(ListView):
    model = CustomerCommitment
    template_name = 'customers/customer_commitment_list.html'
    context_object_name = 'commitments'


class CustomerCommitmentCreateView(CreateView):
    model = CustomerCommitment
    template_name = 'customers/customer_commitment_form.html'
    fields = '__all__'
    success_url = reverse_lazy('customers:customer_list')
