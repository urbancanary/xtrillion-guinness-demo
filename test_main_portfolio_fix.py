#!/usr/bin/env python3
"""
Test the main portfolio processing with our T+0 settlement fix
"""

import sys
sys.path.append('.')
from google_analysis10 import process_bonds_with_weightings
import pandas as pd

print("🧪 TESTING MAIN PORTFOLIO API WITH T+0 SETTLEMENT FIX")
print("=" * 60)

# Test the exact same data that was failing
test_data = {
    'data': [{
        'BOND_CD': 'US912810TJ79',
        'CLOSING PRICE': 71.66,
        'WEIGHTING': 100.0,
        'Inventory Date': '2025/06/30'
    }]
}

print("🔧 Testing main portfolio processing function...")
print(f"Input: {test_data}")
print()

try:
    # Test the main processing function directly
    result = process_bonds_with_weightings(test_data, './bonds_data.db')
    
    print("📊 MAIN PORTFOLIO PROCESSING RESULTS:")
    print(result.to_dict('records'))
    
    if not result.empty:
        bond_result = result.iloc[0]
        print()
        print("🎯 TREASURY BOND RESULTS:")
        print(f"  ISIN: {bond_result['isin']}")
        print(f"  Yield: {bond_result.get('yield', 'N/A')}")
        print(f"  Duration: {bond_result.get('duration', 'N/A')}")
        print(f"  Accrued: {bond_result.get('accrued_interest', 'N/A')}")
        print(f"  Error: {bond_result.get('error', 'None')}")
        
        if bond_result.get('duration') and bond_result.get('accrued_interest'):
            bbg_duration = 16.3578392273866
            bbg_accrued_per_mil = 11187.845
            
            duration_diff = bond_result['duration'] - bbg_duration
            # Convert accrued to per million for comparison
            accrued_per_mil = bond_result['accrued_interest'] * 10000
            accrued_diff = accrued_per_mil - bbg_accrued_per_mil
            
            print()
            print("📊 VS BLOOMBERG EXPECTATIONS:")
            print(f"  Duration Diff: {duration_diff:+.8f} (Expected: {bbg_duration:.10f})")
            print(f"  Accrued per Million: {accrued_per_mil:.2f} (Expected: {bbg_accrued_per_mil:.3f})")
            print(f"  Accrued Diff: {accrued_diff:+.3f}")
            
            if abs(duration_diff) < 0.01 and abs(accrued_diff) < 100:
                print("✅ Treasury calculation working with T+0 settlement!")
            else:
                print("⚠️  Treasury calculation needs more adjustments")
    else:
        print("❌ No results returned from portfolio processing")
        
except Exception as e:
    print(f"❌ Portfolio processing error: {e}")
    import traceback
    traceback.print_exc()
