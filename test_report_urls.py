#!/usr/bin/env python
"""
Test script to check all report URLs
"""
import os
import sys
import django
from django.test import Client
from django.urls import reverse

# Add the project root to Python path
sys.path.append('/home/giasudin/PycharmProjects/djangoerp/building_materials_full')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def test_report_urls():
    """Test all report URLs"""
    client = Client()
    
    # Report URLs to test
    report_urls = [
        'reports:dashboard',
        'reports:financial_report',
        'reports:inventory_report',
        'reports:sales_report',
        'reports:purchase_report',
        'reports:customer_report',
        'reports:supplier_report',
        'reports:template_list',
        'reports:log_list',
    ]
    
    print("🔍 Testing Report URLs...")
    print("=" * 50)
    
    results = {}
    
    for url_name in report_urls:
        try:
            url = reverse(url_name)
            response = client.get(url)
            
            if response.status_code == 200:
                results[url_name] = "✅ PASS"
                print(f"✅ {url_name}: {url} - Status: {response.status_code}")
            else:
                results[url_name] = f"❌ FAIL - Status: {response.status_code}"
                print(f"❌ {url_name}: {url} - Status: {response.status_code}")
                
        except Exception as e:
            results[url_name] = f"❌ ERROR: {str(e)}"
            print(f"❌ {url_name}: ERROR - {str(e)}")
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if "✅" in result)
    total = len(results)
    
    for url_name, result in results.items():
        print(f"{result} {url_name}")
    
    print(f"\n🎯 Results: {passed}/{total} URLs working")
    
    if passed == total:
        print("🎉 All report URLs are working correctly!")
    else:
        print("⚠️  Some report URLs have issues that need to be fixed.")
    
    return results

if __name__ == "__main__":
    test_report_urls()
