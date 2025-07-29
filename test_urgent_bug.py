#!/usr/bin/env python3
"""
🚨 URGENT BUG TEST for T 3 15/08/52 at price 71.66
Testing the calculation locally to find the exact bug.
"""

import sys
import os
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

from google_analysis10 import calculate_bond_metrics_with_conventions_using_shared_engine
from datetime import datetime, date
import QuantLib as ql

def test_problematic_bond():
    print("🚨 TESTING T 3 15/08/52 at price 71.66")
    print("=" * 60)
    
    # Test parameters
    isin = "US912810TJ79"  # Example ISIN for testing
    coupon = 3.0  # 3% coupon
    maturity_date = datetime(2052, 8, 15)  # Aug 15, 2052
    price = 71.66  # CRITICAL: This should be used in calculation
    trade_date = date(2025, 7, 29)  # Today
    
    print(f"📊 INPUTS:")
    print(f"   ISIN: {isin}")
    print(f"   Coupon: {coupon}%")
    print(f"   Maturity: {maturity_date.strftime('%Y-%m-%d')}")
    print(f"   Price: {price} 👈 THIS IS THE CRITICAL INPUT")
    print(f"   Trade Date: {trade_date}")
    print()
    
    # Expected values for validation
    print(f"🎯 EXPECTED VALUES (approximate):")
    print(f"   YTM: ~5.0-6.0% (deep discount bond)")
    print(f"   Duration: ~18-22 years (long maturity, low coupon)")
    print(f"   Clean Price: 71.66 (should match input)")
    print(f"   Dirty Price: ~72.0-73.0 (clean + accrued)")
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
    
    print("🧮 CALLING CALCULATION ENGINE...")
    
    try:
        # Call the calculation function
        result = calculate_bond_metrics_with_conventions_using_shared_engine(
            isin=isin,
            coupon=coupon,
            maturity_date=maturity_date,
            price=price,  # This should be used correctly
            trade_date=trade_date,
            treasury_handle=treasury_handle,
            default_conventions=default_conventions,
            is_treasury=True,  # It's a Treasury
            settlement_days=0,
            validated_db_path=None
        )
        
        print("📊 CALCULATION RESULTS:")
        print("=" * 60)
        
        if result.get('successful'):
            ytm = result.get('ytm')
            duration = result.get('duration')
            accrued = result.get('accrued_interest')
            
            print(f"✅ Success: {result.get('successful')}")
            print(f"📈 YTM: {ytm:.4f}%")
            print(f"⏱️  Duration: {duration:.2f} years")
            print(f"💰 Accrued Interest: {accrued:.6f}")
            print(f"🏛️ Conventions: {result.get('conventions')}")
            print()
            
            # Bug detection
            print("🔍 BUG ANALYSIS:")
            print("=" * 40)
            
            bugs_found = []
            
            # Check if price input was used (should show as clean_price)
            if 'clean_price' in result:
                if abs(result['clean_price'] - 71.66) > 0.01:
                    bugs_found.append(f"❌ PRICE BUG: Expected 71.66, got {result['clean_price']}")
                else:
                    print("✅ Price input correctly processed")
            else:
                bugs_found.append("❌ MISSING: clean_price not in result")
            
            # Check duration reasonableness for 27-year bond
            if duration and duration < 15:
                bugs_found.append(f"❌ DURATION BUG: {duration:.2f} years too low for 27-year bond")
            elif duration and duration > 25:
                bugs_found.append(f"❌ DURATION BUG: {duration:.2f} years too high for 27-year bond")
            else:
                print("✅ Duration appears reasonable")
            
            # Check yield reasonableness for deep discount
            if ytm and ytm < 4.5:
                bugs_found.append(f"❌ YIELD BUG: {ytm:.4f}% too low for deep discount bond")
            elif ytm and ytm > 7.0:
                bugs_found.append(f"❌ YIELD BUG: {ytm:.4f}% too high")
            else:
                print("✅ Yield appears reasonable")
                
            if bugs_found:
                print()
                print("🚨 CRITICAL BUGS DETECTED:")
                for bug in bugs_found:
                    print(bug)
            else:
                print()
                print("🎉 No obvious bugs detected - calculations appear correct!")
                
        else:
            print(f"❌ CALCULATION FAILED: {result.get('error')}")
            
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_problematic_bond()
