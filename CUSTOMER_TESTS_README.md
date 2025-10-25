# Customer Module Test Suite

This document describes the comprehensive test suite for the Customer module in the Django ERP system.

## Test Coverage

The test suite covers all aspects of the Customer module:

### 1. Model Tests (`CustomerModelTest`, `CustomerLedgerModelTest`, `CustomerCommitmentModelTest`)
- **Customer Model**: Creation, string representation, meta options, choices, opening balance functionality
- **CustomerLedger Model**: Creation, string representation, meta options, transaction types, payment methods
- **CustomerCommitment Model**: Creation, string representation, meta options

### 2. Form Tests (`CustomerFormTest`, `CustomerLedgerFormTest`, `CustomerCommitmentFormTest`, `SetOpeningBalanceFormTest`)
- **CustomerForm**: Valid data, required fields, form saving
- **CustomerLedgerForm**: Valid data, required fields, date cleaning
- **CustomerCommitmentForm**: Valid data, form saving
- **SetOpeningBalanceForm**: Valid data, required fields

### 3. View Tests (`CustomerViewsTest`, `CustomerCommitmentViewsTest`)
- **CRUD Operations**: List, detail, create, update, delete views
- **Ledger Management**: Ledger detail, ledger creation, opening balance setting
- **Commitment Management**: List, create, update, delete commitments
- **Authentication**: All views require user authentication

### 4. URL Tests (`CustomerURLsTest`)
- **URL Resolution**: All customer URLs resolve correctly
- **URL Patterns**: Verify correct URL patterns for all views

### 5. Business Logic Tests (`CustomerBusinessLogicTest`)
- **Balance Calculations**: After sales, payments, multiple transactions
- **Credit Limit Validation**: Exceeding credit limits
- **Opening Balance**: Creating ledger entries when setting opening balance

### 6. Integration Tests (`CustomerIntegrationTest`)
- **Complete Workflow**: Customer creation → opening balance → transactions → commitments
- **Ledger Detail Integration**: All transaction types in ledger view

## Test Classes Overview

### Model Tests
```python
class CustomerModelTest(TestCase):
    - test_customer_creation()
    - test_customer_str_representation()
    - test_customer_meta()
    - test_customer_choices()
    - test_set_opening_balance()

class CustomerLedgerModelTest(TestCase):
    - test_ledger_entry_creation()
    - test_ledger_entry_str_representation()
    - test_ledger_entry_meta()
    - test_transaction_type_choices()
    - test_payment_method_choices()

class CustomerCommitmentModelTest(TestCase):
    - test_commitment_creation()
    - test_commitment_str_representation()
    - test_commitment_meta()
```

### Form Tests
```python
class CustomerFormTest(TestCase):
    - test_customer_form_valid_data()
    - test_customer_form_required_fields()
    - test_customer_form_save()

class CustomerLedgerFormTest(TestCase):
    - test_ledger_form_valid_data()
    - test_ledger_form_required_fields()
    - test_ledger_form_clean_transaction_date()

class CustomerCommitmentFormTest(TestCase):
    - test_commitment_form_valid_data()
    - test_commitment_form_save()

class SetOpeningBalanceFormTest(TestCase):
    - test_opening_balance_form_valid_data()
    - test_opening_balance_form_required_amount()
```

### View Tests
```python
class CustomerViewsTest(TestCase):
    - test_customer_list_view()
    - test_customer_detail_view()
    - test_customer_create_view_get/post()
    - test_customer_update_view_get/post()
    - test_customer_delete_view_get/post()
    - test_customer_ledger_detail_view()
    - test_customer_ledger_create_view_get/post()
    - test_set_opening_balance_view_get/post()

class CustomerCommitmentViewsTest(TestCase):
    - test_commitment_list_view()
    - test_commitment_create_view_get/post()
    - test_commitment_update_view_get/post()
    - test_commitment_delete_view_get/post()
```

### URL Tests
```python
class CustomerURLsTest(TestCase):
    - test_customer_list_url()
    - test_customer_create_url()
    - test_customer_detail_url()
    - test_customer_edit_url()
    - test_customer_delete_url()
    - test_customer_ledger_detail_url()
    - test_customer_ledger_create_url()
    - test_customer_opening_balance_url()
    - test_commitment_list_url()
    - test_commitment_create_url()
    - test_commitment_edit_url()
    - test_commitment_delete_url()
```

### Business Logic Tests
```python
class CustomerBusinessLogicTest(TestCase):
    - test_balance_calculation_after_sale()
    - test_balance_calculation_after_payment()
    - test_balance_calculation_with_multiple_transactions()
    - test_credit_limit_validation()
    - test_opening_balance_creates_ledger_entry()
```

### Integration Tests
```python
class CustomerIntegrationTest(TestCase):
    - test_complete_customer_workflow()
    - test_customer_ledger_detail_integration()
```

## Running the Tests

### Method 1: Using Django's test runner
```bash
# Run all customer tests
python manage.py test customers.tests

# Run specific test class
python manage.py test customers.tests.CustomerModelTest

# Run specific test method
python manage.py test customers.tests.CustomerModelTest.test_customer_creation

# Run with verbose output
python manage.py test customers.tests --verbosity=2
```

### Method 2: Using the custom test runner
```bash
# Run the custom test runner script
python run_customer_tests.py
```

### Method 3: Using pytest (if installed)
```bash
# Install pytest-django
pip install pytest-django

# Run tests with pytest
pytest customers/tests.py -v
```

## Test Data Setup

Each test class uses `setUp()` method to create test data:

- **Users**: Test users for authentication
- **Customers**: Sample customer records
- **Ledger Entries**: Sample transaction records
- **Commitments**: Sample commitment records

## Key Test Scenarios

### 1. Customer Creation and Management
- Valid customer creation with all fields
- Required field validation
- Customer type choices validation
- Credit limit handling

### 2. Ledger Management
- Opening balance setting
- Sale transaction recording
- Payment transaction recording
- Balance calculation accuracy
- Multiple transaction handling

### 3. Commitment Management
- Commitment creation and editing
- Commitment deletion
- Customer association

### 4. Business Logic Validation
- Credit limit enforcement
- Balance calculation accuracy
- Transaction type handling
- Payment method validation

### 5. Integration Testing
- Complete customer workflow
- Ledger detail view with all transaction types
- Form validation across all views

## Test Assertions

The tests verify:
- **Model Creation**: Objects are created with correct attributes
- **String Representation**: `__str__` methods return expected strings
- **Form Validation**: Forms accept valid data and reject invalid data
- **View Responses**: Views return correct status codes and content
- **URL Resolution**: URLs resolve to correct views
- **Business Logic**: Balance calculations and credit limits work correctly
- **Integration**: Complete workflows function end-to-end

## Coverage Areas

✅ **Models**: All model fields, methods, and meta options
✅ **Forms**: All form fields, validation, and cleaning
✅ **Views**: All CRUD operations and business logic
✅ **URLs**: All URL patterns and routing
✅ **Business Logic**: Balance calculations, credit limits, opening balances
✅ **Integration**: Complete user workflows

## Maintenance

When adding new features to the Customer module:

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
