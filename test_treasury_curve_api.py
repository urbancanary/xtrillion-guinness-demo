#!/usr/bin/env python3
"""
Test if API is using updated Treasury yield curve
"""

import requests
import json
from datetime import datetime

# API configuration
API_URL = "https://future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis"
API_KEY = "gax10_test_9r4t7w2k5m8p1z6x3v"

def test_treasury_curve():
    """Test if the API is using updated Treasury data."""
    
    # Test bond: 10-year Treasury
    test_bond = {
        "description": "T 4.25 05/15/35",
        "price": 100.0,  # At par
        "settlement_date": "2025-07-31"
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    print("🔍 Testing Treasury Yield Curve in API")
    print("=" * 40)
    print(f"API URL: {API_URL}")
    print(f"Settlement: {test_bond['settlement_date']}")
    print(f"Bond: {test_bond['description']} @ ${test_bond['price']}")
    print()
    
    try:
        response = requests.post(API_URL, headers=headers, json=test_bond)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') == 'success' or 'analytics' in data:
            analytics = data.get('analytics', data.get('results', {}).get('analytics', {}))
            
            print("✅ API Response:")
            print(f"   YTM: {analytics.get('ytm', 'N/A'):.4f}%")
            print(f"   Duration: {analytics.get('duration', 'N/A'):.4f} years")
            print(f"   Z-Spread: {analytics.get('z_spread', 'N/A')}")
            print()
            
            # The Z-spread would be different with updated Treasury curve
            if analytics.get('z_spread') is not None:
                print("📊 Z-spread calculation indicates Treasury curve is being used")
            else:
                print("⚠️  Z-spread not calculated - Treasury curve may not be available")
                
        else:
            print(f"❌ API Error: {data.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test portfolio endpoint which might show more info
    print("\n" + "=" * 40)
    print("📦 Testing Portfolio Endpoint...")
    
    portfolio_url = API_URL.replace('/bond/analysis', '/portfolio/analysis')
    portfolio_data = {
        "data": [{
            "description": "T 4.25 05/15/35",
            "CLOSING PRICE": 100.0,
            "WEIGHTING": 100.0,
            "Inventory Date": "2025/07/31"
        }]
    }
    
    try:
        response = requests.post(portfolio_url, headers=headers, json=portfolio_data)
        response.raise_for_status()
        
        data = response.json()
        if 'portfolio_summary' in data:
            summary = data['portfolio_summary']
            print("✅ Portfolio calculation successful")
            print(f"   Portfolio YTM: {summary.get('weighted_ytm', 'N/A')}%")
            
            # Check metadata for database info
            if 'metadata' in data:
                print(f"\n🗒️  Metadata:")
                for key, value in data['metadata'].items():
                    if 'date' in key.lower() or 'treasury' in key.lower():
                        print(f"   {key}: {value}")
        else:
            print(f"❌ Portfolio error: {data.get('error', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Portfolio request failed: {e}")

if __name__ == "__main__":
    test_treasury_curve()