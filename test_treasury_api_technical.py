#!/usr/bin/env python3
"""
Test Treasury API endpoint with technical details
"""

import requests
import json

# Test the API with technical details
api_url = "http://localhost:8080/api/v1/portfolio/analyze?technical=true"

test_data = {
    "data": [{
        "BOND_CD": "US912810TJ79", 
        "CLOSING PRICE": 71.66,
        "WEIGHTING": 100.0,
        "Inventory Date": "2025/06/30"
    }]
}

headers = {
    "Content-Type": "application/json",
    "X-API-Key": "gax10_test_9r4t7w2k5m8p1z6x3v"
}

print("🔧 Testing Treasury bond via API (technical details)...")
print(f"Data: {test_data}")
print()

try:
    response = requests.post(api_url, json=test_data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("Technical Response:")
        print(json.dumps(result, indent=2))
    else:
        print("Error Response:")
        print(response.text)
        
except Exception as e:
    print(f"❌ API Error: {e}")
