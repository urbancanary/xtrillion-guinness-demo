#!/usr/bin/env python3
"""
Direct test of Treasury calculation in main processing engine
"""

import sys
sys.path.append('.')
from google_analysis10 import calculate_bond_metrics_with_conventions_using_shared_engine
import QuantLib as ql
import sqlite3
import pandas as pd

# Get Treasury data from database
conn = sqlite3.connect('./bonds_data.db')
query = "SELECT * FROM static WHERE ISIN = 'US912810TJ79'"
bond_data = pd.read_sql_query(query, conn)
conn.close()

print("🧪 Testing main calculation engine directly...")
print(f"ISIN: {bond_data.iloc[0]['isin']}")
print(f"Name: {bond_data.iloc[0]['name']}")  
print(f"Coupon: {bond_data.iloc[0]['coupon']}")
print(f"Maturity: {bond_data.iloc[0]['maturity']}")
print()

# Test the main calculation function directly
try:
    # Create treasury handle (simplified)
    from google_analysis10 import fetch_treasury_yields, create_treasury_curve
    import datetime
    
    # Use June 30 as trade date since we're overriding T+1 settlement
    trade_date = datetime.datetime(2025, 6, 30)  # Will be used directly as settlement with override
    ql_trade_date = ql.Date(30, 6, 2025)
    
    print("🏛️ Creating treasury curve...")
    print(f"Trade date: {trade_date} (will be used directly as settlement date)")
    treasury_yields = fetch_treasury_yields(trade_date, './bonds_data.db')
    print(f"Treasury yields: {treasury_yields}")
    
    treasury_handle = create_treasury_curve(treasury_yields, ql_trade_date)
    print("✅ Treasury curve created")
    print()
    
    print("🔧 Testing main calculation function with settlement override...")
    
    # Treasury ticker conventions with DIRECT SETTLEMENT override
    ticker_conventions = {
        'treasury_override': True,
        'source': 'treasury_override',
        'day_count': 'ActualActual_Bond',
        'business_convention': 'Following',
        'frequency': 'Semiannual',
        'use_direct_settlement': True  # ⚙️ KEY: Override T+1 settlement, use June 30 directly
    }
    
    print(f"🎯 Using direct settlement override: trade_date = settlement_date")
    
    result = calculate_bond_metrics_with_conventions_using_shared_engine(
        isin="US912810TJ79",
        coupon=bond_data.iloc[0]['coupon'],
        maturity_date=bond_data.iloc[0]['maturity'],
        price=71.66,
        trade_date=ql.Date(30, 6, 2025),  # June 30 as trade date AND settlement date
        treasury_handle=treasury_handle,
        ticker_conventions=ticker_conventions,
        validated_db_path="./validated_quantlib_bonds.db"
    )
    
    print("📊 MAIN ENGINE RESULTS:")
    print(f"Yield: {result[0]}")
    print(f"Duration: {result[1]}")
    print(f"Spread: {result[2]}")
    print(f"Accrued: {result[3]}")
    print(f"Error: {result[4]}")
    
except Exception as e:
    print(f"❌ Error in main calculation: {e}")
    import traceback
    traceback.print_exc()
