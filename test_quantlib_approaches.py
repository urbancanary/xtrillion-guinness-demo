#!/usr/bin/env python3
"""
🔧 TEST DIFFERENT QUANTLIB APPROACHES
Find the RIGHT way to calculate Treasury bonds without manual issue dates
"""

import QuantLib as ql
from datetime import datetime, date

def test_quantlib_approaches():
    print("🔧 TESTING DIFFERENT QUANTLIB APPROACHES FOR TREASURY")
    print("=" * 65)
    
    # Set evaluation date
    trade_date = date(2025, 7, 29)
    calculation_date = ql.Date(trade_date.day, trade_date.month, trade_date.year)
    ql.Settings.instance().evaluationDate = calculation_date
    
    # Bond parameters
    coupon = 3.0  # 3% annual
    price = 71.66
    maturity_date = datetime(2052, 8, 15)
    ql_maturity = ql.Date(maturity_date.day, maturity_date.month, maturity_date.year)
    
    # Standard setup
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    day_counter = ql.ActualActual(ql.ActualActual.ISDA)
    frequency = ql.Semiannual
    settlement_date = calculation_date
    
    print(f"Settlement: {settlement_date}")
    print(f"Maturity: {ql_maturity}")
    print(f"Coupon: {coupon}%")
    print(f"Price: {price}")
    print()
    
    # APPROACH 1: QuantLib's MakeSchedule (automatic)
    print("🧪 APPROACH 1: QuantLib MakeSchedule (automatic)")
    try:
        schedule1 = ql.MakeSchedule(
            settlement_date,
            ql_maturity,
            ql.Period(frequency),
            calendar
        )
        
        bond1 = ql.FixedRateBond(0, 100.0, schedule1, [coupon/100.0], day_counter)
        yield1 = bond1.bondYield(price, day_counter, ql.Compounded, frequency)
        duration1 = ql.BondFunctions.duration(bond1, yield1*100, day_counter, ql.Compounded, frequency, ql.Duration.Modified)
        accrued1 = bond1.accruedAmount()
        
        print(f"   Yield: {yield1*100:.4f}%")
        print(f"   Duration: {duration1:.2f} years")
        print(f"   Accrued: {accrued1:.6f}")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print()
    
    # APPROACH 2: Standard Treasury conventions with proper day count
    print("🧪 APPROACH 2: Treasury-specific day count (ActualActual_ISMA)")
    try:
        day_counter_treasury = ql.ActualActual(ql.ActualActual.ISMA)
        
        schedule2 = ql.Schedule(
            settlement_date,
            ql_maturity,
            ql.Period(frequency),
            calendar,
            ql.Following,
            ql.Following,
            ql.DateGeneration.Backward,
            False
        )
        
        bond2 = ql.FixedRateBond(0, 100.0, schedule2, [coupon/100.0], day_counter_treasury)
        yield2 = bond2.bondYield(price, day_counter_treasury, ql.Compounded, frequency)
        duration2 = ql.BondFunctions.duration(bond2, yield2*100, day_counter_treasury, ql.Compounded, frequency, ql.Duration.Modified)
        accrued2 = bond2.accruedAmount()
        
        print(f"   Yield: {yield2*100:.4f}%")
        print(f"   Duration: {duration2:.2f} years")
        print(f"   Accrued: {accrued2:.6f}")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print()
    
    # APPROACH 3: Use QuantLib's Treasury-specific functions
    print("🧪 APPROACH 3: Calculate duration directly with QuantLib helpers")
    try:
        # Create minimal bond
        schedule3 = ql.Schedule(
            settlement_date,
            ql_maturity,
            ql.Period(frequency),
            calendar,
            ql.Following,
            ql.Following,
            ql.DateGeneration.Backward,
            False
        )
        
        bond3 = ql.FixedRateBond(0, 100.0, schedule3, [coupon/100.0], day_counter)
        
        # Use different compounding for yield calculation
        yield3_simple = bond3.bondYield(price, day_counter, ql.Simple, frequency)
        yield3_compound = bond3.bondYield(price, day_counter, ql.Compounded, frequency)
        
        # Try duration with different yield formats
        duration3_simple = ql.BondFunctions.duration(bond3, yield3_simple*100, day_counter, ql.Simple, frequency, ql.Duration.Modified)
        duration3_compound = ql.BondFunctions.duration(bond3, yield3_compound*100, day_counter, ql.Compounded, frequency, ql.Duration.Modified)
        
        print(f"   Simple yield: {yield3_simple*100:.4f}% → Duration: {duration3_simple:.2f}")
        print(f"   Compound yield: {yield3_compound*100:.4f}% → Duration: {duration3_compound:.2f}")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print()
    
    # APPROACH 4: Manual analytical duration (for comparison)
    print("🧪 APPROACH 4: Analytical duration estimation")
    try:
        years_to_maturity = (ql_maturity - settlement_date) / 365.25
        # Approximate yield from price
        approx_yield = coupon / 100.0 + (100 - price) / (price * years_to_maturity)
        
        # Modified duration approximation: Macaulay Duration / (1 + y/2)
        # For semi-annual bond: approximately years_to_maturity / (1 + yield/2)
        approx_duration = years_to_maturity / (1 + approx_yield/2)
        
        print(f"   Years to maturity: {years_to_maturity:.2f}")
        print(f"   Approximate yield: {approx_yield*100:.4f}%")
        print(f"   Approximate duration: {approx_duration:.2f} years")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print()
    print("🎯 EXPECTED: Duration should be ~19-20 years for this bond")
    print("   Which approach gives the most reasonable result?")

if __name__ == "__main__":
    test_quantlib_approaches()
