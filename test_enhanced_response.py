#!/usr/bin/env python3
"""
Test Enhanced vs Basic Response
==============================

Run this to see the difference between your current basic response
and the enhanced response with 6 additional Phase 1 outputs.
"""

import sys
import json
from pathlib import Path

# Add project path
project_root = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10'
sys.path.append(project_root)

def test_basic_vs_enhanced():
    print("🎯 TESTING BASIC vs ENHANCED RESPONSES")
    print("=" * 60)
    
    # Test basic version
    print("\n📊 BASIC VERSION (Current):")
    print("-" * 30)
    try:
        from bond_master_hierarchy import calculate_bond_master as basic_calc
        basic_result = basic_calc(
            isin="US912810TJ79",
            description="T 3 15/08/52",
            price=71.66
        )
        
        print("✅ Basic Response:")
        basic_keys = list(basic_result.keys())
        for key in sorted(basic_keys):
            print(f"   {key}: {basic_result[key]}")
        
        print(f"\n📈 Basic Output Count: {len(basic_keys)} fields")
        
    except Exception as e:
        print(f"❌ Basic version error: {e}")
        basic_result = None
    
    # Test enhanced version
    print("\n🚀 ENHANCED VERSION (Available):")
    print("-" * 30)
    try:
        from bond_master_hierarchy_enhanced import calculate_bond_master as enhanced_calc
        enhanced_result = enhanced_calc(
            isin="US912810TJ79",
            description="T 3 15/08/52",
            price=71.66
        )
        
        print("✅ Enhanced Response:")
        enhanced_keys = list(enhanced_result.keys())
        for key in sorted(enhanced_keys):
            print(f"   {key}: {enhanced_result[key]}")
        
        print(f"\n📈 Enhanced Output Count: {len(enhanced_keys)} fields")
        
        # Show new Phase 1 outputs specifically
        if enhanced_result.get('new_outputs'):
            print(f"\n🚀 NEW PHASE 1 OUTPUTS:")
            for output in enhanced_result['new_outputs']:
                value = enhanced_result.get(output)
                print(f"   {output}: {value}")
        
    except Exception as e:
        print(f"❌ Enhanced version error: {e}")
        enhanced_result = None
    
    # Compare if both work
    if basic_result and enhanced_result:
        print(f"\n🔍 COMPARISON:")
        print(f"   Basic fields: {len(basic_result.keys())}")
        print(f"   Enhanced fields: {len(enhanced_result.keys())}")
        
        # Show added fields
        basic_keys = set(basic_result.keys())
        enhanced_keys = set(enhanced_result.keys())
        new_fields = enhanced_keys - basic_keys
        
        if new_fields:
            print(f"\n✨ ADDED FIELDS ({len(new_fields)}):")
            for field in sorted(new_fields):
                print(f"   + {field}: {enhanced_result[field]}")
        
        # Check if core calculations match
        core_fields = ['yield', 'duration', 'spread']
        core_match = True
        for field in core_fields:
            basic_val = basic_result.get(field)
            enhanced_val = enhanced_result.get(field)
            if basic_val != enhanced_val:
                core_match = False
                print(f"   ⚠️ {field} differs: {basic_val} vs {enhanced_val}")
        
        if core_match:
            print("   ✅ Core calculations match - enhanced version is safe upgrade!")
    
        print(f"\n🎯 RECOMMENDATION:")
        if enhanced_result and enhanced_result.get('phase1_outputs_added'):
            print("   ✅ Use enhanced version for 6 additional outputs")
            print("   ✅ Simply change import: from bond_master_hierarchy_enhanced import calculate_bond_master")
            print("   ✅ Duration calculations now use PROPER conversion formulas:")
            print("      - mod_dur_annual = mod_dur_semi / (1 + yield_semi/2)")
            print("      - mac_dur_annual = mac_dur_semi / (1 + yield_semi/2)")
            print("      - NOT just dividing by 2!")
            
            # Calculate what the values should be with proper formula
            if enhanced_result.get('yield') and enhanced_result.get('duration'):
                ytm = enhanced_result.get('yield')
                ytm_decimal = ytm / 100.0 if ytm > 1 else ytm
                mod_dur_semi = enhanced_result.get('duration')
                
                # Show the math
                print(f"\n📐 CORRECTED CALCULATION EXAMPLE:")
                print(f"   Semi-annual yield: {ytm_decimal:.6f}")
                print(f"   Semi-annual mod duration: {mod_dur_semi:.6f}")
                print(f"   Formula: {mod_dur_semi:.6f} / (1 + {ytm_decimal:.6f}/2)")
                print(f"   Formula: {mod_dur_semi:.6f} / {1 + ytm_decimal/2:.6f}")
                
                corrected_annual = mod_dur_semi / (1 + ytm_decimal/2)
                wrong_annual = mod_dur_semi / 2
                
                print(f"   ✅ CORRECT annual duration: {corrected_annual:.6f}")
                print(f"   ❌ WRONG (÷2) annual duration: {wrong_annual:.6f}")
                print(f"   📊 Difference: {abs(corrected_annual - wrong_annual):.6f} years")
        
        # Show sample enhanced JSON
        print(f"\n📋 SAMPLE ENHANCED JSON (CORRECTED FORMULAS):")
        sample_response = {
            "success": True,
            "yield": enhanced_result.get('yield'),
            "duration": enhanced_result.get('duration'),
            "spread": enhanced_result.get('spread'),
            "accrued_interest": enhanced_result.get('accrued_interest'),
            # Phase 1 outputs
            "mac_dur_semi": enhanced_result.get('mac_dur_semi'),
            "clean_price": enhanced_result.get('clean_price'),
            "dirty_price": enhanced_result.get('dirty_price'),
            "ytm_annual": enhanced_result.get('ytm_annual'),
            "mod_dur_annual": enhanced_result.get('mod_dur_annual'),  # Now correctly calculated
            "mac_dur_annual": enhanced_result.get('mac_dur_annual'),  # Now correctly calculated
            # API compatibility
            "ytm_semi": enhanced_result.get('ytm_semi'),
            "mod_dur_semi": enhanced_result.get('mod_dur_semi'),
            "tsy_spread_semi": enhanced_result.get('tsy_spread_semi'),
            # Metadata
            "phase1_outputs_added": True,
            "new_outputs": enhanced_result.get('new_outputs')
        }
        
        print(json.dumps(sample_response, indent=2))
    else:
        print("   ⚠️ Enhanced version not working - debug needed")


if __name__ == "__main__":
    test_basic_vs_enhanced()
