#!/usr/bin/env python3
"""Debug spread calculation in production vs local"""

import sys
import requests
import json
from bond_master_hierarchy_enhanced import calculate_bond_master

def test_local_spread():
    """Test local spread calculation"""
    print("🧪 Testing LOCAL spread calculation...")
    
    # Test Treasury bond - Fix parameter order
    print("\n1. Treasury Bond: T 3 15/08/52")
    try:
        result = calculate_bond_master(
            description="T 3 15/08/52", 
            price=71.66,
            settlement_date="2025-07-30"  # Use date when yields are available
        )
        print(f"   Spread: {result.get('spread')}")
        print(f"   Z-spread: {result.get('z_spread')}")
        print(f"   Status: {result.get('status')}")
        print(f"   YTM: {result.get('ytm')}")
        if result.get('error'):
            print(f"   Error details: {result.get('error')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test Corporate bond
    print("\n2. Corporate Bond: ECOPETROL SA, 5.875%, 28-May-2045")
    try:
        result = calculate_bond_master(
            description="ECOPETROL SA, 5.875%, 28-May-2045", 
            price=69.31,
            settlement_date="2025-07-30"  # Use date when yields are available
        )
        print(f"   Spread: {result.get('spread')}")
        print(f"   Z-spread: {result.get('z_spread')}")
        print(f"   Status: {result.get('status')}")
        print(f"   YTM: {result.get('ytm')}")
        if result.get('error'):
            print(f"   Error details: {result.get('error')}")
    except Exception as e:
        print(f"   Error: {e}")

def test_production_spread():
    """Test production API spread calculation"""
    print("\n🌐 Testing PRODUCTION API spread calculation...")
    
    base_url = "https://future-footing-414610.uc.r.appspot.com"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "gax10_demo_3j5h8m9k2p6r4t7w1q"
    }
    
    bonds = [
        {"description": "T 3 15/08/52", "price": 71.66, "name": "Treasury"},
        {"description": "ECOPETROL SA, 5.875%, 28-May-2045", "price": 69.31, "name": "Corporate"}
    ]
    
    for bond in bonds:
        print(f"\n{bond['name']} Bond: {bond['description']}")
        try:
            response = requests.post(
                f"{base_url}/api/v1/bond/analysis",
                headers=headers,
                json={
                    "description": bond["description"],
                    "price": bond["price"]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                analytics = data.get("analytics", {})
                print(f"   Spread: {analytics.get('spread')}")
                print(f"   Z-spread: {analytics.get('z_spread')}")
                print(f"   Status: {data.get('status')}")
                print(f"   YTM: {analytics.get('ytm')}")
            else:
                print(f"   HTTP Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   Error: {e}")

def test_treasury_yield_availability():
    """Check if treasury yield data is available"""
    print("\n📊 Testing treasury yield data availability...")
    
    try:
        from google_analysis10 import fetch_treasury_yields
        from datetime import datetime
        
        # Test current date
        trade_date = datetime.now().strftime('%Y-%m-%d')
        yields = fetch_treasury_yields(trade_date, './bonds_data.db')
        
        if yields:
            print(f"   ✅ Treasury yields available for {trade_date}")
            print(f"   Available yields: {list(yields.keys())}")
            print(f"   Sample yield (1Y): {yields.get('1Y', 'N/A')}")
        else:
            print(f"   ❌ No treasury yields available for {trade_date}")
            
        # Test fallback date
        fallback_date = "2025-07-30"  # Known date
        yields = fetch_treasury_yields(fallback_date, './bonds_data.db')
        
        if yields:
            print(f"   ✅ Treasury yields available for {fallback_date} (fallback)")
            print(f"   Available yields: {list(yields.keys())}")
        else:
            print(f"   ❌ No treasury yields available for {fallback_date} (fallback)")
            
    except Exception as e:
        print(f"   Error checking treasury yields: {e}")

if __name__ == "__main__":
    print("🔍 SPREAD CALCULATION DEBUG")
    print("=" * 50)
    
    # Test local calculation
    test_local_spread()
    
    # Test production API
    test_production_spread()
    
    # Test treasury yield data
    test_treasury_yield_availability()
    
    print("\n🏁 Debug complete!")
