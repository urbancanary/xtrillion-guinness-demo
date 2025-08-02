#!/usr/bin/env python3
"""
Debug EMPRESA MAESTRO bond schedule
"""

import QuantLib as ql
from datetime import datetime

def debug_schedule():
    """Debug the bond schedule generation"""
    print("🔍 Debugging EMPRESA MAESTRO bond schedule")
    print("=" * 60)
    
    # Bond parameters
    maturity_date = datetime(2050, 5, 7)
    settlement_date = datetime(2025, 4, 18)
    coupon = 4.7
    
    # Convert to QuantLib dates
    ql_maturity = ql.Date(maturity_date.day, maturity_date.month, maturity_date.year)
    ql_settlement = ql.Date(settlement_date.day, settlement_date.month, settlement_date.year)
    
    # Set evaluation date
    ql.Settings.instance().evaluationDate = ql_settlement
    
    # Create calendar and conventions
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    day_counter = ql.Thirty360(ql.Thirty360.BondBasis)
    frequency = ql.Semiannual
    business_convention = ql.Unadjusted
    
    print(f"📅 Settlement date: {settlement_date.strftime('%Y-%m-%d')}")
    print(f"📅 Maturity date: {maturity_date.strftime('%Y-%m-%d')}")
    print(f"💰 Coupon: {coupon}%")
    print(f"📊 Frequency: Semi-annual")
    print(f"📋 Business Convention: Unadjusted")
    print()
    
    # Method 1: Generate schedule backward from maturity
    print("Method 1: Backward generation from maturity")
    print("-" * 40)
    
    # Start 10 years before settlement
    schedule_start = ql_settlement
    for i in range(20):  # 10 years
        schedule_start = calendar.advance(schedule_start, ql.Period(-6, ql.Months))
    
    schedule_backward = ql.Schedule(
        schedule_start,
        ql_maturity,
        ql.Period(frequency),
        calendar,
        business_convention,
        business_convention,
        ql.DateGeneration.Backward,
        False
    )
    
    print(f"Schedule has {len(schedule_backward)} dates")
    
    # Find dates around settlement
    for i in range(len(schedule_backward) - 1):
        if schedule_backward[i] <= ql_settlement <= schedule_backward[i + 1]:
            prev_date = schedule_backward[i]
            next_date = schedule_backward[i + 1]
            print(f"\n📍 Dates around settlement:")
            print(f"   Previous coupon: {prev_date}")
            print(f"   Settlement:      {ql_settlement}")
            print(f"   Next coupon:     {next_date}")
            
            # Calculate days
            days_accrued = day_counter.dayCount(prev_date, ql_settlement)
            days_in_period = day_counter.dayCount(prev_date, next_date)
            print(f"\n📊 Day count (30/360):")
            print(f"   Days accrued: {days_accrued}")
            print(f"   Days in period: {days_in_period}")
            
            # Calculate accrued
            semi_annual_coupon = coupon / 2.0
            accrued_interest = semi_annual_coupon * (days_accrued / days_in_period)
            accrued_per_million = accrued_interest * 10000
            
            print(f"\n💰 Accrued calculation:")
            print(f"   Semi-annual coupon: {semi_annual_coupon}%")
            print(f"   Accrued fraction: {days_accrued}/{days_in_period} = {days_accrued/days_in_period:.6f}")
            print(f"   Accrued interest: {accrued_interest:.6f}%")
            print(f"   Accrued per million: ${accrued_per_million:,.2f}")
            break
    
    # Method 2: Show the actual coupon dates
    print("\n\nMethod 2: Show actual coupon dates")
    print("-" * 40)
    
    # Create a proper schedule from issue to maturity
    # For a bond maturing May 7, 2050, coupons should be May 7 and Nov 7
    issue_date = ql.Date(7, 5, 2020)  # Assume issued May 7, 2020
    
    schedule_proper = ql.Schedule(
        issue_date,
        ql_maturity,
        ql.Period(frequency),
        calendar,
        business_convention,
        business_convention,
        ql.DateGeneration.Forward,
        False
    )
    
    print(f"Proper schedule has {len(schedule_proper)} dates")
    print("\nCoupon dates around settlement:")
    
    for i in range(len(schedule_proper) - 1):
        if schedule_proper[i] <= ql_settlement <= schedule_proper[i + 1]:
            for j in range(max(0, i-2), min(len(schedule_proper), i+3)):
                marker = " <-- Previous" if j == i else " <-- Next" if j == i+1 else ""
                print(f"   {schedule_proper[j]}{marker}")
            
            # Calculate with proper dates
            prev_date = schedule_proper[i]
            next_date = schedule_proper[i + 1]
            days_accrued = day_counter.dayCount(prev_date, ql_settlement)
            days_in_period = day_counter.dayCount(prev_date, next_date)
            
            print(f"\n📊 Proper calculation:")
            print(f"   From {prev_date} to {ql_settlement}: {days_accrued} days")
            print(f"   Period: {days_in_period} days")
            
            accrued_interest = (coupon / 2.0) * (days_accrued / days_in_period)
            accrued_per_million = accrued_interest * 10000
            
            print(f"   Accrued interest: {accrued_interest:.6f}%")
            print(f"   Accrued per million: ${accrued_per_million:,.2f}")
            
            if abs(accrued_per_million - 21019.44) < 1.0:
                print("\n✅ This matches the expected value!")
            
            break

if __name__ == "__main__":
    debug_schedule()