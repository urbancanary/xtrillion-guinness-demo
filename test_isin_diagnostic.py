#!/usr/bin/env python3
"""
🔍 ISIN vs Description Diagnostic Test
Compares ISIN-only vs description-only vs combined input to understand current API behavior
"""

import requests
import json

# API Configuration
API_BASE = "https://future-footing-414610.uc.r.appspot.com"
API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q"

def test_bond_inputs(isin, description, price):
    """Test different input combinations for the same bond"""
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    results = {}
    
    # Test 1: ISIN only
    print(f"🔍 Test 1: ISIN only")
    try:
        payload = {"isin": isin, "price": price}
        response = requests.post(f"{API_BASE}/api/v1/bond/analysis", json=payload, headers=headers, timeout=15)
        results['isin_only'] = {
            'status_code': response.status_code,
            'response': response.json() if response.status_code == 200 else response.text[:200]
        }
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        results['isin_only'] = {'error': str(e)}
        print(f"   Exception: {e}")
    
    # Test 2: Description only
    print(f"🔍 Test 2: Description only")
    try:
        payload = {"description": description, "price": price}
        response = requests.post(f"{API_BASE}/api/v1/bond/analysis", json=payload, headers=headers, timeout=15)
        results['description_only'] = {
            'status_code': response.status_code,
            'response': response.json() if response.status_code == 200 else response.text[:200]
        }
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            analytics = response.json().get('analytics', {})
            print(f"   Yield: {analytics.get('ytm', 'N/A'):.6f}%")
            print(f"   Duration: {analytics.get('duration', 'N/A'):.6f} years")
            print(f"   Spread: {analytics.get('spread', 'N/A') or 0:.0f} bps")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        results['description_only'] = {'error': str(e)}
        print(f"   Exception: {e}")
    
    # Test 3: Both ISIN and description
    print(f"🔍 Test 3: Both ISIN and description")
    try:
        payload = {"isin": isin, "description": description, "price": price}
        response = requests.post(f"{API_BASE}/api/v1/bond/analysis", json=payload, headers=headers, timeout=15)
        results['both'] = {
            'status_code': response.status_code,
            'response': response.json() if response.status_code == 200 else response.text[:200]
        }
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            analytics = response.json().get('analytics', {})
            print(f"   Yield: {analytics.get('ytm', 'N/A'):.6f}%")
            print(f"   Duration: {analytics.get('duration', 'N/A'):.6f} years")
            print(f"   Spread: {analytics.get('spread', 'N/A') or 0:.0f} bps")
        else:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        results['both'] = {'error': str(e)}
        print(f"   Exception: {e}")
    
    # Test 4: ISIN as description (what the failing test was actually doing)
    print(f"🔍 Test 4: ISIN as description field")
    try:
        payload = {"description": isin, "price": price}  # This is what was failing
        response = requests.post(f"{API_BASE}/api/v1/bond/analysis", json=payload, headers=headers, timeout=15)
        results['isin_as_description'] = {
            'status_code': response.status_code,
            'response': response.json() if response.status_code == 200 else response.text[:200]
        }
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text[:100]}")
    except Exception as e:
        results['isin_as_description'] = {'error': str(e)}
        print(f"   Exception: {e}")
    
    return results

def main():
    """Test different input methods with known working bonds"""
    
    print("🔍 ISIN vs Description Diagnostic Test")
    print("=" * 70)
    
    # Test bonds - using known working examples
    test_bonds = [
        {
            'isin': 'US912810TJ79',
            'description': 'T 3 15/08/52',  # Treasury format that should work
            'price': 71.66,
            'name': 'US Treasury'
        },
        {
            'isin': 'US279158AJ82',
            'description': 'ECOPETROL SA, 5.875%, 28-May-2045',  # Full description format
            'price': 69.31,
            'name': 'Ecopetrol'
        },
        {
            'isin': 'US698299BL70',
            'description': 'PANAMA, 3.87%, 23-Jul-2060',  # Another known format
            'price': 56.60,
            'name': 'Panama'
        }
    ]
    
    for i, bond in enumerate(test_bonds):
        print(f"\n📊 BOND {i+1}: {bond['name']} ({bond['isin']})")
        print(f"   ISIN: {bond['isin']}")
        print(f"   Description: {bond['description']}")
        print(f"   Price: {bond['price']}")
        print("-" * 70)
        
        results = test_bond_inputs(bond['isin'], bond['description'], bond['price'])
        
        print("\n📋 SUMMARY:")
        for test_name, result in results.items():
            if isinstance(result, dict) and 'status_code' in result:
                status = "✅ SUCCESS" if result['status_code'] == 200 else "❌ FAILED"
                print(f"   {test_name}: {status} ({result['status_code']})")
            else:
                print(f"   {test_name}: ❌ EXCEPTION")
        
        print("=" * 70)
    
    print("\n🎯 KEY FINDINGS:")
    print("   • ISIN-only lookups: Status shown above")
    print("   • Description-only lookups: Status shown above") 
    print("   • Combined lookups: Status shown above")
    print("   • This reveals what input format actually works")

if __name__ == "__main__":
    main()
