from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from .models import PurchaseOrder, PurchaseOrderItem, GoodsReceipt
from suppliers.models import Supplier
from stock.models import Product
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
    template_name = 'purchases/order_form.html'
    fields = ['supplier', 'order_date', 'expected_date', 'status', 'notes', 'total_amount']
    success_url = reverse_lazy('purchases:order_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suppliers'] = Supplier.objects.all()
        context['products'] = Product.objects.filter(is_active=True)
        return context
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Generate unique order number
                order_number = f"PO-{uuid.uuid4().hex[:8].upper()}"
                form.instance.order_number = order_number
                form.instance.created_by = self.request.user
                
                # Ensure status is valid (default to draft if invalid)
                if form.instance.status not in ['draft', 'sent', 'received', 'cancelled']:
                    form.instance.status = 'draft'
                
                # Save the order first
                response = super().form_valid(form)
                
                # Handle products - simplified approach
                products = self.request.POST.getlist('products[]')
                quantities = self.request.POST.getlist('quantities[]')
                prices = self.request.POST.getlist('prices[]')
                
                total_amount = 0
                items_created = 0
                
                # Simple validation - just check if we have products
                if products and products[0] and products[0].strip():
                    for i, product_id in enumerate(products):
                        if not product_id or not product_id.strip():
                            continue
                            
                        # Get corresponding data
                        quantity_str = quantities[i] if i < len(quantities) else ''
                        price_str = prices[i] if i < len(prices) else ''
                        
                        # Skip if any required data is missing
                        if not quantity_str or not price_str:
                            continue
                            
                        try:
                            # Get objects
                            product = Product.objects.get(id=product_id)
                            
                            # Convert to numbers
                            quantity = float(quantity_str)
                            unit_price = float(price_str)
                            
                            # Skip if invalid numbers
                            if quantity <= 0 or unit_price <= 0:
                                continue
                            
                            # Create item
                            item_total = quantity * unit_price
                            PurchaseOrderItem.objects.create(
                                purchase_order=self.object,
                                product=product,
                                quantity=quantity,
                                unit_price=unit_price,
                                total_price=item_total
                            )
                            total_amount += item_total
                            items_created += 1
                            
                        except (Product.DoesNotExist, ValueError, IndexError):
                            # Silently skip invalid items
                            continue
                
                # Update total amount
                self.object.total_amount = total_amount
                self.object.save()
                
                # Order created successfully - no message needed
                
                return response
                
        except Exception as e:
            # Simple error message
            messages.error(self.request, f"❌ Failed to create order. Please try again.")
            return self.form_invalid(form)


class PurchaseOrderUpdateView(UpdateView):
    model = PurchaseOrder
    template_name = 'purchases/order_form.html'
    fields = ['supplier', 'order_date', 'expected_date', 'status', 'notes', 'total_amount']
    success_url = reverse_lazy('purchases:order_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['suppliers'] = Supplier.objects.all()
        context['products'] = Product.objects.filter(is_active=True)
        return context
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Save the order first
                response = super().form_valid(form)
                
                # Handle multiple products
                products = self.request.POST.getlist('products[]')
                quantities = self.request.POST.getlist('quantities[]')
                prices = self.request.POST.getlist('prices[]')
                
                # Clear existing items
                self.object.items.all().delete()
                
                total_amount = 0
                items_created = 0
                
                if products and products[0]:  # Check if at least one product is selected
                    for i, product_id in enumerate(products):
                        if product_id and i < len(quantities) and i < len(prices):
                            try:
                                product = Product.objects.get(id=product_id)
                                quantity = float(quantities[i]) if quantities[i] else 0
                                unit_price = float(prices[i]) if prices[i] else 0
                                
                                if quantity > 0 and unit_price > 0:
                                    # Create order item
                                    item_total = quantity * unit_price
                                    PurchaseOrderItem.objects.create(
                                        purchase_order=self.object,
                                        product=product,
                                        quantity=quantity,
                                        unit_price=unit_price,
                                        total_price=item_total
                                    )
                                    total_amount += item_total
                                    items_created += 1
                            except (Product.DoesNotExist, ValueError, IndexError) as e:
                                messages.error(self.request, f"Invalid data for product {i+1}: {str(e)}")
                                continue
                
                # Update total amount
                self.object.total_amount = total_amount
                self.object.save()
                
                # Order updated successfully - no message needed
                
                return response
                
        except Exception as e:
            messages.error(self.request, f"Error updating purchase order: {str(e)}")
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
