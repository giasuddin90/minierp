#!/usr/bin/env python
"""
Test runner script for Supplier module tests
Usage: python run_supplier_tests.py
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == '__main__':
    # Add the project directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()
    
    def run_tests():
        """Run supplier module tests"""
        TestRunner = get_runner(settings)
        test_runner = TestRunner(verbosity=2, interactive=True)
        
        print("=" * 60)
        print("RUNNING SUPPLIER MODULE TESTS")
        print("=" * 60)
        
        # Run supplier tests
        failures = test_runner.run_tests(['suppliers.tests'])
        
        if failures:
            print(f"\n❌ {failures} test(s) failed!")
            return False
        else:
            print("\n✅ All tests passed!")
            return True
    
    success = run_tests()
    sys.exit(0 if success else 1)
