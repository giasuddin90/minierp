from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q, F
from django.db import connection
from decimal import Decimal
from datetime import datetime, timedelta
import json

from .models import ReportTemplate, ReportSchedule, ReportLog
from sales.models import SalesOrder, SalesInvoice, SalesPayment, SalesInvoiceItem
from purchases.models import PurchaseOrder
from stock.models import Product, Stock
from customers.models import Customer, CustomerLedger
from suppliers.models import Supplier, SupplierLedger


class ReportDashboardView(ListView):
    """Main reporting dashboard"""
    model = ReportLog
    template_name = 'reports/dashboard.html'
    context_object_name = 'recent_reports'
    
    def get_queryset(self):
        return ReportLog.objects.all()[:10]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get report statistics
        total_reports = ReportLog.objects.count()
        completed_reports = ReportLog.objects.filter(status='completed').count()
        failed_reports = ReportLog.objects.filter(status='failed').count()
        
        # Get recent activity
        recent_reports = ReportLog.objects.filter(
            generated_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Get report types distribution
        report_types = ReportLog.objects.values('report_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        context.update({
            'total_reports': total_reports,
            'completed_reports': completed_reports,
            'failed_reports': failed_reports,
            'recent_reports_count': recent_reports,
            'report_types': report_types,
        })
        return context


class FinancialReportView(ListView):
    """Financial reports including P&L, Balance Sheet, Cash Flow"""
    model = SalesInvoice
    template_name = 'reports/financial_report.html'
    context_object_name = 'reports'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Get date range
            start_date = self.request.GET.get('start_date', (timezone.now() - timedelta(days=30)).date())
            end_date = self.request.GET.get('end_date', timezone.now().date())
            
            # Get financial data
            context.update({
                'start_date': start_date,
                'end_date': end_date,
                'revenue_data': self.get_revenue_data(start_date, end_date),
                'expense_data': self.get_expense_data(start_date, end_date),
                'profit_loss': self.get_profit_loss(start_date, end_date),
                'cash_flow': self.get_cash_flow(start_date, end_date),
            })
        except Exception as e:
            # Default values if there's an error
            context.update({
                'start_date': timezone.now().date(),
                'end_date': timezone.now().date(),
                'revenue_data': {'total_sales': 0, 'other_income': 0, 'total_revenue': 0},
                'expense_data': {'total_expenses': 0, 'expenses_by_category': []},
                'profit_loss': {'gross_profit': 0, 'profit_margin': 0},
                'cash_flow': {'inflows': 0, 'outflows': 0, 'net_cash_flow': 0},
            })
        return context
    
    def get_revenue_data(self, start_date, end_date):
        """Get revenue data for the period"""
        sales_invoices = SalesInvoice.objects.filter(
            invoice_date__range=[start_date, end_date]
        )
        
        total_sales = sales_invoices.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        return {
            'total_sales': total_sales,
            'other_income': Decimal('0'),
            'total_revenue': total_sales,
        }
    
    def get_expense_data(self, start_date, end_date):
        """Get expense data for the period"""
        return {
            'total_expenses': Decimal('0'),
            'expenses_by_category': [],
        }
    
    def get_profit_loss(self, start_date, end_date):
        """Calculate profit and loss"""
        revenue_data = self.get_revenue_data(start_date, end_date)
        expense_data = self.get_expense_data(start_date, end_date)
        
        gross_profit = revenue_data['total_revenue'] - expense_data['total_expenses']
        
        return {
            'gross_profit': gross_profit,
            'profit_margin': (gross_profit / revenue_data['total_revenue'] * 100) if revenue_data['total_revenue'] > 0 else 0,
        }
    
    def get_cash_flow(self, start_date, end_date):
        """Get cash flow data"""
        # Customer payments
        customer_payments = SalesPayment.objects.filter(
            payment_date__range=[start_date, end_date]
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # No supplier payments in simplified model
        supplier_payments = Decimal('0')
        
        net_cash_flow = customer_payments - supplier_payments
        
        return {
            'inflows': customer_payments,
            'outflows': supplier_payments,
            'net_cash_flow': net_cash_flow,
        }


class InventoryReportView(ListView):
    """Inventory reports including stock levels, movements, and valuation"""
    model = Product
    template_name = 'reports/inventory_report.html'
    context_object_name = 'inventory_data'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get inventory data
        products = Product.objects.filter(is_active=True).prefetch_related('stock_set')
        
        # Calculate inventory metrics
        total_products = products.count()
        total_stock_value = sum(product.get_total_stock_value() for product in products)
        
        # Get stock movements - removed since StockMovement model is removed
        recent_movements = []
        
        # Get low stock items
        low_stock_items = []
        for product in products:
            total_quantity = product.get_total_quantity()
            if total_quantity < 10:  # Assuming 10 is the low stock threshold
                low_stock_items.append({
                    'product': product,
                    'quantity': total_quantity,
                    'value': product.get_total_stock_value(),
                })
        
        # Get top selling products
        try:
            top_selling = SalesInvoiceItem.objects.filter(
                sales_invoice__invoice_date__gte=timezone.now() - timedelta(days=30)
            ).values('product__name').annotate(
                total_sold=Sum('quantity'),
                total_value=Sum('total_price')
            ).order_by('-total_sold')[:10]
        except:
            top_selling = []
        
        context.update({
            'total_products': total_products,
            'total_stock_value': total_stock_value,
            'recent_movements': recent_movements[:20],
            'low_stock_items': low_stock_items,
            'top_selling': top_selling,
        })
        return context


class SalesReportView(ListView):
    """Sales reports including orders, invoices, and payments"""
    model = SalesInvoice
    template_name = 'reports/sales_report.html'
    context_object_name = 'sales_data'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range
        start_date = self.request.GET.get('start_date', (timezone.now() - timedelta(days=30)).date())
        end_date = self.request.GET.get('end_date', timezone.now().date())
        
        # Get sales data
        sales_orders = SalesOrder.objects.filter(
            order_date__range=[start_date, end_date]
        )
        
        sales_invoices = SalesInvoice.objects.filter(
            invoice_date__range=[start_date, end_date]
        )
        
        sales_payments = SalesPayment.objects.filter(
            payment_date__range=[start_date, end_date]
        )
        
        # Calculate metrics
        total_orders = sales_orders.count()
        total_invoices = sales_invoices.count()
        total_sales = sales_invoices.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        total_payments = sales_payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Get top customers
        top_customers = sales_invoices.values('customer__name').annotate(
            total_sales=Sum('total_amount'),
            order_count=Count('id')
        ).order_by('-total_sales')[:10]
        
        # Get sales by product
        try:
            sales_by_product = SalesInvoiceItem.objects.filter(
                sales_invoice__invoice_date__range=[start_date, end_date]
            ).values('product__name').annotate(
                total_quantity=Sum('quantity'),
                total_value=Sum('total_price')
            ).order_by('-total_value')[:10]
        except:
            sales_by_product = []
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'total_orders': total_orders,
            'total_invoices': total_invoices,
            'total_sales': total_sales,
            'total_payments': total_payments,
            'top_customers': top_customers,
            'sales_by_product': sales_by_product,
        })
        return context


