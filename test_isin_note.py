#!/usr/bin/env python3
"""
Test the ISIN fallback note feature
"""

from bond_master_hierarchy_enhanced import calculate_bond_master
import json

# Database paths
DB_PATH = "bonds_data.db"
VALIDATED_DB = "validated_quantlib_bonds.db"
BLOOMBERG_DB = "bloomberg_index.db"

print("🔔 Testing ISIN Fallback Note Feature")
print("=" * 60)

# Test 1: ISIN found in database
print("\n1. Valid ISIN (should show found status)")
result = calculate_bond_master(
    isin="US912810TJ79",
    price=71.66,
    settlement_date="2025-08-01",
    db_path=DB_PATH,
    validated_db_path=VALIDATED_DB,
    bloomberg_db_path=BLOOMBERG_DB
)

if result.get('success'):
    print(f"✅ Success")
    print(f"   ISIN lookup status: {result.get('isin_lookup_status', 'N/A')}")
    print(f"   Database source: {result.get('database_source', 'N/A')}")
    print(f"   Note: {result.get('note', 'None')}")

# Test 2: ISIN not found but description provided
print("\n2. Invalid ISIN with description (should show fallback note)")
result = calculate_bond_master(
    isin="XX9999999999",
    description="T 3 15/08/52",
    price=71.66,
    settlement_date="2025-08-01",
    db_path=DB_PATH,
    validated_db_path=VALIDATED_DB,
    bloomberg_db_path=BLOOMBERG_DB
)

if result.get('success'):
    print(f"✅ Success")
    print(f"   ISIN lookup status: {result.get('isin_lookup_status', 'N/A')}")
    print(f"   Note: {result.get('note', 'None')}")
    print(f"   YTM: {result.get('ytm', 'N/A'):.3f}%")
    print(f"   Duration: {result.get('duration', 'N/A'):.3f}")

# Test 3: Show sample JSON response
print("\n3. Sample JSON Response with fallback note:")
print("-" * 40)
sample_response = {
    "success": True,
    "isin": "XX9999999999",
    "description": "T 3 15/08/52",
    "price": 71.66,
    "ytm": 4.903,
    "duration": 16.259,
    "note": "ISIN XX9999999999 not found in database. Calculation performed using provided description instead.",
    "isin_lookup_status": "not_found_used_description",
    "route_used": "isin_hierarchy"
}
print(json.dumps(sample_response, indent=2))