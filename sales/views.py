from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from .models import (
    SalesOrder, SalesOrderItem, SalesInvoice, SalesInvoiceItem,
    SalesReturn, SalesReturnItem, SalesPayment
)
from customers.models import Customer, CustomerLedger
from stock.models import Product
from django.contrib.auth.models import User
import uuid
import os
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT


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
                quantities = self.request.POST.getlist('quantities[]')
                prices = self.request.POST.getlist('prices[]')
                
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
                                    SalesOrderItem.objects.create(
                                        sales_order=self.object,
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
    fields = ['customer', 'sales_order', 'invoice_date', 'payment_type', 'subtotal', 'labor_charges', 'discount', 'total_amount', 'paid_amount', 'notes']
    success_url = reverse_lazy('sales:invoice_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customers'] = Customer.objects.all()
        context['products'] = Product.objects.filter(is_active=True)
        context['sales_orders'] = SalesOrder.objects.filter(status='confirmed')
        return context
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Generate unique invoice number
                invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
                form.instance.invoice_number = invoice_number
                form.instance.created_by = self.request.user
                
                # Calculate due amount
                form.instance.due_amount = form.instance.total_amount - form.instance.paid_amount
                
                # Save the invoice first
                response = super().form_valid(form)
                
                # Handle multiple products
                products = self.request.POST.getlist('products[]')
                quantities = self.request.POST.getlist('quantities[]')
                prices = self.request.POST.getlist('prices[]')
                
                from decimal import Decimal
                subtotal = Decimal('0')
                items_created = 0
                
                if products and products[0]:  # Check if at least one product is selected
                    for i, product_id in enumerate(products):
                        if product_id and i < len(quantities) and i < len(prices):
                            try:
                                product = Product.objects.get(id=product_id)
                                quantity = float(quantities[i]) if quantities[i] else 0
                                unit_price = float(prices[i]) if prices[i] else 0
                                
                                if quantity > 0 and unit_price > 0:
                                    # Create invoice item
                                    item_total = Decimal(str(quantity)) * Decimal(str(unit_price))
                                    SalesInvoiceItem.objects.create(
                                        sales_invoice=self.object,
                                        product=product,
                                        quantity=quantity,
                                        unit_price=unit_price,
                                        total_price=item_total
                                    )
                                    subtotal += item_total
                                    items_created += 1
                            except (Product.DoesNotExist, ValueError, IndexError) as e:
                                messages.error(self.request, f"Invalid data for product {i+1}: {str(e)}")
                                continue
                
                # Update subtotal and total amount
                from decimal import Decimal
                self.object.subtotal = Decimal(str(subtotal))
                self.object.total_amount = Decimal(str(subtotal)) + self.object.labor_charges - self.object.discount
                self.object.due_amount = self.object.total_amount - self.object.paid_amount
                self.object.save()
                
                # Create customer ledger entries for invoice and payment
                if self.object.total_amount > 0:
                    # Create debit entry for the invoice amount
                    CustomerLedger.objects.create(
                        customer=self.object.customer,
                        transaction_type='sale',
                        amount=self.object.total_amount,
                        description=f"Invoice {self.object.invoice_number}",
                        reference=self.object.invoice_number,
                        created_by=self.request.user
                    )
                
                # Create credit entry for any upfront payment
                if self.object.paid_amount > 0:
                    CustomerLedger.objects.create(
                        customer=self.object.customer,
                        transaction_type='payment',
                        amount=self.object.paid_amount,
                        description=f"Payment for Invoice {self.object.invoice_number}",
                        reference=self.object.invoice_number,
                        created_by=self.request.user
                    )
                
                if items_created > 0:
                    messages.success(self.request, f"Sales invoice {invoice_number} created successfully with {items_created} products! Total: ৳{self.object.total_amount}")
                else:
                    messages.warning(self.request, f"Sales invoice {invoice_number} created without items. Please add products to complete the invoice.")
                
                return response
                
        except Exception as e:
            messages.error(self.request, f"Error creating sales invoice: {str(e)}")
            return self.form_invalid(form)


class SalesInvoiceUpdateView(UpdateView):
    model = SalesInvoice
    template_name = 'sales/invoice_form.html'
    fields = ['customer', 'sales_order', 'invoice_date', 'payment_type', 'subtotal', 'labor_charges', 'discount', 'total_amount', 'paid_amount', 'notes']
    success_url = reverse_lazy('sales:invoice_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customers'] = Customer.objects.all()
        context['products'] = Product.objects.filter(is_active=True)
        context['sales_orders'] = SalesOrder.objects.filter(status='confirmed')
        return context
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                # Update the invoice
                response = super().form_valid(form)
                
                # Handle product updates
                products = self.request.POST.getlist('products[]')
                quantities = self.request.POST.getlist('quantities[]')
                prices = self.request.POST.getlist('prices[]')
                
                # Clear existing items
                self.object.items.all().delete()
                
                from decimal import Decimal
                subtotal = Decimal('0')
                items_created = 0
                
                if products and products[0]:  # Check if at least one product is selected
                    for i, product_id in enumerate(products):
                        if product_id and i < len(quantities) and i < len(prices):
                            try:
                                product = Product.objects.get(id=product_id)
                                quantity = float(quantities[i]) if quantities[i] else 0
                                unit_price = float(prices[i]) if prices[i] else 0
                                
                                if quantity > 0 and unit_price > 0:
                                    # Create invoice item
                                    item_total = Decimal(str(quantity)) * Decimal(str(unit_price))
                                    SalesInvoiceItem.objects.create(
                                        sales_invoice=self.object,
                                        product=product,
                                        quantity=quantity,
                                        unit_price=unit_price,
                                        total_price=item_total
                                    )
                                    subtotal += item_total
                                    items_created += 1
                            except (Product.DoesNotExist, ValueError, IndexError) as e:
                                messages.error(self.request, f"Invalid data for product {i+1}: {str(e)}")
                                continue
                
                # Update subtotal and total amount
                from decimal import Decimal
                self.object.subtotal = Decimal(str(subtotal))
                self.object.total_amount = Decimal(str(subtotal)) + self.object.labor_charges - self.object.discount
                self.object.due_amount = self.object.total_amount - self.object.paid_amount
                self.object.save()
                
                # Create customer ledger entries for invoice and payment (if not already exists)
                if self.object.total_amount > 0:
                    # Check if ledger entry already exists for this invoice
                    existing_ledger = CustomerLedger.objects.filter(
                        customer=self.object.customer,
                        reference=self.object.invoice_number,
                        transaction_type='sale'
                    ).first()
                    
                    if not existing_ledger:
                        # Create debit entry for the invoice amount
                        CustomerLedger.objects.create(
                            customer=self.object.customer,
                            transaction_type='sale',
                            amount=self.object.total_amount,
                            description=f"Invoice {self.object.invoice_number}",
                            reference=self.object.invoice_number,
                            created_by=self.request.user
                        )
                
                # Create credit entry for any upfront payment (if not already exists)
                if self.object.paid_amount > 0:
                    existing_payment = CustomerLedger.objects.filter(
                        customer=self.object.customer,
                        reference=self.object.invoice_number,
                        transaction_type='payment'
                    ).first()
                    
                    if not existing_payment:
                        CustomerLedger.objects.create(
                            customer=self.object.customer,
                            transaction_type='payment',
                            amount=self.object.paid_amount,
                            description=f"Payment for Invoice {self.object.invoice_number}",
                            reference=self.object.invoice_number,
                            created_by=self.request.user
                        )
                
                if items_created > 0:
                    messages.success(self.request, f"Invoice {self.object.invoice_number} updated successfully with {items_created} products! Total: ৳{self.object.total_amount}")
                else:
                    messages.warning(self.request, f"Invoice {self.object.invoice_number} updated without items.")
                
                return response
                
        except Exception as e:
            messages.error(self.request, f"Error updating invoice: {str(e)}")
            return self.form_invalid(form)


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


def create_invoice_from_order(request, order_id):
    """Create invoice directly from sales order"""
    try:
        with transaction.atomic():
            sales_order = get_object_or_404(SalesOrder, id=order_id)
            
            # Check if invoice already exists for this order
            existing_invoice = SalesInvoice.objects.filter(sales_order=sales_order).first()
            if existing_invoice:
                messages.warning(request, f"Invoice {existing_invoice.invoice_number} already exists for this order.")
                return redirect('sales:invoice_detail', existing_invoice.pk)
            
            # Create invoice
            invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
            invoice = SalesInvoice.objects.create(
                invoice_number=invoice_number,
                customer=sales_order.customer,
                sales_order=sales_order,
                invoice_date=sales_order.order_date,
                payment_type='credit',  # Default to credit for orders
                subtotal=sales_order.total_amount,
                total_amount=sales_order.total_amount,
                due_amount=sales_order.total_amount,
                created_by=request.user
            )
            
            # Create invoice items from order items
            for order_item in sales_order.items.all():
                SalesInvoiceItem.objects.create(
                    sales_invoice=invoice,
                    product=order_item.product,
                    quantity=order_item.quantity,
                    unit_price=order_item.unit_price,
                    total_price=order_item.total_price
                )
            
            # Create customer ledger entry for the invoice
            if invoice.total_amount > 0:
                CustomerLedger.objects.create(
                    customer=invoice.customer,
                    transaction_type='sale',
                    amount=invoice.total_amount,
                    description=f"Invoice {invoice.invoice_number}",
                    reference=invoice.invoice_number,
                    created_by=request.user
                )
            
            messages.success(request, f"Invoice {invoice_number} created successfully from order {sales_order.order_number}")
            return redirect('sales:invoice_detail', invoice.pk)
            
    except Exception as e:
        messages.error(request, f"Error creating invoice: {str(e)}")
        return redirect('sales:order_detail', order_id)


def invoice_pdf(request, invoice_id):
    """Generate PDF for invoice"""
    try:
        invoice = get_object_or_404(SalesInvoice, id=invoice_id)
        
        # Create response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
        
        # Create PDF with better margins
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Company info style
        company_style = ParagraphStyle(
            'CompanyInfo',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_LEFT,
            spaceAfter=6
        )
        
        # Invoice details style
        invoice_style = ParagraphStyle(
            'InvoiceDetails',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_RIGHT,
            spaceAfter=6
        )
        
        # Build content
        story = []
        
        # Title
        story.append(Paragraph("INVOICE", title_style))
        story.append(Spacer(1, 30))
        
        # Company and Invoice Details in two columns
        company_details = [
            Paragraph("<b>Company Name</b><br/>Building Materials ERP", company_style),
            Paragraph("<b>Address:</b><br/>123 Business Street<br/>City, State 12345", company_style),
            Paragraph("<b>Phone:</b> (123) 456-7890<br/><b>Email:</b> info@company.com", company_style),
        ]
        
        invoice_details = [
            Paragraph(f"<b>Invoice #:</b> {invoice.invoice_number}", invoice_style),
            Paragraph(f"<b>Date:</b> {invoice.invoice_date.strftime('%B %d, %Y')}", invoice_style),
            Paragraph(f"<b>Customer:</b> {invoice.customer.name}", invoice_style),
            Paragraph(f"<b>Payment Type:</b> {invoice.get_payment_type_display()}", invoice_style),
        ]
        
        # Create two-column layout
        company_info_table = Table([
            [company_details, invoice_details]
        ], colWidths=[3.5*inch, 3.5*inch])
        
        company_info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        story.append(company_info_table)
        story.append(Spacer(1, 30))
        
        # Invoice items table
        items_data = [["Product", "Qty", "Unit Price", "Total"]]
        for item in invoice.items.all():
            items_data.append([
                item.product.name,
                str(item.quantity),
                f"৳{item.unit_price:.2f}",
                f"৳{item.total_price:.2f}"
            ])
        
        # Calculate column widths based on page width
        page_width = A4[0] - 100  # Subtract margins
        items_table = Table(items_data, colWidths=[
            page_width * 0.4,  # Product (40%)
            page_width * 0.2,  # Warehouse (20%)
            page_width * 0.15, # Qty (15%)
            page_width * 0.12, # Unit Price (12%)
            page_width * 0.13  # Total (13%)
        ])
        
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Product names left-aligned
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        story.append(items_table)
        story.append(Spacer(1, 30))
        
        # Totals section
        totals_data = [
            ["", "", "", "Subtotal:", f"৳{invoice.subtotal:.2f}"],
            ["", "", "", "Labor Charges:", f"৳{invoice.labor_charges:.2f}"],
            ["", "", "", "Discount:", f"৳{invoice.discount:.2f}"],
            ["", "", "", "Total Amount:", f"৳{invoice.total_amount:.2f}"],
            ["", "", "", "Paid Amount:", f"৳{invoice.paid_amount:.2f}"],
            ["", "", "", "Due Amount:", f"৳{invoice.due_amount:.2f}"],
        ]
        
        totals_table = Table(totals_data, colWidths=[
            page_width * 0.4,  # Empty
            page_width * 0.2,  # Empty
            page_width * 0.15, # Empty
            page_width * 0.12, # Label
            page_width * 0.13  # Amount
        ])
        
        totals_table.setStyle(TableStyle([
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),  # Labels right-aligned
            ('ALIGN', (4, 0), (4, -1), 'RIGHT'),  # Amounts right-aligned
            ('FONTNAME', (3, 3), (4, 3), 'Helvetica-Bold'),  # Total Amount bold
            ('FONTNAME', (3, 5), (4, 5), 'Helvetica-Bold'),  # Due Amount bold
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LINEBELOW', (3, 2), (4, 2), 1, colors.black),  # Line above total
            ('LINEBELOW', (3, 4), (4, 4), 1, colors.black),  # Line above due
        ]))
        story.append(totals_table)
        
        # Add notes if available
        if invoice.notes:
            story.append(Spacer(1, 20))
            notes_style = ParagraphStyle(
                'Notes',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_LEFT,
                textColor=colors.darkgrey
            )
            story.append(Paragraph(f"<b>Notes:</b> {invoice.notes}", notes_style))
        
        # Build PDF
        doc.build(story)
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        
        return response
        
    except Exception as e:
        messages.error(request, f"Error generating PDF: {str(e)}")
        return redirect('sales:invoice_detail', invoice_id)


