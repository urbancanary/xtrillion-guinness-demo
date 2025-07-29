#!/usr/bin/env python3
"""
🔧 DEBUG: Test raw QuantLib duration calculation
Find where the duration calculation is going wrong
"""

import QuantLib as ql
from datetime import datetime, date

def debug_duration_calculation():
    print("🔍 DEBUGGING RAW QUANTLIB DURATION CALCULATION")
    print("=" * 60)
    
    # Set evaluation date
    trade_date = date(2025, 7, 29)
    calculation_date = ql.Date(trade_date.day, trade_date.month, trade_date.year)
    ql.Settings.instance().evaluationDate = calculation_date
    
    # Bond parameters
    coupon = 3.0  # 3% coupon
    price = 71.66
    maturity_date = datetime(2052, 8, 15)
    ql_maturity = ql.Date(maturity_date.day, maturity_date.month, maturity_date.year)
    
    # Standard conventions
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    day_counter = ql.ActualActual(ql.ActualActual.ISDA)
    frequency = ql.Semiannual
    
    print(f"Evaluation Date: {calculation_date}")
    print(f"Maturity Date: {ql_maturity}")
    print(f"Time to Maturity: {(ql_maturity - calculation_date)/365.25:.2f} years")
    print(f"Price: {price}")
    print(f"Coupon: {coupon}%")
    print()
    
    # Create simple bond (recent issue date)
    issue_date = ql.Date(15, 2, 2025)  # Recent issue
    schedule = ql.Schedule(
        issue_date,
        ql_maturity,
        ql.Period(frequency),
        calendar,
        ql.Following,
        ql.Following,
        ql.DateGeneration.Backward,
        False
    )
    
    bond = ql.FixedRateBond(0, 100.0, schedule, [coupon/100.0], day_counter)
    
    print("🧮 STEP-BY-STEP CALCULATION DEBUG:")
    print("-" * 40)
    
    # Step 1: Calculate yield
    try:
        yield_decimal = bond.bondYield(price, day_counter, ql.Compounded, frequency)
        yield_percent = yield_decimal * 100
        
        print(f"✅ Yield calculated:")
        print(f"   Decimal: {yield_decimal:.6f}")
        print(f"   Percent: {yield_percent:.4f}%")
        print()
        
        # Step 2: Test duration with DECIMAL yield (original QuantLib way)
        print("🧪 TEST 1: Duration with DECIMAL yield")
        try:
            duration_decimal = ql.BondFunctions.duration(
                bond, 
                yield_decimal,  # Use decimal yield
                day_counter, 
                ql.Compounded, 
                frequency, 
                ql.Duration.Modified
            )
            print(f"   Raw duration (decimal yield): {duration_decimal:.6f}")
            print(f"   Scaled x100: {duration_decimal * 100:.2f}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        print()
        
        # Step 3: Test duration with PERCENTAGE yield
        print("🧪 TEST 2: Duration with PERCENTAGE yield")
        try:
            duration_percent = ql.BondFunctions.duration(
                bond,
                yield_percent,  # Use percentage yield
                day_counter,
                ql.Compounded,
                frequency,
                ql.Duration.Modified
            )
            print(f"   Raw duration (percent yield): {duration_percent:.6f}")
            print(f"   No scaling: {duration_percent:.2f}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        print()
        
        # Step 4: Test with different compounding
        print("🧪 TEST 3: Duration with Simple compounding")
        try:
            duration_simple = ql.BondFunctions.duration(
                bond,
                yield_decimal,
                day_counter,
                ql.Simple,  # Simple instead of Compounded
                frequency,
                ql.Duration.Modified
            )
            print(f"   Raw duration (simple): {duration_simple:.6f}")
            print(f"   Scaled x100: {duration_simple * 100:.2f}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        print()
        
        # Step 5: Manual duration estimation for comparison
        print("🧪 MANUAL ESTIMATION:")
        time_to_maturity = (ql_maturity - calculation_date) / 365.25
        # Rough duration approximation: time_to_maturity / (1 + yield/2)
        approx_duration = time_to_maturity / (1 + yield_decimal/2)
        print(f"   Time to maturity: {time_to_maturity:.2f} years")
        print(f"   Approx duration: {approx_duration:.2f} years")
        print(f"   Expected range: 18-22 years for this bond")
        
        print()
        print("🎯 DIAGNOSIS:")
        if duration_decimal < 0.001:
            print("❌ CRITICAL: Raw duration is essentially zero!")
            print("   This suggests QuantLib thinks the bond has no duration sensitivity")
            print("   Possible causes:")
            print("   - Bond appears to be at/past maturity")
            print("   - Pricing engine issue")
            print("   - Schedule creation problem")
        elif duration_percent > 10:
            print("✅ Duration with percentage yield looks reasonable")
        else:
            print("❌ Still problematic - need further investigation")
            
    except Exception as e:
        print(f"❌ Yield calculation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_duration_calculation()
