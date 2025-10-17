from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Sum, Count
from customers.models import Customer
from suppliers.models import Supplier
from stock.models import Product, Stock, StockAlert
from sales.models import SalesOrder, SalesInvoice
from purchases.models import PurchaseOrder, PurchaseInvoice


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get statistics for dashboard
        context['total_customers'] = Customer.objects.count()
        context['total_suppliers'] = Supplier.objects.count()
        context['total_products'] = Product.objects.count()
        
        # Calculate total sales
        total_sales = SalesInvoice.objects.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        context['total_sales'] = total_sales
        
        # Get recent sales orders
        context['recent_orders'] = SalesOrder.objects.select_related('customer').order_by('-created_at')[:5]
        
        # Get low stock alerts
        context['low_stock_alerts'] = StockAlert.objects.filter(
            is_active=True
        ).select_related('product')[:5]
        
        
        return context


@login_required
def dashboard_redirect(request):
    """Redirect to dashboard after login"""
    return render(request, 'dashboard.html', {
        'total_customers': Customer.objects.count(),
        'total_suppliers': Supplier.objects.count(),
        'total_products': Product.objects.count(),
        'total_sales': SalesInvoice.objects.aggregate(total=Sum('total_amount'))['total'] or 0,
        'recent_orders': SalesOrder.objects.select_related('customer').order_by('-created_at')[:5],
        'low_stock_alerts': StockAlert.objects.filter(is_active=True).select_related('product')[:5],
    })