class PurchaseReportView(ListView):
    """Purchase reports including orders and receipts"""
    model = PurchaseOrder
    template_name = 'reports/purchase_report.html'
    context_object_name = 'purchase_data'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range
        start_date = self.request.GET.get('start_date', (timezone.now() - timedelta(days=30)).date())
        end_date = self.request.GET.get('end_date', timezone.now().date())
        
        # Get purchase data
        purchase_orders = PurchaseOrder.objects.filter(
            order_date__range=[start_date, end_date]
        )
        
        # Calculate metrics
        total_orders = purchase_orders.count()
        total_purchases = purchase_orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Get orders by status
        orders_by_status = purchase_orders.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        # Get top suppliers
        top_suppliers = purchase_orders.values('supplier__name').annotate(
            total_purchases=Sum('total_amount'),
            order_count=Count('id')
        ).order_by('-total_purchases')[:10]
        
        # Get purchases by product
        try:
            purchases_by_product = []
            for order in purchase_orders:
                for item in order.items.all():
                    product_name = item.product.name
                    existing = next((p for p in purchases_by_product if p['product'] == product_name), None)
                    if existing:
                        existing['total_quantity'] += float(item.quantity)
                        existing['total_value'] += float(item.total_price)
                    else:
                        purchases_by_product.append({
                            'product': product_name,
                            'total_quantity': float(item.quantity),
                            'total_value': float(item.total_price),
                        })
            purchases_by_product.sort(key=lambda x: x['total_value'], reverse=True)
            purchases_by_product = purchases_by_product[:10]
        except:
            purchases_by_product = []
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'total_orders': total_orders,
            'total_purchases': total_purchases,
            'orders_by_status': orders_by_status,
            'top_suppliers': top_suppliers,
            'purchases_by_product': purchases_by_product,
        })
        return context


