#!/usr/bin/env python3
"""
Test API response times
"""

import requests
import time
import json

BASE_URL = "https://api.x-trillion.ai"
API_KEY = "gax10_maia_7k9d2m5p8w1e6r4t3y2x"

test_cases = [
    {
        "name": "Bond Analysis - Description",
        "endpoint": "/api/v1/bond/analysis",
        "data": {
            "description": "T 3 15/08/52",
            "price": 71.66,
            "settlement_date": "2025-08-01"
        }
    },
    {
        "name": "Bond Analysis - ISIN",
        "endpoint": "/api/v1/bond/analysis",
        "data": {
            "isin": "US912810TJ79",
            "price": 71.66
        }
    },
    {
        "name": "Bond Analysis - Portfolio Context",
        "endpoint": "/api/v1/bond/analysis",
        "data": {
            "description": "T 3 15/08/52",
            "price": 71.66,
            "context": "portfolio"
        }
    },
    {
        "name": "Flexible Analysis",
        "endpoint": "/api/v1/bond/analysis/flexible",
        "data": ["T 3 15/08/52", 71.66, "2025-08-01"]
    },
    {
        "name": "Portfolio Analysis",
        "endpoint": "/api/v1/portfolio/analysis",
        "data": {
            "data": [
                {
                    "description": "T 3 15/08/52",
                    "CLOSING PRICE": 71.66,
                    "WEIGHTING": 50.0
                },
                {
                    "description": "T 4.1 02/15/28",
                    "CLOSING PRICE": 99.5,
                    "WEIGHTING": 50.0
                }
            ]
        }
    }
]

print("API Response Time Analysis")
print("=" * 80)

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

for test in test_cases:
    print(f"\n{test['name']}:")
    print("-" * 60)
    
    # Measure response time
    start_time = time.time()
    
    try:
        response = requests.post(
            BASE_URL + test['endpoint'],
            headers=headers,
            json=test['data'],
            timeout=30
        )
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to ms
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if response contains timing info
            has_timing = False
            if 'metadata' in data and 'response_time' in data.get('metadata', {}):
                has_timing = True
                print(f"✅ Response includes timing: {data['metadata']['response_time']}")
            
            print(f"✅ Success - Response time: {response_time:.0f}ms")
            print(f"   Response size: {len(response.text)} bytes")
            
            # Check response headers for timing
            if 'X-Response-Time' in response.headers:
                print(f"   Header X-Response-Time: {response.headers['X-Response-Time']}")
            
            if not has_timing and 'X-Response-Time' not in response.headers:
                print("   ⚠️  No timing information in response")
                
        else:
            print(f"❌ Error {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

print("\n" + "=" * 80)
print("SUMMARY:")
print("- Response times vary based on calculation complexity")
print("- Cold starts may be slower (App Engine scaling)")
print("- Consider adding response timing to metadata for transparency")