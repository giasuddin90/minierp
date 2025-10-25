# Purchase Order IntegrityError Fix

## Issue Fixed ✅

**Error**: `IntegrityError at /purchases/orders/create/ NOT NULL constraint failed: purchases_purchaseorderitem.total_price`

**Root Cause**: The `PurchaseOrderItem` model requires a `total_price` field, but the form wasn't calculating and setting this value.

## Solution Implemented

### **1. Updated PurchaseOrderItemForm**

#### **Added total_price field to form:**
```python
class Meta:
    model = PurchaseOrderItem
    fields = ['product', 'quantity', 'unit_price', 'total_price']
    widgets = {
        'product': forms.Select(attrs={'class': 'form-select product-select'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control quantity-input', 'step': '0.01', 'min': '0'}),
        'unit_price': forms.NumberInput(attrs={'class': 'form-control price-input', 'step': '0.01', 'min': '0'}),
        'total_price': forms.NumberInput(attrs={'class': 'form-control total-input', 'step': '0.01', 'readonly': True}),
    }
```

#### **Added clean method to calculate total_price:**
```python
def clean(self):
    cleaned_data = super().clean()
    quantity = cleaned_data.get('quantity', 0)
    unit_price = cleaned_data.get('unit_price', 0)
    
    # Calculate total price
    if quantity and unit_price:
        cleaned_data['total_price'] = quantity * unit_price
    
    return cleaned_data
```

#### **Added save method to ensure total_price is set:**
```python
def save(self, commit=True):
    instance = super().save(commit=False)
    # Calculate total price
    quantity = self.cleaned_data.get('quantity', 0)
    unit_price = self.cleaned_data.get('unit_price', 0)
    instance.total_price = quantity * unit_price
    
    if commit:
        instance.save()
    return instance
```

### **2. Updated Formset Configuration**

#### **Included total_price in formset fields:**
```python
PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    fields=['product', 'quantity', 'unit_price', 'total_price'],
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
```

### **3. Updated Template**

#### **Updated template to use form's total_price field:**
```html
<!-- Total and Actions -->
<div class="col-md-2">
    <label class="form-label">Total</label>
    {{ form.total_price }}
    {% if form.total_price.errors %}
        <div class="invalid-feedback d-block">{{ form.total_price.errors.0 }}</div>
    {% endif %}
    {% if not forloop.first %}
    <button type="button" class="btn btn-danger btn-sm mt-1 remove-product">
        <i class="bi bi-trash"></i>
    </button>
    {% endif %}
</div>
```

### **4. Updated JavaScript**

#### **Enhanced calculateRowTotal function:**
```javascript
function calculateRowTotal(row) {
    const quantity = parseFloat(row.querySelector('.quantity-input').value) || 0;
    const price = parseFloat(row.querySelector('.price-input').value) || 0;
    const total = quantity * price;
    
    // Update the total input field
    const totalInput = row.querySelector('.total-input');
    if (totalInput) {
        totalInput.value = total.toFixed(2);
    }
    
    // Update the total_price field in the form
    const totalPriceField = row.querySelector('input[name$="-total_price"]');
    if (totalPriceField) {
        totalPriceField.value = total.toFixed(2);
    }
    
    updateTotalAmount();
}
```

#### **Enhanced updateTotalAmount function:**
```javascript
function updateTotalAmount() {
    let total = 0;
    // Use total_price fields if available, otherwise fall back to total-input
    const totalPriceFields = document.querySelectorAll('input[name$="-total_price"]');
    if (totalPriceFields.length > 0) {
        totalPriceFields.forEach(input => {
            total += parseFloat(input.value) || 0;
        });
    } else {
        document.querySelectorAll('.total-input').forEach(input => {
            total += parseFloat(input.value) || 0;
        });
    }
    
    document.getElementById('id_total_amount').value = total.toFixed(2);
}
```

## Technical Details

### **Form Validation Flow:**
1. **User Input** → Quantity and Unit Price entered
2. **JavaScript Calculation** → Real-time total calculation
3. **Form Clean Method** → Server-side total_price calculation
4. **Form Save Method** → Ensures total_price is set before saving
5. **Database Save** → total_price field is populated

### **Formset Handling:**
- **Fields Included**: `['product', 'quantity', 'unit_price', 'total_price']`
- **Validation**: Both client-side and server-side
- **Calculation**: Automatic total_price calculation
- **Error Handling**: Proper error display for all fields

## Benefits

### ✅ **Fixed Issues**
1. **IntegrityError Resolved** - total_price field is now properly calculated and set
2. **Form Validation** - Both client-side and server-side validation
3. **Real-time Calculation** - JavaScript updates total_price as user types
4. **Data Integrity** - Server-side calculation ensures accuracy

### ✅ **Enhanced User Experience**
1. **Real-time Updates** - Total price updates as user enters data
2. **Visual Feedback** - Clear display of calculated totals
3. **Error Handling** - Proper error messages for validation issues
4. **Form Consistency** - All form fields work together seamlessly

### ✅ **Technical Improvements**
1. **Form Structure** - Proper form field configuration
2. **JavaScript Integration** - Client-side calculation and updates
3. **Server-side Validation** - Robust data validation
4. **Database Integrity** - All required fields are populated

## Summary

The IntegrityError has been completely resolved! The purchase order creation now:

- ✅ **Calculates total_price** automatically
- ✅ **Validates all fields** properly
- ✅ **Updates in real-time** with JavaScript
- ✅ **Saves successfully** to database
- ✅ **Handles errors** gracefully

The purchase order functionality is now fully working! 🎯