class CustomerReportView(ListView):
    """Customer reports including ledger, payments, and analysis"""
    model = Customer
    template_name = 'reports/customer_report.html'
    context_object_name = 'customer_data'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get customer data
        customers = Customer.objects.filter(is_active=True)
        
        # Get customer metrics
        total_customers = customers.count()
        
        # Get customer ledger data
        customer_ledgers = CustomerLedger.objects.all()
        
        # Calculate customer balances
        customer_balances = []
        for customer in customers:
            total_sales = SalesInvoice.objects.filter(customer=customer).aggregate(
                total=Sum('total_amount')
            )['total'] or Decimal('0')
            
            total_payments = SalesPayment.objects.filter(
                sales_invoice__customer=customer
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            balance = total_sales - total_payments
            
            customer_balances.append({
                'customer': customer,
                'total_sales': total_sales,
                'total_payments': total_payments,
                'balance': balance,
            })
        
        # Sort by balance (highest first)
        customer_balances.sort(key=lambda x: x['balance'], reverse=True)
        
        # Get top customers by sales
        top_customers = SalesInvoice.objects.values('customer__name').annotate(
            total_sales=Sum('total_amount'),
            invoice_count=Count('id')
        ).order_by('-total_sales')[:10]
        
        context.update({
            'total_customers': total_customers,
            'customer_balances': customer_balances[:20],
            'top_customers': top_customers,
        })
        return context


class SupplierReportView(ListView):
    """Supplier reports including ledger, payments, and analysis"""
    model = Supplier
    template_name = 'reports/supplier_report.html'
    context_object_name = 'supplier_data'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get supplier data
        suppliers = Supplier.objects.filter(is_active=True)
        
        # Get supplier metrics
        total_suppliers = suppliers.count()
        
        # Calculate supplier balances
        supplier_balances = []
        for supplier in suppliers:
            total_purchases = PurchaseOrder.objects.filter(supplier=supplier).aggregate(
                total=Sum('total_amount')
            )['total'] or Decimal('0')
            
            supplier_balances.append({
                'supplier': supplier,
                'total_purchases': total_purchases,
                'total_payments': Decimal('0'),
                'balance': total_purchases,
            })
        
        # Sort by balance (highest first)
        supplier_balances.sort(key=lambda x: x['balance'], reverse=True)
        
        # Get top suppliers by purchases
        top_suppliers = PurchaseOrder.objects.values('supplier__name').annotate(
            total_purchases=Sum('total_amount'),
            order_count=Count('id')
        ).order_by('-total_purchases')[:10]
        
        context.update({
            'total_suppliers': total_suppliers,
            'supplier_balances': supplier_balances[:20],
            'top_suppliers': top_suppliers,
        })
        return context


class ReportTemplateListView(ListView):
    """List of report templates"""
    model = ReportTemplate
    template_name = 'reports/template_list.html'
    context_object_name = 'templates'


class ReportTemplateCreateView(CreateView):
    """Create new report template"""
    model = ReportTemplate
    template_name = 'reports/template_form.html'
    fields = ['name', 'report_type', 'description', 'template_content']
    success_url = reverse_lazy('reports:template_list')


class ReportTemplateUpdateView(UpdateView):
    """Update report template"""
    model = ReportTemplate
    template_name = 'reports/template_form.html'
    fields = ['name', 'report_type', 'description', 'template_content']
    success_url = reverse_lazy('reports:template_list')


class ReportTemplateDeleteView(DeleteView):
    """Delete report template"""
    model = ReportTemplate
    template_name = 'reports/template_confirm_delete.html'
    success_url = reverse_lazy('reports:template_list')


class ReportLogListView(ListView):
    """List of report logs"""
    model = ReportLog
    template_name = 'reports/log_list.html'
    context_object_name = 'logs'
    paginate_by = 20


def generate_report(request, report_type):
    """Generate specific report"""
    try:
        # Create report log entry
        log = ReportLog.objects.create(
            report_name=f"{report_type.title()} Report",
            report_type=report_type,
            status='generating',
            generated_by=request.user,
            parameters=request.GET.dict()
        )
        
        # Generate report based on type
        if report_type == 'financial':
            data = get_financial_report_data(request)
        elif report_type == 'inventory':
            data = get_inventory_report_data(request)
        elif report_type == 'sales':
            data = get_sales_report_data(request)
        elif report_type == 'purchase':
            data = get_purchase_report_data(request)
        elif report_type == 'customer':
            data = get_customer_report_data(request)
        elif report_type == 'supplier':
            data = get_supplier_report_data(request)
        else:
            return JsonResponse({'error': 'Invalid report type'}, status=400)
        
        # Update log status
        log.status = 'completed'
        log.save()
        
        return JsonResponse({
            'success': True,
            'data': data,
            'log_id': log.id
        })
        
    except Exception as e:
        log.status = 'failed'
        log.error_message = str(e)
        log.save()
        
        return JsonResponse({
            'error': str(e)
        }, status=500)


def get_financial_report_data(request):
    """Get financial report data"""
    start_date = request.GET.get('start_date', (timezone.now() - timedelta(days=30)).date())
    end_date = request.GET.get('end_date', timezone.now().date())
    
    # Get revenue data
    total_sales = SalesInvoice.objects.filter(
        invoice_date__range=[start_date, end_date]
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    
    return {
        'total_sales': float(total_sales),
        'total_income': 0.0,
        'total_expenses': 0.0,
        'net_profit': float(total_sales),
        'start_date': start_date,
        'end_date': end_date,
    }


def get_inventory_report_data(request):
    """Get inventory report data"""
    products = Product.objects.filter(is_active=True)
    
    total_products = products.count()
    total_stock_value = sum(float(product.get_total_stock_value()) for product in products)
    
    low_stock_items = []
    for product in products:
        quantity = product.get_total_quantity()
        if quantity < 10:
            low_stock_items.append({
                'name': product.name,
                'quantity': float(quantity),
                'value': float(product.get_total_stock_value()),
            })
    
    return {
        'total_products': total_products,
        'total_stock_value': total_stock_value,
        'low_stock_items': low_stock_items,
    }


def get_sales_report_data(request):
    """Get sales report data"""
    start_date = request.GET.get('start_date', (timezone.now() - timedelta(days=30)).date())
    end_date = request.GET.get('end_date', timezone.now().date())
    
    total_sales = SalesInvoice.objects.filter(
        invoice_date__range=[start_date, end_date]
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    
    total_orders = SalesOrder.objects.filter(
        order_date__range=[start_date, end_date]
    ).count()
    
    return {
        'total_sales': float(total_sales),
        'total_orders': total_orders,
        'start_date': start_date,
        'end_date': end_date,
    }


def get_purchase_report_data(request):
    """Get purchase report data"""
    start_date = request.GET.get('start_date', (timezone.now() - timedelta(days=30)).date())
    end_date = request.GET.get('end_date', timezone.now().date())
    
    total_purchases = PurchaseOrder.objects.filter(
        order_date__range=[start_date, end_date]
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    
    total_orders = PurchaseOrder.objects.filter(
        order_date__range=[start_date, end_date]
    ).count()
    
    return {
        'total_purchases': float(total_purchases),
        'total_orders': total_orders,
        'start_date': start_date,
        'end_date': end_date,
    }


def get_customer_report_data(request):
    """Get customer report data"""
    customers = Customer.objects.filter(is_active=True)
    
    total_customers = customers.count()
    
    customer_data = []
    for customer in customers:
        total_sales = SalesInvoice.objects.filter(customer=customer).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        total_payments = SalesPayment.objects.filter(
            sales_invoice__customer=customer
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        customer_data.append({
            'name': customer.name,
            'total_sales': float(total_sales),
            'total_payments': float(total_payments),
            'balance': float(total_sales - total_payments),
        })
    
    return {
        'total_customers': total_customers,
        'customers': customer_data,
    }


def get_supplier_report_data(request):
    """Get supplier report data"""
    suppliers = Supplier.objects.filter(is_active=True)
    
    total_suppliers = suppliers.count()
    
    supplier_data = []
    for supplier in suppliers:
        total_purchases = PurchaseOrder.objects.filter(supplier=supplier).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        supplier_data.append({
            'name': supplier.name,
            'total_purchases': float(total_purchases),
            'total_payments': 0.0,
            'balance': float(total_purchases),
        })
    
    return {
        'total_suppliers': total_suppliers,
        'suppliers': supplier_data,
    }
