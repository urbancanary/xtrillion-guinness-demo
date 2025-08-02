#!/usr/bin/env python3
"""
Test the spread calculation fix
Tests both treasury bonds (should have 0 spread) and corporate bonds (should have positive spread)
"""

import sys
import os
sys.path.append('.')

from bond_master_hierarchy import calculate_bond_master
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_spread_calculations():
    """Test the fixed spread calculation functionality"""
    
    print("🧪 Testing Spread Calculation Fix")
    print("=" * 50)
    
    # Test 1: Treasury bond (should have 0 spread)
    print("\n1️⃣ Treasury Bond Test (should have 0 spread)")
    print("-" * 40)
    
    treasury_result = calculate_bond_master(
        description="T 3 15/08/52", 
        price=71.66,
        settlement_date="2025-07-30"
    )
    
    if treasury_result.get('success'):
        spread = treasury_result.get('spread', 'NOT_FOUND')
        print(f"✅ Treasury Result:")
        print(f"   Description: T 3 15/08/52")
        print(f"   Yield: {treasury_result.get('yield', 'N/A'):.3f}%")
        print(f"   Spread: {spread} bps (should be 0)")
        print(f"   Status: {'✅ PASS' if spread == 0 else '❌ FAIL'}")
    else:
        print(f"❌ Treasury calculation failed: {treasury_result.get('error', 'Unknown error')}")
    
    # Test 2: Corporate bond (should have positive spread)
    print("\n2️⃣ Corporate Bond Test (should have positive spread)")
    print("-" * 40)
    
    corporate_result = calculate_bond_master(
        description="SAUDI ARAB OIL, 4.25%, 16-Apr-2039",
        price=87.14,
        settlement_date="2025-07-30"
    )
    
    if corporate_result.get('success'):
        spread = corporate_result.get('spread', 'NOT_FOUND')
        print(f"✅ Corporate Result:")
        print(f"   Description: SAUDI ARAB OIL, 4.25%, 16-Apr-2039")
        print(f"   Yield: {corporate_result.get('yield', 'N/A'):.3f}%")
        print(f"   Spread: {spread} bps")
        
        if isinstance(spread, (int, float)) and spread > 0:
            print(f"   Status: ✅ PASS (positive spread: {spread:.0f} bps)")
        elif spread == 'NOT_FOUND' or spread is None:
            print(f"   Status: ❌ FAIL (spread not calculated)")
        else:
            print(f"   Status: ❌ FAIL (invalid spread: {spread})")
    else:
        print(f"❌ Corporate calculation failed: {corporate_result.get('error', 'Unknown error')}")
    
    # Test 3: Another corporate bond
    print("\n3️⃣ Additional Corporate Bond Test")
    print("-" * 40)
    
    corporate2_result = calculate_bond_master(
        description="ECOPETROL SA, 5.875%, 28-May-2045",
        price=69.31,
        settlement_date="2025-07-30"
    )
    
    if corporate2_result.get('success'):
        spread = corporate2_result.get('spread', 'NOT_FOUND')
        print(f"✅ ECOPETROL Result:")
        print(f"   Description: ECOPETROL SA, 5.875%, 28-May-2045")
        print(f"   Yield: {corporate2_result.get('yield', 'N/A'):.3f}%")
        print(f"   Spread: {spread} bps")
        
        if isinstance(spread, (int, float)) and spread > 0:
            print(f"   Status: ✅ PASS (positive spread: {spread:.0f} bps)")
        else:
            print(f"   Status: ❌ FAIL (spread: {spread})")
    else:
        print(f"❌ ECOPETROL calculation failed: {corporate2_result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("- Treasury bonds should have 0 spread (risk-free benchmark)")
    print("- Corporate bonds should have positive spread (credit risk)")
    print("- Typical corporate spreads: 100-500+ basis points")

def test_api_integration():
    """Test if the fix works with the actual API"""
    print("\n🌐 Testing API Integration")
    print("-" * 40)
    
    import requests
    
    # Test the live API
    api_url = "https://future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "gax10_demo_3j5h8m9k2p6r4t7w1q"
    }
    
    # Test corporate bond via API
    payload = {
        "description": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039",
        "price": 87.14
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                analytics = result.get('analytics', {})
                spread = analytics.get('spread')
                print(f"✅ API Test Result:")
                print(f"   Saudi Arab Oil spread: {spread}")
                
                if spread is not None and spread != 0:
                    print(f"   Status: ✅ PASS - API returns spread: {spread} bps")
                else:
                    print(f"   Status: ❌ FAIL - API still returns null/0 spread")
            else:
                print(f"❌ API returned error: {result.get('error', 'Unknown')}")
        else:
            print(f"❌ API request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API test failed: {e}")

if __name__ == "__main__":
    test_spread_calculations()
    test_api_integration()
