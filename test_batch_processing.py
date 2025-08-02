#!/usr/bin/env python3
"""
XTrillion Core - Batch Processing Test Suite
==========================================

Comprehensive testing of the new batch processing endpoint in DEV environment.

Tests include:
✅ Health check validation
✅ Batch endpoint functionality
✅ Array validation
✅ Parallel processing
✅ Performance metrics
✅ Error handling
✅ Backwards compatibility
"""

import requests
import json
import time
from datetime import datetime

# DEV Environment Configuration
DEV_BASE_URL = "https://development-dot-future-footing-414610.uc.r.appspot.com"
DEV_API_KEY = "gax10_dev_4n8s6k2x7p9v5m8p1z"

# Test Bond Data
TEST_BONDS = [
    ["T 3 15/08/52", 71.66, "2025-08-01"],
    ["PANAMA, 3.87%, 23-Jul-2060", 56.60, "2025-08-01"],
    ["ECOPETROL SA, 5.875%, 28-May-2045", 69.31, "2025-08-01"],
    ["COLOMBIA REP OF, 3.875%, 15-Feb-2061", 52.71, "2025-08-01"]
]

def test_health_check():
    """Test 1: Health Check with Batch Processing Info"""
    print("\n🔍 TEST 1: Health Check")
    print("-" * 50)
    
    try:
        response = requests.get(f"{DEV_BASE_URL}/health", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API Status: {health_data.get('status', 'unknown')}")
            print(f"✅ Version: {health_data.get('version', 'unknown')}")
            print(f"✅ Environment: {health_data.get('environment', 'unknown')}")
            
            # Check batch processing capabilities
            batch_info = health_data.get('batch_processing', {})
            print(f"✅ Batch Processing Available: {batch_info.get('available', False)}")
            print(f"✅ Max Bonds Per Request: {batch_info.get('max_bonds_per_request', 'unknown')}")
            print(f"✅ Parallel Execution: {batch_info.get('parallel_execution', False)}")
            
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_batch_status():
    """Test 2: Batch Status Endpoint"""
    print("\n🔍 TEST 2: Batch Status Endpoint")
    print("-" * 50)
    
    try:
        response = requests.get(f"{DEV_BASE_URL}/api/v1/batch/status", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ Batch Status: {status_data.get('status', 'unknown')}")
            
            batch_info = status_data.get('batch_processing', {})
            print(f"✅ Max Bonds: {batch_info.get('max_bonds_per_request', 'unknown')}")
            print(f"✅ Max Workers: {batch_info.get('max_workers', 'unknown')}")
            
            endpoints = status_data.get('endpoints', {})
            print(f"✅ Batch Analysis Endpoint: {endpoints.get('batch_analysis', 'unknown')}")
            
            return True
        else:
            print(f"❌ Batch status failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Batch status error: {e}")
        return False

def test_basic_batch_processing():
    """Test 3: Basic Batch Processing"""
    print("\n🔍 TEST 3: Basic Batch Processing")
    print("-" * 50)
    
    try:
        # Test with 2 bonds
        test_data = {
            "bonds": TEST_BONDS[:2],
            "parallel": True,
            "max_workers": 2
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": DEV_API_KEY
        }
        
        print(f"Sending batch request with {len(test_data['bonds'])} bonds...")
        start_time = time.time()
        
        response = requests.post(
            f"{DEV_BASE_URL}/api/v1/bonds/batch",
            json=test_data,
            headers=headers,
            timeout=30
        )
        
        request_time = round((time.time() - start_time) * 1000, 2)
        print(f"Request Time: {request_time}ms")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            batch_result = response.json()
            print(f"✅ Batch Status: {batch_result.get('status', 'unknown')}")
            
            # Check batch performance
            performance = batch_result.get('batch_performance', {})
            print(f"✅ Total Bonds: {performance.get('total_bonds', 'unknown')}")
            print(f"✅ Successful: {performance.get('successful_calculations', 'unknown')}")
            print(f"✅ Success Rate: {performance.get('success_rate', 'unknown')}%")
            print(f"✅ Batch Time: {performance.get('batch_processing_time_ms', 'unknown')}ms")
            print(f"✅ Avg Calc Time: {performance.get('average_calculation_time_ms', 'unknown')}ms")
            print(f"✅ Parallel Processing: {performance.get('parallel_processing', 'unknown')}")
            
            # Check individual results
            results = batch_result.get('batch_results', [])
            print(f"✅ Individual Results: {len(results)} bonds")
            
            for i, result in enumerate(results):
                status = result.get('status', 'unknown')
                calc_time = result.get('calculation_time_ms', 'unknown')
                print(f"   Bond {i+1}: {status} ({calc_time}ms)")
                
                if status == 'success':
                    analytics = result.get('analytics', {})
                    ytm = analytics.get('ytm', 'N/A')
                    duration = analytics.get('duration', 'N/A')
                    print(f"     YTM: {ytm:.4f}%, Duration: {duration:.2f} years")
            
            return True
        else:
            print(f"❌ Batch processing failed with status {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Batch processing error: {e}")
        return False

def test_large_batch():
    """Test 4: Large Batch Processing"""
    print("\n🔍 TEST 4: Large Batch Processing")
    print("-" * 50)
    
    try:
        # Create larger batch with all test bonds
        test_data = {
            "bonds": TEST_BONDS,
            "parallel": True,
            "max_workers": 4
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": DEV_API_KEY
        }
        
        print(f"Sending large batch request with {len(test_data['bonds'])} bonds...")
        start_time = time.time()
        
        response = requests.post(
            f"{DEV_BASE_URL}/api/v1/bonds/batch",
            json=test_data,
            headers=headers,
            timeout=60
        )
        
        request_time = round((time.time() - start_time) * 1000, 2)
        print(f"Request Time: {request_time}ms")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            batch_result = response.json()
            performance = batch_result.get('batch_performance', {})
            
            print(f"✅ Success Rate: {performance.get('success_rate', 'unknown')}%")
            print(f"✅ Batch Time: {performance.get('batch_processing_time_ms', 'unknown')}ms")
            print(f"✅ Workers Used: {performance.get('max_workers_used', 'unknown')}")
            
            return True
        else:
            print(f"❌ Large batch failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Large batch error: {e}")
        return False

def test_error_handling():
    """Test 5: Error Handling and Validation"""
    print("\n🔍 TEST 5: Error Handling and Validation")
    print("-" * 50)
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": DEV_API_KEY
    }
    
    # Test 5a: Invalid bond format
    print("Testing invalid bond format...")
    try:
        test_data = {
            "bonds": [
                ["T 3 15/08/52"],  # Missing price
                ["PANAMA", 56.60, "2025-08-01"]
            ]
        }
        
        response = requests.post(
            f"{DEV_BASE_URL}/api/v1/bonds/batch",
            json=test_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 400:
            print("✅ Correctly rejected invalid bond format")
        else:
            print(f"❌ Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
    
    # Test 5b: Empty bonds array
    print("Testing empty bonds array...")
    try:
        test_data = {"bonds": []}
        
        response = requests.post(
            f"{DEV_BASE_URL}/api/v1/bonds/batch",
            json=test_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 400:
            print("✅ Correctly rejected empty bonds array")
        else:
            print(f"❌ Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
    
    # Test 5c: Missing API key
    print("Testing missing API key...")
    try:
        test_data = {"bonds": TEST_BONDS[:1]}
        headers_no_key = {"Content-Type": "application/json"}
        
        response = requests.post(
            f"{DEV_BASE_URL}/api/v1/bonds/batch",
            json=test_data,
            headers=headers_no_key,
            timeout=10
        )
        
        if response.status_code == 401:
            print("✅ Correctly rejected missing API key")
        else:
            print(f"❌ Expected 401, got {response.status_code}")
    except Exception as e:
        print(f"❌ API key test failed: {e}")

def test_backwards_compatibility():
    """Test 6: Backwards Compatibility"""
    print("\n🔍 TEST 6: Backwards Compatibility")
    print("-" * 50)
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": DEV_API_KEY
    }
    
    # Test individual bond endpoint
    print("Testing individual bond endpoint...")
    try:
        test_data = {
            "description": "T 3 15/08/52",
            "price": 71.66,
            "settlement_date": "2025-08-01"
        }
        
        response = requests.post(
            f"{DEV_BASE_URL}/api/v1/bond/analysis",
            json=test_data,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ Individual bond endpoint working")
                analytics = result.get('analytics', {})
                print(f"   YTM: {analytics.get('ytm', 'N/A'):.4f}%")
                print(f"   Duration: {analytics.get('duration', 'N/A'):.2f} years")
            else:
                print(f"❌ Individual bond calculation failed: {result.get('error', 'unknown')}")
        else:
            print(f"❌ Individual bond endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Individual bond test error: {e}")
    
    # Test portfolio endpoint
    print("Testing portfolio endpoint...")
    try:
        test_data = {
            "data": [
                {
                    "BOND_CD": "T 3 15/08/52",
                    "CLOSING PRICE": 71.66,
                    "WEIGHTING": 60.0
                },
                {
                    "BOND_CD": "PANAMA, 3.87%, 23-Jul-2060",
                    "CLOSING PRICE": 56.60,
                    "WEIGHTING": 40.0
                }
            ]
        }
        
        response = requests.post(
            f"{DEV_BASE_URL}/api/v1/portfolio/analysis",
            json=test_data,
            headers=headers,
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ Portfolio endpoint working")
                metrics = result.get('portfolio_metrics', {})
                print(f"   Portfolio Yield: {metrics.get('portfolio_yield', 'N/A')}")
                print(f"   Portfolio Duration: {metrics.get('portfolio_duration', 'N/A')}")
            else:
                print(f"❌ Portfolio calculation failed")
        else:
            print(f"❌ Portfolio endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Portfolio test error: {e}")

def main():
    """Run comprehensive batch processing test suite"""
    print("🧪 XTrillion Core - Batch Processing Test Suite")
    print("=" * 60)
    print(f"Target: {DEV_BASE_URL}")
    print(f"API Key: {DEV_API_KEY[:20]}...")
    print(f"Test Time: {datetime.now().isoformat()}")
    
    tests = [
        test_health_check,
        test_batch_status,
        test_basic_batch_processing,
        test_large_batch,
        test_error_handling,
        test_backwards_compatibility
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Batch processing is ready for development!")
        print("\n✅ Next Steps:")
        print("   1. Create JavaScript batch functions for Excel integration")
        print("   2. Test performance with larger datasets")
        print("   3. Validate production readiness")
    else:
        print("⚠️  Some tests failed. Review output above for details.")
    
    print(f"\nTest completed at: {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()
