from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Sum
from decimal import Decimal
from .models import Customer, CustomerLedger, CustomerCommitment
from sales.models import SalesOrder, SalesInvoice, SalesPayment, SalesReturn


class CustomerListView(ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customers = self.get_queryset()
        
        total_receivable = sum(customer.current_balance for customer in customers if customer.current_balance > 0)
        total_payable = sum(abs(customer.current_balance) for customer in customers if customer.current_balance < 0)
        active_customers = customers.filter(is_active=True).count()
        
        context.update({
            'total_receivable': total_receivable,
            'total_payable': total_payable,
            'active_customers': active_customers,
        })
        return context


class CustomerDetailView(DetailView):
    model = Customer
    template_name = 'customers/customer_detail.html'


class CustomerCreateView(CreateView):
    model = Customer
    template_name = 'customers/customer_form.html'
    fields = '__all__'
    success_url = reverse_lazy('customers:customer_list')


class CustomerUpdateView(UpdateView):
    model = Customer
    template_name = 'customers/customer_form.html'
    fields = '__all__'
    success_url = reverse_lazy('customers:customer_list')


class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'customers/customer_confirm_delete.html'
    success_url = reverse_lazy('customers:customer_list')


class CustomerLedgerListView(ListView):
    model = CustomerLedger
    template_name = 'customers/ledger_list.html'
    context_object_name = 'items'


class CustomerLedgerDetailView(DetailView):
    model = Customer
    template_name = 'customers/customer_ledger_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_object()
        transactions = []
        
        # Sales Orders
        sales_orders = SalesOrder.objects.filter(customer=customer).order_by('-order_date')
        for order in sales_orders:
            transactions.append({
                'date': order.order_date,
                'type': 'Sales Order',
                'reference': f"SO-{order.order_number}",
                'description': f"Sales Order - {order.customer.name}",
                'debit': order.total_amount,
                'credit': Decimal('0.00'),
                'status': order.status,
                'created_at': order.created_at,
            })
        
        # Sales Invoices
        sales_invoices = SalesInvoice.objects.filter(customer=customer).order_by('-invoice_date')
        for invoice in sales_invoices:
            transactions.append({
                'date': invoice.invoice_date,
                'type': 'Sales Invoice',
                'reference': f"INV-{invoice.invoice_number}",
                'description': f"Sales Invoice - {invoice.customer.name}",
                'debit': invoice.total_amount,
                'credit': Decimal('0.00'),
                'status': 'invoiced',
                'created_at': invoice.created_at,
            })
        
        # Sales Payments
        sales_payments = SalesPayment.objects.filter(sales_invoice__customer=customer).order_by('-payment_date')
        for payment in sales_payments:
            transactions.append({
                'date': payment.payment_date,
                'type': 'Payment',
                'reference': payment.reference or f"PAY-{payment.id}",
                'description': f"Payment - {payment.sales_invoice.invoice_number}",
                'debit': Decimal('0.00'),
                'credit': payment.amount,
                'status': 'paid',
                'created_at': payment.created_at,
                'payment_method': payment.payment_method,
            })
        
        # Sales Returns
        sales_returns = SalesReturn.objects.filter(sales_invoice__customer=customer).order_by('-return_date')
        for ret in sales_returns:
            transactions.append({
                'date': ret.return_date,
                'type': 'Return',
                'reference': f"RET-{ret.return_number}",
                'description': f"Sales Return - {ret.sales_invoice.customer.name}",
                'debit': Decimal('0.00'),
                'credit': ret.total_amount,
                'status': ret.status,
                'created_at': ret.created_at,
            })
        
        # Manual Ledger Entries
        ledger_entries = CustomerLedger.objects.filter(customer=customer).order_by('-transaction_date')
        for entry in ledger_entries:
            if entry.transaction_type == 'sale':
                debit = entry.amount
                credit = Decimal('0.00')
            elif entry.transaction_type == 'payment':
                debit = Decimal('0.00')
                credit = entry.amount
            elif entry.transaction_type == 'opening_balance':
                debit = entry.amount if entry.amount > 0 else Decimal('0.00')
                credit = abs(entry.amount) if entry.amount < 0 else Decimal('0.00')
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
                'payment_method': entry.payment_method,
            })
        
        # Sort all transactions by date (newest first)
        transactions.sort(key=lambda x: x['date'], reverse=True)
        
        # Calculate running balance
        running_balance = Decimal('0.00')
        for transaction in reversed(transactions):
            running_balance += transaction['debit'] - transaction['credit']
            transaction['balance'] = running_balance
        
        # Reverse to show newest first
        transactions.reverse()
        
        # Calculate totals
        total_debit = sum(t['debit'] for t in transactions)
        total_credit = sum(t['credit'] for t in transactions)
        current_balance = total_debit - total_credit
        
        # Calculate actual opening balance from ledger entries
        opening_balance_entry = next((t for t in transactions if t['type'] == 'Opening Balance'), None)
        if opening_balance_entry:
            actual_opening_balance = opening_balance_entry['debit'] - opening_balance_entry['credit']
        else:
            actual_opening_balance = Decimal('0.00')
        
        context.update({
            'transactions': transactions,
            'total_debit': total_debit,
            'total_credit': total_credit,
            'opening_balance': actual_opening_balance,
            'current_balance': current_balance,
        })
        
        return context


class CustomerLedgerCreateView(CreateView):
    model = CustomerLedger
    template_name = 'customers/ledger_form.html'
    fields = ['transaction_type', 'amount', 'description', 'reference', 'transaction_date', 'payment_method']
    
    def get_success_url(self):
        return reverse_lazy('customers:customer_ledger_detail', kwargs={'pk': self.kwargs['customer_id']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customer_id'] = self.kwargs['customer_id']
        return context
    
    def form_valid(self, form):
        form.instance.customer_id = self.kwargs['customer_id']
        form.instance.created_by = self.request.user
        return super().form_valid(form)




class CustomerCommitmentListView(ListView):
    model = CustomerCommitment
    template_name = 'customers/commitment_list.html'
    context_object_name = 'items'


class CustomerCommitmentCreateView(CreateView):
    model = CustomerCommitment
    template_name = 'customers/commitment_form.html'
    fields = '__all__'
    success_url = reverse_lazy('customers:commitment_list')


def set_opening_balance(request, pk):
    """Set opening balance for a customer"""
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', 0))
            customer.set_opening_balance(amount, user=request.user)
            messages.success(request, f'Opening balance set to ৳{amount} for {customer.name}')
            return redirect('customers:customer_ledger_detail', pk=customer.pk)
        except (ValueError, TypeError):
            messages.error(request, 'Invalid amount entered')
    
    return render(request, 'customers/set_opening_balance.html', {'customer': customer})
