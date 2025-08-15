#!/usr/bin/env python3
"""
Deep comparison to find ALL differences between ISIN and description routes
"""

from bond_master_hierarchy_enhanced import calculate_bond_master
import json
from deepdiff import DeepDiff

# Database paths
DB_PATH = "bonds_data.db"
VALIDATED_DB = "validated_quantlib_bonds.db"
BLOOMBERG_DB = "bloomberg_index.db"

print("🔍 Deep Difference Analysis")
print("=" * 80)

# Calculate both routes
print("Calculating via description route...")
desc_result = calculate_bond_master(
    description="T 3 15/08/52",
    price=71.66,
    settlement_date="2025-08-01",
    db_path=DB_PATH,
    validated_db_path=VALIDATED_DB,
    bloomberg_db_path=BLOOMBERG_DB
)

print("Calculating via ISIN route...")
isin_result = calculate_bond_master(
    isin="US912810TJ79",
    price=71.66,
    settlement_date="2025-08-01",
    db_path=DB_PATH,
    validated_db_path=VALIDATED_DB,
    bloomberg_db_path=BLOOMBERG_DB
)

# Find all differences
print("\n" + "=" * 80)
print("COMPLETE FIELD-BY-FIELD COMPARISON:")
print("=" * 80)

# Get all keys from both results
all_keys = sorted(set(desc_result.keys()) | set(isin_result.keys()))

differences = []
for key in all_keys:
    desc_val = desc_result.get(key, "NOT PRESENT")
    isin_val = isin_result.get(key, "NOT PRESENT")
    
    if desc_val != isin_val:
        differences.append((key, desc_val, isin_val))
        print(f"\n❌ DIFFERENCE in '{key}':")
        print(f"   Description route: {desc_val}")
        print(f"   ISIN route:        {isin_val}")
    else:
        print(f"✅ '{key}': {desc_val}")

# Use DeepDiff for nested differences
print("\n" + "=" * 80)
print("DEEP DIFF ANALYSIS:")
print("=" * 80)

try:
    from deepdiff import DeepDiff
    diff = DeepDiff(desc_result, isin_result, significant_digits=10, verbose_level=2)
    if diff:
        print(json.dumps(diff, indent=2, default=str))
    else:
        print("No differences found by DeepDiff")
except ImportError:
    print("DeepDiff not installed. Showing manual differences:")
    for key, desc_val, isin_val in differences:
        if isinstance(desc_val, (int, float)) and isinstance(isin_val, (int, float)):
            print(f"{key}: {abs(desc_val - isin_val):.10f} difference")

# Focus on calculation inputs
print("\n" + "=" * 80)
print("KEY CALCULATION INPUTS:")
print("=" * 80)

for key in ['description', 'isin', 'price', 'settlement_date', 'accrued_interest', 
            'ytm', 'duration', 'convexity', 'conventions']:
    desc_val = desc_result.get(key)
    isin_val = isin_result.get(key)
    
    if key == 'conventions' and isinstance(desc_val, dict) and isinstance(isin_val, dict):
        print(f"\n{key}:")
        all_conv_keys = sorted(set(desc_val.keys()) | set(isin_val.keys()))
        for conv_key in all_conv_keys:
            desc_conv = desc_val.get(conv_key, "NOT PRESENT")
            isin_conv = isin_val.get(conv_key, "NOT PRESENT") 
            if desc_conv != isin_conv:
                print(f"  ❌ {conv_key}: desc={desc_conv}, isin={isin_conv}")
            else:
                print(f"  ✅ {conv_key}: {desc_conv}")
    else:
        match = "✅" if desc_val == isin_val else "❌"
        print(f"{match} {key}: desc={desc_val}, isin={isin_val}")

print("\n" + "=" * 80)
print("HYPOTHESIS: The difference must be in the conventions passed to QuantLib")