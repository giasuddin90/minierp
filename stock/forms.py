from django import forms
from django.utils import timezone
from .models import Product, ProductCategory, ProductBrand, Stock, StockAlert


class ProductCategoryForm(forms.ModelForm):
    """Form for creating and editing product categories"""
    
    class Meta:
        model = ProductCategory
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter category description'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'name': 'Category Name',
            'description': 'Description',
            'is_active': 'Active'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True


class ProductBrandForm(forms.ModelForm):
    """Form for creating and editing product brands"""
    
    class Meta:
        model = ProductBrand
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter brand name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter brand description'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'name': 'Brand Name',
            'description': 'Description',
            'is_active': 'Active'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True


class ProductForm(forms.ModelForm):
    """Form for creating and editing products"""
    
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'brand', 'unit_type', 'description',
            'cost_price', 'selling_price', 'min_stock_level', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'brand': forms.Select(attrs={
                'class': 'form-select'
            }),
            'unit_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter product description'
            }),
            'cost_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'selling_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'min_stock_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'name': 'Product Name',
            'category': 'Category',
            'brand': 'Brand',
            'unit_type': 'Unit Type',
            'description': 'Description',
            'cost_price': 'Cost Price',
            'selling_price': 'Selling Price',
            'min_stock_level': 'Minimum Stock Level',
            'is_active': 'Active'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make name field required
        self.fields['name'].required = True
        
        # Filter active categories and brands
        self.fields['category'].queryset = ProductCategory.objects.filter(is_active=True).order_by('name')
        self.fields['brand'].queryset = ProductBrand.objects.filter(is_active=True).order_by('name')
        
        # Add empty option for category and brand
        self.fields['category'].empty_label = "Select Category (Optional)"
        self.fields['brand'].empty_label = "Select Brand (Optional)"
    
    def clean_selling_price(self):
        """Validate selling price"""
        selling_price = self.cleaned_data.get('selling_price')
        cost_price = self.cleaned_data.get('cost_price')
        
        if selling_price and cost_price and selling_price < cost_price:
            raise forms.ValidationError("Selling price cannot be less than cost price.")
        
        return selling_price
    
    def clean_min_stock_level(self):
        """Validate minimum stock level"""
        min_stock_level = self.cleaned_data.get('min_stock_level')
        
        if min_stock_level is not None and min_stock_level < 0:
            raise forms.ValidationError("Minimum stock level cannot be negative.")
        
        return min_stock_level


class StockForm(forms.ModelForm):
    """Form for updating stock quantities"""
    
    class Meta:
        model = Stock
        fields = ['quantity', 'unit_cost']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'unit_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            })
        }
        labels = {
            'quantity': 'Stock Quantity',
            'unit_cost': 'Unit Cost'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantity'].required = True
        self.fields['unit_cost'].required = True
    
    def clean_quantity(self):
        """Validate quantity"""
        quantity = self.cleaned_data.get('quantity')
        
        if quantity is not None and quantity < 0:
            raise forms.ValidationError("Stock quantity cannot be negative.")
        
        return quantity
    
    def clean_unit_cost(self):
        """Validate unit cost"""
        unit_cost = self.cleaned_data.get('unit_cost')
        
        if unit_cost is not None and unit_cost < 0:
            raise forms.ValidationError("Unit cost cannot be negative.")
        
        return unit_cost


class StockAdjustmentForm(forms.Form):
    """Form for stock adjustments"""
    
    ADJUSTMENT_TYPES = [
        ('inward', 'Stock Inward'),
        ('outward', 'Stock Outward'),
        ('adjustment', 'Stock Adjustment'),
    ]
    
    adjustment_type = forms.ChoiceField(
        choices=ADJUSTMENT_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Adjustment Type'
    )
    
    quantity = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'placeholder': '0.00'
        }),
        label='Quantity'
    )
    
    unit_cost = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'placeholder': '0.00'
        }),
        label='Unit Cost (Optional)'
    )
    
    reference = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter reference number'
        }),
        label='Reference'
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter adjustment description'
        }),
        label='Description'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['adjustment_type'].required = True
        self.fields['quantity'].required = True
        self.fields['description'].required = True
    
    def clean_quantity(self):
        """Validate quantity"""
        quantity = self.cleaned_data.get('quantity')
        
        if quantity is not None and quantity < 0:
            raise forms.ValidationError("Quantity cannot be negative.")
        
        return quantity
    
    def clean_unit_cost(self):
        """Validate unit cost"""
        unit_cost = self.cleaned_data.get('unit_cost')
        
        if unit_cost is not None and unit_cost < 0:
            raise forms.ValidationError("Unit cost cannot be negative.")
        
        return unit_cost


class StockAlertForm(forms.ModelForm):
    """Form for managing stock alerts"""
    
    class Meta:
        model = StockAlert
        fields = ['current_quantity', 'min_quantity', 'is_active']
        widgets = {
            'current_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'min_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'current_quantity': 'Current Quantity',
            'min_quantity': 'Minimum Quantity',
            'is_active': 'Active Alert'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['current_quantity'].required = True
        self.fields['min_quantity'].required = True
    
    def clean_current_quantity(self):
        """Validate current quantity"""
        current_quantity = self.cleaned_data.get('current_quantity')
        
        if current_quantity is not None and current_quantity < 0:
            raise forms.ValidationError("Current quantity cannot be negative.")
        
        return current_quantity
    
    def clean_min_quantity(self):
        """Validate minimum quantity"""
        min_quantity = self.cleaned_data.get('min_quantity')
        
        if min_quantity is not None and min_quantity < 0:
            raise forms.ValidationError("Minimum quantity cannot be negative.")
        
        return min_quantity


class ProductSearchForm(forms.Form):
    """Form for product search and filtering"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search products...'
        }),
        label='Search'
    )
    
    category = forms.ModelChoiceField(
        queryset=ProductCategory.objects.filter(is_active=True).order_by('name'),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Category'
    )
    
    brand = forms.ModelChoiceField(
        queryset=ProductBrand.objects.filter(is_active=True).order_by('name'),
        required=False,
        empty_label="All Brands",
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Brand'
    )
    
    status = forms.ChoiceField(
        choices=[
            ('', 'All Status'),
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Status'
    )
    
    unit_type = forms.ChoiceField(
        choices=[('', 'All Units')] + Product.UNIT_TYPES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Unit Type'
    )


class StockReportForm(forms.Form):
    """Form for stock report filtering"""
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='From Date'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='To Date'
    )
    
    category = forms.ModelChoiceField(
        queryset=ProductCategory.objects.filter(is_active=True).order_by('name'),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Category'
    )
    
    brand = forms.ModelChoiceField(
        queryset=ProductBrand.objects.filter(is_active=True).order_by('name'),
        required=False,
        empty_label="All Brands",
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Brand'
    )
    
    stock_status = forms.ChoiceField(
        choices=[
            ('', 'All Stock Status'),
            ('in_stock', 'In Stock'),
            ('low_stock', 'Low Stock'),
            ('out_of_stock', 'Out of Stock'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Stock Status'
    )
    
    def clean(self):
        """Validate date range"""
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("From date cannot be after to date.")
        
        return cleaned_data
