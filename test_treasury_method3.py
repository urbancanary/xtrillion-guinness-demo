#!/usr/bin/env python3
"""
Test Treasury Method 3 with database data
"""

import sqlite3
import pandas as pd
from treasury_method3_debug import calculate_treasury_with_debug

# Get the bond data from database
conn = sqlite3.connect("./bonds_data.db")
query = "SELECT * FROM static WHERE ISIN = 'US912810TJ79'"
bond_data = pd.read_sql_query(query, conn)

print("📋 Bond data from database:")
print(f"ISIN: {bond_data.iloc[0]['isin']}")
print(f"Name: {bond_data.iloc[0]['name']}")
print(f"Coupon: {bond_data.iloc[0]['coupon']}")
print(f"Maturity: {bond_data.iloc[0]['maturity']}")
print()

# Test Method 3 calculation with expected Bloomberg values
result = calculate_treasury_with_debug(
    bond_data.iloc[0]['name'], 
    price=71.66, 
    settlement_date_str="2025-06-30"
)

print()
print("✅ Method 3 Results Summary:")
print(f"Yield: {result['yield']:.5f}%")
print(f"Duration: {result['duration']:.5f} years")  
print(f"Accrued: ${result['accrued']:.4f}")
print(f"Days Accrued: {result['days_accrued']}")
print(f"Accrued per Million: {result['accrued_per_million']:.2f}")
print()
print("🎯 Comparison to Expected Bloomberg:")
print(f"Duration Diff: {result['duration_diff']:.8f} years")
print(f"Accrued per Million Diff: {result['accrued_per_million_diff']:+.3f}")

conn.close()
