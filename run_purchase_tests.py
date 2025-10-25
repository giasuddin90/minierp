#!/usr/bin/env python
"""
Test Runner for Purchase Module
Executes comprehensive tests for purchase functionality
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

def run_purchase_tests():
    """Run all purchase module tests"""
    print("=" * 60)
    print("RUNNING COMPREHENSIVE PURCHASE MODULE TESTS")
    print("=" * 60)
    
    # Setup Django
    setup_django()
    
    # Get test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True)
    
    # Run tests
    print("\n1. Running Purchase Order Model Tests...")
    print("-" * 40)
    failures = test_runner.run_tests(['purchases.test_comprehensive.PurchaseOrderModelTest'])
    
    print("\n2. Running Goods Receipt Model Tests...")
    print("-" * 40)
    failures += test_runner.run_tests(['purchases.test_comprehensive.GoodsReceiptModelTest'])
    
    print("\n3. Running Purchase Order View Tests...")
    print("-" * 40)
    failures += test_runner.run_tests(['purchases.test_comprehensive.PurchaseOrderViewTest'])
    
    print("\n4. Running Goods Receipt View Tests...")
    print("-" * 40)
    failures += test_runner.run_tests(['purchases.test_comprehensive.GoodsReceiptViewTest'])
    
    print("\n5. Running Integration Tests...")
    print("-" * 40)
    failures += test_runner.run_tests(['purchases.test_comprehensive.PurchaseOrderIntegrationTest'])
    
    print("\n6. Running Form Tests...")
    print("-" * 40)
    failures += test_runner.run_tests(['purchases.test_comprehensive.PurchaseOrderFormTest'])
    
    print("\n7. Running Authentication Tests...")
    print("-" * 40)
    failures += test_runner.run_tests(['purchases.test_comprehensive.PurchaseOrderAuthenticationTest'])
    
    print("\n8. Running Report Tests...")
    print("-" * 40)
    failures += test_runner.run_tests(['purchases.test_comprehensive.PurchaseOrderReportTest'])
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if failures == 0:
        print("✅ ALL TESTS PASSED!")
        print("✅ Purchase module functionality is working correctly")
        print("✅ Inventory updates after goods receipt are working")
        print("✅ All purchase workflows are functioning properly")
    else:
        print(f"❌ {failures} TEST(S) FAILED!")
        print("❌ Please check the failed tests above")
    
    print("=" * 60)
    return failures

def run_specific_test(test_class):
    """Run a specific test class"""
    setup_django()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True)
    
    print(f"Running {test_class}...")
    failures = test_runner.run_tests([f'purchases.test_comprehensive.{test_class}'])
    
    if failures == 0:
        print(f"✅ {test_class} PASSED!")
    else:
        print(f"❌ {test_class} FAILED!")
    
    return failures

def run_inventory_tests():
    """Run tests specifically for inventory functionality"""
    print("=" * 60)
    print("RUNNING INVENTORY INTEGRATION TESTS")
    print("=" * 60)
    
    setup_django()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True)
    
    # Run inventory-specific tests
    test_classes = [
        'PurchaseOrderModelTest.test_purchase_order_receive_goods',
        'PurchaseOrderIntegrationTest.test_inventory_increase_after_goods_receipt',
        'PurchaseOrderIntegrationTest.test_direct_goods_receipt_workflow',
        'GoodsReceiptViewTest.test_direct_goods_receipt_create_view'
    ]
    
    failures = 0
    for test_class in test_classes:
        print(f"\nRunning {test_class}...")
        failures += test_runner.run_tests([f'purchases.test_comprehensive.{test_class}'])
    
    print("\n" + "=" * 60)
    print("INVENTORY TEST SUMMARY")
    print("=" * 60)
    
    if failures == 0:
        print("✅ INVENTORY TESTS PASSED!")
        print("✅ Inventory increases correctly after goods receipt")
        print("✅ Stock updates are working properly")
        print("✅ Direct goods receipt updates inventory")
    else:
        print(f"❌ {failures} INVENTORY TEST(S) FAILED!")
        print("❌ Inventory functionality needs attention")
    
    return failures

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Purchase Module Tests')
    parser.add_argument('--inventory-only', action='store_true', 
                       help='Run only inventory-related tests')
    parser.add_argument('--test-class', type=str, 
                       help='Run specific test class')
    
    args = parser.parse_args()
    
    if args.inventory_only:
        failures = run_inventory_tests()
    elif args.test_class:
        failures = run_specific_test(args.test_class)
    else:
        failures = run_purchase_tests()
    
    sys.exit(failures)

