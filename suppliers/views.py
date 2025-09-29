from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Sum
from django.utils import timezone
from decimal import Decimal
from .models import Supplier, SupplierLedger, SupplierCommission
from purchases.models import PurchaseOrder, PurchaseInvoice, PurchasePayment, PurchaseReturn


class SupplierListView(ListView):
    model = Supplier
    template_name = 'suppliers/supplier_list.html'
    context_object_name = 'suppliers'


class SupplierDetailView(DetailView):
    model = Supplier
    template_name = 'suppliers/supplier_detail.html'


class SupplierCreateView(CreateView):
    model = Supplier
    template_name = 'suppliers/supplier_form.html'
    fields = '__all__'
    success_url = reverse_lazy('suppliers:supplier_list')


class SupplierUpdateView(UpdateView):
    model = Supplier
    template_name = 'suppliers/supplier_form.html'
    fields = '__all__'
    success_url = reverse_lazy('suppliers:supplier_list')


class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'suppliers/supplier_confirm_delete.html'
    success_url = reverse_lazy('suppliers:supplier_list')


class SupplierLedgerListView(ListView):
    model = SupplierLedger
    template_name = 'suppliers/ledger_list.html'
    context_object_name = 'items'


class SupplierLedgerCreateView(CreateView):
    model = SupplierLedger
    template_name = 'suppliers/ledger_form.html'
    fields = ['transaction_type', 'amount', 'description', 'reference', 'transaction_date']
    
    def get_success_url(self):
        return reverse_lazy('suppliers:supplier_ledger_detail', kwargs={'pk': self.kwargs['supplier_id']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['supplier_id'] = self.kwargs['supplier_id']
        return context
    
    def form_valid(self, form):
        form.instance.supplier_id = self.kwargs['supplier_id']
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class SupplierCommissionListView(ListView):
    model = SupplierCommission
    template_name = 'suppliers/commission_list.html'
    context_object_name = 'items'


class SupplierCommissionCreateView(CreateView):
    model = SupplierCommission
    template_name = 'suppliers/commission_form.html'
    fields = '__all__'
    success_url = reverse_lazy('suppliers:commission_list')


class SupplierLedgerDetailView(DetailView):
    model = Supplier
    template_name = 'suppliers/supplier_ledger_detail.html'
    context_object_name = 'supplier'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplier = self.get_object()
        
        # Get all transactions for this supplier
        transactions = []
        
        # Purchase Orders
        purchase_orders = PurchaseOrder.objects.filter(supplier=supplier).order_by('-order_date')
        for po in purchase_orders:
            transactions.append({
                'date': po.order_date,
                'type': 'Purchase Order',
                'reference': f"PO-{po.order_number}",
                'description': f"Purchase Order - {po.supplier.name}",
                'debit': po.total_amount,
                'credit': Decimal('0.00'),
                'status': po.status,
                'created_at': po.created_at,
            })
        
        # Purchase Invoices
        purchase_invoices = PurchaseInvoice.objects.filter(supplier=supplier).order_by('-invoice_date')
        for inv in purchase_invoices:
            transactions.append({
                'date': inv.invoice_date,
                'type': 'Purchase Invoice',
                'reference': f"PINV-{inv.invoice_number}",
                'description': f"Purchase Invoice - {inv.supplier.name}",
                'debit': inv.total_amount,
                'credit': Decimal('0.00'),
                'status': 'invoiced',
                'created_at': inv.created_at,
            })
        
        # Purchase Payments
        purchase_payments = PurchasePayment.objects.filter(purchase_invoice__supplier=supplier).order_by('-payment_date')
        for payment in purchase_payments:
            transactions.append({
                'date': payment.payment_date,
                'type': 'Payment',
                'reference': payment.reference or f"PAY-{payment.id}",
                'description': f"Payment - {payment.purchase_invoice.invoice_number}",
                'debit': Decimal('0.00'),
                'credit': payment.amount,
                'status': 'paid',
                'created_at': payment.created_at,
            })
        
        # Purchase Returns
        purchase_returns = PurchaseReturn.objects.filter(purchase_invoice__supplier=supplier).order_by('-return_date')
        for ret in purchase_returns:
            transactions.append({
                'date': ret.return_date,
                'type': 'Return',
                'reference': f"PRET-{ret.return_number}",
                'description': f"Purchase Return - {ret.purchase_invoice.supplier.name}",
                'debit': Decimal('0.00'),
                'credit': ret.total_amount,
                'status': ret.status,
                'created_at': ret.created_at,
            })
        
        # Manual Ledger Entries
        ledger_entries = SupplierLedger.objects.filter(supplier=supplier).order_by('-transaction_date')
        for entry in ledger_entries:
            if entry.transaction_type == 'purchase':
                debit = entry.amount
                credit = Decimal('0.00')
            elif entry.transaction_type == 'payment':
                debit = Decimal('0.00')
                credit = entry.amount
            else:
                debit = entry.amount if entry.amount > 0 else Decimal('0.00')
                credit = abs(entry.amount) if entry.amount < 0 else Decimal('0.00')
            
            transactions.append({
                'date': entry.transaction_date.date(),
                'type': entry.get_transaction_type_display(),
                'reference': entry.reference or f"LED-{entry.id}",
                'description': entry.description,
                'debit': debit,
                'credit': credit,
                'status': 'manual',
                'created_at': entry.created_at,
            })
        
        # Sort all transactions by date (newest first)
        transactions.sort(key=lambda x: x['date'], reverse=True)
        
        # Calculate running balance
        running_balance = supplier.opening_balance
        for transaction in reversed(transactions):  # Process oldest first for balance calculation
            running_balance += transaction['debit'] - transaction['credit']
            transaction['balance'] = running_balance
        
        # Reverse to show newest first
        transactions.reverse()
        
        # Calculate totals
        total_debit = sum(t['debit'] for t in transactions)
        total_credit = sum(t['credit'] for t in transactions)
        current_balance = supplier.opening_balance + total_debit - total_credit
        
        context.update({
            'transactions': transactions,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'opening_balance': supplier.opening_balance,
            'current_balance': current_balance,
        })
        
        return context
