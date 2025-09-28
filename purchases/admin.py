from django.contrib import admin
from .models import (
    PurchaseOrder, PurchaseOrderItem, GoodsReceipt, GoodsReceiptItem,
    PurchaseInvoice, PurchaseInvoiceItem, PurchaseReturn, PurchaseReturnItem, PurchasePayment
)


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'supplier', 'order_date', 'expected_date', 'status', 'total_amount']
    list_filter = ['status', 'order_date', 'expected_date', 'created_at']
    search_fields = ['order_number', 'supplier__name', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PurchaseOrderItemInline]


class GoodsReceiptItemInline(admin.TabularInline):
    model = GoodsReceiptItem
    extra = 1


@admin.register(GoodsReceipt)
class GoodsReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'purchase_order', 'receipt_date', 'status', 'total_amount']
    list_filter = ['status', 'receipt_date', 'created_at']
    search_fields = ['receipt_number', 'purchase_order__supplier__name', 'notes']
    readonly_fields = ['created_at']
    inlines = [GoodsReceiptItemInline]


class PurchaseInvoiceItemInline(admin.TabularInline):
    model = PurchaseInvoiceItem
    extra = 1


@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'supplier', 'invoice_date', 'payment_type', 'total_amount', 'due_amount']
    list_filter = ['payment_type', 'invoice_date', 'created_at']
    search_fields = ['invoice_number', 'supplier__name', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PurchaseInvoiceItemInline]


class PurchaseReturnItemInline(admin.TabularInline):
    model = PurchaseReturnItem
    extra = 1


@admin.register(PurchaseReturn)
class PurchaseReturnAdmin(admin.ModelAdmin):
    list_display = ['return_number', 'purchase_invoice', 'return_date', 'status', 'total_amount']
    list_filter = ['status', 'return_date', 'created_at']
    search_fields = ['return_number', 'purchase_invoice__supplier__name', 'reason']
    readonly_fields = ['created_at']
    inlines = [PurchaseReturnItemInline]


@admin.register(PurchasePayment)
class PurchasePaymentAdmin(admin.ModelAdmin):
    list_display = ['purchase_invoice', 'payment_date', 'payment_method', 'amount', 'created_by']
    list_filter = ['payment_method', 'payment_date', 'created_at']
    search_fields = ['purchase_invoice__invoice_number', 'reference', 'notes']
    readonly_fields = ['created_at']
