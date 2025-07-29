#!/usr/bin/env python3
"""
🔍 COMPLETE RESPONSE DUMP: Show everything from local calculation
to identify remaining Treasury issues
"""

import sys
import os
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

from google_analysis10 import calculate_bond_metrics_with_conventions_using_shared_engine
from datetime import datetime, date
import QuantLib as ql
import json

def get_complete_response():
    print("🔍 COMPLETE LOCAL RESPONSE DUMP")
    print("=" * 60)
    
    # Test parameters - exact same as API should use
    isin = "US912810TJ79"
    coupon = 3.0
    maturity_date = datetime(2052, 8, 15)
    price = 71.66
    trade_date = date(2025, 7, 29)
    
    print(f"📊 INPUT PARAMETERS:")
    print(f"   ISIN: {isin}")
    print(f"   Coupon: {coupon}%")
    print(f"   Maturity: {maturity_date}")
    print(f"   Price: {price}")
    print(f"   Trade Date: {trade_date}")
    print()
    
    # Setup same as API
    treasury_handle = ql.YieldTermStructureHandle(
        ql.FlatForward(ql.Date(29, 7, 2025), 0.03, ql.Actual365Fixed())
    )
    
    default_conventions = {
        'fixed_frequency': 'Semiannual',
        'day_count': 'ActualActual_Bond',
        'business_day_convention': 'Following',
        'end_of_month': True
    }
    
    print("🧮 CALLING LOCAL CALCULATION ENGINE...")
    print("-" * 40)
    
    try:
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
        
        print("📋 COMPLETE RESPONSE JSON:")
        print("=" * 60)
        print(json.dumps(result, indent=2, default=str, sort_keys=True))
        print("=" * 60)
        print()
        
        if result.get('successful'):
            print("🔍 KEY METRICS EXTRACTED:")
            print("-" * 30)
            for key in ['isin', 'ytm', 'duration', 'convexity', 'accrued_interest', 
                       'clean_price', 'dirty_price', 'pvbp', 'g_spread', 'z_spread']:
                value = result.get(key)
                if isinstance(value, float):
                    print(f"   {key}: {value:.6f}")
                else:
                    print(f"   {key}: {value}")
            print()
            
            print("🏛️ CONVENTIONS APPLIED:")
            print("-" * 25)
            conventions = result.get('conventions', {})
            for key, value in conventions.items():
                print(f"   {key}: {value}")
            print()
            
            print("📅 DATE INFORMATION:")
            print("-" * 20)
            print(f"   settlement_date_str: {result.get('settlement_date_str')}")
            print()
            
            # Cross-validation with Bloomberg expectations
            ytm = result.get('ytm', 0)
            duration = result.get('duration', 0) 
            accrued = result.get('accrued_interest', 0)
            
            print("🎯 BLOOMBERG VALIDATION:")
            print("-" * 25)
            print(f"   YTM: {ytm:.4f}% (expect ~4.9-5.1%)")
            print(f"   Duration: {duration:.2f} years (expect ~19-20 years)")
            print(f"   Accrued: {accrued:.4f} (expect ~1.32)")
            
            # Flag any remaining issues
            issues = []
            if ytm < 4.8 or ytm > 5.2:
                issues.append(f"YTM {ytm:.4f}% outside expected range")
            if duration < 18 or duration > 22:
                issues.append(f"Duration {duration:.2f} outside expected range")
            if accrued < 1.0 or accrued > 2.0:
                issues.append(f"Accrued {accrued:.4f} outside expected range")
                
            if issues:
                print()
                print("🚨 REMAINING ISSUES:")
                for issue in issues:
                    print(f"   ❌ {issue}")
            else:
                print()
                print("✅ All metrics within expected ranges!")
                
        else:
            print(f"❌ CALCULATION FAILED: {result.get('error')}")
            
    except Exception as e:
        print(f"💥 CALCULATION EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_complete_response()
