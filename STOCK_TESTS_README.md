# Stock Module Test Suite

This document describes the comprehensive test suite for the Stock module in the Django ERP system.

## Test Coverage

The test suite covers all aspects of the Stock module:

### 1. Model Tests
- **ProductCategory Model**: Creation, string representation, meta options
- **ProductBrand Model**: Creation, string representation, meta options  
- **Product Model**: Creation, string representation, unit types, business methods
- **Stock Model**: Creation, string representation, stock update methods, business logic
- **StockAlert Model**: Creation, string representation, meta options

### 2. Form Tests
- **ProductCategoryForm**: Valid data, required fields, form saving
- **ProductBrandForm**: Valid data, required fields, form saving
- **ProductForm**: Valid data, required fields, validation, form saving
- **StockForm**: Valid data, required fields, validation, form saving
- **StockAdjustmentForm**: Valid data, required fields, validation
- **StockAlertForm**: Valid data, required fields, validation
- **ProductSearchForm**: Valid data, empty data handling
- **StockReportForm**: Valid data, date validation

### 3. View Tests
- **CRUD Operations**: List, detail, create, update, delete views for products
- **Stock Management**: Stock list, detail, update views
- **Stock Adjustments**: Stock adjustment functionality
- **Inventory Dashboard**: Dashboard view with comprehensive data
- **Authentication**: All views require user authentication

### 4. URL Tests
- **URL Resolution**: All stock URLs resolve correctly
- **URL Patterns**: Verify correct URL patterns for all views

### 5. Business Logic Tests
- **Stock Updates**: Inward, outward, and adjustment movements
- **Stock Alerts**: Automatic alert creation for low stock
- **Stock Calculations**: Total quantity and value calculations

### 6. Integration Tests
- **Complete Workflow**: Product creation → stock management → adjustments
- **Alert Workflow**: Low stock alert creation and management

## Test Classes Overview

### Model Tests
```python
class ProductCategoryModelTest(TestCase):
    - test_category_creation()
    - test_category_str_representation()
    - test_category_meta()

class ProductBrandModelTest(TestCase):
    - test_brand_creation()
    - test_brand_str_representation()
    - test_brand_meta()

class ProductModelTest(TestCase):
    - test_product_creation()
    - test_product_str_representation()
    - test_product_meta()
    - test_product_unit_types()
    - test_get_total_quantity()
    - test_get_total_stock_value()

class StockModelTest(TestCase):
    - test_stock_creation()
    - test_stock_str_representation()
    - test_stock_meta()
    - test_total_value_property()
    - test_update_stock_inward()
    - test_update_stock_outward()
    - test_update_stock_adjustment()

class StockAlertModelTest(TestCase):
    - test_alert_creation()
    - test_alert_str_representation()
    - test_alert_meta()
```

### Form Tests
```python
class ProductCategoryFormTest(TestCase):
    - test_category_form_valid_data()
    - test_category_form_required_fields()
    - test_category_form_save()

class ProductBrandFormTest(TestCase):
    - test_brand_form_valid_data()
    - test_brand_form_required_fields()
    - test_brand_form_save()

class ProductFormTest(TestCase):
    - test_product_form_valid_data()
    - test_product_form_required_fields()
    - test_product_form_save()
    - test_product_form_selling_price_validation()
    - test_product_form_min_stock_level_validation()

class StockFormTest(TestCase):
    - test_stock_form_valid_data()
    - test_stock_form_required_fields()
    - test_stock_form_save()
    - test_stock_form_quantity_validation()
    - test_stock_form_unit_cost_validation()

class StockAdjustmentFormTest(TestCase):
    - test_adjustment_form_valid_data()
    - test_adjustment_form_required_fields()
    - test_adjustment_form_quantity_validation()
    - test_adjustment_form_unit_cost_validation()

class StockAlertFormTest(TestCase):
    - test_alert_form_valid_data()
    - test_alert_form_required_fields()
    - test_alert_form_quantity_validation()

class ProductSearchFormTest(TestCase):
    - test_search_form_valid_data()
    - test_search_form_empty_data()

class StockReportFormTest(TestCase):
    - test_report_form_valid_data()
    - test_report_form_date_validation()
```

### View Tests
```python
class StockViewsTest(TestCase):
    - test_product_list_view()
    - test_product_detail_view()
    - test_product_create_view_get/post()
    - test_product_update_view_get/post()
    - test_product_delete_view_get/post()
    - test_stock_list_view()
    - test_stock_detail_view()
    - test_stock_update_view_get/post()
    - test_stock_adjustment_view_get/post()
    - test_inventory_dashboard_view()
```

