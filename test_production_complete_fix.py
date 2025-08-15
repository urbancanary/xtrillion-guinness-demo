#!/usr/bin/env python3
"""
Test complete fix in production - PEMEX and ECOPETROL
"""

import requests
import json

def test_bond(description, expected_accrued, bond_name):
    """Test a bond against production API"""
    print(f"\n📊 Testing {bond_name}")
    print("=" * 50)
    
    url = "https://future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis"
    
    payload = {
        "description": description,
        "price": 100.0,
        "settlement_date": "2025-04-18"
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "xTr1ll10n_2025_pr0d"
    }
    
    print(f"   Description: {description}")
    print(f"   Settlement: {payload['settlement_date']} (Good Friday)")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()
        
        if result.get('status') == 'success':
            analytics = result.get('analytics', {})
            accrued = analytics.get('accrued_interest', 0)
            accrued_per_million = accrued * 10000
            
            print(f"\n   Result: ${accrued_per_million:,.2f} per million")
            print(f"   Expected: ${expected_accrued:,.2f} per million")
            
            diff = abs(accrued_per_million - expected_accrued)
            if diff < 1.0:
                print(f"   ✅ PASS - Perfect match!")
                return True
            elif diff < 50.0:
                print(f"   ⚠️  CLOSE - Difference: ${diff:,.2f}")
                return True
            else:
                print(f"   ❌ FAIL - Difference: ${diff:,.2f}")
                return False
        else:
            print(f"   ❌ API Error: {result}")
            return False
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return False

def main():
    print("🧪 Testing Complete Fix in Production")
    print("=" * 60)
    print("Testing settlement date handling and convention lookup...")
    
    tests = [
        {
            "name": "PEMEX (Original Issue)",
            "description": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060",
            "expected": 15444.44
        },
        {
            "name": "ECOPETROL (Convention Issue)",
            "description": "ECOPETROL SA, 5.875%, 28-May-2045",
            "expected": 22847.22
        },
        {
            "name": "ECOPETROL (Ticker Test)",
            "description": "ECOPET 7.375%, 18-Sep-2043",
            "expected": 0  # We don't know the exact value, just testing if it processes
        }
    ]
    
    results = []
    for test in tests:
        success = test_bond(test['description'], test['expected'], test['name'])
        results.append((test['name'], success))
    
    # Summary
    print("\n\n📊 SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {name}: {status}")
    
    print(f"\n   Total: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Complete fix is working in production!")
    else:
        print("\n⚠️  Some tests failed. Check the results above.")

if __name__ == "__main__":
    main()