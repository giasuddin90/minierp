# Purchase Order Debug Fix

## Issue Identified 🔍

**Problem**: In purchase order HTML, product unit price and total value are not showing.

**Symptoms**:
- Unit price field appears empty
- Total value field appears empty
- JavaScript calculations not working properly

## Debugging Changes Made

### **1. Enhanced JavaScript Element Selection**

#### **Updated Product Selection Handler:**
```javascript
// Product selection change
document.addEventListener('change', function(e) {
    if (e.target.classList.contains('product-select')) {
        const option = e.target.selectedOptions[0];
        const row = e.target.closest('.product-row');
        
        console.log('Product selected:', option.value, option.dataset.price);
        
        if (option.dataset.price) {
            // Try multiple selectors to find the price input
            const priceInput = row.querySelector('.price-input') || 
                             row.querySelector('input[name$="-unit_price"]') ||
                             row.querySelector('input[name*="unit_price"]');
            console.log('Price input found:', priceInput);
            if (priceInput) {
                priceInput.value = option.dataset.price;
                calculateRowTotal(row);
            }
        }
        
        // Show product info
        if (option.value) {
            showProductInfo(row, option);
        } else {
            hideProductInfo(row);
        }
        
        validateForm();
    }
});
```

#### **Enhanced calculateRowTotal Function:**
```javascript
function calculateRowTotal(row) {
    // Try multiple selectors to find quantity input
    const quantityInput = row.querySelector('.quantity-input') || 
                        row.querySelector('input[name$="-quantity"]') ||
                        row.querySelector('input[name*="quantity"]');
    const quantity = parseFloat(quantityInput ? quantityInput.value : 0) || 0;
    
    // Try multiple selectors to find price input
    const priceInput = row.querySelector('.price-input') || 
                     row.querySelector('input[name$="-unit_price"]') ||
                     row.querySelector('input[name*="unit_price"]');
    const price = parseFloat(priceInput ? priceInput.value : 0) || 0;
    
    console.log('calculateRowTotal:', {quantity, price, quantityInput, priceInput});
    
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

### **2. Added Debug Information to Template**

#### **Unit Price Field Debug:**
```html
<!-- Unit Price -->
<div class="col-md-2">
    <label class="form-label">
        <i class="bi bi-currency-dollar"></i> Unit Price <span class="text-danger fw-bold">*</span>
    </label>
    {{ form.unit_price }}
    {% if form.unit_price.errors %}
        <div class="invalid-feedback d-block">{{ form.unit_price.errors.0 }}</div>
    {% endif %}
    <!-- Debug info -->
    <small class="text-muted">Unit Price Field: {{ form.unit_price.value|default:"No value" }}</small>
</div>
```

#### **Total Price Field Debug:**
```html
<!-- Total and Actions -->
<div class="col-md-2">
    <label class="form-label">Total</label>
    {{ form.total_price }}
    {% if form.total_price.errors %}
        <div class="invalid-feedback d-block">{{ form.total_price.errors.0 }}</div>
    {% endif %}
    <!-- Debug info -->
    <small class="text-muted">Total Price Field: {{ form.total_price.value|default:"No value" }}</small>
    {% if not forloop.first %}
    <button type="button" class="btn btn-danger btn-sm mt-1 remove-product">
        <i class="bi bi-trash"></i>
    </button>
    {% endif %}
</div>
```

## Debugging Strategy

### **1. Console Logging**
- Added console.log statements to track:
  - Product selection events
  - Element finding success/failure
  - Calculation values
  - Form field values

### **2. Template Debug Info**
- Added debug information to show:
  - Current form field values
  - Whether fields have values
  - Form rendering status

### **3. Robust Element Selection**
- Multiple selector strategies:
  - CSS class selectors (`.price-input`, `.quantity-input`)
  - Name attribute selectors (`input[name$="-unit_price"]`)
  - Partial name selectors (`input[name*="unit_price"]`)

## Expected Debug Output

### **Console Logs:**
```
Product selected: 123 150.00
Price input found: <input name="form-0-unit_price" ...>
calculateRowTotal: {quantity: 2, price: 150, quantityInput: <input>, priceInput: <input>}
```

### **Template Debug Info:**
```
Unit Price Field: 150.00
Total Price Field: 300.00
```

## Next Steps

### **1. Test the Form**
1. Open the purchase order creation page
2. Select a product from the dropdown
3. Check browser console for debug logs
4. Verify form field values are populated
5. Check if calculations are working

### **2. Identify Issues**
- If console shows "Price input found: null" → Element selection issue
- If form fields show "No value" → Form rendering issue
- If calculations show 0 → Value parsing issue

### **3. Fix Based on Debug Results**
- Element selection issues → Update selectors
- Form rendering issues → Check form configuration
- Value parsing issues → Check data types and formats

## Benefits

### ✅ **Enhanced Debugging**
1. **Console Logging** - Track JavaScript execution
2. **Template Debug** - See form field values
3. **Robust Selection** - Multiple ways to find elements
4. **Error Tracking** - Identify specific failure points

### ✅ **Improved Reliability**
1. **Fallback Selectors** - Multiple ways to find form elements
2. **Error Handling** - Graceful handling of missing elements
3. **Value Validation** - Check if values are being set correctly
4. **Real-time Feedback** - Immediate visibility of issues

## Summary

The debugging changes will help identify exactly where the issue is occurring:

- ✅ **JavaScript Issues** - Console logs will show element selection problems
- ✅ **Form Rendering Issues** - Template debug will show field values
- ✅ **Calculation Issues** - Console logs will show calculation values
- ✅ **Element Selection Issues** - Multiple selector strategies for reliability

Once the debug information is collected, the specific issue can be identified and fixed! 🔍
