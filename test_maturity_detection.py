#!/usr/bin/env python3
"""
Test Maturity Detection
======================

Test the new maturity detection logic to ensure bonds that have expired
return appropriate responses instead of invalid analytics.
"""

import requests
import json
from datetime import datetime, date

# Test configurations
API_BASE = "http://localhost:8080"  # Local testing
API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q"

def test_maturity_detection():
    """Test maturity detection with various bonds"""
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    print("🧪 Testing Maturity Detection Logic")
    print("=" * 50)
    
    # Test cases
    test_bonds = [
        {
            "description": "T 4.625 02/15/25",  # MATURED in Feb 2025
            "price": 99.5,
            "expected_status": "matured",
            "note": "Should be matured (Feb 2025 vs current July 2025)"
        },
        {
            "description": "T 3 15/08/52",     # ACTIVE until Aug 2052
            "price": 71.66,
            "expected_status": "success", 
            "note": "Should be active (matures Aug 2052)"
        },
        {
            "description": "T 2.5 05/31/24",   # MATURED in May 2024
            "price": 100.0,
            "expected_status": "matured",
            "note": "Should be matured (May 2024 vs current July 2025)"
        }
    ]
    
    for i, bond in enumerate(test_bonds, 1):
        print(f"\n{i}️⃣ Testing: {bond['description']}")
        print(f"   Expected: {bond['expected_status']} - {bond['note']}")
        
        try:
            response = requests.post(f"{API_BASE}/api/v1/bond/parse-and-calculate", 
                                   json=bond, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                actual_status = data.get('status')
                
                print(f"   ✅ Response Status: {actual_status}")
                
                if actual_status == "matured":
                    # Check matured bond response structure
                    maturity_info = data.get('maturity_info', {})
                    print(f"   📅 Maturity Date: {maturity_info.get('maturity_date')}")
                    print(f"   📅 Settlement Date: {maturity_info.get('settlement_date')}")
                    print(f"   ⚠️  Message: {maturity_info.get('message')}")
                    print(f"   📊 Analytics Status: All null/zero as expected")
                    
                    # Verify analytics are null/zero
                    analytics = data.get('analytics', {})
                    non_null_metrics = {k: v for k, v in analytics.items() 
                                      if v is not None and v != 0 and k != 'settlement_date'}
                    
                    if not non_null_metrics:
                        print(f"   ✅ Correct: All analytics null/zero for matured bond")
                    else:
                        print(f"   ❌ Error: Found non-null metrics: {non_null_metrics}")
                        
                elif actual_status == "success":
                    # Check active bond response
                    analytics = data.get('analytics', {})
                    ytm = analytics.get('ytm')
                    duration = analytics.get('duration')
                    
                    print(f"   📊 YTM: {ytm}")
                    print(f"   📊 Duration: {duration}")
                    
                    if ytm and duration:
                        print(f"   ✅ Correct: Active bond with valid analytics")
                    else:
                        print(f"   ❌ Error: Active bond missing analytics")
                
                # Check if result matches expectation
                if actual_status == bond['expected_status']:
                    print(f"   🎯 PASS: Status matches expectation")
                else:
                    print(f"   ❌ FAIL: Expected {bond['expected_status']}, got {actual_status}")
                    
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Maturity detection test complete!")
    print()
    print("💡 Expected behavior:")
    print("   - Bonds past maturity → status: 'matured', analytics: null/zero")
    print("   - Active bonds → status: 'success', analytics: calculated values") 
    print("   - Clear maturity messages for expired bonds")

if __name__ == "__main__":
    test_maturity_detection()
