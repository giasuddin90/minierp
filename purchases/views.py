from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import (
    PurchaseOrder, PurchaseOrderItem, GoodsReceipt, GoodsReceiptItem,
    PurchaseInvoice, PurchaseInvoiceItem, PurchaseReturn, PurchaseReturnItem, PurchasePayment
)


class PurchaseOrderListView(ListView):
    model = PurchaseOrder
    template_name = 'purchases/order_list.html'
    context_object_name = 'orders'


class PurchaseOrderDetailView(DetailView):
    model = PurchaseOrder
    template_name = 'purchases/order_detail.html'


class PurchaseOrderCreateView(CreateView):
    model = PurchaseOrder
    template_name = 'purchases/order_form.html'
    fields = '__all__'
    success_url = reverse_lazy('purchases:order_list')


class PurchaseOrderUpdateView(UpdateView):
    model = PurchaseOrder
    template_name = 'purchases/order_form.html'
    fields = '__all__'
    success_url = reverse_lazy('purchases:order_list')


class PurchaseOrderDeleteView(DeleteView):
    model = PurchaseOrder
    template_name = 'purchases/order_confirm_delete.html'
    success_url = reverse_lazy('purchases:order_list')


class GoodsReceiptListView(ListView):
    model = GoodsReceipt
    template_name = 'purchases/receipt_list.html'
    context_object_name = 'receipts'


class GoodsReceiptDetailView(DetailView):
    model = GoodsReceipt
    template_name = 'purchases/receipt_detail.html'


class GoodsReceiptCreateView(CreateView):
    model = GoodsReceipt
    template_name = 'purchases/receipt_form.html'
    fields = '__all__'
    success_url = reverse_lazy('purchases:receipt_list')


class GoodsReceiptUpdateView(UpdateView):
    model = GoodsReceipt
    template_name = 'purchases/receipt_form.html'
    fields = '__all__'
    success_url = reverse_lazy('purchases:receipt_list')


class GoodsReceiptDeleteView(DeleteView):
    model = GoodsReceipt
    template_name = 'purchases/receipt_confirm_delete.html'
    success_url = reverse_lazy('purchases:receipt_list')


class PurchaseInvoiceListView(ListView):
    model = PurchaseInvoice
    template_name = 'purchases/invoice_list.html'
    context_object_name = 'invoices'


class PurchaseInvoiceDetailView(DetailView):
    model = PurchaseInvoice
    template_name = 'purchases/invoice_detail.html'


class PurchaseInvoiceCreateView(CreateView):
    model = PurchaseInvoice
    template_name = 'purchases/invoice_form.html'
    fields = '__all__'
    success_url = reverse_lazy('purchases:invoice_list')


class PurchaseInvoiceUpdateView(UpdateView):
    model = PurchaseInvoice
    template_name = 'purchases/invoice_form.html'
    fields = '__all__'
    success_url = reverse_lazy('purchases:invoice_list')


class PurchaseInvoiceDeleteView(DeleteView):
    model = PurchaseInvoice
    template_name = 'purchases/invoice_confirm_delete.html'
    success_url = reverse_lazy('purchases:invoice_list')


class PurchaseReturnListView(ListView):
    model = PurchaseReturn
    template_name = 'purchases/return_list.html'
    context_object_name = 'returns'


class PurchaseReturnDetailView(DetailView):
    model = PurchaseReturn
    template_name = 'purchases/return_detail.html'


class PurchaseReturnCreateView(CreateView):
    model = PurchaseReturn
    template_name = 'purchases/return_form.html'
    fields = '__all__'
    success_url = reverse_lazy('purchases:return_list')


class PurchaseReturnUpdateView(UpdateView):
    model = PurchaseReturn
    template_name = 'purchases/return_form.html'
    fields = '__all__'
    success_url = reverse_lazy('purchases:return_list')


class PurchaseReturnDeleteView(DeleteView):
    model = PurchaseReturn
    template_name = 'purchases/return_confirm_delete.html'
    success_url = reverse_lazy('purchases:return_list')


class PurchasePaymentListView(ListView):
    model = PurchasePayment
    template_name = 'purchases/payment_list.html'
    context_object_name = 'payments'


class PurchasePaymentCreateView(CreateView):
    model = PurchasePayment
    template_name = 'purchases/payment_form.html'
    fields = '__all__'
    success_url = reverse_lazy('purchases:payment_list')


class PurchasePaymentUpdateView(UpdateView):
    model = PurchasePayment
    template_name = 'purchases/payment_form.html'
    fields = '__all__'
    success_url = reverse_lazy('purchases:payment_list')


class PurchasePaymentDeleteView(DeleteView):
    model = PurchasePayment
    template_name = 'purchases/payment_confirm_delete.html'
    success_url = reverse_lazy('purchases:payment_list')


class PurchaseDailyReportView(ListView):
    template_name = 'purchases/purchase_daily_report.html'
    context_object_name = 'reports'


class PurchaseMonthlyReportView(ListView):
    template_name = 'purchases/purchase_monthly_report.html'
    context_object_name = 'reports'


class PurchaseSupplierReportView(ListView):
    template_name = 'purchases/purchase_supplier_report.html'
    context_object_name = 'reports'
