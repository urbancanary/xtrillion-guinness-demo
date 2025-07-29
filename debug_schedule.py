#!/usr/bin/env python3
"""
🔍 SCHEDULE DEBUG: Investigate why accrued interest = 0
"""

import QuantLib as ql
from datetime import datetime, date

def debug_bond_schedule():
    print("🔍 DEBUGGING BOND SCHEDULE FOR ACCRUED INTEREST")
    print("=" * 60)
    
    # Set evaluation date
    trade_date = date(2025, 7, 29)
    calculation_date = ql.Date(trade_date.day, trade_date.month, trade_date.year)
    ql.Settings.instance().evaluationDate = calculation_date
    
    # Bond parameters
    maturity_date = datetime(2052, 8, 15)
    ql_maturity = ql.Date(maturity_date.day, maturity_date.month, maturity_date.year)
    
    # Calendar and conventions
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    frequency = ql.Semiannual
    settlement_date = calculation_date
    
    print(f"Settlement Date: {settlement_date}")
    print(f"Maturity Date: {ql_maturity}")
    print()
    
    # TEST 1: Current broken schedule (settlement → maturity)
    print("🧪 TEST 1: Current schedule (settlement → maturity)")
    schedule_current = ql.Schedule(
        settlement_date,  # This is the problem!
        ql_maturity,
        ql.Period(frequency),
        calendar,
        ql.Following,
        ql.Following,
        ql.DateGeneration.Backward,
        False
    )
    
    print("Schedule dates:")
    dates = list(schedule_current.dates())
    for i in range(min(5, len(dates))):  # Show first 5 dates
        print(f"   {i}: {dates[i]}")
    print(f"   ... (total {len(dates)} dates)")
    print()
    
    # TEST 2: Proper Treasury schedule (issue date approach)
    print("🧪 TEST 2: Proper Treasury schedule with historical issue")
    # For Aug 15, 2052 maturity, use reasonable issue date
    issue_date = ql.Date(15, 8, 2022)  # Issued 30 years before maturity
    
    schedule_proper = ql.Schedule(
        issue_date,
        ql_maturity,
        ql.Period(frequency),
        calendar,
        ql.Following,
        ql.Following,
        ql.DateGeneration.Backward,
        False
    )
    
    proper_dates = list(schedule_proper.dates())
    print("Proper schedule (first/last dates):")
    print(f"   Issue: {proper_dates[0]}")
    print(f"   2nd payment: {proper_dates[1]}")
    print(f"   3rd payment: {proper_dates[2]}")
    print("   ...")
    print(f"   Last payment: {proper_dates[-1]}")
    print(f"   Total payments: {len(proper_dates)}")
    print()
    
    # Find the last coupon before settlement
    print("🔍 FINDING LAST COUPON BEFORE SETTLEMENT:")
    last_coupon = None
    next_coupon = None
    
    for i in range(len(proper_dates)-1):
        coupon_date = proper_dates[i]
        if coupon_date <= settlement_date:
            last_coupon = coupon_date
        elif next_coupon is None:
            next_coupon = coupon_date
            break
    
    print(f"   Last coupon: {last_coupon}")
    print(f"   Settlement: {settlement_date}")  
    print(f"   Next coupon: {next_coupon}")
    
    if last_coupon:
        days_accrued = settlement_date - last_coupon
        print(f"   Days accrued: {days_accrued}")
        
        # Rough accrued calculation for 3% coupon
        # Semi-annual coupon = 3% / 2 = 1.5% per 6 months
        days_in_period = next_coupon - last_coupon if next_coupon else 182
        accrued_fraction = days_accrued / days_in_period
        estimated_accrued = 1.5 * accrued_fraction  # 1.5% per period
        print(f"   Estimated accrued: {estimated_accrued:.4f}% of face value")
    print()
    
    # TEST 3: Create bonds with both schedules and compare accrued
    print("🧪 TEST 3: Compare accrued interest calculations")
    day_counter = ql.ActualActual(ql.ActualActual.ISDA)
    coupon = 0.03  # 3% annual
    
    # Bond with broken schedule
    bond_broken = ql.FixedRateBond(0, 100.0, schedule_current, [coupon], day_counter)
    accrued_broken = bond_broken.accruedAmount()
    
    # Bond with proper schedule  
    bond_proper = ql.FixedRateBond(0, 100.0, schedule_proper, [coupon], day_counter)
    accrued_proper = bond_proper.accruedAmount()
    
    print(f"   Broken schedule accrued: {accrued_broken:.6f}")
    print(f"   Proper schedule accrued: {accrued_proper:.6f}")
    print()
    
    if accrued_proper > 0:
        print("✅ SOLUTION FOUND: Use proper issue date for Treasury schedule!")
        print("   The current code starts schedule from settlement date")
        print("   Should start from historical issue date to get correct coupons")
    else:
        print("❌ Still investigating...")

if __name__ == "__main__":
    debug_bond_schedule()
