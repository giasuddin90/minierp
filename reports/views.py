from django.shortcuts import render
from django.views.generic import ListView
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count
from decimal import Decimal
from datetime import timedelta
import csv
from django.utils.dateparse import parse_date

from .models import ReportLog
from sales.models import SalesOrder
from purchases.models import PurchaseOrder
from stock.models import Product
from customers.models import Customer
from suppliers.models import Supplier
from expenses.models import Expense


# ReportDashboardView removed - using enhanced reports instead


# Old report views removed - replaced with enhanced versions


# Report template views removed - not needed for simplified reports


# ==================== ENHANCED REPORTS WITH TIME RANGE FILTERING ====================

class SalesReportEnhancedView(ListView):
    """Enhanced Sales Report with time range filtering and CSV download"""
    model = SalesOrder
    template_name = 'reports/sales_report_enhanced.html'
    context_object_name = 'sales_data'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from request
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        
        # Default to last 30 days if no dates provided
        if start_date_str:
            start_date = parse_date(start_date_str)
        else:
            start_date = (timezone.now() - timedelta(days=30)).date()
            
        if end_date_str:
            end_date = parse_date(end_date_str)
        else:
            end_date = timezone.now().date()
        
        # Get sales data
        sales_orders = SalesOrder.objects.filter(
            order_date__range=[start_date, end_date]
        ).select_related('customer').prefetch_related('items__product')
        
        delivered_orders = sales_orders.filter(status='delivered')
        
        # Calculate metrics
        total_orders = sales_orders.count()
        delivered_count = delivered_orders.count()
        total_sales = delivered_orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        average_order_value = total_sales / delivered_count if delivered_count > 0 else Decimal('0')
        
        # Get sales by day for chart
        daily_sales = []
        current_date = start_date
        while current_date <= end_date:
            day_sales = delivered_orders.filter(order_date=current_date).aggregate(
                total=Sum('total_amount')
            )['total'] or Decimal('0')
            daily_sales.append({
                'date': current_date,
                'amount': float(day_sales)
            })
            current_date += timedelta(days=1)
        
        # Get top customers
        top_customers = delivered_orders.values('customer__name').annotate(
            total_sales=Sum('total_amount'),
            order_count=Count('id')
        ).order_by('-total_sales')[:10]
        
        # Get sales by product
        sales_by_product = []
        for order in delivered_orders:
            for item in order.items.all():
                product_name = item.product.name
                existing = next((p for p in sales_by_product if p['product_name'] == product_name), None)
                if existing:
                    existing['total_quantity'] += float(item.quantity)
                    existing['total_value'] += float(item.total_price)
                    existing['order_count'] += 1
                else:
                    sales_by_product.append({
                        'product_name': product_name,
                        'total_quantity': float(item.quantity),
                        'total_value': float(item.total_price),
                        'order_count': 1,
                    })
        
        sales_by_product.sort(key=lambda x: x['total_value'], reverse=True)
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'total_orders': total_orders,
            'delivered_count': delivered_count,
            'total_sales': total_sales,
            'average_order_value': average_order_value,
            'daily_sales': daily_sales,
            'top_customers': top_customers,
            'sales_by_product': sales_by_product[:20],
            'sales_orders': sales_orders[:50],  # Recent orders for table
        })
        return context


class TopSellingProductsReportView(ListView):
    """Top Selling Products Report with time range filtering and CSV download"""
    model = Product
    template_name = 'reports/top_selling_products.html'
    context_object_name = 'top_products'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from request
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        
        # Default to last 30 days if no dates provided
        if start_date_str:
            start_date = parse_date(start_date_str)
        else:
            start_date = (timezone.now() - timedelta(days=30)).date()
            
        if end_date_str:
            end_date = parse_date(end_date_str)
        else:
            end_date = timezone.now().date()
        
        # Get sales data
        sales_orders = SalesOrder.objects.filter(
            order_date__range=[start_date, end_date],
            status='delivered'
        ).prefetch_related('items__product')
        
        # Calculate top selling products
        top_products = []
        for order in sales_orders:
            for item in order.items.all():
                product_name = item.product.name
                product_brand = item.product.brand.name if item.product.brand else "No Brand"
                product_category = item.product.category.name if item.product.category else "No Category"
                existing = next((p for p in top_products if p['product_name'] == product_name), None)
                if existing:
                    existing['total_quantity'] += float(item.quantity)
                    existing['total_value'] += float(item.total_price)
                    existing['order_count'] += 1
                else:
                    top_products.append({
                        'product_name': product_name,
                        'product_brand': product_brand,
                        'product_category': product_category,
                        'total_quantity': float(item.quantity),
                        'total_value': float(item.total_price),
                        'order_count': 1,
                        'average_price': float(item.unit_price),
                    })
        
        # Sort by total value
        top_products.sort(key=lambda x: x['total_value'], reverse=True)
        
        # Calculate summary metrics
        total_products_sold = len(top_products)
        total_quantity_sold = sum(p['total_quantity'] for p in top_products)
        total_value_sold = sum(p['total_value'] for p in top_products)
        average_price = total_value_sold / total_quantity_sold if total_quantity_sold > 0 else 0
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'top_products': top_products[:50],
            'total_products_sold': total_products_sold,
            'total_quantity_sold': total_quantity_sold,
            'total_value_sold': total_value_sold,
            'average_price': average_price,
        })
        return context


