#!/usr/bin/env python3
"""
Debug script to trace ISIN route processing
"""

import requests
import json

# Test both routes
test_cases = [
    {
        "name": "Description route (T 3 15/08/52)",
        "payload": {
            "description": "T 3 15/08/52",
            "price": 71.66,
            "settlement_date": "2025-08-01"
        }
    },
    {
        "name": "ISIN route (US912810TJ79)",
        "payload": {
            "isin": "US912810TJ79",
            "price": 71.66,
            "settlement_date": "2025-08-01"
        }
    },
    {
        "name": "Both ISIN and description",
        "payload": {
            "isin": "US912810TJ79",
            "description": "T 3 15/08/52",
            "price": 71.66,
            "settlement_date": "2025-08-01"
        }
    }
]

API_URL = "https://development-dot-future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis"

print("=== ISIN Route Debugging ===\n")

for test in test_cases:
    print(f"Test: {test['name']}")
    print(f"Payload: {json.dumps(test['payload'], indent=2)}")
    
    response = requests.post(API_URL, json=test['payload'])
    result = response.json()
    
    # Extract key fields
    print(f"\nResults:")
    print(f"  Route used: {result.get('route_used', 'N/A')}")
    print(f"  YTM: {result.get('ytm', 'N/A'):.3f}%" if result.get('ytm') else "  YTM: N/A")
    print(f"  Duration: {result.get('duration', 'N/A'):.3f}" if result.get('duration') else "  Duration: N/A")
    print(f"  Convexity: {result.get('convexity', 'N/A'):.3f}" if result.get('convexity') else "  Convexity: N/A")
    print(f"  Accrued Interest: {result.get('accrued_interest', 'N/A'):.3f}" if result.get('accrued_interest') else "  Accrued Interest: N/A")
    print(f"  Description in result: {result.get('description', 'N/A')}")
    print(f"  ISIN in result: {result.get('isin', 'N/A')}")
    print(f"  Success: {result.get('success', False)}")
    
    if result.get('error'):
        print(f"  Error: {result['error']}")
    
    print("-" * 60)
    print()

print("\n🔍 CONCLUSION:")
print("The ISIN route appears to be using the ISIN as a description,")
print("which causes the parser to fail and return incorrect bond data.")
print("This explains why the analytics are completely different.")