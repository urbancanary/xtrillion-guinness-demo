#!/usr/bin/env python3
"""
🔍 Field Mapping Investigation
Check what fields are returned vs what API expects
"""

import sys
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

from bond_master_hierarchy_enhanced import calculate_bond_master
import json

def investigate_field_mapping():
    """Compare direct function output with API expectations"""
    
    print("🔍 FIELD MAPPING INVESTIGATION")
    print("=" * 60)
    
    # Get direct calculation result
    result = calculate_bond_master(
        description="T 3 15/08/52",
        price=71.66
    )
    
    print("📊 DIRECT FUNCTION RETURNS:")
    print("-" * 30)
    for key, value in result.items():
        print(f"   '{key}': {value}")
    
    print()
    print("🎯 API EXPECTED MAPPINGS:")
    print("-" * 30)
    
    # API mapping logic (from google_analysis10_api.py line 587)
    api_expected = {
        # Core fields
        'yield': result.get('yield'),
        'duration': result.get('duration'), 
        'spread': result.get('spread'),
        'accrued_interest': result.get('accrued_interest'),
        'price': result.get('price'),
        
        # Enhanced fields - checking field name mismatches
        'macaulay_duration': result.get('mac_dur_semi'),     # ✅ Should work
        'clean_price': result.get('clean_price'),            # ✅ Should work
        'dirty_price': result.get('dirty_price'),            # ✅ Should work
        'annual_yield': result.get('ytm_annual'),            # ✅ Should work
        'annual_duration': result.get('mod_dur_annual'),     # ✅ Should work
        'annual_macaulay_duration': result.get('mac_dur_annual'), # ✅ Should work
        'convexity': result.get('convexity_semi'),           # ❌ MISMATCH!
        'pvbp': result.get('pvbp'),                          # ✅ Should work
        'z_spread': result.get('z_spread_semi')              # ❌ MISSING!
    }
    
    print("✅ WORKING MAPPINGS:")
    for key, value in api_expected.items():
        if value is not None:
            print(f"   '{key}': {value}")
    
    print()
    print("❌ BROKEN MAPPINGS:")
    for key, value in api_expected.items():
        if value is None:
            expected_field = {
                'convexity': 'convexity_semi',
                'z_spread': 'z_spread_semi'
            }.get(key, 'unknown')
            actual_field = 'convexity' if key == 'convexity' else 'not_present'
            print(f"   '{key}': API expects '{expected_field}' but function returns '{actual_field}'")
    
    print()
    print("🔧 FIELD NAME CORRECTIONS NEEDED:")
    print("   API line ~599: 'convexity_semi' → should be 'convexity'")
    print("   API line ~600: 'z_spread_semi' → field doesn't exist (should be null for Treasuries)")

if __name__ == "__main__":
    investigate_field_mapping()
