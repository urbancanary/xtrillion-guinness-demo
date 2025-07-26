#!/usr/bin/env python3
"""
Quick diagnostic test for the yield calculation bug
"""

import os
import sys
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis9')

from google_analysis9 import calculate_bond_metrics, fetch_treasury_yields, create_treasury_curve, parse_date
import pandas as pd
import QuantLib as ql
from datetime import datetime

def test_treasury_yield_calculation():
    """Test the specific Treasury bond calculation to find the bug"""
    
    # Test data
    isin = "US912810TJ79"
    coupon = 0.03  # 3% as decimal
    maturity_date = "2052-08-15"
    price = 71.66
    trade_date_str = "2024-06-28"  # Use a date where we have data
    db_path = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis9/bonds_data.db"
    
    print(f"🧪 Testing bond calculation for:")
    print(f"   ISIN: {isin}")
    print(f"   Coupon: {coupon*100:.2f}%")
    print(f"   Maturity: {maturity_date}")
    print(f"   Price: {price}")
    print(f"   Trade Date: {trade_date_str}")
    
    try:
        # Step 1: Parse trade date
        trade_date_ql = parse_date(trade_date_str)
        print(f"✅ Parsed trade date: {trade_date_ql}")
        
        # Step 2: Fetch treasury yields
        yield_dict = fetch_treasury_yields(pd.to_datetime(trade_date_str), db_path)
        print(f"✅ Treasury yields: {yield_dict}")
        
        # Step 3: Create treasury curve
        treasury_handle = create_treasury_curve(yield_dict, trade_date_ql)
        print(f"✅ Treasury curve created: {type(treasury_handle)}")
        
        # Step 4: Calculate bond metrics
        bond_yield, bond_duration, spread, accrued_interest, error_msg = calculate_bond_metrics(
            isin, coupon, maturity_date, price, trade_date_ql, treasury_handle
        )
        
        if error_msg:
            print(f"❌ Error: {error_msg}")
        else:
            print(f"✅ Calculation successful!")
            print(f"   Yield: {bond_yield:.3f}%")
            print(f"   Duration: {bond_duration:.2f} years")
            print(f"   Spread: {spread:.0f} bps")
            print(f"   Accrued Interest: {accrued_interest:.3f}%")
            
        # Manual yield calculation for comparison
        print(f"\n🔍 Manual yield check:")
        
        # Simple approximation: Current Yield = Annual Coupon / Price
        current_yield = (coupon * 100) / price * 100
        print(f"   Current Yield (rough): {current_yield:.2f}%")
        
        # For a 30-year bond at discount, yield should be higher than coupon
        expected_yield_range = (4.0, 6.0)  # Reasonable range for 30yr at 71.66 price
        if bond_yield and expected_yield_range[0] <= bond_yield <= expected_yield_range[1]:
            print(f"   ✅ Yield {bond_yield:.2f}% is in reasonable range {expected_yield_range}")
        elif bond_yield:
            print(f"   ⚠️  Yield {bond_yield:.2f}% seems outside reasonable range {expected_yield_range}")
        
        return bond_yield, error_msg
        
    except Exception as e:
        print(f"❌ Exception during calculation: {e}")
        import traceback
        traceback.print_exc()
        return None, str(e)

def test_api_response_format():
    """Test what the API is actually trying to return"""
    print(f"\n🔍 Testing API response format...")
    
    # Simulate what the API does
    test_data = {
        "data": [
            {
                "BOND_CD": "US912810TJ79",
                "CLOSING PRICE": 71.66,
                "WEIGHTING": 100.0,
                "Inventory Date": "2025/07/14"
            }
        ]
    }
    
    try:
        from google_analysis9 import process_bonds_with_weightings
        
        print("Processing with portfolio analyzer...")
        results = process_bonds_with_weightings(test_data, 
            "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis9/bonds_data.db")
        
        print(f"Results shape: {results.shape}")
        print(f"Columns: {list(results.columns)}")
        
        if not results.empty:
            result_row = results.iloc[0]
            print(f"Result for {result_row.get('isin', 'Unknown')}:")
            for col in ['yield', 'duration', 'spread', 'error']:
                print(f"   {col}: {result_row.get(col, 'Missing')}")
                
    except Exception as e:
        print(f"❌ API processing error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 DIAGNOSTIC TEST FOR TREASURY BOND YIELD BUG")
    print("=" * 60)
    
    # Test 1: Direct calculation
    bond_yield, error = test_treasury_yield_calculation()
    
    # Test 2: API processing
    test_api_response_format()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    
    if error:
        print(f"❌ Calculation failed: {error}")
        print("🔧 The bug is in the bond calculation engine.")
    elif bond_yield:
        print(f"✅ Calculation succeeded: {bond_yield:.2f}% yield")
        print("🔧 The issue may be in the API response formatting.")
    else:
        print("❌ Unknown issue detected")
