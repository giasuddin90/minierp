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
    template_name = 'customers/ledger_list.html'
    context_object_name = 'items'


class CustomerLedgerCreateView(CreateView):
    model = CustomerLedger
    template_name = 'customers/ledger_form.html'
    fields = '__all__'
    success_url = reverse_lazy('customers:ledger_list')


class CustomerCommissionListView(ListView):
    model = CustomerCommission
    template_name = 'customers/commission_list.html'
    context_object_name = 'items'


class CustomerCommissionCreateView(CreateView):
    model = CustomerCommission
    template_name = 'customers/commission_form.html'
    fields = '__all__'
    success_url = reverse_lazy('customers:commission_list')


class CustomerCommitmentListView(ListView):
    model = CustomerCommitment
    template_name = 'customers/commitment_list.html'
    context_object_name = 'items'


class CustomerCommitmentCreateView(CreateView):
    model = CustomerCommitment
    template_name = 'customers/commitment_form.html'
    fields = '__all__'
    success_url = reverse_lazy('customers:commitment_list')
