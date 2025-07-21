#!/usr/bin/env python3
"""
Treasury Bond Method 3 Implementation with Debug Info
====================================================

Implement the successful Method 3 approach:
1. Use proper issue date (Feb 15, 2025 for our Treasury)
2. Let QuantLib handle all coupon calculations  
3. Return days accrued and accrued per million for debug
"""

import sys
sys.path.append('.')
import QuantLib as ql

def calculate_treasury_with_debug(description, price=71.66, settlement_date_str="2025-06-30"):
    """
    Calculate Treasury bond using Method 3 with debug information
    
    Returns:
        dict with yield, duration, accrued, days_accrued, accrued_per_million
    """
    
    print("🏛️ TREASURY BOND METHOD 3 + DEBUG")
    print("=" * 50)
    
    # Bond parameters
    coupon_rate = 3.0 / 100.0
    price = 71.66
    face_value = 100.0
    
    # Dates
    settlement_date = ql.Date(30, 6, 2025)
    maturity_date = ql.Date(15, 8, 2052)
    issue_date = ql.Date(15, 2, 2025)  # Key: Proper Treasury issue date
    
    print(f"📋 Bond: {description}")
    print(f"💰 Price: {price}")
    print(f"📅 Settlement: {settlement_date}")
    print(f"📅 Issue Date: {issue_date} (KEY FIX)")
    print(f"📅 Maturity: {maturity_date}")
    print()
    
    # QuantLib setup
    ql.Settings.instance().evaluationDate = settlement_date
    
    # US Treasury conventions
    day_count = ql.ActualActual(ql.ActualActual.Bond)
    business_convention = ql.Following
    frequency = ql.Semiannual
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    
    # Create schedule FROM ISSUE DATE (Method 3)
    schedule = ql.Schedule(
        issue_date, maturity_date, ql.Period(frequency),  # ✅ Start from issue_date, not settlement_date
        calendar, business_convention, business_convention,
        ql.DateGeneration.Backward, False
    )
    
    print(f"📅 Payment Schedule (from issue date):")
    print(f"   First Payment: {schedule[1]}")
    print(f"   Second Payment: {schedule[2]}")
    print(f"   Total Payments: {len(schedule) - 1}")
    print()
    
    # Create bond
    coupons = [coupon_rate]
    bond = ql.FixedRateBond(0, face_value, schedule, coupons, day_count)
    
    # Set up pricing engine
    bond_engine = ql.DiscountingBondEngine(ql.YieldTermStructureHandle())
    bond.setPricingEngine(bond_engine)
    
    # Calculate metrics
    yield_rate = bond.bondYield(price, day_count, ql.Compounded, frequency, settlement_date)
    duration = ql.BondFunctions.duration(
        bond,
        ql.InterestRate(yield_rate, day_count, ql.Compounded, frequency),
        ql.Duration.Modified,
        settlement_date
    )
    accrued = bond.accruedAmount(settlement_date)
    
    # DEBUG INFO: Get days accrued and accrued per million
    days_accrued = 0
    accrued_per_million = 0
    
    # Find the coupon period containing settlement date
    for i, cf in enumerate(bond.cashflows()):
        try:
            # Try to cast to coupon
            coupon_cf = ql.as_coupon(cf)
            if coupon_cf:
                accrual_start = coupon_cf.accrualStartDate()
                accrual_end = coupon_cf.accrualEndDate()
                
                if accrual_start <= settlement_date < accrual_end:
                    # This is the current coupon period
                    days_accrued = day_count.dayCount(accrual_start, settlement_date)
                    days_in_period = day_count.dayCount(accrual_start, accrual_end)
                    
                    # Calculate accrued per million (10,000 basis points per 1%)
                    accrued_per_million = (accrued / face_value) * 1000000
                    
                    print(f"🧾 ACCRUED INTEREST DEBUG:")
                    print(f"   Accrual Start: {accrual_start}")
                    print(f"   Settlement: {settlement_date}")
                    print(f"   Accrual End: {accrual_end}")
                    print(f"   Days Accrued: {days_accrued}")
                    print(f"   Days in Period: {days_in_period}")
                    print(f"   Accrued Amount: ${accrued:.4f}")
                    print(f"   Accrued per Million: {accrued_per_million:.2f}")
                    break
        except:
            continue
    
    print()
    print(f"💰 FINAL RESULTS:")
    print(f"   Yield: {yield_rate * 100:.5f}%")
    print(f"   Duration: {duration:.5f} years")
    print(f"   Accrued: ${accrued:.4f}")
    print(f"   Days Accrued: {days_accrued}")
    print(f"   Accrued per Million: {accrued_per_million:.2f}")
    print()
    
    # Compare to expected BBG values (provided by user)
    expected_yield = 4.89916  # Keep original yield expectation
    expected_duration = 16.3578392273866  # User provided BBG duration
    expected_accrued_per_million = 11187.845  # User provided BBG accrued per million
    expected_accrued = expected_accrued_per_million / 10000  # Convert to dollar amount
    
    yield_diff = (yield_rate * 100) - expected_yield
    duration_diff = duration - expected_duration
    accrued_diff = accrued - expected_accrued
    accrued_per_million_diff = accrued_per_million - expected_accrued_per_million
    
    print(f"📊 VS EXPECTED BBG VALUES:")
    print(f"   Yield Diff: {yield_diff:+.5f}% (Expected: {expected_yield:.5f}%)")
    print(f"   Duration Diff: {duration_diff:+.8f} (Expected: {expected_duration:.10f})")
    print(f"   Accrued Diff: ${accrued_diff:+.4f} (Expected: ${expected_accrued:.4f})")
    print(f"   Accrued per Million Diff: {accrued_per_million_diff:+.3f} (Expected: {expected_accrued_per_million:.3f})")
    
    return {
        'yield': yield_rate * 100,
        'duration': duration,
        'accrued': accrued,
        'days_accrued': days_accrued,
        'accrued_per_million': accrued_per_million,
        'yield_diff': yield_diff,
        'duration_diff': duration_diff,
        'accrued_diff': accrued_diff,
        'accrued_per_million_diff': accrued_per_million_diff,
        'expected_duration': expected_duration,
        'expected_accrued_per_million': expected_accrued_per_million
    }

