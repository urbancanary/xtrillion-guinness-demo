#!/usr/bin/env python3
"""
Debug Script to Find Treasury Frequency Issue
===========================================

Tests the exact Treasury bond that should give 16.35 duration
but is returning 16.60, to identify where the frequency issue occurs.
"""

import sys
import os
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

from bond_master_hierarchy import calculate_bond_master
import logging

# Set up detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_treasury_frequency_issue():
    """Debug the specific Treasury bond frequency issue"""
    
    print("🔍 DEBUGGING TREASURY FREQUENCY ISSUE")
    print("=" * 60)
    
    # The Treasury bond that should give 16.35 but gives 16.60
    test_bond = {
        'isin': 'US912810TJ79',
        'description': 'US TREASURY N/B, 3%, 15-Aug-2052',
        'price': 71.66,
        'expected_yield': 4.89960,
        'expected_duration': 16.35658  # Bloomberg correct value
    }
    
    print(f"📊 Testing: {test_bond['description']}")
    print(f"📊 ISIN: {test_bond['isin']}")
    print(f"💰 Price: {test_bond['price']}")
    print(f"🎯 Expected Duration: {test_bond['expected_duration']}")
    print()
    
    # Test with ISIN (Route 1: ISIN Hierarchy)
    print("🔍 Route 1: ISIN Hierarchy")
    result_isin = calculate_bond_master(
        isin=test_bond['isin'],
        description=test_bond['description'],
        price=test_bond['price']
    )
    
    if result_isin['success']:
        actual_duration = result_isin['duration']
        duration_diff = abs(actual_duration - test_bond['expected_duration'])
        
        print(f"✅ Calculation Success:")
        print(f"   📈 Yield: {result_isin['yield']:.5f}% (expected: {test_bond['expected_yield']:.5f}%)")
        print(f"   ⏱️  Duration: {actual_duration:.5f} (expected: {test_bond['expected_duration']:.5f})")
        print(f"   📊 Duration Difference: {duration_diff:.5f}")
        print(f"   🎯 Route Used: {result_isin['route_used']}")
        
        # Check if we have the frequency issue
        if duration_diff > 0.2:  # More than 0.2 years difference
            print(f"🚨 FREQUENCY ISSUE DETECTED!")
            print(f"   Expected: {test_bond['expected_duration']:.5f}")
            print(f"   Actual:   {actual_duration:.5f}")
            print(f"   Difference: {duration_diff:.5f}")
            
            if actual_duration > test_bond['expected_duration']:
                print(f"   🔍 Analysis: Duration too HIGH - likely using ANNUAL frequency instead of SEMIANNUAL")
            else:
                print(f"   🔍 Analysis: Duration too LOW - unexpected error")
                
        else:
            print(f"✅ Duration calculation appears CORRECT!")
            
    else:
        print(f"❌ Calculation FAILED: {result_isin.get('error')}")
    
    print()
    
    # Test without ISIN (Route 2: Parse Hierarchy)  
    print("🔍 Route 2: Parse Hierarchy (no ISIN)")
    result_parse = calculate_bond_master(
        isin=None,  # No ISIN provided
        description=test_bond['description'],
        price=test_bond['price']
    )
    
    if result_parse['success']:
        actual_duration = result_parse['duration']
        duration_diff = abs(actual_duration - test_bond['expected_duration'])
        
        print(f"✅ Calculation Success:")
        print(f"   📈 Yield: {result_parse['yield']:.5f}% (expected: {test_bond['expected_yield']:.5f}%)")
        print(f"   ⏱️  Duration: {actual_duration:.5f} (expected: {test_bond['expected_duration']:.5f})")
        print(f"   📊 Duration Difference: {duration_diff:.5f}")
        print(f"   🎯 Route Used: {result_parse['route_used']}")
        
        # Check if we have the frequency issue
        if duration_diff > 0.2:  # More than 0.2 years difference
            print(f"🚨 FREQUENCY ISSUE DETECTED!")
            print(f"   Expected: {test_bond['expected_duration']:.5f}")
            print(f"   Actual:   {actual_duration:.5f}")
            print(f"   Difference: {duration_diff:.5f}")
            
            if actual_duration > test_bond['expected_duration']:
                print(f"   🔍 Analysis: Duration too HIGH - likely using ANNUAL frequency instead of SEMIANNUAL")
            else:
                print(f"   🔍 Analysis: Duration too LOW - unexpected error")
                
        else:
            print(f"✅ Duration calculation appears CORRECT!")
            
    else:
        print(f"❌ Calculation FAILED: {result_parse.get('error')}")
    
    print()
    print("🔍 FREQUENCY DEBUGGING RECOMMENDATIONS:")
    print("-" * 50)
    print("1. Check if Treasury bond is being detected correctly")
    print("2. Verify 'is_treasury' flag is being set to True")
    print("3. Confirm 'calculation_frequency' is ql.Semiannual in debug logs")
    print("4. Check if yield calculation uses same frequency as duration")
    print("5. Verify no Annual frequency override elsewhere in code")

if __name__ == "__main__":
    test_treasury_frequency_issue()
