from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import (
    SalesOrder, SalesOrderItem, SalesInvoice, SalesInvoiceItem,
    SalesReturn, SalesReturnItem, SalesPayment
)


class SalesOrderListView(ListView):
    model = SalesOrder
    template_name = 'sales/order_list.html'
    context_object_name = 'orders'


class SalesOrderDetailView(DetailView):
    model = SalesOrder
    template_name = 'sales/order_detail.html'


class SalesOrderCreateView(CreateView):
    model = SalesOrder
    template_name = 'sales/order_form.html'
    fields = '__all__'
    success_url = reverse_lazy('sales:order_list')


class SalesOrderUpdateView(UpdateView):
    model = SalesOrder
    template_name = 'sales/order_form.html'
    fields = '__all__'
    success_url = reverse_lazy('sales:order_list')


class SalesOrderDeleteView(DeleteView):
    model = SalesOrder
    template_name = 'sales/order_confirm_delete.html'
    success_url = reverse_lazy('sales:order_list')


class SalesInvoiceListView(ListView):
    model = SalesInvoice
    template_name = 'sales/invoice_list.html'
    context_object_name = 'invoices'


class SalesInvoiceDetailView(DetailView):
    model = SalesInvoice
    template_name = 'sales/invoice_detail.html'


class SalesInvoiceCreateView(CreateView):
    model = SalesInvoice
    template_name = 'sales/invoice_form.html'
    fields = '__all__'
    success_url = reverse_lazy('sales:invoice_list')


class SalesInvoiceUpdateView(UpdateView):
    model = SalesInvoice
    template_name = 'sales/invoice_form.html'
    fields = '__all__'
    success_url = reverse_lazy('sales:invoice_list')


class SalesInvoiceDeleteView(DeleteView):
    model = SalesInvoice
    template_name = 'sales/invoice_confirm_delete.html'
    success_url = reverse_lazy('sales:invoice_list')


class SalesReturnListView(ListView):
    model = SalesReturn
    template_name = 'sales/return_list.html'
    context_object_name = 'returns'


class SalesReturnDetailView(DetailView):
    model = SalesReturn
    template_name = 'sales/return_detail.html'


class SalesReturnCreateView(CreateView):
    model = SalesReturn
    template_name = 'sales/return_form.html'
    fields = '__all__'
    success_url = reverse_lazy('sales:return_list')


class SalesReturnUpdateView(UpdateView):
    model = SalesReturn
    template_name = 'sales/return_form.html'
    fields = '__all__'
    success_url = reverse_lazy('sales:return_list')


class SalesReturnDeleteView(DeleteView):
    model = SalesReturn
    template_name = 'sales/return_confirm_delete.html'
    success_url = reverse_lazy('sales:return_list')


class SalesPaymentListView(ListView):
    model = SalesPayment
    template_name = 'sales/payment_list.html'
    context_object_name = 'payments'


class SalesPaymentCreateView(CreateView):
    model = SalesPayment
    template_name = 'sales/payment_form.html'
    fields = '__all__'
    success_url = reverse_lazy('sales:payment_list')


class SalesPaymentUpdateView(UpdateView):
    model = SalesPayment
    template_name = 'sales/payment_form.html'
    fields = '__all__'
    success_url = reverse_lazy('sales:payment_list')


class SalesPaymentDeleteView(DeleteView):
    model = SalesPayment
    template_name = 'sales/payment_confirm_delete.html'
    success_url = reverse_lazy('sales:payment_list')


class SalesDailyReportView(ListView):
    template_name = 'sales/sales_daily_report.html'
    context_object_name = 'reports'


class SalesMonthlyReportView(ListView):
    template_name = 'sales/sales_monthly_report.html'
    context_object_name = 'reports'


class SalesCustomerReportView(ListView):
    template_name = 'sales/sales_customer_report.html'
    context_object_name = 'reports'
