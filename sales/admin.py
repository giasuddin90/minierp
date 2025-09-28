from django.contrib import admin
from .models import (
    SalesOrder, SalesOrderItem, SalesInvoice, SalesInvoiceItem,
    SalesReturn, SalesReturnItem, SalesPayment
)


class SalesOrderItemInline(admin.TabularInline):
    model = SalesOrderItem
    extra = 1


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'order_date', 'delivery_date', 'status', 'total_amount']
    list_filter = ['status', 'order_date', 'delivery_date', 'created_at']
    search_fields = ['order_number', 'customer__name', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [SalesOrderItemInline]


class SalesInvoiceItemInline(admin.TabularInline):
    model = SalesInvoiceItem
    extra = 1


@admin.register(SalesInvoice)
class SalesInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer', 'invoice_date', 'payment_type', 'total_amount', 'due_amount']
    list_filter = ['payment_type', 'invoice_date', 'created_at']
    search_fields = ['invoice_number', 'customer__name', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [SalesInvoiceItemInline]


class SalesReturnItemInline(admin.TabularInline):
    model = SalesReturnItem
    extra = 1


@admin.register(SalesReturn)
class SalesReturnAdmin(admin.ModelAdmin):
    list_display = ['return_number', 'sales_invoice', 'return_date', 'status', 'total_amount']
    list_filter = ['status', 'return_date', 'created_at']
    search_fields = ['return_number', 'sales_invoice__customer__name', 'reason']
    readonly_fields = ['created_at']
    inlines = [SalesReturnItemInline]


@admin.register(SalesPayment)
class SalesPaymentAdmin(admin.ModelAdmin):
    list_display = ['sales_invoice', 'payment_date', 'payment_method', 'amount', 'created_by']
    list_filter = ['payment_method', 'payment_date', 'created_at']
    search_fields = ['sales_invoice__invoice_number', 'reference', 'notes']
    readonly_fields = ['created_at']
