#!/usr/bin/env python3
"""
Quick test of the fixed QuantLib calculation
"""

import sys
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis9')

from bond_calculation_registry import get_working_accrued_calculation

def quick_test():
    print("🧪 Quick Test - Fixed QuantLib Calculator")
    print("=" * 50)
    
    # Test a few failing bonds
    test_bonds = [
        "US25278XBA63",  # FANG 5¾ 04/18/54 - was returning 0
        "US86562MAV28",  # SUMIBK 3.352 10/18/27 - was returning 0
        "US053332AW26"   # AZO 3¾ 04/18/29 - was returning 0
    ]
    
    calc_func = get_working_accrued_calculation()
    
    for isin in test_bonds:
        result = calc_func(isin, None, None, "2025-04-18")
        
        if result['success']:
            print(f"✅ {isin}: {result['accrued_per_million']:.0f} per million")
        else:
            print(f"❌ {isin}: {result['error']}")

if __name__ == "__main__":
    quick_test()
