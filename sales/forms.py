from django import forms
from django.forms import inlineformset_factory
from decimal import Decimal, ROUND_HALF_UP
from .models import SalesOrder, SalesOrderItem
from customers.models import Customer
from stock.models import Product, ProductCategory, ProductBrand


class RoundedDecimalField(forms.DecimalField):
    """Custom DecimalField that rounds input to 2 decimal places"""
    
    def to_python(self, value):
        if value is None or value == '':
            return None
        
        # Convert to Decimal and round to 2 decimal places
        decimal_value = Decimal(str(value))
        rounded_value = decimal_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return rounded_value


class SalesOrderForm(forms.ModelForm):
    """Form for creating and editing sales orders"""
    
    class Meta:
        model = SalesOrder
        fields = ['sales_type', 'customer', 'customer_name', 'order_date', 'delivery_date', 'status', 'notes']
        widgets = {
            'sales_type': forms.Select(attrs={'class': 'form-select'}),
            'order_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'delivery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter customer name for instant sales'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'sales_type': 'Sales Type',
            'customer': 'Customer',
            'customer_name': 'Customer Name',
            'order_date': 'Order Date',
            'delivery_date': 'Delivery Date',
            'status': 'Status',
            'notes': 'Notes',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.filter(is_active=True)
        self.fields['status'].choices = [
            ('order', 'Order'),
            ('delivered', 'Delivered'),
            ('cancel', 'Cancel'),
        ]
        
        # Add JavaScript for conditional field display
        self.fields['sales_type'].widget.attrs.update({
            'onchange': 'toggleCustomerFields()'
        })
        
        # Set default status
        if not self.instance.pk:
            self.fields['status'].initial = 'order'
    
    def clean(self):
        cleaned_data = super().clean()
        sales_type = cleaned_data.get('sales_type')
        customer = cleaned_data.get('customer')
        customer_name = cleaned_data.get('customer_name')
        delivery_date = cleaned_data.get('delivery_date')
        
        # For instant sales, customer is optional but customer_name is required
        if sales_type == 'instant':
            if not customer and not customer_name:
                raise forms.ValidationError("For instant sales, either select a customer or enter a customer name.")
            # Delivery date is not required for instant sales
            if delivery_date:
                cleaned_data['delivery_date'] = None
        
        # For regular sales, customer is required
        elif sales_type == 'regular':
            if not customer:
                raise forms.ValidationError("Customer is required for regular sales.")
        
        return cleaned_data


class InstantSalesForm(forms.ModelForm):
    """Form specifically for instant sales"""
    
    class Meta:
        model = SalesOrder
        fields = ['customer_name', 'order_date', 'notes', 'sales_type']
        widgets = {
            'order_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter customer name (optional)'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sales_type': forms.HiddenInput(),
        }
        labels = {
            'customer_name': 'Customer Name',
            'order_date': 'Sale Date',
            'notes': 'Notes',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values for instant sales
        if not self.instance.pk:
            from django.utils import timezone
            self.fields['order_date'].initial = timezone.now().date()
            self.fields['sales_type'].initial = 'instant'
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.sales_type = 'instant'
        instance.status = 'delivered'  # Instant sales are immediately delivered
        if commit:
            instance.save()
        return instance


class SalesOrderItemForm(forms.ModelForm):
    """Form for sales order items"""
    
    # Override fields to handle decimal places properly
    quantity = RoundedDecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control quantity-input', 'step': '0.01', 'min': '0'}),
        label='Quantity'
    )
    
    unit_price = RoundedDecimalField(
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control price-input', 'step': '0.01', 'min': '0'}),
        label='Unit Price'
    )
    
    total_price = RoundedDecimalField(
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control total-input', 'step': '0.01', 'readonly': True}),
        label='Total Price',
        required=False
    )
    
    class Meta:
        model = SalesOrderItem
        fields = ['product', 'quantity', 'unit_price', 'total_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select product-select'}),
        }
        labels = {
            'product': 'Product',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True).select_related('category', 'brand')
        
        # Add data attributes for JavaScript filtering
        if 'product' in self.fields:
            self.fields['product'].widget.attrs.update({
                'class': 'form-select product-select',
            })

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None:
            if quantity <= 0:
                raise forms.ValidationError('Quantity must be greater than 0.')
            # Round to 2 decimal places
            quantity = round(quantity, 2)
        return quantity

    def clean_unit_price(self):
        unit_price = self.cleaned_data.get('unit_price')
        if unit_price is not None:
            if unit_price <= 0:
                raise forms.ValidationError('Unit price must be greater than 0.')
            # Round to 2 decimal places
            unit_price = round(unit_price, 2)
        return unit_price

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity', 0)
        unit_price = cleaned_data.get('unit_price', 0)
        
        # Calculate total price and round to 2 decimal places
        if quantity and unit_price:
            total = quantity * unit_price
            cleaned_data['total_price'] = round(total, 2)
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Calculate total price and round to 2 decimal places
        quantity = self.cleaned_data.get('quantity', 0)
        unit_price = self.cleaned_data.get('unit_price', 0)
        instance.total_price = round(quantity * unit_price, 2)
        
        if commit:
            instance.save()
        return instance


# Inline formset for sales order items
SalesOrderItemFormSet = inlineformset_factory(
    SalesOrder,
    SalesOrderItem,
    form=SalesOrderItemForm,
    fields=['product', 'quantity', 'unit_price', 'total_price'],
    extra=0,  # No extra forms by default
    can_delete=True,
    min_num=0,  # Allow zero items initially
    validate_min=False,
)

# Custom formset class to handle creation without instance
class SalesOrderItemFormSetCustom(SalesOrderItemFormSet):
    def __init__(self, *args, **kwargs):
        # If no instance is provided, add one extra form for new orders
        if 'instance' not in kwargs or kwargs['instance'] is None:
            self.extra = 1
        else:
            # No extra forms for existing orders
            self.extra = 0
        super().__init__(*args, **kwargs)


class SalesOrderSearchForm(forms.Form):
    """Form for searching sales orders"""
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by order number, customer, or status...'
        })
    )
