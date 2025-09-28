from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from .models import (
    PurchaseOrder, PurchaseOrderItem, GoodsReceipt, GoodsReceiptItem,
    PurchaseInvoice, PurchaseInvoiceItem, PurchaseReturn, PurchaseReturnItem, PurchasePayment
)
from suppliers.models import Supplier
from stock.models import Product, Warehouse
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
        context['warehouses'] = Warehouse.objects.filter(is_active=True)
        return context
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Generate unique order number
                order_number = f"PO-{uuid.uuid4().hex[:8].upper()}"
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
                errors = []
                
                # Validate product data
                if products and products[0]:
                    for i, product_id in enumerate(products):
                        if not product_id:
                            continue
                            
                        # Check if we have all required data for this product
                        if i >= len(warehouses) or i >= len(quantities) or i >= len(prices):
                            errors.append(f"Product {i+1}: Missing warehouse, quantity, or price")
                            continue
                            
                        warehouse_id = warehouses[i]
                        quantity_str = quantities[i]
                        price_str = prices[i]
                        
                        # Validate product exists
                        try:
                            product = Product.objects.get(id=product_id)
                        except Product.DoesNotExist:
                            errors.append(f"Product {i+1}: Product not found")
                            continue
                        
                        # Validate warehouse exists
                        try:
                            warehouse = Warehouse.objects.get(id=warehouse_id)
                        except Warehouse.DoesNotExist:
                            errors.append(f"Product {i+1}: Warehouse not found")
                            continue
                        
                        # Validate quantity
                        try:
                            quantity = float(quantity_str) if quantity_str else 0
                            if quantity <= 0:
                                errors.append(f"Product {i+1} ({product.name}): Quantity must be greater than 0")
                                continue
                        except ValueError:
                            errors.append(f"Product {i+1} ({product.name}): Invalid quantity '{quantity_str}'")
                            continue
                        
                        # Validate price
                        try:
                            unit_price = float(price_str) if price_str else 0
                            if unit_price <= 0:
                                errors.append(f"Product {i+1} ({product.name}): Price must be greater than 0")
                                continue
                        except ValueError:
                            errors.append(f"Product {i+1} ({product.name}): Invalid price '{price_str}'")
                            continue
                        
                        # Create order item
                        try:
                            item_total = quantity * unit_price
                            PurchaseOrderItem.objects.create(
                                purchase_order=self.object,
                                product=product,
                                warehouse=warehouse,
                                quantity=quantity,
                                unit_price=unit_price,
                                total_price=item_total
                            )
                            total_amount += item_total
                            items_created += 1
                            
                        except Exception as e:
                            errors.append(f"Product {i+1} ({product.name}): Failed to create item - {str(e)}")
                            continue
                
                # Show errors if any
                if errors:
                    for error in errors:
                        messages.error(self.request, error)
                
                # Update total amount
                self.object.total_amount = total_amount
                self.object.save()
                
                # Show success message
                if items_created > 0:
                    messages.success(self.request, f"✅ Purchase order {order_number} created successfully!")
                    messages.info(self.request, f"📦 Added {items_created} products with total value: ৳{total_amount:,.2f}")
                else:
                    messages.warning(self.request, f"⚠️ Purchase order {order_number} created without products")
                    messages.info(self.request, "💡 You can edit the order later to add products")
                
                return response
                
        except Exception as e:
            messages.error(self.request, f"❌ Error creating purchase order: {str(e)}")
            messages.info(self.request, "💡 Please check all fields and try again")
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
        context['warehouses'] = Warehouse.objects.filter(is_active=True)
        return context
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Save the order first
                response = super().form_valid(form)
                
                # Handle multiple products
                products = self.request.POST.getlist('products[]')
                warehouses = self.request.POST.getlist('warehouses[]')
                quantities = self.request.POST.getlist('quantities[]')
                prices = self.request.POST.getlist('prices[]')
                
                # Clear existing items
                self.object.items.all().delete()
                
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
                                    PurchaseOrderItem.objects.create(
                                        purchase_order=self.object,
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
                    messages.success(self.request, f"Purchase order updated successfully with {items_created} products! Total: ৳{total_amount}")
                else:
                    messages.warning(self.request, f"Purchase order updated without items. Please add products to complete the order.")
                
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
