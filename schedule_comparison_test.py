#!/usr/bin/env python3
"""
Schedule Comparison Test
======================

Compare the actual payment schedules to find the yield difference cause
"""

import QuantLib as ql
from datetime import datetime

def compare_schedules():
    """Compare payment schedules between working and non-working approaches"""
    
    print("📅 SCHEDULE COMPARISON TEST")
    print("=" * 80)
    
    # Common parameters
    calculation_date = ql.Date(30, 6, 2025)
    ql.Settings.instance().evaluationDate = calculation_date
    maturity_date = ql.Date(15, 8, 2052)
    coupon_rate = 0.03
    clean_price = 71.66
    
    print("=" * 80)
    print("📅 WORKING SCHEDULE (Direct Test)")
    print("=" * 80)
    
    # Working approach schedule
    schedule_working = ql.Schedule(
        calculation_date,  # issue date
        maturity_date,
        ql.Period(ql.Semiannual),
        ql.UnitedStates(ql.UnitedStates.GovernmentBond),
        ql.Following,
        ql.Following,
        ql.DateGeneration.Backward,
        False
    )
    
    print("Payment Dates (First 10):")
    for i, date in enumerate(schedule_working):
        if i < 10:  # Show first 10 payments
            print(f"   {i+1}: {date}")
        elif i == 10:
            print("   ...")
            break
    
    print(f"Total payments: {len(schedule_working)}")
    print(f"First payment: {schedule_working[0]}")
    print(f"Last payment: {schedule_working[-1]}")
    
    # Create bond and calculate yield
    bond_working = ql.FixedRateBond(0, 100.0, schedule_working, [coupon_rate], ql.ActualActual(ql.ActualActual.ISDA))
    yield_working = bond_working.bondYield(clean_price, ql.ActualActual(ql.ActualActual.ISDA), ql.Compounded, ql.Semiannual)
    print(f"Calculated yield: {yield_working*100:.6f}%")
    
    print()
    print("=" * 80)
    print("📅 YOUR IMPLEMENTATION SCHEDULE")
    print("=" * 80)
    
    # Your implementation schedule - exactly as in your code
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    issue_date = calculation_date  # This might be different
    
    schedule_yours = ql.Schedule(
        issue_date,  
        maturity_date, 
        ql.Period(ql.Semiannual), 
        calendar, 
        ql.Following,
        ql.Following,
        ql.DateGeneration.Backward, 
        False
    )
    
    print("Payment Dates (First 10):")
    for i, date in enumerate(schedule_yours):
        if i < 10:  # Show first 10 payments
            print(f"   {i+1}: {date}")
        elif i == 10:
            print("   ...")
            break
    
    print(f"Total payments: {len(schedule_yours)}")
    print(f"First payment: {schedule_yours[0]}")
    print(f"Last payment: {schedule_yours[-1]}")
    
    # Create bond and calculate yield
    bond_yours = ql.FixedRateBond(0, 100.0, schedule_yours, [coupon_rate], ql.ActualActual(ql.ActualActual.ISDA))
    yield_yours = bond_yours.bondYield(clean_price, ql.ActualActual(ql.ActualActual.ISDA), ql.Compounded, ql.Semiannual)
    print(f"Calculated yield: {yield_yours*100:.6f}%")
    
    print()
    print("=" * 80)
    print("🔍 COMPARISON ANALYSIS")
    print("=" * 80)
    
    print("Schedule Differences:")
    schedules_match = True
    min_len = min(len(schedule_working), len(schedule_yours))
    
    for i in range(min_len):
        if schedule_working[i] != schedule_yours[i]:
            print(f"   Date {i+1}: Working={schedule_working[i]}, Yours={schedule_yours[i]} ❌")
            schedules_match = False
    
    if len(schedule_working) != len(schedule_yours):
        print(f"   Different number of payments: Working={len(schedule_working)}, Yours={len(schedule_yours)} ❌")
        schedules_match = False
    
    if schedules_match:
        print("   ✅ Schedules are IDENTICAL")
    else:
        print("   ❌ Schedules are DIFFERENT")
    
    print(f"\nYield Comparison:")
    print(f"   Working yield: {yield_working*100:.6f}%")
    print(f"   Your yield: {yield_yours*100:.6f}%")
    print(f"   Difference: {abs(yield_working - yield_yours)*100:.6f}%")
    
    if abs(yield_working - yield_yours) < 0.0001:
        print("   ✅ Yields MATCH")
    else:
        print("   ❌ Yields DIFFERENT")
    
    print()
    print("🧪 TESTING ALTERNATIVE SCENARIOS:")
    print("-" * 50)
    
    # Test with different settlement dates
    alt_issue_date = ql.Date(29, 6, 2025)  # One day earlier
    schedule_alt = ql.Schedule(
        alt_issue_date,  
        maturity_date, 
        ql.Period(ql.Semiannual), 
        calendar, 
        ql.Following,
        ql.Following,
        ql.DateGeneration.Backward, 
        False
    )
    
    bond_alt = ql.FixedRateBond(0, 100.0, schedule_alt, [coupon_rate], ql.ActualActual(ql.ActualActual.ISDA))
    yield_alt = bond_alt.bondYield(clean_price, ql.ActualActual(ql.ActualActual.ISDA), ql.Compounded, ql.Semiannual)
    print(f"With issue date 29-Jun-2025: {yield_alt*100:.6f}%")
    
    # Test if your implementation yield matches any of these
    your_actual_yield = 4.935783
    print(f"\nYour actual implementation yield: {your_actual_yield:.6f}%")
    print("Checking if it matches any scenario...")

if __name__ == "__main__":
    compare_schedules()
