#!/usr/bin/env python3
"""
🔍 DEBUG DURATION CALCULATION 
Test different yield formats and day counts to get correct ~19-20 year duration
"""

import QuantLib as ql
from datetime import datetime, date

def debug_duration_calculation():
    print("🔍 DEBUGGING DURATION CALCULATION FOR TREASURY")
    print("=" * 55)
    
    # Set evaluation date
    trade_date = date(2025, 7, 29)
    calculation_date = ql.Date(trade_date.day, trade_date.month, trade_date.year)
    ql.Settings.instance().evaluationDate = calculation_date
    
    # Bond parameters
    coupon = 3.0
    price = 71.66
    maturity_date = datetime(2052, 8, 15)
    ql_maturity = ql.Date(maturity_date.day, maturity_date.month, maturity_date.year)
    
    # Standard setup with Treasury issue date
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    frequency = ql.Semiannual
    issue_date = ql.Date(15, 8, 2022)  # 30 years before maturity
    
    print(f"Settlement: {calculation_date}")
    print(f"Issue Date: {issue_date}")
    print(f"Maturity: {ql_maturity}")
    print(f"Price: {price}")
    print(f"Coupon: {coupon}%")
    print()
    
    # Create schedule
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
    
    print(f"Schedule has {len(list(schedule.dates()))} payment dates")
    print()
    
    # TEST DIFFERENT DAY COUNT CONVENTIONS
    day_counts = [
        ("ActualActual_ISDA", ql.ActualActual(ql.ActualActual.ISDA)),
        ("ActualActual_ISMA", ql.ActualActual(ql.ActualActual.ISMA)), 
        ("ActualActual_Bond", ql.ActualActual(ql.ActualActual.Bond)),
        ("Actual360", ql.Actual360()),
        ("Actual365Fixed", ql.Actual365Fixed()),
        ("Thirty360_BondBasis", ql.Thirty360(ql.Thirty360.BondBasis))
    ]
    
    for name, day_counter in day_counts:
        print(f"🧪 TESTING: {name}")
        try:
            bond = ql.FixedRateBond(0, 100.0, schedule, [coupon/100.0], day_counter)
            yield_decimal = bond.bondYield(price, day_counter, ql.Compounded, frequency)
            
            # Test duration with decimal yield
            duration_decimal = ql.BondFunctions.duration(
                bond, yield_decimal, day_counter, ql.Compounded, frequency, ql.Duration.Modified
            )
            
            # Test duration with percentage yield  
            duration_percent = ql.BondFunctions.duration(
                bond, yield_decimal*100, day_counter, ql.Compounded, frequency, ql.Duration.Modified
            )
            
            accrued = bond.accruedAmount()
            
            print(f"   Yield: {yield_decimal*100:.4f}%")
            print(f"   Duration (decimal yield): {duration_decimal:.2f} years")
            print(f"   Duration (percent yield): {duration_percent:.2f} years")
            print(f"   Accrued: {accrued:.6f}")
            
            # Check which is in expected range
            if 18 <= duration_decimal <= 22:
                print(f"   ✅ DECIMAL YIELD gives expected duration!")
            elif 18 <= duration_percent <= 22:
                print(f"   ✅ PERCENT YIELD gives expected duration!")
            else:
                print(f"   ❌ Neither gives expected ~19-20 years")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        print()
    
    # MANUAL CHECK: What should duration actually be?
    print("🎯 MANUAL DURATION CHECK:")
    print("-" * 25)
    
    # Use standard Treasury day count for manual calculation
    day_counter_std = ql.ActualActual(ql.ActualActual.ISDA)
    bond_std = ql.FixedRateBond(0, 100.0, schedule, [coupon/100.0], day_counter_std)
    yield_std = bond_std.bondYield(price, day_counter_std, ql.Compounded, frequency)
    
    # Check what Bloomberg/market would use
    print(f"Standard yield: {yield_std*100:.4f}%")
    print(f"Years to maturity: {(ql_maturity - calculation_date)/365.25:.2f}")
    
    # Try Macaulay duration for comparison
    macaulay_duration = ql.BondFunctions.duration(
        bond_std, yield_std, day_counter_std, ql.Compounded, frequency, ql.Duration.Macaulay
    )
    print(f"Macaulay duration: {macaulay_duration:.2f} years")
    print(f"Expected modified duration: ~{macaulay_duration/(1+yield_std/2):.2f} years")

if __name__ == "__main__":
    debug_duration_calculation()
