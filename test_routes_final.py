#!/usr/bin/env python3
"""
Test ISIN vs description routes to ensure identical results
"""

import json
from bond_master_hierarchy_enhanced import calculate_bond_master

DB_PATH = "bonds_data.db"
VALIDATED_DB = "validated_quantlib_bonds.db"
BLOOMBERG_DB = "bloomberg_index.db"

print("Testing T 3 15/08/52 bond via both routes")
print("=" * 80)

# Common parameters
price = 71.66
settlement_date = "2025-08-01"

# Test 1: ISIN route
print("\n1. ISIN Route (US912810TJ79):")
print("-" * 60)
isin_result = calculate_bond_master(
    isin="US912810TJ79",
    price=price,
    settlement_date=settlement_date,
    db_path=DB_PATH,
    validated_db_path=VALIDATED_DB,
    bloomberg_db_path=BLOOMBERG_DB
)

if isin_result.get('success'):
    isin_data = isin_result
    print(f"✅ Success")
    print(f"   Description: {isin_data.get('description')}")
    print(f"   YTM: {isin_data.get('ytm', 0):.6f}%")
    print(f"   Duration: {isin_data.get('duration', 0):.6f}")
    print(f"   Convexity: {isin_data.get('convexity', 0):.6f}")
    print(f"   Clean Price: {isin_data.get('clean_price', 0):.6f}")
    print(f"   Dirty Price: {isin_data.get('dirty_price', 0):.6f}")
    print(f"   Accrued: {isin_data.get('accrued_interest', 0):.6f}")
    print(f"   PVBP: {isin_data.get('pvbp', 0):.6f}")
    print(f"   Spread: {isin_data.get('spread')}")
    print(f"   Z-Spread: {isin_data.get('z_spread')}")
    print(f"\n   Conventions:")
    for k, v in isin_data.get('conventions', {}).items():
        print(f"     {k}: {v}")
else:
    print(f"❌ Error: {isin_result}")

# Test 2: Description route
print("\n\n2. Description Route (T 3 15/08/52):")
print("-" * 60)
desc_result = calculate_bond_master(
    description="T 3 15/08/52",
    price=price,
    settlement_date=settlement_date,
    db_path=DB_PATH,
    validated_db_path=VALIDATED_DB,
    bloomberg_db_path=BLOOMBERG_DB
)

if desc_result.get('success'):
    desc_data = desc_result
    print(f"✅ Success")
    print(f"   Description: {desc_data.get('description')}")
    print(f"   YTM: {desc_data.get('ytm', 0):.6f}%")
    print(f"   Duration: {desc_data.get('duration', 0):.6f}")
    print(f"   Convexity: {desc_data.get('convexity', 0):.6f}")
    print(f"   Clean Price: {desc_data.get('clean_price', 0):.6f}")
    print(f"   Dirty Price: {desc_data.get('dirty_price', 0):.6f}")
    print(f"   Accrued: {desc_data.get('accrued_interest', 0):.6f}")
    print(f"   PVBP: {desc_data.get('pvbp', 0):.6f}")
    print(f"   Spread: {desc_data.get('spread')}")
    print(f"   Z-Spread: {desc_data.get('z_spread')}")
    print(f"\n   Conventions:")
    for k, v in desc_data.get('conventions', {}).items():
        print(f"     {k}: {v}")
else:
    print(f"❌ Error: {desc_result}")

# Compare results
print("\n\n" + "=" * 80)
print("COMPARISON:")
print("-" * 60)

if isin_result.get('success') and desc_result.get('success'):
    isin_data = isin_result
    desc_data = desc_result
    
    # Compare key metrics
    metrics = ['ytm', 'duration', 'convexity', 'clean_price', 'dirty_price', 
               'accrued_interest', 'pvbp', 'spread', 'z_spread']
    
    all_match = True
    for metric in metrics:
        isin_val = isin_data.get(metric, 0)
        desc_val = desc_data.get(metric, 0)
        
        if isin_val is None and desc_val is None:
            match = "✅"
            diff = "Both None"
        elif isin_val is None or desc_val is None:
            match = "❌"
            diff = f"ISIN: {isin_val}, Desc: {desc_val}"
            all_match = False
        else:
            # For numerical comparison
            diff = abs(isin_val - desc_val)
            if diff < 0.000001:  # Very small tolerance
                match = "✅"
                diff = f"{diff:.9f}"
            else:
                match = "❌"
                diff = f"{diff:.9f} (ISIN: {isin_val:.6f}, Desc: {desc_val:.6f})"
                all_match = False
        
        print(f"{match} {metric:<20}: {diff}")
    
    # Compare conventions
    print("\nConventions:")
    isin_conv = isin_data.get('conventions', {})
    desc_conv = desc_data.get('conventions', {})
    
    for key in set(list(isin_conv.keys()) + list(desc_conv.keys())):
        isin_val = isin_conv.get(key)
        desc_val = desc_conv.get(key)
        if isin_val == desc_val:
            print(f"✅ {key:<25}: {isin_val}")
        else:
            print(f"❌ {key:<25}: ISIN={isin_val}, Desc={desc_val}")
            all_match = False
    
    print("\n" + "=" * 80)
    if all_match:
        print("✅ SUCCESS: Both routes return IDENTICAL results!")
    else:
        print("❌ FAILURE: Routes return different results!")
else:
    print("❌ Could not compare - one or both routes failed")