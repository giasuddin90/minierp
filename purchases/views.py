from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from .models import PurchaseOrder, PurchaseOrderItem
from .forms import (
    PurchaseOrderForm, PurchaseOrderItemFormSet, PurchaseOrderSearchForm, PurchaseOrderItemForm
)
from suppliers.models import Supplier
from stock.models import Product, ProductCategory, ProductBrand, Stock
from django.contrib.auth.models import User
import uuid


class PurchaseOrderListView(ListView):
    model = PurchaseOrder
    template_name = 'purchases/order_list.html'
    context_object_name = 'orders'
    paginate_by = 20
    ordering = ['-order_date', '-created_at']
    
    def get_queryset(self):
        from django.db import models
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        
        if search_query:
            queryset = queryset.filter(
                models.Q(order_number__icontains=search_query) |
                models.Q(supplier__name__icontains=search_query) |
                models.Q(status__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = PurchaseOrderSearchForm(self.request.GET)
        return context


class PurchaseOrderDetailView(DetailView):
    model = PurchaseOrder
    template_name = 'purchases/order_detail.html'
    context_object_name = 'order'


class PurchaseOrderCreateView(CreateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'purchases/order_form.html'
    success_url = reverse_lazy('purchases:order_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = PurchaseOrderItemFormSet(self.request.POST)
        else:
            context['formset'] = PurchaseOrderItemFormSet()
        
        context['categories'] = ProductCategory.objects.filter(is_active=True)
        context['brands'] = ProductBrand.objects.filter(is_active=True)
        context['products'] = Product.objects.filter(is_active=True).select_related('category', 'brand')
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            with transaction.atomic():
                # Set created_by
                form.instance.created_by = self.request.user
                
                # Save the order first
                self.object = form.save()
                
                # Set the instance for the formset
                formset.instance = self.object
                
                # Save formset
                formset.save()
                
                # Calculate total amount and round to 2 decimal places
                total_amount = sum(item.total_price for item in self.object.items.all())
                self.object.total_amount = round(total_amount, 2)
                self.object.save()
                
                messages.success(self.request, f'✅ Purchase Order {self.object.order_number} created successfully!')
                return redirect(self.success_url)
        else:
            messages.error(self.request, '❌ Please correct the errors below.')
            return self.form_invalid(form)


class PurchaseOrderUpdateView(UpdateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'purchases/order_form.html'
    success_url = reverse_lazy('purchases:order_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = PurchaseOrderItemFormSet(self.request.POST, instance=self.object)
        else:
            # For edit view, don't show extra empty forms
            from .forms import inlineformset_factory
            EditFormSet = inlineformset_factory(
                PurchaseOrder,
                PurchaseOrderItem,
                form=PurchaseOrderItemForm,
                fields=['product', 'quantity', 'unit_price', 'total_price'],
                extra=0,  # No extra forms for edit
                can_delete=True,
                min_num=0,
                validate_min=False,
            )
            context['formset'] = EditFormSet(instance=self.object)
        
        context['categories'] = ProductCategory.objects.filter(is_active=True)
        context['brands'] = ProductBrand.objects.filter(is_active=True)
        context['products'] = Product.objects.filter(is_active=True).select_related('category', 'brand')
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            with transaction.atomic():
                # Store the old status before saving
                old_status = self.object.status
                new_status = form.cleaned_data.get('status')
                
                # Save the order first
                response = super().form_valid(form)
                
                # Save formset
                formset.save()
                
                # Calculate total amount and round to 2 decimal places
                total_amount = sum(item.total_price for item in self.object.items.all())
                self.object.total_amount = round(total_amount, 2)
                self.object.save()
                
                # Update inventory based on status change
                self.object.update_inventory_on_status_change(old_status, new_status, user=self.request.user)
                
                # Show appropriate success message
                if old_status != new_status:
                    if new_status == 'goods-received':
                        messages.success(self.request, f'✅ Purchase Order {self.object.order_number} marked as received! Inventory updated.')
                    elif new_status == 'canceled':
                        messages.success(self.request, f'✅ Purchase Order {self.object.order_number} cancelled! Inventory adjusted.')
                    else:
                        messages.success(self.request, f'✅ Purchase Order {self.object.order_number} updated successfully!')
                else:
                    messages.success(self.request, f'✅ Purchase Order {self.object.order_number} updated successfully!')
                
                return response
        else:
            messages.error(self.request, '❌ Please correct the errors below.')
            return self.form_invalid(form)


class PurchaseOrderDeleteView(DeleteView):
    model = PurchaseOrder
    template_name = 'purchases/order_confirm_delete.html'
    success_url = reverse_lazy('purchases:order_list')


# Reports
class PurchaseDailyReportView(ListView):
    model = PurchaseOrder
    template_name = 'purchases/reports/daily_report.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        date = self.request.GET.get('date', timezone.now().date())
        return PurchaseOrder.objects.filter(order_date=date)


class PurchaseMonthlyReportView(ListView):
    model = PurchaseOrder
    template_name = 'purchases/reports/monthly_report.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        year = self.request.GET.get('year', timezone.now().year)
        month = self.request.GET.get('month', timezone.now().month)
        return PurchaseOrder.objects.filter(
            order_date__year=year,
            order_date__month=month
        )


class PurchaseSupplierReportView(ListView):
    model = PurchaseOrder
    template_name = 'purchases/reports/supplier_report.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        supplier_id = self.request.GET.get('supplier')
        if supplier_id:
            return PurchaseOrder.objects.filter(supplier_id=supplier_id)
        return PurchaseOrder.objects.none()
