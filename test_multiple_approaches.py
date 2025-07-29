#!/usr/bin/env python3
"""
🔧 ULTIMATE FIX: Use QuantLib's standard bond creation WITHOUT custom schedules
Test multiple approaches to find what works
"""

import QuantLib as ql
from datetime import datetime, date

def test_multiple_approaches():
    print("🔧 TESTING MULTIPLE QUANTLIB APPROACHES")
    print("=" * 70)
    
    # Set evaluation date
    trade_date = date(2025, 7, 29)
    calculation_date = ql.Date(trade_date.day, trade_date.month, trade_date.year)
    ql.Settings.instance().evaluationDate = calculation_date
    
    # Bond parameters
    coupon = 3.0  # 3% coupon
    price = 71.66
    maturity_date = datetime(2052, 8, 15)
    ql_maturity = ql.Date(maturity_date.day, maturity_date.month, maturity_date.year)
    
    print(f"Settlement Date: {calculation_date}")
    print(f"Maturity Date: {ql_maturity}")
    print(f"Price: {price}")
    print(f"Coupon: {coupon}%")
    print()
    
    # Standard conventions
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    day_counter = ql.ActualActual(ql.ActualActual.ISDA)
    frequency = ql.Semiannual
    
    # APPROACH 1: Use reasonable issue date (not 30 years ago!)
    print("🧪 APPROACH 1: Reasonable issue date (2 years ago)")
    try:
        issue_date_reasonable = ql.Date(15, 8, 2023)  # 2 years ago, same month/day
        schedule1 = ql.Schedule(
            issue_date_reasonable,
            ql_maturity,
            ql.Period(frequency),
            calendar,
            ql.Following,
            ql.Following,
            ql.DateGeneration.Backward,
            False
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
    
    # APPROACH 2: Use settlement date as effective issue (standard for pricing)
    print("🧪 APPROACH 2: Settlement as issue (standard pricing approach)")
    try:
        # Create a schedule that goes backwards from maturity with proper frequency
        schedule2 = ql.Schedule(
            calculation_date,
            ql_maturity,
            ql.Period(frequency),
            calendar,
            ql.Following,
            ql.Following,
            ql.DateGeneration.Forward,  # Forward from settlement
            False
        )
        
        bond2 = ql.FixedRateBond(0, 100.0, schedule2, [coupon/100.0], day_counter)
        yield2 = bond2.bondYield(price, day_counter, ql.Compounded, frequency)
        duration2 = ql.BondFunctions.duration(bond2, yield2*100, day_counter, ql.Compounded, frequency, ql.Duration.Modified)
        accrued2 = bond2.accruedAmount()
        
        print(f"   Yield: {yield2*100:.4f}%")
        print(f"   Duration: {duration2:.2f} years")
        print(f"   Accrued: {accrued2:.6f}")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print()
    
    # APPROACH 3: Use QuantLib's automatic Treasury schedule generation
    print("🧪 APPROACH 3: Let QuantLib auto-generate Treasury schedule")
    try:
        # Use original issue date that makes sense for a 30-year Treasury
        # For a bond maturing Aug 15, 2052, it was likely issued Aug 15, 2022
        original_issue = ql.Date(15, 8, 2022)  # Standard 30-year Treasury issue
        
        schedule3 = ql.Schedule(
            original_issue,
            ql_maturity, 
            ql.Period(frequency),
            calendar,
            ql.Following,
            ql.Following,
            ql.DateGeneration.Backward,  # Backward from maturity (standard)
            False
        )
        
        bond3 = ql.FixedRateBond(0, 100.0, schedule3, [coupon/100.0], day_counter)
        yield3 = bond3.bondYield(price, day_counter, ql.Compounded, frequency)
        duration3 = ql.BondFunctions.duration(bond3, yield3*100, day_counter, ql.Compounded, frequency, ql.Duration.Modified)
        accrued3 = bond3.accruedAmount()
        
        print(f"   Yield: {yield3*100:.4f}%")
        print(f"   Duration: {duration3:.2f} years")
        print(f"   Accrued: {accrued3:.6f}")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print()
    
    # APPROACH 4: Direct calculation using bond functions (no schedule)
    print("🧪 APPROACH 4: Direct QuantLib bond calculation") 
    try:
        # Calculate directly using time to maturity
        years_to_maturity = (ql_maturity - calculation_date) / 365.25
        
        # Create minimal bond for calculation
        simple_schedule = ql.Schedule(
            calculation_date,
            ql_maturity,
            ql.Period(frequency),
            calendar,
            ql.Following,
            ql.Following,
            ql.DateGeneration.Backward,
            False
        )
        
        bond4 = ql.FixedRateBond(0, 100.0, simple_schedule, [coupon/100.0], day_counter)
        
        # Manual yield calculation for validation
        print(f"   Time to maturity: {years_to_maturity:.2f} years")
        
        yield4 = bond4.bondYield(price, day_counter, ql.Compounded, frequency)
        duration4 = ql.BondFunctions.duration(bond4, yield4*100, day_counter, ql.Compounded, frequency, ql.Duration.Modified)
        
        print(f"   Yield: {yield4*100:.4f}%")
        print(f"   Duration: {duration4:.2f} years")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print()
    print("🎯 ANALYSIS: Which approach gives reasonable ~20-year duration?")

if __name__ == "__main__":
    test_multiple_approaches()
