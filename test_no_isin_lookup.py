#!/usr/bin/env python3
"""
Test that description route doesn't look up ISINs
"""

from bond_master_hierarchy_enhanced import calculate_bond_master
import json

# Database paths
DB_PATH = "bonds_data.db"
VALIDATED_DB = "validated_quantlib_bonds.db"
BLOOMBERG_DB = "bloomberg_index.db"

print("🔍 Testing Description Route WITHOUT ISIN Lookup")
print("=" * 60)

# Test description route
print("\n1. Description Route (T 3 15/08/52)")
print("-" * 40)

desc_result = calculate_bond_master(
    description="T 3 15/08/52",
    price=71.66,
    settlement_date="2025-08-01",
    db_path=DB_PATH,
    validated_db_path=VALIDATED_DB,
    bloomberg_db_path=BLOOMBERG_DB
)

print(f"✅ Success: {desc_result.get('success', False)}")
print(f"YTM: {desc_result.get('ytm', 'N/A'):.6f}%")
print(f"Duration: {desc_result.get('duration', 'N/A'):.6f}")
print(f"ISIN in result: {desc_result.get('isin', 'None')}")
print(f"Route used: {desc_result.get('route_used')}")

# Test ISIN route with correct ISIN
print("\n\n2. ISIN Route (US912810TJ79)")
print("-" * 40)

isin_result = calculate_bond_master(
    isin="US912810TJ79",
    price=71.66,
    settlement_date="2025-08-01",
    db_path=DB_PATH,
    validated_db_path=VALIDATED_DB,
    bloomberg_db_path=BLOOMBERG_DB
)

print(f"✅ Success: {isin_result.get('success', False)}")
print(f"YTM: {isin_result.get('ytm', 'N/A'):.6f}%")
print(f"Duration: {isin_result.get('duration', 'N/A'):.6f}")
print(f"ISIN in result: {isin_result.get('isin', 'None')}")
print(f"Route used: {isin_result.get('route_used')}")

# Compare
print("\n\n3. Comparison")
print("-" * 40)

if desc_result.get('isin') == 'US91282CJZ59':
    print("❌ Description route is STILL looking up ISIN (found US91282CJZ59)")
    print("   This needs to be fixed in the deployed code")
else:
    print("✅ Description route is NOT looking up ISIN")
    
print(f"\nYTM difference: {abs(desc_result.get('ytm', 0) - isin_result.get('ytm', 0)):.6f}%")
print(f"Duration difference: {abs(desc_result.get('duration', 0) - isin_result.get('duration', 0)):.6f}")

print("\n" + "=" * 60)
print("Expected: Description route should NOT find/use any ISIN")
print("This avoids confusion between Reg S and 144A bonds")