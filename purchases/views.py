from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from .models import PurchaseOrder, PurchaseOrderItem, GoodsReceipt
from .forms import (
    PurchaseOrderForm, PurchaseOrderItemFormSet, GoodsReceiptForm, 
    DirectGoodsReceiptForm, GoodsReceiptItemForm, PurchaseOrderSearchForm
)
from suppliers.models import Supplier
from stock.models import Product, ProductCategory, ProductBrand, Stock
from django.contrib.auth.models import User
import uuid


class PurchaseOrderListView(ListView):
    model = PurchaseOrder
    template_name = 'purchases/order_list.html'
    context_object_name = 'orders'


class PurchaseOrderDetailView(DetailView):
    model = PurchaseOrder
    template_name = 'purchases/order_detail.html'


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
                # Generate unique order number
                order_number = f"PO-{uuid.uuid4().hex[:8].upper()}"
                form.instance.order_number = order_number
                form.instance.created_by = self.request.user
                form.instance.status = 'purchase-order'
                
                # Save the order first
                response = super().form_valid(form)
                
                # Save formset
                formset.instance = self.object
                formset.save()
                
                # Calculate total amount
                total_amount = sum(item.total_price for item in self.object.items.all())
                self.object.total_amount = total_amount
                self.object.save()
                
                messages.success(self.request, f'✅ Purchase Order {self.object.order_number} created successfully!')
                return response
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
            context['formset'] = PurchaseOrderItemFormSet(instance=self.object)
        
        context['categories'] = ProductCategory.objects.filter(is_active=True)
        context['brands'] = ProductBrand.objects.filter(is_active=True)
        context['products'] = Product.objects.filter(is_active=True).select_related('category', 'brand')
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            with transaction.atomic():
                # Save the order first
                response = super().form_valid(form)
                
                # Save formset
                formset.save()
                
                # Calculate total amount
                total_amount = sum(item.total_price for item in self.object.items.all())
                self.object.total_amount = total_amount
                self.object.save()
                
                messages.success(self.request, f'✅ Purchase Order {self.object.order_number} updated successfully!')
                return response
        else:
            messages.error(self.request, '❌ Please correct the errors below.')
            return self.form_invalid(form)


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
    form_class = GoodsReceiptForm
    template_name = 'purchases/receipt_form.html'
    success_url = reverse_lazy('purchases:receipt_list')
    
    def form_valid(self, form):
        with transaction.atomic():
            # Generate unique receipt number
            receipt_number = f"GR-{uuid.uuid4().hex[:8].upper()}"
            form.instance.receipt_number = receipt_number
            form.instance.created_by = self.request.user
            
            # If linked to purchase order, update its status
            if form.instance.purchase_order:
                form.instance.purchase_order.receive_goods(user=self.request.user)
            
            response = super().form_valid(form)
            messages.success(self.request, f'✅ Goods Receipt {form.instance.receipt_number} created successfully!')
            return response


class DirectGoodsReceiptCreateView(CreateView):
    """Create goods receipt directly without purchase order"""
    model = GoodsReceipt
    form_class = DirectGoodsReceiptForm
    template_name = 'purchases/direct_receipt_form.html'
    success_url = reverse_lazy('purchases:receipt_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ProductCategory.objects.filter(is_active=True)
        context['brands'] = ProductBrand.objects.filter(is_active=True)
        context['products'] = Product.objects.filter(is_active=True)
        return context
    
    def form_valid(self, form):
        with transaction.atomic():
            # Generate unique receipt number
            receipt_number = f"GR-{uuid.uuid4().hex[:8].upper()}"
            form.instance.receipt_number = receipt_number
            form.instance.created_by = self.request.user
            
            # Save the receipt first
            response = super().form_valid(form)
            
            # Handle direct items
            products = self.request.POST.getlist('products[]')
            quantities = self.request.POST.getlist('quantities[]')
            unit_costs = self.request.POST.getlist('unit_costs[]')
            
            total_amount = 0
            
            if products and products[0]:
                for i, product_id in enumerate(products):
                    if product_id and i < len(quantities) and i < len(unit_costs):
                        try:
                            product = Product.objects.get(id=product_id)
                            quantity = float(quantities[i]) if quantities[i] else 0
                            unit_cost = float(unit_costs[i]) if unit_costs[i] else 0
                            
                            if quantity > 0 and unit_cost > 0:
                                # Update stock directly
                                Stock.update_stock(
                                    product=product,
                                    quantity_change=quantity,
                                    unit_cost=unit_cost,
                                    movement_type='inward',
                                    reference=f"GR-{receipt_number}",
                                    description=f"Direct goods receipt - {form.cleaned_data['supplier'].name}",
                                    user=self.request.user
                                )
                                
                                total_amount += quantity * unit_cost
                                
                        except (Product.DoesNotExist, ValueError, IndexError):
                            continue
            
            # Update total amount
            self.object.total_amount = total_amount
            self.object.save()
            
            messages.success(self.request, f'✅ Direct Goods Receipt {form.instance.receipt_number} created successfully!')
            return response


class GoodsReceiptUpdateView(UpdateView):
    model = GoodsReceipt
    template_name = 'purchases/receipt_form.html'
    fields = '__all__'
    success_url = reverse_lazy('purchases:receipt_list')


class GoodsReceiptDeleteView(DeleteView):
    model = GoodsReceipt
    template_name = 'purchases/receipt_confirm_delete.html'
    success_url = reverse_lazy('purchases:receipt_list')


# Removed unnecessary models and views for simplified purchase flow


class PurchaseDailyReportView(ListView):
    model = PurchaseOrder
    template_name = 'purchases/purchase_daily_report.html'
    context_object_name = 'reports'
    
    def get_queryset(self):
        from django.utils import timezone
        today = timezone.now().date()
        return PurchaseOrder.objects.filter(order_date=today)


class PurchaseMonthlyReportView(ListView):
    model = PurchaseOrder
    template_name = 'purchases/purchase_monthly_report.html'
    context_object_name = 'reports'
    
    def get_queryset(self):
        from django.utils import timezone
        now = timezone.now()
        return PurchaseOrder.objects.filter(
            order_date__year=now.year,
            order_date__month=now.month
        )


class PurchaseSupplierReportView(ListView):
    model = PurchaseOrder
    template_name = 'purchases/purchase_supplier_report.html'
    context_object_name = 'reports'
