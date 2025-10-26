from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from .models import (
    SalesOrder, SalesOrderItem
)
from .forms import SalesOrderForm, SalesOrderItemFormSet, SalesOrderItemFormSetCustom
from customers.models import Customer
from stock.models import Product, ProductCategory, ProductBrand
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
    form_class = SalesOrderForm
    template_name = 'sales/order_form.html'
    success_url = reverse_lazy('sales:order_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Create formset for order items
        if self.request.POST:
            context['formset'] = SalesOrderItemFormSetCustom(self.request.POST)
        else:
            context['formset'] = SalesOrderItemFormSetCustom()
        
        # Add data for filtering
        context['products'] = Product.objects.filter(is_active=True).select_related('category', 'brand')
        context['categories'] = ProductCategory.objects.filter(is_active=True)
        context['brands'] = ProductBrand.objects.filter(is_active=True)
        
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
                
                # Handle formset
                formset = SalesOrderItemFormSetCustom(self.request.POST, instance=self.object)
                if formset.is_valid():
                    formset.save()
                    
                    # Calculate total amount
                    total_amount = sum(item.total_price for item in self.object.items.all())
                    self.object.total_amount = total_amount
                    self.object.save()
                    
                    items_count = self.object.items.count()
                    if items_count > 0:
                        messages.success(self.request, f"Sales order {order_number} created successfully with {items_count} products! Total: ৳{total_amount}")
                    else:
                        messages.warning(self.request, f"Sales order {order_number} created without items. Please add products to complete the order.")
                else:
                    messages.error(self.request, "Please fix the errors in the product selection.")
                    return self.form_invalid(form)
                
                return response
                
        except Exception as e:
            messages.error(self.request, f"Error creating sales order: {str(e)}")
            return self.form_invalid(form)


class SalesOrderUpdateView(UpdateView):
    model = SalesOrder
    form_class = SalesOrderForm
    template_name = 'sales/order_form.html'
    success_url = reverse_lazy('sales:order_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Create formset for order items
        if self.request.POST:
            context['formset'] = SalesOrderItemFormSet(self.request.POST, instance=self.object)
        else:
            # For editing, only show existing items, no extra blank forms
            context['formset'] = SalesOrderItemFormSet(instance=self.object)
        
        # Add data for filtering
        context['products'] = Product.objects.filter(is_active=True).select_related('category', 'brand')
        context['categories'] = ProductCategory.objects.filter(is_active=True)
        context['brands'] = ProductBrand.objects.filter(is_active=True)
        
        return context
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Save the order
                response = super().form_valid(form)
                
                # Handle formset
                formset = SalesOrderItemFormSet(self.request.POST, instance=self.object)
                if formset.is_valid():
                    formset.save()
                    
                    # Calculate total amount
                    total_amount = sum(item.total_price for item in self.object.items.all())
                    self.object.total_amount = total_amount
                    self.object.save()
                    
                    items_count = self.object.items.count()
                    messages.success(self.request, f"Sales order {self.object.order_number} updated successfully with {items_count} products! Total: ৳{total_amount}")
                else:
                    messages.error(self.request, "Please fix the errors in the product selection.")
                    return self.form_invalid(form)
                
                return response
                
        except Exception as e:
            messages.error(self.request, f"Error updating sales order: {str(e)}")
            return self.form_invalid(form)


class SalesOrderDeleteView(DeleteView):
    model = SalesOrder
    template_name = 'sales/order_confirm_delete.html'
    success_url = reverse_lazy('sales:order_list')




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




def mark_order_delivered(request, order_id):
    """Mark sales order as delivered"""
    try:
        with transaction.atomic():
            order = get_object_or_404(SalesOrder, id=order_id)
            
            if order.status != 'order':
                messages.error(request, f"Order {order.order_number} cannot be marked as delivered. Current status: {order.get_status_display()}")
                return redirect('sales:order_detail', order_id)
            
            order.mark_delivered(user=request.user)
            messages.success(request, f"Order {order.order_number} marked as delivered successfully!")
            
    except Exception as e:
        messages.error(request, f"Error marking order as delivered: {str(e)}")
    
    return redirect('sales:order_detail', order_id)


def cancel_sales_order(request, order_id):
    """Cancel sales order"""
    try:
        with transaction.atomic():
            order = get_object_or_404(SalesOrder, id=order_id)
            
            if order.status == 'cancel':
                messages.warning(request, f"Order {order.order_number} is already cancelled.")
                return redirect('sales:order_detail', order_id)
            
            order.cancel_order(user=request.user)
            messages.success(request, f"Order {order.order_number} cancelled successfully!")
            
    except Exception as e:
        messages.error(request, f"Error cancelling order: {str(e)}")
    
    return redirect('sales:order_detail', order_id)
