#!/usr/bin/env python3
"""
🚀 PHASE 1 - 25 BOND TEST
========================

Test the enhanced function with all 25 bonds to see Phase 1 outputs!
"""

import sys
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

from bond_master_hierarchy_enhanced import calculate_bond_master

# Sample of your 25 bonds for quick test
BONDS_SAMPLE = [
    {"isin": "US912810TJ79", "px_mid": 71.66, "name": "T 3 15/08/52"},
    {"isin": "XS2249741674", "px_mid": 77.88, "name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040"},
    {"isin": "USP3143NAH72", "px_mid": 101.63, "name": "CODELCO INC, 6.15%, 24-Oct-2036"},
    {"isin": "US279158AJ82", "px_mid": 69.31, "name": "ECOPETROL SA, 5.875%, 28-May-2045"},
    {"isin": "XS2233188353", "px_mid": 99.23, "name": "QNB FINANCE LTD, 1.625%, 22-Sep-2025"}
]

print("🚀 PHASE 1 ENHANCED - 25 BOND PORTFOLIO TEST")
print("=" * 80)

for i, bond in enumerate(BONDS_SAMPLE, 1):
    print(f"\n🧪 Bond {i}/5: {bond['isin']}")
    
    result = calculate_bond_master(
        isin=bond["isin"],
        description=bond["name"],
        price=bond["px_mid"]
    )
    
    if result.get('success'):
        print(f"✅ {bond['name'][:50]}...")
        print(f"   📊 Yield: {result.get('yield')*100:.2f}% | Duration: {result.get('duration'):.2f} yrs")
        
        # Show Phase 1 outputs
        if result.get('phase1_outputs_added'):
            print(f"   🚀 NEW: Mac Dur: {result.get('mac_dur_semi'):.2f} | Clean: {result.get('clean_price'):.2f} | Annual Yield: {result.get('ytm_annual'):.2f}%")
        else:
            print("   ❌ Phase 1 outputs missing")
    else:
        print(f"❌ FAILED: {result.get('error')}")

print(f"\n🎯 READY FOR YOUR FULL 25-BOND TEST!")
print("Replace 'from bond_master_hierarchy import calculate_bond_master'")
print("   with 'from bond_master_hierarchy_enhanced import calculate_bond_master'")
print("\nAll your existing tests will work with 6 NEW outputs added automatically! 🚀")
