# Supplier Module Test Suite

This document describes the comprehensive test suite for the Supplier module in the Django ERP system.

## Test Coverage

The test suite covers all aspects of the Supplier module:

### 1. Model Tests (`SupplierModelTest`, `SupplierLedgerModelTest`)
- **Supplier Model**: Creation, string representation, meta options, opening balance functionality
- **SupplierLedger Model**: Creation, string representation, meta options, transaction types, payment methods

### 2. Form Tests (`SupplierFormTest`, `SupplierLedgerFormTest`, `SetOpeningBalanceFormTest`, `SupplierFormValidationTest`, `SupplierLedgerFormValidationTest`)
- **SupplierForm**: Valid data, required fields, form saving, widget attributes
- **SupplierLedgerForm**: Valid data, required fields, amount validation, initial values
- **SetOpeningBalanceForm**: Valid data, required fields

### 3. View Tests (`SupplierViewsTest`)
- **CRUD Operations**: List, detail, create, update, delete views
- **Ledger Management**: Ledger detail, ledger creation, opening balance setting
- **Authentication**: All views require user authentication

### 4. URL Tests (`SupplierURLsTest`)
- **URL Resolution**: All supplier URLs resolve correctly
- **URL Patterns**: Verify correct URL patterns for all views

### 5. Business Logic Tests (`SupplierBusinessLogicTest`)
- **Balance Calculations**: After purchases, payments, multiple transactions
- **Opening Balance**: Creating ledger entries when setting opening balance

### 6. Integration Tests (`SupplierIntegrationTest`)
- **Complete Workflow**: Supplier creation → opening balance → transactions
- **Ledger Detail Integration**: All transaction types in ledger view

### 7. List View Tests (`SupplierListViewTest`)
- **Context Calculations**: Total payable, receivable, active suppliers
- **Template Content**: Supplier information display

## Test Classes Overview

### Model Tests
```python
class SupplierModelTest(TestCase):
    - test_supplier_creation()
    - test_supplier_str_representation()
    - test_supplier_meta()
    - test_set_opening_balance()

class SupplierLedgerModelTest(TestCase):
    - test_ledger_entry_creation()
    - test_ledger_entry_str_representation()
    - test_ledger_entry_meta()
    - test_transaction_type_choices()
    - test_payment_method_choices()
```

### Form Tests
```python
class SupplierFormTest(TestCase):
    - test_supplier_form_valid_data()
    - test_supplier_form_required_fields()
    - test_supplier_form_save()

class SupplierFormValidationTest(TestCase):
    - test_supplier_form_name_required()
    - test_supplier_form_optional_fields()
    - test_supplier_form_widget_attributes()

class SupplierLedgerFormTest(TestCase):
    - test_ledger_form_valid_data()
    - test_ledger_form_required_fields()
    - test_ledger_form_save()

class SupplierLedgerFormValidationTest(TestCase):
    - test_ledger_form_amount_validation()
    - test_ledger_form_initial_values()
    - test_ledger_form_required_fields()

class SetOpeningBalanceFormTest(TestCase):
    - test_opening_balance_form_valid_data()
    - test_opening_balance_form_required_amount()
```

### View Tests
```python
class SupplierViewsTest(TestCase):
    - test_supplier_list_view()
    - test_supplier_detail_view()
    - test_supplier_create_view_get/post()
    - test_supplier_update_view_get/post()
    - test_supplier_delete_view_get/post()
    - test_supplier_ledger_detail_view()
    - test_supplier_ledger_create_view_get/post()
    - test_set_opening_balance_view_get/post()

class SupplierListViewTest(TestCase):
    - test_supplier_list_context_calculations()
    - test_supplier_list_template_content()
```

### URL Tests
```python
class SupplierURLsTest(TestCase):
    - test_supplier_list_url()
    - test_supplier_create_url()
    - test_supplier_detail_url()
    - test_supplier_edit_url()
    - test_supplier_delete_url()
    - test_supplier_ledger_detail_url()
    - test_supplier_ledger_create_url()
    - test_supplier_opening_balance_url()
    - test_ledger_list_url()
    - test_ledger_create_url()
```

