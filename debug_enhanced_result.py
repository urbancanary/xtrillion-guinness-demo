#!/usr/bin/env python3
"""
Debug Enhanced Calculator Results
=================================

Debug what keys are actually available in the enhanced calculator result.
"""

import sys
import os
import json

# Add project path
project_root = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10'
sys.path.append(project_root)

from bond_master_hierarchy_enhanced import calculate_bond_master

def debug_enhanced_calculator():
    """Debug the enhanced calculator result"""
    
    print("🔍 DEBUGGING ENHANCED CALCULATOR RESULTS")
    print("=" * 60)
    
    # Test with the Treasury bond
    result = calculate_bond_master(
        description='T 3 15/08/52',
        price=71.66,
        settlement_date='2025-07-26'
    )
    
    if result.get('success'):
        print("✅ CALCULATION SUCCESSFUL!")
        print()
        
        print("📊 ALL AVAILABLE KEYS:")
        for key in sorted(result.keys()):
            value = result[key]
            if isinstance(value, (int, float)):
                print(f"  {key}: {value}")
            elif isinstance(value, list):
                print(f"  {key}: {value} (list)")
            elif isinstance(value, dict):
                print(f"  {key}: {{...}} (dict)")
            else:
                print(f"  {key}: {value}")
        
        print()
        print("🎯 SPECIFIC CHECKS:")
        
        checks = [
            'convexity_semi', 'pvbp', 'convexity', 
            'accrued_interest', 'ytm_semi', 'mod_dur_semi'
        ]
        
        for check in checks:
            value = result.get(check)
            if value is not None:
                print(f"  ✅ {check}: {value}")
            else:
                print(f"  ❌ {check}: None")
        
        print()
        print("📋 RAW RESULT (first 1000 chars):")
        print(str(result)[:1000] + "...")
        
    else:
        print("❌ CALCULATION FAILED!")
        print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    debug_enhanced_calculator()