def process_invoice_payment(request, invoice_id):
    """Process payment for invoice and create ledger entry"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                invoice = get_object_or_404(SalesInvoice, id=invoice_id)
                paid_amount = float(request.POST.get('paid_amount', 0))
                
                if paid_amount > 0:
                    # Update invoice
                    invoice.paid_amount += paid_amount
                    invoice.due_amount = invoice.total_amount - invoice.paid_amount
                    invoice.save()
                    
                    # Create customer ledger entry
                    CustomerLedger.objects.create(
                        customer=invoice.customer,
                        transaction_type='payment',
                        amount=paid_amount,
                        description=f"Payment for Invoice {invoice.invoice_number}",
                        reference=invoice.invoice_number,
                        created_by=request.user
                    )
                    
                    # Create sales payment record
                    SalesPayment.objects.create(
                        sales_invoice=invoice,
                        payment_date=invoice.invoice_date,
                        payment_method='cash',
                        amount=paid_amount,
                        reference=f"Payment for {invoice.invoice_number}",
                        created_by=request.user
                    )
                    
                    messages.success(request, f"Payment of ৳{paid_amount:.2f} processed successfully!")
                else:
                    messages.error(request, "Please enter a valid payment amount.")
                    
        except Exception as e:
            messages.error(request, f"Error processing payment: {str(e)}")
    
    return redirect('sales:invoice_detail', invoice_id)