### Business Logic Tests
```python
class SupplierBusinessLogicTest(TestCase):
    - test_balance_calculation_after_purchase()
    - test_balance_calculation_after_payment()
    - test_balance_calculation_with_multiple_transactions()
    - test_opening_balance_creates_ledger_entry()
```

### Integration Tests
```python
class SupplierIntegrationTest(TestCase):
    - test_complete_supplier_workflow()
    - test_supplier_ledger_detail_integration()
```

## Running the Tests

### Method 1: Using Django's test runner
```bash
# Run all supplier tests
python manage.py test suppliers.tests

# Run specific test class
python manage.py test suppliers.tests.SupplierModelTest

# Run specific test method
python manage.py test suppliers.tests.SupplierModelTest.test_supplier_creation

# Run with verbose output
python manage.py test suppliers.tests --verbosity=2
```

### Method 2: Using the custom test runner
```bash
# Run the custom test runner script
python run_supplier_tests.py
```

### Method 3: Using pytest (if installed)
```bash
# Install pytest-django
pip install pytest-django

# Run tests with pytest
pytest suppliers/tests.py -v
```

## Test Data Setup

Each test class uses `setUp()` method to create test data:

- **Users**: Test users for authentication
- **Suppliers**: Sample supplier records
- **Ledger Entries**: Sample transaction records

## Key Test Scenarios

### 1. Supplier Creation and Management
- Valid supplier creation with all fields
- Required field validation (name is required)
- Optional fields handling
- Widget attributes and form configuration

### 2. Ledger Management
- Opening balance setting
- Purchase transaction recording
- Payment transaction recording
- Balance calculation accuracy
- Multiple transaction handling

### 3. Business Logic Validation
- Balance calculation accuracy
- Transaction type handling
- Payment method validation
- Opening balance functionality

### 4. Integration Testing
- Complete supplier workflow
- Ledger detail view with all transaction types
- Form validation across all views

## Test Assertions

The tests verify:
- **Model Creation**: Objects are created with correct attributes
- **String Representation**: `__str__` methods return expected strings
- **Form Validation**: Forms accept valid data and reject invalid data
- **View Responses**: Views return correct status codes and content
- **URL Resolution**: URLs resolve to correct views
- **Business Logic**: Balance calculations work correctly
- **Integration**: Complete workflows function end-to-end

## Coverage Areas

✅ **Models**: All model fields, methods, and meta options
✅ **Forms**: All form fields, validation, and widget configuration
✅ **Views**: All CRUD operations and business logic
✅ **URLs**: All URL patterns and routing
✅ **Business Logic**: Balance calculations, opening balances
✅ **Integration**: Complete user workflows
✅ **List View**: Context calculations and template content

## Key Differences from Customer Tests

### Supplier-Specific Features
- **Balance Logic**: Positive balances = you owe money to supplier
- **Transaction Types**: Purchase, payment, return, adjustment, commission
- **No Customer Type**: Suppliers don't have type classification
- **City Field**: Additional location field for suppliers
- **No Credit Limit**: Suppliers don't have credit limit validation

### Test Coverage Differences
- **No Commitment Tests**: Suppliers don't have commitment functionality
- **Simplified Form Tests**: Fewer form validation scenarios
- **Balance Calculations**: Different logic for supplier balances
- **List View Context**: Different calculations for payable/receivable

## Maintenance

When adding new features to the Supplier module:

1. **Add corresponding tests** for new functionality
2. **Update existing tests** if behavior changes
3. **Run tests** before committing changes
4. **Ensure test coverage** remains comprehensive

## Test Dependencies

- Django TestCase framework
- Django Client for view testing
- User authentication system
- Decimal precision for financial calculations
- Timezone handling for dates and times

## Notes

- All tests use Django's TestCase which provides database isolation
- Tests create and clean up their own data
- Financial calculations use Decimal for precision
- Authentication is required for all view tests
- Tests cover both positive and negative scenarios
- Supplier balance logic: positive = you owe them, negative = they owe you

## Test Results Summary

- **Total Tests**: 54
- **Passed**: 54 ✅
- **Failed**: 0 ❌
- **Success Rate**: 100%

The test suite provides comprehensive coverage of the Supplier module and ensures code quality and reliability as the system evolves.
