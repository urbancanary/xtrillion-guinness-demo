#!/usr/bin/env python3
"""
Test with Proper Treasury Coupon Schedule
=========================================

US Treasury bonds typically pay on specific dates (Feb 15, Aug 15)
Let's test with the proper schedule.
"""

import sys
sys.path.append('.')
import QuantLib as ql

def test_proper_treasury_schedule():
    """Test with proper Treasury bond coupon schedule"""
    
    print("🏛️ TESTING PROPER TREASURY COUPON SCHEDULE")
    print("=" * 60)
    
    # Bond parameters
    coupon_rate = 3.0 / 100.0
    price = 71.66
    face_value = 100.0
    
    # Settlement date from your document
    settlement_date = ql.Date(30, 6, 2025)
    maturity_date = ql.Date(15, 8, 2052)
    
    print(f"📅 Settlement Date: {settlement_date}")
    print(f"📅 Maturity Date: {maturity_date}")
    print()
    
    # QuantLib setup
    ql.Settings.instance().evaluationDate = settlement_date
    
    # US Treasury conventions
    day_count = ql.ActualActual(ql.ActualActual.Bond)
    business_convention = ql.Following
    frequency = ql.Semiannual
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    
    # Method 1: Standard schedule generation (what we used before)
    print("🔧 METHOD 1: Standard Schedule Generation")
    schedule1 = ql.Schedule(
        settlement_date, maturity_date, ql.Period(frequency),
        calendar, business_convention, business_convention,
        ql.DateGeneration.Backward, False
    )
    
    print(f"   First 3 payments: {schedule1[1]}, {schedule1[2]}, {schedule1[3]}")
    
    # Create bond with method 1
    bond1 = ql.FixedRateBond(0, face_value, schedule1, [coupon_rate], day_count)
    bond_engine = ql.DiscountingBondEngine(ql.YieldTermStructureHandle())
    bond1.setPricingEngine(bond_engine)
    
    accrued1 = bond1.accruedAmount(settlement_date)
    yield1 = bond1.bondYield(price, day_count, ql.Compounded, frequency, settlement_date)
    duration1 = ql.BondFunctions.duration(
        bond1,
        ql.InterestRate(yield1, day_count, ql.Compounded, frequency),
        ql.Duration.Modified,
        settlement_date
    )
    
    print(f"   Accrued: ${accrued1:.4f} | Yield: {yield1*100:.5f}% | Duration: {duration1:.5f}")
    print()
    
    # Method 2: Explicit Treasury schedule (Feb 15, Aug 15)
    print("🔧 METHOD 2: Explicit Treasury Schedule (Feb 15, Aug 15)")
    
    # Create explicit payment dates
    payment_dates = []
    current_year = 2025
    
    # Start with August 15, 2025 (next coupon after June 30, 2025 settlement)
    while current_year <= 2052:
        # February 15
        feb_date = ql.Date(15, 2, current_year)
        if feb_date > settlement_date:
            payment_dates.append(feb_date)
        
        # August 15
        aug_date = ql.Date(15, 8, current_year)
        if aug_date > settlement_date:
            payment_dates.append(aug_date)
            
        current_year += 1
    
    # Ensure we end on maturity date
    if payment_dates[-1] != maturity_date:
        payment_dates[-1] = maturity_date
    
    print(f"   First 3 payments: {payment_dates[0]}, {payment_dates[1]}, {payment_dates[2]}")
    print(f"   Total payments: {len(payment_dates)}")
    
    # Calculate accrued interest manually for explicit schedule
    # Find previous coupon date
    previous_coupon = ql.Date(15, 2, 2025)  # Feb 15, 2025 (before June 30, 2025)
    next_coupon = ql.Date(15, 8, 2025)      # Aug 15, 2025 (after June 30, 2025)
    
    print(f"   Previous Coupon: {previous_coupon}")
    print(f"   Next Coupon: {next_coupon}")
    
    # Calculate accrued interest using day count
    days_accrued = day_count.dayCount(previous_coupon, settlement_date)
    days_in_period = day_count.dayCount(previous_coupon, next_coupon)
    year_fraction = day_count.yearFraction(previous_coupon, settlement_date)
    
    manual_accrued = (coupon_rate / 2) * (days_accrued / days_in_period) * face_value
    manual_accrued_alt = coupon_rate * year_fraction * face_value
    
    print(f"   Days Accrued: {days_accrued}")
    print(f"   Days in Period: {days_in_period}")
    print(f"   Year Fraction: {year_fraction:.6f}")
    print(f"   Manual Accrued (method 1): ${manual_accrued:.4f}")
    print(f"   Manual Accrued (method 2): ${manual_accrued_alt:.4f}")
    print()
    
    # Method 3: Create bond with proper issue date
    print("🔧 METHOD 3: Bond with Proper Issue Date")
    
    # Set issue date to previous coupon (Feb 15, 2025)
    issue_date = ql.Date(15, 2, 2025)
    
    schedule3 = ql.Schedule(
        issue_date, maturity_date, ql.Period(frequency),
        calendar, business_convention, business_convention,
        ql.DateGeneration.Backward, False
    )
    
    print(f"   Issue Date: {issue_date}")
    print(f"   First 3 payments: {schedule3[1]}, {schedule3[2]}, {schedule3[3]}")
    
    # Create bond with issue date
    bond3 = ql.FixedRateBond(0, face_value, schedule3, [coupon_rate], day_count)
    bond3.setPricingEngine(bond_engine)
    
    accrued3 = bond3.accruedAmount(settlement_date)
    yield3 = bond3.bondYield(price, day_count, ql.Compounded, frequency, settlement_date)
    duration3 = ql.BondFunctions.duration(
        bond3,
        ql.InterestRate(yield3, day_count, ql.Compounded, frequency),
        ql.Duration.Modified,
        settlement_date
    )
    
    print(f"   Accrued: ${accrued3:.4f} | Yield: {yield3*100:.5f}% | Duration: {duration3:.5f}")
    print()
    
    # Summary
    print("=" * 60)
    print("📊 SUMMARY OF ALL METHODS")
    print("=" * 60)
    print(f"Expected: Yield: 4.89916% | Duration: 16.35658 | Accrued: $1.08")
    print()
    print(f"Method 1: Yield: {yield1*100:.5f}% | Duration: {duration1:.5f} | Accrued: ${accrued1:.4f}")
    print(f"Method 2: Manual Accrued Calculation: ${manual_accrued:.4f}")
    print(f"Method 3: Yield: {yield3*100:.5f}% | Duration: {duration3:.5f} | Accrued: ${accrued3:.4f}")
    print()
    
    # Check which is closest to expected
    if abs(accrued3 - 1.08) < 0.01:
        print("🎯 Method 3 gives the correct accrued interest!")
    elif abs(manual_accrued - 1.08) < 0.01:
        print("🎯 Manual calculation gives the correct accrued interest!")
    else:
        print("❌ None of the methods give the expected accrued interest")

if __name__ == "__main__":
    test_proper_treasury_schedule()
