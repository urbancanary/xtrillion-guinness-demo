#!/usr/bin/env python3
"""Verify bond schedule generation affects duration"""

import QuantLib as ql

def calculate_with_schedule_method(method_name, issue_date):
    """Calculate duration with specific schedule generation"""
    
    settlement = ql.Date(18, 4, 2025)
    maturity = ql.Date(15, 8, 2052)
    coupon = 0.03
    price = 71.66
    
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    day_count = ql.ActualActual(ql.ActualActual.Bond)
    
    # Create schedule
    schedule = ql.Schedule(
        issue_date,
        maturity,
        ql.Period(ql.Semiannual),
        calendar,
        ql.Unadjusted,  # For treasuries
        ql.Unadjusted,  # For treasuries
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
    
    # Calculate yield
    ytm = bond.bondYield(price, day_count, ql.Compounded, ql.Semiannual, settlement)
    
    # Get accrued
    accrued = bond.accruedAmount(settlement)
    
    # Calculate durations
    mod_duration = ql.BondFunctions.duration(
        bond, ytm, day_count, ql.Compounded, ql.Semiannual, 
        ql.Duration.Modified, settlement
    )
    
    mac_duration = ql.BondFunctions.duration(
        bond, ytm, day_count, ql.Compounded, ql.Semiannual, 
        ql.Duration.Macaulay, settlement
    )
    
    print(f"\n{method_name}:")
    print(f"  Issue Date: {issue_date}")
    print(f"  YTM: {ytm*100:.6f}%")
    print(f"  Accrued: ${accrued:.6f}")
    print(f"  Modified Duration: {mod_duration:.6f}")
    print(f"  Macaulay Duration: {mac_duration:.6f}")
    
    # Check cashflow dates
    cashflows = list(bond.cashflows())
    print(f"  Number of cashflows: {len(cashflows)}")
    print(f"  First coupon: {cashflows[0].date()}")
    print(f"  Second coupon: {cashflows[1].date()}")
    
    return mod_duration, accrued

print("Testing different issue dates for US Treasury 3% 2052")
print("Settlement: 2025-04-18, Price: 71.66")
print("="*60)

# Test 1: Issue date = First of year long ago
dur1, acc1 = calculate_with_schedule_method(
    "Long ago issue (2020-02-15)", 
    ql.Date(15, 2, 2020)
)

# Test 2: Issue date = Settlement - 6 months
dur2, acc2 = calculate_with_schedule_method(
    "Recent issue (2024-08-15)", 
    ql.Date(15, 8, 2024)
)

# Test 3: Issue date = Way back to align with maturity
dur3, acc3 = calculate_with_schedule_method(
    "Aligned with maturity cycle (2022-08-15)", 
    ql.Date(15, 8, 2022)
)

print("\n" + "="*60)
print("COMPARISON:")
print(f"Long ago issue: Duration={dur1:.6f}, Accrued=${acc1:.6f}")
print(f"Recent issue: Duration={dur2:.6f}, Accrued=${acc2:.6f}")
print(f"Aligned issue: Duration={dur3:.6f}, Accrued=${acc3:.6f}")
print(f"\nAPI values: Duration=16.547934, Accrued=$0.513812")
print("="*60)

# Test what happens if we don't use end of month
print("\nTesting without end_of_month flag...")
settlement = ql.Date(18, 4, 2025)
maturity = ql.Date(15, 8, 2052)
issue = ql.Date(15, 8, 2022)

schedule_no_eom = ql.Schedule(
    issue,
    maturity,
    ql.Period(ql.Semiannual),
    ql.UnitedStates(ql.UnitedStates.GovernmentBond),
    ql.Unadjusted,
    ql.Unadjusted,
    ql.DateGeneration.Backward,
    False  # No end of month
)

bond_no_eom = ql.FixedRateBond(
    2, 100.0, schedule_no_eom, [0.03],
    ql.ActualActual(ql.ActualActual.Bond),
    ql.Following, 100.0
)

ytm_no_eom = bond_no_eom.bondYield(71.66, ql.ActualActual(ql.ActualActual.Bond), 
                                   ql.Compounded, ql.Semiannual, settlement)
dur_no_eom = ql.BondFunctions.duration(
    bond_no_eom, ytm_no_eom, ql.ActualActual(ql.ActualActual.Bond), 
    ql.Compounded, ql.Semiannual, ql.Duration.Modified, settlement
)
acc_no_eom = bond_no_eom.accruedAmount(settlement)

print(f"\nWithout end_of_month: Duration={dur_no_eom:.6f}, Accrued=${acc_no_eom:.6f}")