class TopSellingCustomersReportView(ListView):
    """Top Selling Customers Report with time range filtering and CSV download"""
    model = Customer
    template_name = 'reports/top_selling_customers.html'
    context_object_name = 'top_customers'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from request
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        
        # Default to last 30 days if no dates provided
        if start_date_str:
            start_date = parse_date(start_date_str)
        else:
            start_date = (timezone.now() - timedelta(days=30)).date()
            
        if end_date_str:
            end_date = parse_date(end_date_str)
        else:
            end_date = timezone.now().date()
        
        # Get sales data
        sales_orders = SalesOrder.objects.filter(
            order_date__range=[start_date, end_date],
            status='delivered'
        ).select_related('customer')
        
        # Calculate top customers
        top_customers = []
        for order in sales_orders:
            customer_name = order.customer.name if order.customer else order.customer_name or "Anonymous"
            customer_type = order.customer.customer_type if order.customer else "Unknown"
            
            existing = next((c for c in top_customers if c['customer_name'] == customer_name), None)
            if existing:
                existing['total_orders'] += 1
                existing['total_value'] += float(order.total_amount)
                existing['last_order_date'] = max(existing['last_order_date'], order.order_date)
            else:
                top_customers.append({
                    'customer_name': customer_name,
                    'customer_type': customer_type,
                    'total_orders': 1,
                    'total_value': float(order.total_amount),
                    'last_order_date': order.order_date,
                    'average_order_value': float(order.total_amount),
                })
        
        # Calculate average order value for each customer
        for customer in top_customers:
            customer['average_order_value'] = customer['total_value'] / customer['total_orders']
        
        # Sort by total value
        top_customers.sort(key=lambda x: x['total_value'], reverse=True)
        
        # Calculate summary metrics
        total_customers = len(top_customers)
        total_orders = sum(c['total_orders'] for c in top_customers)
        total_value = sum(c['total_value'] for c in top_customers)
        average_customer_value = total_value / total_customers if total_customers > 0 else 0
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'top_customers': top_customers[:50],
            'total_customers': total_customers,
            'total_orders': total_orders,
            'total_value': total_value,
            'average_customer_value': average_customer_value,
        })
        return context


