from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from .models import (
    SalesOrder, SalesOrderItem, SalesInvoice, SalesInvoiceItem,
    SalesReturn, SalesReturnItem, SalesPayment
)
from customers.models import Customer
from stock.models import Product, Warehouse
from django.contrib.auth.models import User
import uuid


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
    fields = ['customer', 'order_date', 'delivery_date', 'status', 'notes', 'total_amount']
    success_url = reverse_lazy('sales:order_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customers'] = Customer.objects.all()
        context['products'] = Product.objects.filter(is_active=True)
        context['warehouses'] = Warehouse.objects.filter(is_active=True)
        return context
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Generate unique order number
                order_number = f"SO-{uuid.uuid4().hex[:8].upper()}"
                form.instance.order_number = order_number
                form.instance.created_by = self.request.user
                
                # Save the order first
                response = super().form_valid(form)
                
                # Handle multiple products
                products = self.request.POST.getlist('products[]')
                warehouses = self.request.POST.getlist('warehouses[]')
                quantities = self.request.POST.getlist('quantities[]')
                prices = self.request.POST.getlist('prices[]')
                
                total_amount = 0
                items_created = 0
                
                if products and products[0]:  # Check if at least one product is selected
                    for i, product_id in enumerate(products):
                        if product_id and i < len(warehouses) and i < len(quantities) and i < len(prices):
                            try:
                                product = Product.objects.get(id=product_id)
                                warehouse = Warehouse.objects.get(id=warehouses[i])
                                quantity = float(quantities[i]) if quantities[i] else 0
                                unit_price = float(prices[i]) if prices[i] else 0
                                
                                if quantity > 0 and unit_price > 0:
                                    # Create order item
                                    item_total = quantity * unit_price
                                    SalesOrderItem.objects.create(
                                        sales_order=self.object,
                                        product=product,
                                        warehouse=warehouse,
                                        quantity=quantity,
                                        unit_price=unit_price,
                                        total_price=item_total
                                    )
                                    total_amount += item_total
                                    items_created += 1
                            except (Product.DoesNotExist, Warehouse.DoesNotExist, ValueError, IndexError) as e:
                                messages.error(self.request, f"Invalid data for product {i+1}: {str(e)}")
                                continue
                
                # Update total amount
                self.object.total_amount = total_amount
                self.object.save()
                
                if items_created > 0:
                    messages.success(self.request, f"Sales order {order_number} created successfully with {items_created} products! Total: ৳{total_amount}")
                else:
                    messages.warning(self.request, f"Sales order {order_number} created without items. Please add products to complete the order.")
                
                return response
                
        except Exception as e:
            messages.error(self.request, f"Error creating sales order: {str(e)}")
            return self.form_invalid(form)


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
    model = SalesOrder
    template_name = 'sales/sales_daily_report.html'
    context_object_name = 'reports'
    
    def get_queryset(self):
        from django.utils import timezone
        today = timezone.now().date()
        return SalesOrder.objects.filter(order_date=today)


class SalesMonthlyReportView(ListView):
    model = SalesOrder
    template_name = 'sales/sales_monthly_report.html'
    context_object_name = 'reports'
    
    def get_queryset(self):
        from django.utils import timezone
        now = timezone.now()
        return SalesOrder.objects.filter(
            order_date__year=now.year,
            order_date__month=now.month
        )


class SalesCustomerReportView(ListView):
    model = SalesOrder
    template_name = 'sales/sales_customer_report.html'
    context_object_name = 'reports'
