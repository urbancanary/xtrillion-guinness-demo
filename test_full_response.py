#!/usr/bin/env python3
"""
🔍 FULL RESPONSE DEBUG: Show complete calculation result 
to identify accrued interest and pricing issues
"""

import sys
import os
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

from google_analysis10 import calculate_bond_metrics_with_conventions_using_shared_engine
from datetime import datetime, date
import QuantLib as ql
import json

def test_full_response():
    print("🔍 FULL RESPONSE DEBUG FOR T 3 15/08/52 at 71.66")
    print("=" * 70)
    
    # Test parameters
    isin = "US912810TJ79"
    coupon = 3.0  # 3% coupon
    maturity_date = datetime(2052, 8, 15)  # Aug 15, 2052
    price = 71.66  # Clean price input
    trade_date = date(2025, 7, 29)  # Today
    
    print(f"📊 INPUTS:")
    print(f"   ISIN: {isin}")
    print(f"   Coupon: {coupon}%")
    print(f"   Maturity: {maturity_date.strftime('%Y-%m-%d')}")
    print(f"   Price: {price}")
    print(f"   Trade Date: {trade_date}")
    print()
    
    # Create treasury handle (dummy)
    treasury_handle = ql.YieldTermStructureHandle(ql.FlatForward(ql.Date(29, 7, 2025), 0.03, ql.Actual365Fixed()))
    
    # Default conventions
    default_conventions = {
        'fixed_frequency': 'Semiannual',
        'day_count': 'ActualActual_Bond',
        'business_day_convention': 'Following',
        'end_of_month': True
    }
    
    try:
        # Call the calculation function
        result = calculate_bond_metrics_with_conventions_using_shared_engine(
            isin=isin,
            coupon=coupon,
            maturity_date=maturity_date,
            price=price,
            trade_date=trade_date,
            treasury_handle=treasury_handle,
            default_conventions=default_conventions,
            is_treasury=True,
            settlement_days=0,
            validated_db_path=None
        )
        
        print("📋 COMPLETE CALCULATION RESULT:")
        print("=" * 70)
        print(json.dumps(result, indent=2, default=str))
        print()
        
        if result.get('successful'):
            print("🔍 DETAILED ANALYSIS:")
            print("-" * 40)
            
            # Check each field
            clean_price = result.get('clean_price')
            dirty_price = result.get('dirty_price')
            accrued = result.get('accrued_interest')
            ytm = result.get('ytm')
            duration = result.get('duration')
            
            print(f"✅ Clean Price: {clean_price}")
            print(f"📊 Dirty Price: {dirty_price}")
            print(f"💰 Accrued Interest: {accrued}")
            print(f"📈 YTM: {ytm:.4f}%")
            print(f"⏱️  Duration: {duration:.2f} years")
            print()
            
            # Validate the pricing logic
            print("🧮 PRICING VALIDATION:")
            print("-" * 30)
            
            expected_dirty = clean_price + accrued if clean_price and accrued else None
            print(f"Expected Dirty Price: {clean_price} + {accrued} = {expected_dirty}")
            print(f"Actual Dirty Price: {dirty_price}")
            
            if accrued == 0.0:
                print("🚨 ISSUE: Accrued interest is zero!")
                print("   Possible causes:")
                print("   - Settlement date coincides with coupon payment date")
                print("   - Bond schedule issue (no accrued period)")
                print("   - QuantLib calculation error")
                
                # Check settlement vs maturity timing
                settlement_str = result.get('settlement_date_str')
                print(f"   Settlement Date: {settlement_str}")
                print(f"   Maturity Date: {maturity_date.strftime('%Y-%m-%d')}")
                
                # For Treasury bonds, coupons are typically paid on 15th of month
                print(f"   Expected coupon dates: Feb 15, Aug 15 each year")
                print(f"   Settlement day: {trade_date.day} (should accrue from last coupon)")
                
            if clean_price != price:
                print(f"🚨 ISSUE: Clean price doesn't match input!")
                print(f"   Input price: {price}")
                print(f"   Output clean_price: {clean_price}")
                
            if abs(dirty_price - expected_dirty) > 0.01 if expected_dirty else False:
                print(f"🚨 ISSUE: Dirty price calculation wrong!")
                print(f"   Expected: {expected_dirty}")
                print(f"   Actual: {dirty_price}")
        else:
            print(f"❌ CALCULATION FAILED: {result.get('error')}")
            
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_response()