class AccountsReceivableReportView(ListView):
    """Accounts Receivable Report with time range filtering and CSV download"""
    model = Customer
    template_name = 'reports/accounts_receivable.html'
    context_object_name = 'receivables_data'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from request
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        
        # Default to last 30 days if no dates provided
        if start_date_str:
            start_date = parse_date(start_date_str)
        else:
            start_date = (timezone.now() - timedelta(days=30)).date()
            
        if end_date_str:
            end_date = parse_date(end_date_str)
        else:
            end_date = timezone.now().date()
        
        # Get customer data
        customers = Customer.objects.filter(is_active=True)
        
        # Calculate receivables
        receivables_data = []
        total_receivables = Decimal('0')
        
        for customer in customers:
            # Get total sales (delivered orders)
            total_sales = SalesOrder.objects.filter(
                customer=customer, 
                status='delivered'
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            
            # Get total payments (simplified - all delivered orders are considered paid)
            total_payments = total_sales
            
            # Calculate outstanding balance
            outstanding_balance = customer.current_balance
            
            # Get recent orders
            recent_orders = SalesOrder.objects.filter(
                customer=customer,
                order_date__range=[start_date, end_date],
                status='delivered'
            ).order_by('-order_date')[:5]
            
            # Get last payment date
            last_payment_date = None
            if recent_orders.exists():
                last_payment_date = recent_orders.first().order_date
            
            receivables_data.append({
                'customer': customer,
                'total_sales': total_sales,
                'total_payments': total_payments,
                'outstanding_balance': outstanding_balance,
                'last_payment_date': last_payment_date,
                'recent_orders': recent_orders,
                'days_since_last_payment': (timezone.now().date() - last_payment_date).days if last_payment_date else None,
            })
            
            total_receivables += outstanding_balance
        
        # Sort by outstanding balance (highest first)
        receivables_data.sort(key=lambda x: x['outstanding_balance'], reverse=True)
        
        # Calculate aging analysis
        aging_analysis = {
            'current': Decimal('0'),      # 0-30 days
            '30_60': Decimal('0'),        # 31-60 days
            '60_90': Decimal('0'),        # 61-90 days
            'over_90': Decimal('0'),      # Over 90 days
        }
        
        for data in receivables_data:
            days = data['days_since_last_payment']
            if days is None:
                aging_analysis['over_90'] += data['outstanding_balance']
            elif days <= 30:
                aging_analysis['current'] += data['outstanding_balance']
            elif days <= 60:
                aging_analysis['30_60'] += data['outstanding_balance']
            elif days <= 90:
                aging_analysis['60_90'] += data['outstanding_balance']
            else:
                aging_analysis['over_90'] += data['outstanding_balance']
        
        # Calculate percentages
        current_percentage = (aging_analysis['current'] / total_receivables * 100) if total_receivables > 0 else 0
        thirty_sixty_percentage = (aging_analysis['30_60'] / total_receivables * 100) if total_receivables > 0 else 0
        sixty_ninety_percentage = (aging_analysis['60_90'] / total_receivables * 100) if total_receivables > 0 else 0
        over_ninety_percentage = (aging_analysis['over_90'] / total_receivables * 100) if total_receivables > 0 else 0
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'receivables_data': receivables_data,
            'total_receivables': total_receivables,
            'aging_analysis': aging_analysis,
            'total_customers': len(receivables_data),
            'current_percentage': current_percentage,
            'thirty_sixty_percentage': thirty_sixty_percentage,
            'sixty_ninety_percentage': sixty_ninety_percentage,
            'over_ninety_percentage': over_ninety_percentage,
        })
        return context


# ==================== CSV DOWNLOAD VIEWS ====================

def download_sales_report_csv(request):
    """Download Sales Report as CSV"""
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if start_date_str:
        start_date = parse_date(start_date_str)
    else:
        start_date = (timezone.now() - timedelta(days=30)).date()
        
    if end_date_str:
        end_date = parse_date(end_date_str)
    else:
        end_date = timezone.now().date()
    
    # Get sales data
    sales_orders = SalesOrder.objects.filter(
        order_date__range=[start_date, end_date],
        status='delivered'
    ).select_related('customer').prefetch_related('items__product')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="sales_report_{start_date}_to_{end_date}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Order Number', 'Customer', 'Order Date', 'Total Amount', 'Status'])
    
    for order in sales_orders:
        customer_name = order.customer.name if order.customer else order.customer_name or "Anonymous"
        writer.writerow([
            order.order_number,
            customer_name,
            order.order_date,
            order.total_amount,
            order.status
        ])
    
    return response


def download_top_products_csv(request):
    """Download Top Selling Products Report as CSV"""
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if start_date_str:
        start_date = parse_date(start_date_str)
    else:
        start_date = (timezone.now() - timedelta(days=30)).date()
        
    if end_date_str:
        end_date = parse_date(end_date_str)
    else:
        end_date = timezone.now().date()
    
    # Get sales data
    sales_orders = SalesOrder.objects.filter(
        order_date__range=[start_date, end_date],
        status='delivered'
    ).prefetch_related('items__product')
    
    # Calculate top products
    top_products = []
    for order in sales_orders:
        for item in order.items.all():
            product_name = item.product.name
            product_brand = item.product.brand.name if item.product.brand else "No Brand"
            product_category = item.product.category.name if item.product.category else "No Category"
            existing = next((p for p in top_products if p['product_name'] == product_name), None)
            if existing:
                existing['total_quantity'] += float(item.quantity)
                existing['total_value'] += float(item.total_price)
                existing['order_count'] += 1
            else:
                top_products.append({
                    'product_name': product_name,
                    'product_brand': product_brand,
                    'product_category': product_category,
                    'total_quantity': float(item.quantity),
                    'total_value': float(item.total_price),
                    'order_count': 1,
                })
    
    top_products.sort(key=lambda x: x['total_value'], reverse=True)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="top_products_{start_date}_to_{end_date}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Product Name', 'Brand', 'Category', 'Total Quantity Sold', 'Total Value', 'Order Count'])
    
    for product in top_products:
        writer.writerow([
            product['product_name'],
            product['product_brand'],
            product['product_category'],
            product['total_quantity'],
            product['total_value'],
            product['order_count']
        ])
    
    return response