def create_treasury_bond_method3(settlement_date, maturity_date, coupon_rate, day_count, frequency, calendar):
    """
    Create Treasury bond using Method 3 approach
    
    Args:
        settlement_date: ql.Date
        maturity_date: ql.Date  
        coupon_rate: float (as decimal)
        day_count: ql.DayCounter
        frequency: ql.Frequency
        calendar: ql.Calendar
        
    Returns:
        tuple: (bond, issue_date, days_accrued, accrued_per_million)
    """
    
    # Calculate proper Treasury issue date
    # For Aug 15 maturity, use Feb 15 of the same year or previous year
    if maturity_date.month() == 8 and maturity_date.dayOfMonth() == 15:
        # Aug 15 maturity, try Feb 15 of same year first
        issue_year = settlement_date.year()
        issue_date = ql.Date(15, 2, issue_year)
        
        # If Feb 15 is after settlement, use previous year
        if issue_date >= settlement_date:
            issue_date = ql.Date(15, 2, issue_year - 1)
    else:
        # For other maturities, use standard approach
        # Find the most recent Feb 15 or Aug 15 before settlement
        settlement_month = settlement_date.month()
        settlement_year = settlement_date.year()
        
        if settlement_month < 2 or (settlement_month == 2 and settlement_date.dayOfMonth() < 15):
            # Before Feb 15, use Aug 15 of previous year
            issue_date = ql.Date(15, 8, settlement_year - 1)
        elif settlement_month < 8 or (settlement_month == 8 and settlement_date.dayOfMonth() < 15):
            # Before Aug 15, use Feb 15 of current year
            issue_date = ql.Date(15, 2, settlement_year)
        else:
            # After Aug 15, use Aug 15 of current year
            issue_date = ql.Date(15, 8, settlement_year)
    
    # Create schedule from issue date
    schedule = ql.Schedule(
        issue_date, maturity_date, ql.Period(frequency),
        calendar, ql.Following, ql.Following,
        ql.DateGeneration.Backward, False
    )
    
    # Create bond
    bond = ql.FixedRateBond(0, 100.0, schedule, [coupon_rate], day_count)
    
    # Calculate debug info
    days_accrued = 0
    accrued_per_million = 0
    
    # Get accrued information
    accrued = bond.accruedAmount(settlement_date)
    accrued_per_million = (accrued / 100.0) * 1000000
    
    # Find days accrued
    for cf in bond.cashflows():
        try:
            coupon_cf = ql.as_coupon(cf)
            if coupon_cf:
                if coupon_cf.accrualStartDate() <= settlement_date < coupon_cf.accrualEndDate():
                    days_accrued = day_count.dayCount(coupon_cf.accrualStartDate(), settlement_date)
                    break
        except:
            continue
    
    return bond, issue_date, days_accrued, accrued_per_million

if __name__ == "__main__":
    result = calculate_treasury_with_debug("US TREASURY N/B, 3%, 15-Aug-2052")
