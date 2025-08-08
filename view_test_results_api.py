#!/usr/bin/env python3
"""
View test results via API endpoints
"""

import requests
import json
import sys

# API configuration
API_URL = "https://future-footing-414610.uc.r.appspot.com"
API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q"

def test_endpoint(endpoint, method='GET', data=None):
    """Test an API endpoint"""
    url = f"{API_URL}{endpoint}"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    print(f"\n{'='*60}")
    print(f"Testing: {method} {endpoint}")
    print(f"{'='*60}")
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        else:
            response = requests.post(url, headers=headers, json=data, timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

def main():
    """Test all endpoints"""
    
    # 1. Test status endpoint
    test_endpoint("/test/status")
    
    # 2. Test treasury endpoint
    test_endpoint("/test/treasury")
    
    # 3. Test baseline endpoint
    test_endpoint("/test/baseline")
    
    # 4. Test quick analysis
    print(f"\n{'='*60}")
    print("Quick Bond Analysis Test")
    print(f"{'='*60}")
    
    test_data = {
        "description": "T 3 15/08/52",
        "price": 71.66,
        "settlement_date": "2025-06-30"
    }
    
    test_endpoint("/api/v1/bond/analysis", method='POST', data=test_data)

if __name__ == "__main__":
    main()