def download_top_customers_csv(request):
    """Download Top Selling Customers Report as CSV"""
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if start_date_str:
        start_date = parse_date(start_date_str)
    else:
        start_date = (timezone.now() - timedelta(days=30)).date()
        
    if end_date_str:
        end_date = parse_date(end_date_str)
    else:
        end_date = timezone.now().date()
    
    # Get sales data
    sales_orders = SalesOrder.objects.filter(
        order_date__range=[start_date, end_date],
        status='delivered'
    ).select_related('customer')
    
    # Calculate top customers
    top_customers = []
    for order in sales_orders:
        customer_name = order.customer.name if order.customer else order.customer_name or "Anonymous"
        customer_type = order.customer.customer_type if order.customer else "Unknown"
        
        existing = next((c for c in top_customers if c['customer_name'] == customer_name), None)
        if existing:
            existing['total_orders'] += 1
            existing['total_value'] += float(order.total_amount)
            existing['last_order_date'] = max(existing['last_order_date'], order.order_date)
        else:
            top_customers.append({
                'customer_name': customer_name,
                'customer_type': customer_type,
                'total_orders': 1,
                'total_value': float(order.total_amount),
                'last_order_date': order.order_date,
            })
    
    # Calculate average order value
    for customer in top_customers:
        customer['average_order_value'] = customer['total_value'] / customer['total_orders']
    
    top_customers.sort(key=lambda x: x['total_value'], reverse=True)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="top_customers_{start_date}_to_{end_date}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Customer Name', 'Customer Type', 'Total Orders', 'Total Value', 'Average Order Value', 'Last Order Date'])
    
    for customer in top_customers:
        writer.writerow([
            customer['customer_name'],
            customer['customer_type'],
            customer['total_orders'],
            customer['total_value'],
            customer['average_order_value'],
            customer['last_order_date']
        ])
    
    return response


