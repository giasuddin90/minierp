from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import models
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Warehouse, Product, Stock, StockMovement, StockAlert
from sales.models import SalesOrderItem, SalesInvoiceItem
from purchases.models import PurchaseOrderItem


class WarehouseListView(ListView):
    model = Warehouse
    template_name = 'stock/warehouse_list.html'
    context_object_name = 'warehouses'


class WarehouseDetailView(DetailView):
    model = Warehouse
    template_name = 'stock/warehouse_detail.html'


class WarehouseCreateView(CreateView):
    model = Warehouse
    template_name = 'stock/warehouse_form.html'
    fields = '__all__'
    success_url = reverse_lazy('stock:warehouse_list')


class WarehouseUpdateView(UpdateView):
    model = Warehouse
    template_name = 'stock/warehouse_form.html'
    fields = '__all__'
    success_url = reverse_lazy('stock:warehouse_list')


class WarehouseDeleteView(DeleteView):
    model = Warehouse
    template_name = 'stock/warehouse_confirm_delete.html'
    success_url = reverse_lazy('stock:warehouse_list')




class ProductListView(ListView):
    model = Product
    template_name = 'stock/product_list.html'
    context_object_name = 'products'


class ProductDetailView(DetailView):
    model = Product
    template_name = 'stock/product_detail.html'


class ProductCreateView(CreateView):
    model = Product
    template_name = 'stock/product_form.html'
    fields = '__all__'
    success_url = reverse_lazy('stock:product_list')


class ProductUpdateView(UpdateView):
    model = Product
    template_name = 'stock/product_form.html'
    fields = '__all__'
    success_url = reverse_lazy('stock:product_list')


class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'stock/product_confirm_delete.html'
    success_url = reverse_lazy('stock:product_list')


class StockListView(ListView):
    model = Stock
    template_name = 'stock/stock_list.html'
    context_object_name = 'stocks'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stocks = self.get_queryset()
        
        # Calculate summary statistics
        total_products = stocks.count()
        in_stock = stocks.filter(quantity__gt=0).count()
        low_stock = stocks.filter(quantity__gt=0, quantity__lte=models.F('product__min_stock_level')).count()
        out_of_stock = stocks.filter(quantity__lte=0).count()
        
        context.update({
            'total_products': total_products,
            'in_stock': in_stock,
            'low_stock': low_stock,
            'out_of_stock': out_of_stock,
        })
        
        return context


class StockDetailView(DetailView):
    model = Stock
    template_name = 'stock/stock_detail.html'


class StockUpdateView(UpdateView):
    model = Stock
    template_name = 'stock/stock_form.html'
    fields = '__all__'
    success_url = reverse_lazy('stock:stock_list')


class StockMovementListView(ListView):
    model = StockMovement
    template_name = 'stock/movement_list.html'
    context_object_name = 'movements'


class StockMovementCreateView(CreateView):
    model = StockMovement
    template_name = 'stock/movement_form.html'
    fields = '__all__'
    success_url = reverse_lazy('stock:movement_list')


class StockAlertListView(ListView):
    model = StockAlert
    template_name = 'stock/alert_list.html'
    context_object_name = 'alerts'


class StockReportView(ListView):
    model = Stock
    template_name = 'stock/stock_report.html'
    context_object_name = 'reports'


class StockValuationReportView(ListView):
    model = Stock
    template_name = 'stock/stock_valuation_report.html'
    context_object_name = 'reports'


class InventoryDashboardView(ListView):
    """Comprehensive inventory dashboard showing real inventory scenarios"""
    model = Product
    template_name = 'stock/inventory_dashboard.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True).prefetch_related('stock_set', 'stockmovement_set')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all products with their stock information
        products = self.get_queryset()
        
        # Calculate inventory statistics
        inventory_data = []
        total_products = 0
        in_stock_products = 0
        low_stock_products = 0
        out_of_stock_products = 0
        total_stock_value = 0
        
        for product in products:
            # Get stock information for this product
            stocks = Stock.objects.filter(product=product)
            total_quantity = stocks.aggregate(total=Sum('quantity'))['total'] or 0
            total_value = sum(stock.total_value for stock in stocks)
            
            # Calculate quantities sold (from sales orders and invoices)
            sold_from_orders = SalesOrderItem.objects.filter(
                product=product,
                sales_order__status='delivered'
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            sold_from_invoices = SalesInvoiceItem.objects.filter(
                product=product
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            total_sold = sold_from_orders + sold_from_invoices
            
            # Calculate quantities purchased
            purchased = PurchaseOrderItem.objects.filter(
                product=product
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            # Determine stock status
            if total_quantity <= 0:
                stock_status = 'out_of_stock'
                out_of_stock_products += 1
            elif total_quantity <= product.min_stock_level:
                stock_status = 'low_stock'
                low_stock_products += 1
            else:
                stock_status = 'in_stock'
                in_stock_products += 1
            
            total_products += 1
            total_stock_value += total_value
            
            inventory_data.append({
                'product': product,
                'total_quantity': total_quantity,
                'total_value': total_value,
                'total_sold': total_sold,
                'total_purchased': purchased,
                'stock_status': stock_status,
                'min_stock_level': product.min_stock_level,
                'stocks': stocks,
                'last_movement': StockMovement.objects.filter(product=product).order_by('-movement_date').first()
            })
        
        # Get recent stock movements
        recent_movements = StockMovement.objects.select_related(
            'product', 'warehouse', 'created_by'
        ).order_by('-movement_date')[:10]
        
        # Get low stock alerts
        low_stock_alerts = StockAlert.objects.filter(
            is_active=True
        ).select_related('product', 'warehouse')
        
        # Get top selling products (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        top_selling = SalesOrderItem.objects.filter(
            sales_order__order_date__gte=thirty_days_ago,
            sales_order__status='delivered'
        ).values('product__name').annotate(
            total_sold=Sum('quantity')
        ).order_by('-total_sold')[:5]
        
        # Get warehouse-wise stock summary
        warehouse_summary = []
        for warehouse in Warehouse.objects.filter(is_active=True):
            warehouse_stocks = Stock.objects.filter(warehouse=warehouse)
            warehouse_total_quantity = warehouse_stocks.aggregate(total=Sum('quantity'))['total'] or 0
            warehouse_total_value = sum(stock.total_value for stock in warehouse_stocks)
            warehouse_products = warehouse_stocks.count()
            
            warehouse_summary.append({
                'warehouse': warehouse,
                'total_quantity': warehouse_total_quantity,
                'total_value': warehouse_total_value,
                'product_count': warehouse_products
            })
        
        context.update({
            'inventory_data': inventory_data,
            'total_products': total_products,
            'in_stock_products': in_stock_products,
            'low_stock_products': low_stock_products,
            'out_of_stock_products': out_of_stock_products,
            'total_stock_value': total_stock_value,
            'recent_movements': recent_movements,
            'low_stock_alerts': low_stock_alerts,
            'top_selling': top_selling,
            'warehouse_summary': warehouse_summary,
        })
        
        return context
