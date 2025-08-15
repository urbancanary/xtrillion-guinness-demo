#!/usr/bin/env python3
"""
Test that ISIN lookup uses database conventions, not parsed description
"""

from bond_master_hierarchy_enhanced import calculate_bond_master
import json

# Database paths
DB_PATH = "bonds_data.db"
VALIDATED_DB = "validated_quantlib_bonds.db"
BLOOMBERG_DB = "bloomberg_index.db"

print("🔍 Testing ISIN Database Conventions")
print("=" * 60)

# Test with US Treasury ISIN
print("\n1. Testing US912810TJ79 (US Treasury)")
print("-" * 40)

result = calculate_bond_master(
    isin="US912810TJ79",
    price=71.66,
    settlement_date="2025-08-01",
    db_path=DB_PATH,
    validated_db_path=VALIDATED_DB,
    bloomberg_db_path=BLOOMBERG_DB
)

if result.get('success'):
    print("✅ Calculation successful")
    print(f"   Description from DB: {result.get('description')}")
    print(f"   YTM: {result.get('ytm', 'N/A'):.4f}%")
    print(f"   Duration: {result.get('duration', 'N/A'):.4f}")
    print(f"   Conventions used:")
    conventions = result.get('conventions', {})
    for key, value in conventions.items():
        print(f"     - {key}: {value}")
    print(f"   ISIN lookup status: {result.get('isin_lookup_status')}")
    print(f"   Database source: {result.get('database_source')}")
else:
    print("❌ Calculation failed")
    print(f"   Error: {result.get('error')}")

# Compare with description-based calculation
print("\n2. Comparing with description-based calculation")
print("-" * 40)

desc_result = calculate_bond_master(
    description="T 3 15/08/52",
    price=71.66,
    settlement_date="2025-08-01",
    db_path=DB_PATH,
    validated_db_path=VALIDATED_DB,
    bloomberg_db_path=BLOOMBERG_DB
)

if desc_result.get('success'):
    print("✅ Description-based calculation successful")
    print(f"   YTM: {desc_result.get('ytm', 'N/A'):.4f}%")
    print(f"   Duration: {desc_result.get('duration', 'N/A'):.4f}")
    
    # Compare results
    print("\n3. Comparison:")
    print("-" * 40)
    
    ytm_diff = abs(result.get('ytm', 0) - desc_result.get('ytm', 0))
    duration_diff = abs(result.get('duration', 0) - desc_result.get('duration', 0))
    
    print(f"   YTM difference: {ytm_diff:.6f}%")
    print(f"   Duration difference: {duration_diff:.6f}")
    
    if ytm_diff < 0.01 and duration_diff < 0.01:
        print("   ✅ Results match! ISIN lookup is using correct conventions.")
    else:
        print("   ❌ Results differ! ISIN lookup may not be using correct conventions.")

print("\n" + "=" * 60)
print("Expected behavior:")
print("- ISIN lookup should find bond in database")
print("- Use database conventions (ActualActual_Bond for Treasury)")
print("- Results should match description-based calculation")