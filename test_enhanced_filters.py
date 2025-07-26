#!/usr/bin/env python3
"""
GA10 Enhanced Cash Flow Filter Testing Script
=============================================

Tests all enhanced filtering capabilities:
- Next cash flow filter
- Period-based filtering
- All new endpoints
- Response validation
"""

import requests
import json
import time
from datetime import datetime

def test_enhanced_filters():
    """Test all enhanced filtering capabilities"""
    print("🧪 Testing GA10 Enhanced Cash Flow Filters")
    print("=" * 60)
    
    test_portfolio = {
        "bonds": [
            {"description": "T 2 1/2 07/31/27", "nominal": 1000000},
            {"description": "T 3 15/08/52", "nominal": 500000}
        ]
    }
    
    base_url = "http://localhost:8080"
    
    # Test 1: All Cash Flows
    print("\n🔍 TEST 1: All Cash Flows")
    test_endpoint(f"{base_url}/v1/bond/cashflow", test_portfolio)
    
    # Test 2: Next Cash Flow Filter
    print("\n🔍 TEST 2: Next Cash Flow Filter")
    test_endpoint(f"{base_url}/v1/bond/cashflow?filter=next", test_portfolio)
    
    # Test 3: Period Filter
    print("\n🔍 TEST 3: Period Filter (90 days)")
    test_endpoint(f"{base_url}/v1/bond/cashflow?filter=period&days=90", test_portfolio)
    
    # Test 4: Convenience Endpoints
    print("\n🔍 TEST 4: Next Convenience Endpoint")
    test_endpoint(f"{base_url}/v1/bond/cashflow/next", test_portfolio)
    
    print("\n🔍 TEST 5: Period Convenience Endpoint")
    test_endpoint(f"{base_url}/v1/bond/cashflow/period/90", test_portfolio)

def test_endpoint(url, data):
    """Test a specific endpoint"""
    try:
        response = requests.post(
            url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {url}")
            
            cash_flows = result.get("portfolio_cash_flows", [])
            filter_info = result.get("filter_applied", {})
            
            print(f"   📊 Filter: {filter_info}")
            print(f"   💰 Cash flows: {len(cash_flows)}")
            
            if cash_flows:
                print(f"   📅 First flow: {cash_flows[0]}")
        else:
            print(f"❌ FAILED: {url} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION FAILED: {url}")
        print("💡 Start GA10 API: python google_analysis10_api.py")
    except Exception as e:
        print(f"❌ ERROR: {url} - {e}")

if __name__ == "__main__":
    test_enhanced_filters()
