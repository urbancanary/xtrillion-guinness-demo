#!/usr/bin/env python3
"""
Test script to verify XT_SMART regression issue
This simulates what XT_SMART function should be doing in Google Sheets
"""

import requests
import json

def test_portfolio_api():
    """Test the portfolio API endpoint that XT_SMART uses"""
    
    url = "http://localhost:8081/api/v1/portfolio/analysis"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "gax10_demo_3j5h8m9k2p6r4t7w1q"
    }
    
    # Simulate the payload that XT_SMART would send
    payload = {
        "data": [
            {
                "description": "T 3 15/08/52",
                "CLOSING PRICE": 71.66,
                "WEIGHTING": 1.0
            }
        ],
        "metrics": ["ytm", "duration", "spread"]
    }
    
    print("Testing portfolio API endpoint that XT_SMART uses...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nResponse Status: {response.status_code}")
            print(f"Full Response: {json.dumps(data, indent=2)}")
            
            if 'bond_data' in data and len(data['bond_data']) > 0:
                bond = data['bond_data'][0]
                print(f"\nBond Data Analysis:")
                print(f"  Yield: {repr(bond.get('yield'))} (type: {type(bond.get('yield'))})")
                print(f"  Duration: {repr(bond.get('duration'))} (type: {type(bond.get('duration'))})")
                print(f"  Spread: {repr(bond.get('spread'))} (type: {type(bond.get('spread'))})")
                
                # This is what XT_SMART would extract
                ytm = bond.get('yield')
                duration = bond.get('duration') 
                spread = bond.get('spread')
                
                print(f"\nWhat XT_SMART should extract:")
                print(f"  YTM: {ytm}")
                print(f"  Duration: {duration}")
                print(f"  Spread: {spread}")
                
                # Check if these are raw numbers or formatted strings
                if isinstance(ytm, (int, float)):
                    print(f"  ✅ YTM is a raw number: {ytm}")
                elif isinstance(ytm, str) and '%' in ytm:
                    print(f"  ❌ YTM is a formatted string: {ytm}")
                else:
                    print(f"  ⚠️  YTM type unexpected: {type(ytm)} - {repr(ytm)}")
                    
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_portfolio_api()