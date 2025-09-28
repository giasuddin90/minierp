from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import models
from .models import Warehouse, Product, Stock, StockMovement, StockAlert


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
