from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Supplier, SupplierLedger, SupplierCommission


class SupplierListView(ListView):
    model = Supplier
    template_name = 'suppliers/supplier_list.html'
    context_object_name = 'suppliers'


class SupplierDetailView(DetailView):
    model = Supplier
    template_name = 'suppliers/supplier_detail.html'


class SupplierCreateView(CreateView):
    model = Supplier
    template_name = 'suppliers/supplier_form.html'
    fields = '__all__'
    success_url = reverse_lazy('suppliers:supplier_list')


class SupplierUpdateView(UpdateView):
    model = Supplier
    template_name = 'suppliers/supplier_form.html'
    fields = '__all__'
    success_url = reverse_lazy('suppliers:supplier_list')


class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'suppliers/supplier_confirm_delete.html'
    success_url = reverse_lazy('suppliers:supplier_list')


class SupplierLedgerListView(ListView):
    model = SupplierLedger
    template_name = 'suppliers/supplier_ledger_list.html'
    context_object_name = 'ledger_entries'


class SupplierLedgerCreateView(CreateView):
    model = SupplierLedger
    template_name = 'suppliers/supplier_ledger_form.html'
    fields = '__all__'
    success_url = reverse_lazy('suppliers:supplier_list')


class SupplierCommissionListView(ListView):
    model = SupplierCommission
    template_name = 'suppliers/supplier_commission_list.html'
    context_object_name = 'commissions'


class SupplierCommissionCreateView(CreateView):
    model = SupplierCommission
    template_name = 'suppliers/supplier_commission_form.html'
    fields = '__all__'
    success_url = reverse_lazy('suppliers:supplier_list')
