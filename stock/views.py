from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import models
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta
from .models import ProductCategory, ProductBrand, UnitType, Product, Stock, StockAlert
from .forms import (
    ProductForm, ProductCategoryForm, ProductBrandForm, UnitTypeForm, StockForm, 
    StockAdjustmentForm, StockAlertForm, ProductSearchForm, StockReportForm
)
from sales.models import SalesOrderItem
from purchases.models import PurchaseOrderItem






class ProductListView(ListView):
    model = Product
    template_name = 'stock/product_list.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Product.objects.select_related('category', 'brand').all()
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter by brand
        brand = self.request.GET.get('brand')
        if brand:
            queryset = queryset.filter(brand_id=brand)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # Search by name
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ProductCategory.objects.filter(is_active=True).order_by('name')
        context['brands'] = ProductBrand.objects.filter(is_active=True).order_by('name')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_brand'] = self.request.GET.get('brand', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_search'] = self.request.GET.get('search', '')
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'stock/product_detail.html'


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'stock/product_form.html'
    success_url = reverse_lazy('stock:product_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ProductCategory.objects.filter(is_active=True)
        context['brands'] = ProductBrand.objects.filter(is_active=True)
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Product "{form.instance.name}" created successfully.')
        return super().form_valid(form)


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'stock/product_form.html'
    success_url = reverse_lazy('stock:product_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ProductCategory.objects.filter(is_active=True)
        context['brands'] = ProductBrand.objects.filter(is_active=True)
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Product "{form.instance.name}" updated successfully.')
        return super().form_valid(form)


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
    form_class = StockForm
    template_name = 'stock/stock_form.html'
    success_url = reverse_lazy('stock:stock_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Stock updated successfully for {form.instance.product.name}.')
        return super().form_valid(form)




# Category Management Views
class ProductCategoryListView(ListView):
    model = ProductCategory
    template_name = 'stock/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ProductCategory.objects.all()
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # Search by name
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', '')
        context['current_search'] = self.request.GET.get('search', '')
        return context


class ProductCategoryCreateView(CreateView):
    model = ProductCategory
    form_class = ProductCategoryForm
    template_name = 'stock/category_form.html'
    success_url = reverse_lazy('stock:category_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" created successfully.')
        return super().form_valid(form)


class ProductCategoryUpdateView(UpdateView):
    model = ProductCategory
    form_class = ProductCategoryForm
    template_name = 'stock/category_form.html'
    success_url = reverse_lazy('stock:category_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" updated successfully.')
        return super().form_valid(form)


class ProductCategoryDeleteView(DeleteView):
    model = ProductCategory
    template_name = 'stock/category_confirm_delete.html'
    success_url = reverse_lazy('stock:category_list')


# Brand Management Views
class ProductBrandListView(ListView):
    model = ProductBrand
    template_name = 'stock/brand_list.html'
    context_object_name = 'brands'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ProductBrand.objects.all()
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # Search by name
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', '')
        context['current_search'] = self.request.GET.get('search', '')
        return context


class ProductBrandCreateView(CreateView):
    model = ProductBrand
    form_class = ProductBrandForm
    template_name = 'stock/brand_form.html'
    success_url = reverse_lazy('stock:brand_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Brand "{form.instance.name}" created successfully.')
        return super().form_valid(form)


class ProductBrandUpdateView(UpdateView):
    model = ProductBrand
    form_class = ProductBrandForm
    template_name = 'stock/brand_form.html'
    success_url = reverse_lazy('stock:brand_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Brand "{form.instance.name}" updated successfully.')
        return super().form_valid(form)


class ProductBrandDeleteView(DeleteView):
    model = ProductBrand
    template_name = 'stock/brand_confirm_delete.html'
    success_url = reverse_lazy('stock:brand_list')


# Stock Adjustment View
def stock_adjustment(request, pk):
    """Handle stock adjustments"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            adjustment_type = form.cleaned_data['adjustment_type']
            quantity = form.cleaned_data['quantity']
            unit_cost = form.cleaned_data['unit_cost']
            reference = form.cleaned_data['reference']
            description = form.cleaned_data['description']
            
            # Update stock using the model method
            stock = Stock.update_stock(
                product=product,
                quantity_change=quantity,
                unit_cost=unit_cost,
                movement_type=adjustment_type,
                reference=reference,
                description=description,
                user=request.user
            )
            
            messages.success(
                request, 
                f'Stock {adjustment_type} completed for {product.name}. '
                f'New quantity: {stock.quantity}'
            )
            return redirect('stock:product_detail', pk=product.pk)
    else:
        form = StockAdjustmentForm()
    
    return render(request, 'stock/stock_adjustment.html', {
        'product': product,
        'form': form
    })


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
        return Product.objects.filter(is_active=True).prefetch_related('stock_set')
    
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
            
            # In simplified model, only sales orders are tracked
            total_sold = sold_from_orders
            
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
            })
        
        # Get recent stock movements - removed since StockMovement model is removed
        recent_movements = []
        
        # Get low stock alerts
        low_stock_alerts = StockAlert.objects.filter(
            is_active=True
        ).select_related('product')
        
        # Get top selling products (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        top_selling = SalesOrderItem.objects.filter(
            sales_order__order_date__gte=thirty_days_ago,
            sales_order__status='delivered'
        ).values('product__name').annotate(
            total_sold=Sum('quantity')
        ).order_by('-total_sold')[:5]
        
        # Warehouse summary removed since warehouses are not used
        warehouse_summary = []
        
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


# UnitType Management Views
class UnitTypeListView(ListView):
    model = UnitType
    template_name = 'stock/unittype_list.html'
    context_object_name = 'unit_types'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = UnitType.objects.all()
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # Search by name or code
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(code__icontains=search)
            )
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', '')
        context['current_search'] = self.request.GET.get('search', '')
        return context


class UnitTypeCreateView(CreateView):
    model = UnitType
    form_class = UnitTypeForm
    template_name = 'stock/unittype_form.html'
    success_url = reverse_lazy('stock:unittype_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Unit Type "{form.instance.name}" created successfully.')
        return super().form_valid(form)


class UnitTypeUpdateView(UpdateView):
    model = UnitType
    form_class = UnitTypeForm
    template_name = 'stock/unittype_form.html'
    success_url = reverse_lazy('stock:unittype_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Unit Type "{form.instance.name}" updated successfully.')
        return super().form_valid(form)


class UnitTypeDeleteView(DeleteView):
    model = UnitType
    template_name = 'stock/unittype_confirm_delete.html'
    success_url = reverse_lazy('stock:unittype_list')
    
    def delete(self, request, *args, **kwargs):
        unit_type = self.get_object()
        messages.success(request, f'Unit Type "{unit_type.name}" deleted successfully.')
        return super().delete(request, *args, **kwargs)