### URL Tests
```python
class StockURLsTest(TestCase):
    - test_product_list_url()
    - test_product_create_url()
    - test_product_detail_url()
    - test_product_edit_url()
    - test_product_delete_url()
    - test_stock_adjustment_url()
    - test_category_list_url()
    - test_category_create_url()
    - test_brand_list_url()
    - test_brand_create_url()
    - test_stock_list_url()
    - test_alert_list_url()
    - test_inventory_dashboard_url()
```

### Business Logic Tests
```python
class StockBusinessLogicTest(TestCase):
    - test_stock_update_inward_creates_alert()
    - test_stock_update_above_minimum_removes_alert()
    - test_stock_update_with_unit_cost()
    - test_stock_update_without_unit_cost()
```

### Integration Tests
```python
class StockIntegrationTest(TestCase):
    - test_complete_product_workflow()
    - test_low_stock_alert_workflow()
```

## Running the Tests

### Method 1: Using Django's test runner
```bash
# Run all stock tests
python manage.py test stock.tests

# Run specific test class
python manage.py test stock.tests.ProductModelTest

# Run specific test method
python manage.py test stock.tests.ProductModelTest.test_product_creation

# Run with verbose output
python manage.py test stock.tests --verbosity=2
```

### Method 2: Using the custom test runner
```bash
# Run the custom test runner script
python run_stock_tests.py
```

### Method 3: Using pytest (if installed)
```bash
# Install pytest-django
pip install pytest-django

# Run tests with pytest
pytest stock/tests.py -v
```

## Test Data Setup

Each test class uses `setUp()` method to create test data:

- **Users**: Test users for authentication
- **Categories**: Product categories for testing
- **Brands**: Product brands for testing
- **Products**: Sample product records
- **Stock**: Sample stock records
- **Alerts**: Sample stock alert records

## Key Test Scenarios

### 1. Product Management
- Valid product creation with all fields
- Required field validation (name is required)
- Category and brand relationships
- Unit type validation
- Price validation (selling price vs cost price)
- Minimum stock level validation

### 2. Stock Management
- Stock quantity updates (inward, outward, adjustment)
- Unit cost tracking
- Stock value calculations
- Low stock alert creation
- Stock adjustment workflows

### 3. Form Validation
- Required field validation
- Data type validation
- Business rule validation
- Widget configuration testing

### 4. Business Logic
- Stock update methods
- Alert creation logic
- Stock calculations
- Inventory management

### 5. Integration Testing
- Complete product workflow
- Stock adjustment workflows
- Alert management workflows

## Test Assertions

The tests verify:
- **Model Creation**: Objects are created with correct attributes
- **String Representation**: `__str__` methods return expected strings
- **Form Validation**: Forms accept valid data and reject invalid data
- **View Responses**: Views return correct status codes and content
- **URL Resolution**: URLs resolve to correct views
- **Business Logic**: Stock calculations and alert logic work correctly
- **Integration**: Complete workflows function end-to-end

## Coverage Areas

✅ **Models**: All model fields, methods, and meta options
✅ **Forms**: All form fields, validation, and widget configuration
✅ **Views**: All CRUD operations and business logic
✅ **URLs**: All URL patterns and routing
✅ **Business Logic**: Stock calculations, alert creation, inventory management
✅ **Integration**: Complete user workflows and real-world scenarios

## Key Features of the Test Suite

- **Database Isolation**: Each test runs in isolation
- **Authentication Testing**: All view tests require user login
- **Financial Precision**: Uses Decimal for accurate calculations
- **Comprehensive Assertions**: Tests both positive and negative scenarios
- **Real Data Testing**: Uses realistic test data and scenarios
- **Template Content Validation**: Tests actual rendered content
- **Business Logic Verification**: Ensures stock calculations are correct

## Stock Module Specific Features

### Product Management
- **Categories and Brands**: Hierarchical product organization
- **Unit Types**: Multiple unit type support (pieces, kg, liters, etc.)
- **Pricing**: Cost price and selling price tracking
- **Stock Levels**: Minimum stock level management

### Stock Management
- **Stock Updates**: Inward, outward, and adjustment movements
- **Unit Cost Tracking**: Cost tracking for inventory valuation
- **Stock Alerts**: Automatic low stock notifications
- **Stock Calculations**: Total quantity and value calculations

### Inventory Features
- **Stock Adjustments**: Manual stock corrections
- **Stock Reports**: Comprehensive inventory reporting
- **Dashboard**: Real-time inventory overview
- **Alerts**: Low stock notifications

## Test Results Summary

- **Total Tests**: 83
- **Passed**: 83 ✅
- **Failed**: 0 ❌
- **Success Rate**: 100%

## Maintenance

When adding new features to the Stock module:

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
- Stock module includes complex business logic for inventory management
- Tests verify stock update methods and alert creation
- Integration tests cover complete product and stock workflows

The test suite provides comprehensive coverage of the Stock module and ensures code quality and reliability as the system evolves.
