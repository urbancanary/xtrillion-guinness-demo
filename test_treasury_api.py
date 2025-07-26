#!/usr/bin/env python3
"""
Test Treasury API endpoint with Method 3
"""

import requests
import json

# Test the API with our Treasury bond
api_url = "http://localhost:8080/api/v1/portfolio/analyze"

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
    "X-API-Key": "gax10_test_9r4t7w2k5m8p1z6x3v"  # Test API key
}

print("🌐 Testing Treasury bond via API...")
print(f"Data: {test_data}")
print()

try:
    response = requests.post(api_url, json=test_data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print("Response:")
    
    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2))
        
        # Look for our Treasury bond in the results
        if 'portfolio' in result and 'holdings' in result['portfolio']:
            treasury_holding = result['portfolio']['holdings'][0] if result['portfolio']['holdings'] else None
            if treasury_holding:
                print()
                print("🏛️ Treasury Bond Results:")
                print(f"Yield: {treasury_holding.get('yield', 'N/A')}")
                print(f"Duration: {treasury_holding.get('duration', 'N/A')}")
                print(f"Price: {treasury_holding.get('price', 'N/A')}")
    else:
        print(response.text)
        
except Exception as e:
    print(f"❌ API Error: {e}")
