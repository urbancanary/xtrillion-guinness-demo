#!/usr/bin/env python3
"""
Test settlement date impact on YTM calculations
"""

import requests
import json

def test_settlement_impact():
    """Test how settlement date affects YTM calculations"""
    
    url = 'https://development-dot-future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis'
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': 'gax10_test_8k3n6p9v2x1m4z7q'
    }
    
    bond_data = {
        "description": "T 3 15/08/52",
        "price": 71.66
    }
    
    print("🧪 Testing Settlement Date Impact on YTM")
    print("=" * 50)
    
    # Test 1: No settlement date (uses default)
    response1 = requests.post(url, headers=headers, json=bond_data)
    data1 = response1.json()
    ytm1 = data1['analytics']['ytm']
    settlement1 = data1['analytics']['settlement_date']
    
    print(f"1. Default settlement: {settlement1}")
    print(f"   YTM: {ytm1:.8f}%")
    
    # Test 2: June 30, 2025 (Bloomberg comparison date)
    bond_data_june = bond_data.copy()
    bond_data_june['settlement_date'] = '2025-06-30'
    
    response2 = requests.post(url, headers=headers, json=bond_data_june)
    data2 = response2.json()
    ytm2 = data2['analytics']['ytm']
    settlement2 = data2['analytics']['settlement_date']
    
    print(f"\n2. June 30 settlement: {settlement2}")
    print(f"   YTM: {ytm2:.8f}%")
    
    # Test 3: August 14, 2025 (current fresh data)
    bond_data_aug = bond_data.copy()
    bond_data_aug['settlement_date'] = '2025-08-14'
    
    response3 = requests.post(url, headers=headers, json=bond_data_aug)
    data3 = response3.json()
    ytm3 = data3['analytics']['ytm']
    settlement3 = data3['analytics']['settlement_date']
    
    print(f"\n3. August 14 settlement: {settlement3}")
    print(f"   YTM: {ytm3:.8f}%")
    
    print(f"\n📊 Analysis:")
    print(f"   Bloomberg YTM (June 30): 4.89916%")
    print(f"   Our YTM (June 30):      {ytm2:.5f}% (diff: {abs(ytm2 - 4.89916):.5f}%)")
    print(f"   Our YTM (July 31):      {ytm1:.5f}% (diff: {abs(ytm1 - 4.89916):.5f}%)")
    print(f"   Our YTM (Aug 14):       {ytm3:.5f}% (diff: {abs(ytm3 - 4.89916):.5f}%)")
    
    print(f"\n🎯 Conclusion:")
    if abs(ytm2 - 4.89916) < 0.01:
        print("   ✅ June 30 settlement matches Bloomberg perfectly!")
    print(f"   📋 Google Sheets is using: {settlement1} → {ytm1:.5f}%")
    print(f"   📋 Bloomberg comparison used: 2025-06-30 → {ytm2:.5f}%")

if __name__ == "__main__":
    test_settlement_impact()