#!/usr/bin/env python3
"""
Direct test of the fixed duration calculation
"""

import QuantLib as ql
import sys
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

from google_analysis9 import calculate_bond_metrics_with_conventions_using_shared_engine, get_correct_quantlib_compounding

def create_test_treasury_handle():
    """Create a simple flat treasury curve for testing"""
    # Settlement date
    settlement_date = ql.Date(30, 7, 2025)
    ql.Settings.instance().evaluationDate = settlement_date
    
    # Create a flat yield curve at 4.1%
    flat_rate = 0.041
    day_count = ql.ActualActual(ql.ActualActual.ISDA)
    compounding = ql.Compounded
    frequency = ql.Semiannual
    
    flat_curve = ql.FlatForward(settlement_date, flat_rate, day_count, compounding, frequency)
    treasury_handle = ql.YieldTermStructureHandle(flat_curve)
    
    return treasury_handle, settlement_date

def test_fixed_treasury_duration_direct():
    print("🎯 Direct Test of FIXED Treasury Duration Calculation")
    print("=" * 60)
    
    # Create test environment
    treasury_handle, settlement_date = create_test_treasury_handle()
    
    # Treasury bond parameters
    isin = "US912810TJ79"
    coupon = 0.03  # 3%
    maturity_date = "2052-08-15"  # August 15, 2052
    price = 71.66
    trade_date = ql.Date(30, 7, 2025)
    
    # Dummy ticker conventions (will be overridden for Treasury)
    ticker_conventions = {
        'day_count': 'ActualActual_ISDA',
        'business_convention': 'Following', 
        'frequency': 'Semiannual'
    }
    
    print(f"Testing: {isin}")
    print(f"Coupon: {coupon*100}%")
    print(f"Maturity: {maturity_date}")
    print(f"Price: {price}")
    print(f"Settlement: {settlement_date}")
    print()
    
    try:
        # Test the fixed duration calculation directly
        yield_result, duration_result, spread_result, accrued_result, error_msg = calculate_bond_metrics_with_conventions_using_shared_engine(
            isin, coupon, maturity_date, price, trade_date, treasury_handle, ticker_conventions
        )
        
        if error_msg:
            print(f"❌ Calculation failed: {error_msg}")
        else:
            print("📊 FIXED CALCULATION RESULTS:")
            print(f"Yield: {yield_result:.4f}%")
            print(f"Duration: {duration_result:.6f} years")  
            print(f"Spread: {spread_result:.0f} bps")
            print(f"Accrued: {accrued_result:.4f}%")
            print()
            
            # Test what conventions are detected
            print("🔍 CONVENTION DETECTION:")
            compounding_freq = get_correct_quantlib_compounding(isin, description=None, issuer=None)
            is_treasury = (compounding_freq == ql.Semiannual)
            print(f"Detected as: {'Treasury' if is_treasury else 'Corporate'}")
            print(f"Compounding: {'Semiannual' if compounding_freq == ql.Semiannual else 'Annual'}")
            print()
            
            # Compare with target
            target_duration = 16.35
            if duration_result:
                difference = abs(duration_result - target_duration)
                print("🎯 COMPARISON WITH TARGET:")
                print(f"Target Duration: {target_duration:.2f} years")
                print(f"Fixed Duration: {duration_result:.2f} years") 
                print(f"Difference: {difference:.4f} years")
                
                if difference < 0.01:
                    print("✅ SPOT-ON ACCURACY ACHIEVED!")
                elif difference < 0.05:
                    print("✅ EXCELLENT ACCURACY!") 
                elif difference < 0.22:
                    print("✅ IMPROVED ACCURACY!")
                else:
                    print("⚠️ Still needs improvement")
                    
                print()
                print("📋 ANALYSIS:")
                print(f"Previous manual calculation: 16.57 years")
                print(f"Fixed calculation: {duration_result:.2f} years")
                print(f"Improvement: {abs(16.57 - duration_result):.4f} years")
                
        return duration_result
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = test_fixed_treasury_duration_direct()
    
    if result:
        print("\n" + "="*60)
        print("🏆 FIXED DURATION CALCULATION COMPLETE")
        print(f"Result: {result:.6f} years")
        print("The InterestRate object approach is now implemented!")
    else:
        print("\n❌ Test failed to complete")
