#!/usr/bin/env python3
"""Test duration calculation with different issue date assumptions"""

import QuantLib as ql

def test_treasury_duration(issue_date_method="calculated"):
    """Test US Treasury 3% 2052 duration with different issue date methods"""
    
    # Setup
    settlement = ql.Date(18, 4, 2025)
    maturity = ql.Date(15, 8, 2052)
    coupon = 0.03
    price = 71.66
    
    # Day count and calendar
    day_count = ql.ActualActual(ql.ActualActual.Bond)
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    
    print(f"\nTesting with issue_date_method: {issue_date_method}")
    
    # Method 1: Calculate issue date based on coupon schedule
    if issue_date_method == "calculated":
        # Work backwards from maturity to find theoretical issue date
        # For a bond maturing Aug 15, 2052, paying semi-annually
        # The issue date would be some Feb 15 or Aug 15
        issue_date = ql.Date(15, 8, 2022)  # Arbitrary but on schedule
        print(f"Calculated issue date: {issue_date}")
        
    # Method 2: Use settlement date as issue date (no past coupons)
    elif issue_date_method == "settlement":
        issue_date = settlement
        print(f"Using settlement as issue date: {issue_date}")
        
    # Method 3: Recent issue date (like a new bond)
    elif issue_date_method == "recent":
        issue_date = ql.Date(15, 2, 2025)  # Recent Feb 15
        print(f"Recent issue date: {issue_date}")
    
    # Create schedule
    schedule = ql.Schedule(
        issue_date,
        maturity,
        ql.Period(ql.Semiannual),
        calendar,
        ql.Unadjusted,
        ql.Unadjusted,
        ql.DateGeneration.Backward,
        True  # endOfMonth
    )
    
    # Create bond
    bond = ql.FixedRateBond(
        2,  # settlementDays
        100.0,  # faceAmount
        schedule,
        [coupon],
        day_count,
        ql.Following,  # paymentConvention
        100.0  # redemption
    )
    
    # Calculate analytics
    ytm_calc = bond.bondYield(price, day_count, ql.Compounded, ql.Semiannual, settlement)
    
    # Duration calculations
    duration = ql.BondFunctions.duration(
        bond, ytm_calc, day_count, ql.Compounded, ql.Semiannual, 
        ql.Duration.Modified, settlement
    )
    
    macaulay = ql.BondFunctions.duration(
        bond, ytm_calc, day_count, ql.Compounded, ql.Semiannual, 
        ql.Duration.Macaulay, settlement
    )
    
    # Accrued interest
    accrued = bond.accruedAmount(settlement)
    
    print(f"YTM: {ytm_calc * 100:.6f}%")
    print(f"Modified Duration: {duration:.6f}")
    print(f"Macaulay Duration: {macaulay:.6f}")
    print(f"Accrued Interest: {accrued:.6f}")
    print(f"Number of cashflows: {len(list(bond.cashflows()))}")
    
    # Show first few and last few cashflows
    cashflows = list(bond.cashflows())
    print("\nFirst 3 cashflows:")
    for i, cf in enumerate(cashflows[:3]):
        print(f"  {i+1}: {cf.date()} - ${cf.amount():.2f}")
    print("...")
    print("Last 3 cashflows:")
    for i, cf in enumerate(cashflows[-3:], len(cashflows)-3):
        print(f"  {i+1}: {cf.date()} - ${cf.amount():.2f}")
    
    return duration

# Test different methods
print("="*60)
print("US Treasury 3% 2052 Duration Test")
print("Price: 71.66, Settlement: 2025-04-18")
print("="*60)

dur1 = test_treasury_duration("calculated")
dur2 = test_treasury_duration("settlement")
dur3 = test_treasury_duration("recent")

print("\n" + "="*60)
print("SUMMARY:")
print(f"Duration with calculated issue date: {dur1:.6f}")
print(f"Duration with settlement as issue: {dur2:.6f}")
print(f"Duration with recent issue date: {dur3:.6f}")
print(f"Difference (calculated vs settlement): {dur1 - dur2:.6f}")
print("="*60)