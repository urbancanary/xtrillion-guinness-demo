#!/usr/bin/env python3
"""
Quick Test: ISIN vs Description Field Mapping Issue
=================================================
Test individual bond to see field differences between ISIN and description inputs
"""

import requests
import json

# Local API Configuration
BASE_URL = "http://localhost:8080"
API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q"

headers = {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
}

def test_individual_bond(bond_input, test_name):
    """Test individual bond analysis"""
    print(f"\n🧪 Testing {test_name}")
    print("=" * 50)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/bond/analysis",
            headers=headers,
            json={
                "description": bond_input,
                "price": 71.66
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS")
            print(f"📊 Analytics fields returned:")
            analytics = result.get('analytics', {})
            for key, value in analytics.items():
                print(f"   {key}: {value}")
            return result
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_portfolio_single_bond(bond_input, test_name):
    """Test single bond in portfolio format"""
    print(f"\n📊 Testing Portfolio Format: {test_name}")
    print("=" * 50)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/portfolio/analysis",
            headers=headers,
            json={
                "data": [
                    {
                        "BOND_CD": bond_input,
                        "CLOSING PRICE": 71.66,
                        "WEIGHTING": 100.0
                    }
                ]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS")
            bond_data = result.get('bond_data', [])
            if bond_data:
                bond = bond_data[0]
                print(f"📊 YAS formatted fields:")
                for key, value in bond.items():
                    print(f"   {key}: {value}")
            return result
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    """Test field mapping differences"""
    print("🔍 Field Mapping Diagnosis Test")
    print("=" * 80)
    
    # Test same bond with ISIN vs Description
    isin_input = "US912810TJ79"
    desc_input = "T 3 15/08/52"
    
    # Test individual bond endpoint
    print("\n🔧 INDIVIDUAL BOND ANALYSIS ENDPOINT TESTS:")
    isin_individual = test_individual_bond(isin_input, "ISIN Individual")
    desc_individual = test_individual_bond(desc_input, "Description Individual")
    
    # Test portfolio endpoint  
    print("\n\n📊 PORTFOLIO ANALYSIS ENDPOINT TESTS:")
    isin_portfolio = test_portfolio_single_bond(isin_input, "ISIN Portfolio")
    desc_portfolio = test_portfolio_single_bond(desc_input, "Description Portfolio")
    
    # Compare results
    print("\n\n🔍 COMPARISON ANALYSIS:")
    print("=" * 80)
    
    if isin_individual and desc_individual:
        print("📈 Individual Bond Analytics Comparison:")
        isin_analytics = isin_individual.get('analytics', {})
        desc_analytics = desc_individual.get('analytics', {})
        
        print(f"   ISIN YTM: {isin_analytics.get('ytm', 'MISSING')}")
        print(f"   DESC YTM: {desc_analytics.get('ytm', 'MISSING')}")
        print(f"   ISIN Duration: {isin_analytics.get('duration', 'MISSING')}")
        print(f"   DESC Duration: {desc_analytics.get('duration', 'MISSING')}")
    
    if isin_portfolio and desc_portfolio:
        print("\n📊 Portfolio YAS Format Comparison:")
        isin_bond = isin_portfolio.get('bond_data', [{}])[0]
        desc_bond = desc_portfolio.get('bond_data', [{}])[0]
        
        print(f"   ISIN Status: {isin_bond.get('status', 'MISSING')}")
        print(f"   DESC Status: {desc_bond.get('status', 'MISSING')}")
        print(f"   ISIN Yield: {isin_bond.get('yield', 'MISSING')}")
        print(f"   DESC Yield: {desc_bond.get('yield', 'MISSING')}")
        print(f"   ISIN Duration: {isin_bond.get('duration', 'MISSING')}")
        print(f"   DESC Duration: {desc_bond.get('duration', 'MISSING')}")
    
    print("\n🎯 DIAGNOSIS COMPLETE")
    print("This will help identify the exact field mapping issue!")

if __name__ == "__main__":
    main()
