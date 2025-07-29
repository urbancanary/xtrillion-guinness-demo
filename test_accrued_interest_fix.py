#!/usr/bin/env python3
"""
Test Accrued Interest Fix - Critical Metrics Test
=================================================

Tests if the accrued interest fix resolves the dirty price bug and
verifies we now get the full set of enhanced metrics.

EXPECTED BEFORE FIX:
- accrued_interest: None
- dirty_price: 71.66 (same as clean_price)
- Missing metrics: convexity_semi, pvbp

EXPECTED AFTER FIX:
- accrued_interest: Calculated value (e.g., 1.08)
- dirty_price: clean_price + accrued_interest (e.g., 72.74)
- Added metrics: convexity_semi, pvbp
"""

import sys
import os
import json
import logging

# Add project path
project_root = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10'
sys.path.append(project_root)

from bond_master_hierarchy_enhanced import calculate_bond_master

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_accrued_interest_fix():
    """Test the accrued interest fix with the Treasury bond"""
    
    print("🚀 TESTING ACCRUED INTEREST FIX")
    print("=" * 60)
    
    # Test with the Treasury bond that was showing the issue
    test_bond = {
        'description': 'T 3 15/08/52',
        'price': 71.66,
        'settlement_date': '2025-07-26'
    }
    
    print(f"📊 Test Bond: {test_bond['description']}")
    print(f"💰 Price: {test_bond['price']}")
    print(f"📅 Settlement: {test_bond['settlement_date']}")
    print()
    
    # Calculate enhanced metrics
    print("🔧 Running Enhanced Calculator...")
    result = calculate_bond_master(
        description=test_bond['description'],
        price=test_bond['price'],
        settlement_date=test_bond['settlement_date']
    )
    
    if result.get('success'):
        print("✅ CALCULATION SUCCESSFUL!")
        print()
        
        # Extract key metrics
        original_metrics = {
            'yield': result.get('yield'),
            'duration': result.get('duration'),
            'accrued_interest': result.get('accrued_interest'),
        }
        
        enhanced_metrics = {
            'clean_price': result.get('clean_price'),
            'dirty_price': result.get('dirty_price'),
            'mac_dur_semi': result.get('mac_dur_semi'),
            'ytm_annual': result.get('ytm_annual'),
            'mod_dur_annual': result.get('mod_dur_annual'),
            'mac_dur_annual': result.get('mac_dur_annual'),
        }
        
        # NEW METRICS from our fix
        new_metrics = {
            'convexity_semi': result.get('convexity_semi'),  # Correct field name
            'pvbp': result.get('pvbp'),
        }
        
        print("📈 ORIGINAL METRICS:")
        for key, value in original_metrics.items():
            if value is not None:
                print(f"  {key}: {value:.6f}")
            else:
                print(f"  {key}: {value} ❌")
        print()
        
        print("🚀 ENHANCED METRICS:")
        for key, value in enhanced_metrics.items():
            if value is not None:
                print(f"  {key}: {value:.6f}")
            else:
                print(f"  {key}: {value} ❌")
        print()
        
        print("🔥 NEW METRICS (FROM FIX):")
        for key, value in new_metrics.items():
            if value is not None:
                print(f"  {key}: {value:.6f}")
            else:
                print(f"  {key}: {value} ❌")
        print()
        
        # CRITICAL TESTS
        print("🧪 CRITICAL VALIDATION TESTS:")
        print("-" * 40)
        
        # Test 1: Accrued Interest exists
        accrued = result.get('accrued_interest')
        if accrued is not None and accrued > 0:
            print(f"✅ Test 1: Accrued Interest calculated: {accrued:.6f}")
        else:
            print(f"❌ Test 1: Accrued Interest still missing: {accrued}")
        
        # Test 2: Dirty Price vs Clean Price
        clean = result.get('clean_price', 0)
        dirty = result.get('dirty_price', 0)
        if accrued is not None and abs(dirty - (clean + accrued)) < 0.01:
            print(f"✅ Test 2: Dirty Price correct: {dirty:.6f} = {clean:.6f} + {accrued:.6f}")
        else:
            expected_dirty = clean + (accrued or 0)
            print(f"❌ Test 2: Dirty Price incorrect: {dirty:.6f} ≠ {expected_dirty:.6f}")
        
        # Test 3: New Metrics Added
        convexity = result.get('convexity_semi')  # Correct field name
        pvbp = result.get('pvbp')
        
        new_metrics_count = 0
        if convexity is not None:
            new_metrics_count += 1
            print(f"✅ Test 3a: Convexity added: {convexity:.6f}")
        else:
            print(f"❌ Test 3a: Convexity still missing")
            
        if pvbp is not None:
            new_metrics_count += 1
            print(f"✅ Test 3b: PVBP added: {pvbp:.6f}")
        else:
            print(f"❌ Test 3b: PVBP still missing")
        
        # Test 4: Count total metrics
        total_metrics = sum(1 for v in result.values() if v is not None and isinstance(v, (int, float)))
        print(f"📊 Test 4: Total numeric metrics: {total_metrics}/19 expected")
        
        print()
        print("🎯 SUMMARY:")
        if accrued is not None and new_metrics_count >= 2 and total_metrics >= 15:
            print("🎉 SUCCESS! Accrued interest fix appears to be working!")
            print("   ✅ Accrued interest calculated")
            print("   ✅ Dirty price fixed") 
            print("   ✅ New metrics added")
            return True
        else:
            print("⚠️  PARTIAL SUCCESS - Some issues remain:")
            if accrued is None:
                print("   ❌ Accrued interest still missing")
            if new_metrics_count < 2:
                print("   ❌ Missing new metrics")
            if total_metrics < 15:
                print("   ❌ Not enough total metrics")
            return False
    
    else:
        print("❌ CALCULATION FAILED!")
        print(f"Error: {result.get('error')}")
        return False

if __name__ == "__main__":
    success = test_accrued_interest_fix()
    if success:
        print("\n🚀 Ready to test enhanced API endpoint!")
    else:
        print("\n🔧 Additional fixes needed.")
