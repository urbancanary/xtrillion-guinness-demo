#!/usr/bin/env python3
"""
Debug why ISIN and description routes give slightly different results
"""

from bond_master_hierarchy_enhanced import calculate_bond_master
import json

# Database paths
DB_PATH = "bonds_data.db"
VALIDATED_DB = "validated_quantlib_bonds.db" 
BLOOMBERG_DB = "bloomberg_index.db"

print("🔍 Debugging Convention Differences")
print("=" * 60)

# Test ISIN route
print("\n1. ISIN Route (US912810TJ79)")
print("-" * 40)

isin_result = calculate_bond_master(
    isin="US912810TJ79",
    price=71.66,
    settlement_date="2025-08-01",
    db_path=DB_PATH,
    validated_db_path=VALIDATED_DB,
    bloomberg_db_path=BLOOMBERG_DB
)

print(f"YTM: {isin_result.get('ytm', 'N/A'):.6f}%")
print(f"Duration: {isin_result.get('duration', 'N/A'):.6f}")
print(f"Description used: {isin_result.get('description')}")

print("\nConventions:")
conv = isin_result.get('conventions', {})
for k, v in sorted(conv.items()):
    print(f"  {k}: {v}")

# Test description route
print("\n\n2. Description Route (T 3 15/08/52)")
print("-" * 40)

desc_result = calculate_bond_master(
    description="T 3 15/08/52",
    price=71.66,
    settlement_date="2025-08-01",
    db_path=DB_PATH,
    validated_db_path=VALIDATED_DB,
    bloomberg_db_path=BLOOMBERG_DB
)

print(f"YTM: {desc_result.get('ytm', 'N/A'):.6f}%")
print(f"Duration: {desc_result.get('duration', 'N/A'):.6f}")

print("\nConventions:")
conv = desc_result.get('conventions', {})
for k, v in sorted(conv.items()):
    print(f"  {k}: {v}")

# Compare raw data
print("\n\n3. Raw Comparison")
print("-" * 40)

# Check if ISINs are different
print(f"ISIN from route 1: {isin_result.get('isin')}")
print(f"ISIN from route 2: {desc_result.get('isin')}")

# Check maturity dates
print(f"\nSettlement dates:")
print(f"Route 1: {isin_result.get('settlement_date')}")
print(f"Route 2: {desc_result.get('settlement_date')}")

# Check accrued interest
print(f"\nAccrued interest:")
print(f"Route 1: {isin_result.get('accrued_interest', 'N/A')}")
print(f"Route 2: {desc_result.get('accrued_interest', 'N/A')}")

# Let's also check what description the parser found
print("\n\n4. Parser Lookup Test")
print("-" * 40)

# Import the parser to see what it finds
from smart_bond_parser import SmartBondParser
parser = SmartBondParser(BLOOMBERG_DB, VALIDATED_DB, BLOOMBERG_DB)

parsed = parser.parse_bond_description("T 3 15/08/52")
if parsed:
    print(f"Parser found:")
    print(f"  ISIN: {parsed.get('isin')}")
    print(f"  Issuer: {parsed.get('issuer')}")
    print(f"  Coupon: {parsed.get('coupon')}")
    print(f"  Maturity: {parsed.get('maturity')}")