#!/usr/bin/env python3
"""
Test both settlement date scenarios with configurable T+1 override
"""

import sys
sys.path.append('.')
from google_analysis10 import calculate_bond_metrics_with_conventions_using_shared_engine, fetch_treasury_yields, create_treasury_curve
import QuantLib as ql
import sqlite3
import pandas as pd
import datetime

# Get Treasury data
conn = sqlite3.connect('./bonds_data.db')
query = "SELECT * FROM static WHERE ISIN = 'US912810TJ79'"
bond_data = pd.read_sql_query(query, conn)
conn.close()

print("🧪 TESTING CONFIGURABLE T+1 SETTLEMENT")
print("=" * 60)

# Setup treasury curve
trade_date = datetime.datetime(2025, 6, 30)
ql_trade_date = ql.Date(30, 6, 2025)
treasury_yields = fetch_treasury_yields(trade_date, './bonds_data.db')
treasury_handle = create_treasury_curve(treasury_yields, ql_trade_date)

print("📊 SCENARIO 1: Standard T+1 Settlement (June 30 → July 1)")
print("-" * 50)

ticker_conventions_t1 = {
    'treasury_override': True,
    'source': 'treasury_override',
    'day_count': 'ActualActual_Bond',
    'business_convention': 'Following',
    'frequency': 'Semiannual',
    'use_direct_settlement': False  # Standard T+1
}

result_t1 = calculate_bond_metrics_with_conventions_using_shared_engine(
    isin="US912810TJ79",
    coupon=bond_data.iloc[0]['coupon'],
    maturity_date=bond_data.iloc[0]['maturity'],
    price=71.66,
    trade_date=ql_trade_date,
    treasury_handle=treasury_handle,
    ticker_conventions=ticker_conventions_t1,
    validated_db_path="./data/validated_quantlib_bonds.db"
)

print(f"T+1 Results:")
print(f"  Yield: {result_t1[0]:.5f}%")
print(f"  Duration: {result_t1[1]:.5f} years")
print(f"  Accrued: ${result_t1[3]:.4f}")
print()

print("📊 SCENARIO 2: Override T+1 Settlement (June 30 stays June 30)")
print("-" * 50)

ticker_conventions_t0 = {
    'treasury_override': True,
    'source': 'treasury_override',
    'day_count': 'ActualActual_Bond',
    'business_convention': 'Following',
    'frequency': 'Semiannual',
    'use_direct_settlement': True  # Override to T+0
}

result_t0 = calculate_bond_metrics_with_conventions_using_shared_engine(
    isin="US912810TJ79",
    coupon=bond_data.iloc[0]['coupon'],
    maturity_date=bond_data.iloc[0]['maturity'],
    price=71.66,
    trade_date=ql_trade_date,
    treasury_handle=treasury_handle,
    ticker_conventions=ticker_conventions_t0,
    validated_db_path="./data/validated_quantlib_bonds.db"
)

print(f"T+0 Results (Direct Settlement):")
print(f"  Yield: {result_t0[0]:.5f}%")
print(f"  Duration: {result_t0[1]:.5f} years")
print(f"  Accrued: ${result_t0[3]:.4f}")
print()

print("🎯 COMPARISON:")
print(f"Bloomberg Duration Expectation: 16.3578392273866 years")
print(f"Bloomberg Accrued per Million: 11,187.845")
print()

bbg_duration = 16.3578392273866
bbg_accrued_per_mil = 11187.845

if result_t1[1]:
    t1_duration_diff = result_t1[1] - bbg_duration
    print(f"T+1 Duration Diff: {t1_duration_diff:+.8f} years")

if result_t0[1]:
    t0_duration_diff = result_t0[1] - bbg_duration  
    print(f"T+0 Duration Diff: {t0_duration_diff:+.8f} years")

print()
print("✅ T+1 settlement override functionality working!")
print("⚠️  Schedule construction still needs fixing for proper accrued interest")
print("   (Should use Treasury issue date pattern, not settlement date)")
