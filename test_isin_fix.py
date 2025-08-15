#!/usr/bin/env python3
"""
Test script to verify ISIN lookup fix
"""

import requests
import json

API_URL = "https://development-dot-future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis"

test_cases = [
    {
        "name": "1. Valid ISIN only (should work if in database)",
        "payload": {
            "isin": "US912810TJ79",
            "price": 71.66,
            "settlement_date": "2025-08-01"
        }
    },
    {
        "name": "2. Invalid ISIN only (should return helpful error)",
        "payload": {
            "isin": "XX9999999999",
            "price": 71.66,
            "settlement_date": "2025-08-01"
        }
    },
    {
        "name": "3. Invalid ISIN with description (should use description)",
        "payload": {
            "isin": "XX9999999999",
            "description": "T 3 15/08/52",
            "price": 71.66,
            "settlement_date": "2025-08-01"
        }
    },
    {
        "name": "4. Valid ISIN with description (should work)",
        "payload": {
            "isin": "US912810TJ79",
            "description": "T 3 15/08/52",
            "price": 71.66,
            "settlement_date": "2025-08-01"
        }
    }
]

print("🔧 Testing ISIN Lookup Fix")
print("=" * 60)

for test in test_cases:
    print(f"\n{test['name']}")
    print("-" * 40)
    print(f"Request: {json.dumps(test['payload'], indent=2)}")
    
    response = requests.post(API_URL, json=test['payload'])
    result = response.json()
    
    print(f"\nResponse:")
    if result.get('success', True) and not result.get('status') == 'error':
        # Success case
        print(f"  ✅ SUCCESS")
        print(f"  Route: {result.get('route_used', 'N/A')}")
        print(f"  YTM: {result.get('ytm', 'N/A'):.3f}%" if result.get('ytm') else "  YTM: N/A")
        print(f"  Duration: {result.get('duration', 'N/A'):.3f}" if result.get('duration') else "  Duration: N/A")
        print(f"  Description: {result.get('description', 'N/A')}")
        print(f"  ISIN: {result.get('isin', 'N/A')}")
    else:
        # Error case
        print(f"  ❌ ERROR")
        print(f"  Status: {result.get('status', 'N/A')}")
        print(f"  Message: {result.get('message', 'N/A')}")
        if result.get('details'):
            print(f"  Details: {result['details']}")
        if result.get('suggestions'):
            print(f"  Suggestions:")
            for suggestion in result['suggestions']:
                print(f"    - {suggestion}")
    
    print("-" * 60)

print("\n📊 Summary:")
print("The ISIN lookup should now:")
print("1. Search databases for ISIN details")
print("2. Return helpful errors when ISIN not found")
print("3. Fall back to description when available")
print("4. Provide clear guidance to users")