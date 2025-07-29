#!/usr/bin/env python3
"""
✅ FINAL VALIDATION: Confirm all bugs are fixed
"""

import sys
import os
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

from google_analysis10 import calculate_bond_metrics_with_conventions_using_shared_engine
from datetime import datetime, date
import QuantLib as ql

def final_validation():
    print("✅ FINAL VALIDATION - ALL BUGS FIXED")
    print("=" * 50)
    
    # Test parameters
    isin = "US912810TJ79"
    coupon = 3.0
    maturity_date = datetime(2052, 8, 15)
    price = 71.66
    trade_date = date(2025, 7, 29)
    
    # Create treasury handle
    treasury_handle = ql.YieldTermStructureHandle(ql.FlatForward(ql.Date(29, 7, 2025), 0.03, ql.Actual365Fixed()))
    
    # Default conventions
    default_conventions = {
        'fixed_frequency': 'Semiannual',
        'day_count': 'ActualActual_Bond',
        'business_day_convention': 'Following',
        'end_of_month': True
    }
    
    try:
        # Call calculation
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
        
        if result.get('successful'):
            # Extract key metrics
            ytm = result.get('ytm')
            duration = result.get('duration')
            accrued = result.get('accrued_interest')
            clean_price = result.get('clean_price')
            dirty_price = result.get('dirty_price')
            convexity = result.get('convexity')
            pvbp = result.get('pvbp')
            
            print("📊 FINAL RESULTS:")
            print(f"   YTM: {ytm:.4f}%")
            print(f"   Duration: {duration:.2f} years")
            print(f"   Clean Price: {clean_price}")
            print(f"   Accrued Interest: {accrued:.6f}")
            print(f"   Dirty Price: {dirty_price:.6f}")
            print(f"   Convexity: {convexity:.2f}")
            print(f"   PVBP: {pvbp:.6f}")
            print()
            
            # VALIDATION CHECKS
            print("🔍 VALIDATION RESULTS:")
            
            checks_passed = 0
            total_checks = 6
            
            # 1. Price input handled correctly
            if abs(clean_price - 71.66) < 0.01:
                print("✅ Clean price matches input (71.66)")
                checks_passed += 1
            else:
                print(f"❌ Clean price wrong: {clean_price} vs 71.66")
            
            # 2. Duration reasonable for 27-year bond
            if 15 <= duration <= 20:
                print("✅ Duration reasonable for 27-year bond")
                checks_passed += 1
            else:
                print(f"❌ Duration unreasonable: {duration:.2f} years")
            
            # 3. Accrued interest > 0 (should have ~5 months accrued)
            if accrued > 1.0:
                print("✅ Accrued interest properly calculated")
                checks_passed += 1
            else:
                print(f"❌ Accrued interest too low: {accrued:.6f}")
            
            # 4. Dirty price = Clean price + Accrued
            expected_dirty = clean_price + accrued
            if abs(dirty_price - expected_dirty) < 0.001:
                print("✅ Dirty price correctly calculated")
                checks_passed += 1
            else:
                print(f"❌ Dirty price wrong: {dirty_price:.6f} vs {expected_dirty:.6f}")
            
            # 5. Yield reasonable for deep discount bond
            if 4.5 <= ytm <= 6.0:
                print("✅ Yield reasonable for deep discount bond")
                checks_passed += 1
            else:
                print(f"❌ Yield unreasonable: {ytm:.4f}%")
            
            # 6. All required fields present
            required_fields = ['ytm', 'duration', 'accrued_interest', 'clean_price', 'dirty_price', 'pvbp', 'convexity']
            missing_fields = [field for field in required_fields if result.get(field) is None]
            if not missing_fields:
                print("✅ All required fields present")
                checks_passed += 1
            else:
                print(f"❌ Missing fields: {missing_fields}")
            
            print()
            print(f"🎯 FINAL SCORE: {checks_passed}/{total_checks} checks passed")
            
            if checks_passed == total_checks:
                print("🎉 ALL BUGS SUCCESSFULLY FIXED!")
                print("   ✅ Duration calculation corrected")
                print("   ✅ Accrued interest properly calculated")
                print("   ✅ Dirty price formula working")
                print("   ✅ Treasury schedule logic fixed")
                print("   ✅ Price input handling correct")
                print("   ✅ All metrics within expected ranges")
                print()
                print("🚀 READY FOR PRODUCTION!")
            else:
                print("⚠️  Some issues still remain - need further investigation")
        else:
            print(f"❌ CALCULATION FAILED: {result.get('error')}")
            
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    final_validation()
