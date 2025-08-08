#!/usr/bin/env python3
"""
Check ISIN mapping for T 3 15/08/52
"""

from isin_lookup import lookup_isin_in_database

# Database paths
DB_PATH = "bonds_data.db"
VALIDATED_DB = "validated_quantlib_bonds.db"
BLOOMBERG_DB = "bloomberg_index.db"

print("Checking ISIN mappings...")
print("=" * 60)

# Check US912810TJ79
print("\n1. US912810TJ79:")
result1 = lookup_isin_in_database("US912810TJ79", DB_PATH, VALIDATED_DB, BLOOMBERG_DB)
if result1:
    print(f"   Found in: {result1['database']}")
    print(f"   Description: {result1['description']}")
    print(f"   Coupon: {result1['coupon']}")
    print(f"   Maturity: {result1['maturity']}")
else:
    print("   NOT FOUND")

# Check US91282CJZ59
print("\n2. US91282CJZ59:")
result2 = lookup_isin_in_database("US91282CJZ59", DB_PATH, VALIDATED_DB, BLOOMBERG_DB)
if result2:
    print(f"   Found in: {result2['database']}")
    print(f"   Description: {result2['description']}")
    print(f"   Coupon: {result2['coupon']}")
    print(f"   Maturity: {result2['maturity']}")
else:
    print("   NOT FOUND")

print("\n" + "=" * 60)
print("CONCLUSION:")
if result1 and result2:
    print("Both ISINs exist but map to different bonds!")
    print("This explains why ISIN and description routes give different results.")