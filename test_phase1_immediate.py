#!/usr/bin/env python3
"""
🚀 IMMEDIATE PHASE 1 TEST
======================

Test the enhanced bond master function with Phase 1 outputs!
"""

import sys
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

from bond_master_hierarchy_enhanced import calculate_bond_master, test_enhanced_master_function

print("🚀 PHASE 1 ENHANCED MASTER FUNCTION TEST")
print("=" * 60)

# Quick single bond test
print("🧪 Quick Test - US Treasury:")
result = calculate_bond_master(
    isin="US912810TJ79", 
    description="T 3 15/08/52", 
    price=71.66
)

print(f"✅ Success: {result.get('success')}")
print(f"📊 Route Used: {result.get('route_used')}")

if result.get('success'):
    print("\n📊 ORIGINAL OUTPUTS:")
    # Handle yield display (might be in decimal or percentage format)
    yield_val = result.get('yield')
    if yield_val and yield_val < 1:  # Likely in decimal format
        yield_display = yield_val * 100
    else:
        yield_display = yield_val
    
    print(f"   Yield: {yield_display:.4f}%")
    print(f"   Duration: {result.get('duration'):.4f} years")
    spread = result.get('spread')
    print(f"   Spread: {spread:.1f} bps" if spread is not None else "   Spread: N/A (Treasury)")
    
    print("\n🚀 NEW PHASE 1 OUTPUTS:")
    
    # Handle each Phase 1 output safely
    mac_dur = result.get('mac_dur_semi')
    clean_price = result.get('clean_price')
    dirty_price = result.get('dirty_price')
    ytm_annual = result.get('ytm_annual')
    mod_dur_annual = result.get('mod_dur_annual')
    mac_dur_annual = result.get('mac_dur_annual')
    
    print(f"   ✅ mac_dur_semi: {mac_dur:.6f} years" if mac_dur else "   ❌ mac_dur_semi: None")
    print(f"   ✅ clean_price: {clean_price:.6f}" if clean_price else "   ❌ clean_price: None")
    print(f"   ✅ dirty_price: {dirty_price:.6f}" if dirty_price else "   ❌ dirty_price: None")
    print(f"   ✅ ytm_annual: {ytm_annual:.6f}%" if ytm_annual else "   ❌ ytm_annual: None")
    print(f"   ✅ mod_dur_annual: {mod_dur_annual:.6f} years" if mod_dur_annual else "   ❌ mod_dur_annual: None")
    print(f"   ✅ mac_dur_annual: {mac_dur_annual:.6f} years" if mac_dur_annual else "   ❌ mac_dur_annual: None")
    
    print(f"\n🎯 Total Outputs Available: {len([k for k in result.keys() if not k.startswith('_')])}")
    
    if result.get('phase1_outputs_added'):
        print("🎉 PHASE 1 ENHANCEMENT SUCCESSFUL!")
        
        # XTrillion API compatibility check
        xtrillion_fields = ['ytm_semi', 'mod_dur_semi', 'mac_dur_semi', 'clean_price', 'dirty_price', 'ytm_annual', 'mod_dur_annual', 'mac_dur_annual']
        available_fields = [field for field in xtrillion_fields if result.get(field) is not None]
        print(f"🔗 XTrillion Compatible Fields: {len(available_fields)}/{len(xtrillion_fields)}")
        print(f"📈 Phase 1 Progress: {len(available_fields)}/15 XTrillion outputs ({len(available_fields)/15*100:.1f}%)")
    else:
        print("❌ Phase 1 enhancement failed")
else:
    print(f"❌ Test failed: {result.get('error')}")

print("\n" + "=" * 60)
print("🚀 Run full test with: python bond_master_hierarchy_enhanced.py")