def download_receivables_csv(request):
    """Download Accounts Receivable Report as CSV"""
    customers = Customer.objects.filter(is_active=True)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="accounts_receivable.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Customer Name', 'Customer Type', 'Total Sales', 'Outstanding Balance', 'Last Order Date'])
    
    for customer in customers:
        total_sales = SalesOrder.objects.filter(
            customer=customer,
            status='delivered'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        last_order = SalesOrder.objects.filter(
            customer=customer,
            status='delivered'
        ).order_by('-order_date').first()
        
        last_order_date = last_order.order_date if last_order else None
        
        writer.writerow([
            customer.name,
            customer.customer_type,
            total_sales,
            customer.current_balance,
            last_order_date
        ])
    
    return response


# ==================== PROFIT & LOSS REPORT ====================

class ProfitLossReportView(ListView):
    """Profit & Loss Report with expense tracking, COGS, and sales revenue"""
    template_name = 'reports/profit_loss_report.html'
    context_object_name = 'profit_loss_data'
    
    def get_queryset(self):
        """Return empty queryset since we don't need a list of objects"""
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from request
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        
        # Default to current month if no dates provided
        if start_date_str:
            start_date = parse_date(start_date_str)
        else:
            start_date = timezone.now().date().replace(day=1)
            
        if end_date_str:
            end_date = parse_date(end_date_str)
        else:
            end_date = timezone.now().date()
        
        # Sales Revenue
        sales_revenue = SalesOrder.objects.filter(
            status='delivered',
            order_date__range=[start_date, end_date]
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Cost of Goods Sold (COGS) - Purchase orders for goods received
        cost_of_goods_sold = PurchaseOrder.objects.filter(
            status='goods-received',
            order_date__range=[start_date, end_date]
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        # Operating Expenses
        operating_expenses = Expense.objects.filter(
            expense_date__range=[start_date, end_date]
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Expenses by Category with percentages
        expenses_by_category = []
        raw_expenses = Expense.objects.filter(
            expense_date__range=[start_date, end_date]
        ).values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total')
        
        for expense in raw_expenses:
            expense_dict = dict(expense)
            expense_dict['percentage'] = (expense['total'] / sales_revenue * 100) if sales_revenue > 0 else 0
            expenses_by_category.append(expense_dict)
        
        # Calculate Gross Profit
        gross_profit = sales_revenue - cost_of_goods_sold
        
        # Calculate Net Profit
        net_profit = gross_profit - operating_expenses
        
        # Calculate percentages
        gross_profit_margin = (gross_profit / sales_revenue * 100) if sales_revenue > 0 else 0
        net_profit_margin = (net_profit / sales_revenue * 100) if sales_revenue > 0 else 0
        cogs_percentage = (cost_of_goods_sold / sales_revenue * 100) if sales_revenue > 0 else 0
        operating_expenses_percentage = (operating_expenses / sales_revenue * 100) if sales_revenue > 0 else 0
        
        # Monthly comparison data
        previous_month_start = (start_date - timedelta(days=1)).replace(day=1)
        previous_month_end = start_date - timedelta(days=1)
        
        previous_sales = SalesOrder.objects.filter(
            status='delivered',
            order_date__range=[previous_month_start, previous_month_end]
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        previous_cogs = PurchaseOrder.objects.filter(
            status='goods-received',
            order_date__range=[previous_month_start, previous_month_end]
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        previous_expenses = Expense.objects.filter(
            expense_date__range=[previous_month_start, previous_month_end]
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        previous_gross_profit = previous_sales - previous_cogs
        previous_net_profit = previous_gross_profit - previous_expenses
        
        # Growth calculations
        sales_growth = ((sales_revenue - previous_sales) / previous_sales * 100) if previous_sales > 0 else 0
        gross_profit_growth = ((gross_profit - previous_gross_profit) / previous_gross_profit * 100) if previous_gross_profit > 0 else 0
        net_profit_growth = ((net_profit - previous_net_profit) / previous_net_profit * 100) if previous_net_profit > 0 else 0
        
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'sales_revenue': sales_revenue,
            'cost_of_goods_sold': cost_of_goods_sold,
            'gross_profit': gross_profit,
            'operating_expenses': operating_expenses,
            'net_profit': net_profit,
            'gross_profit_margin': gross_profit_margin,
            'net_profit_margin': net_profit_margin,
            'cogs_percentage': cogs_percentage,
            'operating_expenses_percentage': operating_expenses_percentage,
            'expenses_by_category': expenses_by_category,
            'previous_sales': previous_sales,
            'previous_cogs': previous_cogs,
            'previous_expenses': previous_expenses,
            'previous_gross_profit': previous_gross_profit,
            'previous_net_profit': previous_net_profit,
            'sales_growth': sales_growth,
            'gross_profit_growth': gross_profit_growth,
            'net_profit_growth': net_profit_growth,
        })
        
        return context


def download_profit_loss_csv(request):
    """Download Profit & Loss report as CSV"""
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if start_date_str:
        start_date = parse_date(start_date_str)
    else:
        start_date = timezone.now().date().replace(day=1)
        
    if end_date_str:
        end_date = parse_date(end_date_str)
    else:
        end_date = timezone.now().date()
    
    # Calculate P&L data
    sales_revenue = SalesOrder.objects.filter(
        status='delivered',
        order_date__range=[start_date, end_date]
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    
    cost_of_goods_sold = PurchaseOrder.objects.filter(
        status='goods-received',
        order_date__range=[start_date, end_date]
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    
    operating_expenses = Expense.objects.filter(
        expense_date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    gross_profit = sales_revenue - cost_of_goods_sold
    net_profit = gross_profit - operating_expenses
    
    # Expenses by category
    expenses_by_category = Expense.objects.filter(
        expense_date__range=[start_date, end_date]
    ).values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="profit_loss_report_{start_date}_to_{end_date}.csv"'
    
    writer = csv.writer(response)
    
    # Header
    writer.writerow(['PROFIT & LOSS STATEMENT'])
    writer.writerow([f'Period: {start_date} to {end_date}'])
    writer.writerow([])
    
    # Revenue section
    writer.writerow(['REVENUE'])
    writer.writerow(['Sales Revenue', sales_revenue])
    writer.writerow([])
    
    # Cost of Goods Sold
    writer.writerow(['COST OF GOODS SOLD'])
    writer.writerow(['Cost of Goods Sold', cost_of_goods_sold])
    writer.writerow(['Gross Profit', gross_profit])
    writer.writerow([])
    
    # Operating Expenses
    writer.writerow(['OPERATING EXPENSES'])
    for expense in expenses_by_category:
        category_name = expense['category__name'] if expense['category__name'] else 'Uncategorized'
        writer.writerow([category_name, expense['total']])
    writer.writerow(['Total Operating Expenses', operating_expenses])
    writer.writerow([])
    
    # Net Profit
    writer.writerow(['NET PROFIT', net_profit])
    
    return response
