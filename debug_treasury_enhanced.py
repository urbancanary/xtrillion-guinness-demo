#!/usr/bin/env python3
"""
Enhanced Treasury Bond Debug Test
=================================

Debug the duration and accrued interest calculation issues
"""

import sys
import os
sys.path.append('.')

import QuantLib as ql
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_treasury_detailed():
    """Debug Treasury bond with detailed analysis"""
    
    print("=" * 70)
    print("🔍 ENHANCED TREASURY BOND DEBUG")
    print("=" * 70)
    
    # Bond parameters
    coupon_rate = 3.0 / 100.0
    price = 71.66
    face_value = 100.0
    
    # QuantLib setup
    ql.Settings.instance().evaluationDate = ql.Date(30, 6, 2025)
    settlement_date = ql.Date(30, 6, 2025)
    maturity_date = ql.Date(15, 8, 2052)
    
    # US Treasury conventions
    day_count = ql.ActualActual(ql.ActualActual.Bond)
    business_convention = ql.Following
    frequency = ql.Semiannual
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    
    print(f"📅 Settlement Date: {settlement_date}")
    print(f"📅 Maturity Date: {maturity_date}")
    print()
    
    # Create schedule
    schedule = ql.Schedule(
        settlement_date, maturity_date, ql.Period(frequency),
        calendar, business_convention, business_convention,
        ql.DateGeneration.Backward, False
    )
    
    print("📅 PAYMENT SCHEDULE ANALYSIS:")
    print(f"   Total Payments: {len(schedule) - 1}")
    print(f"   First Payment: {schedule[1]}")
    print(f"   Second Payment: {schedule[2]}")
    print(f"   Last Payment: {schedule[-1]}")
    print()
    
    # Check for accrued interest period
    print("🧾 ACCRUED INTEREST ANALYSIS:")
    previous_coupon = None
    next_coupon = None
    
    for i, date in enumerate(schedule):
        if date <= settlement_date:
            previous_coupon = date
        elif date > settlement_date and next_coupon is None:
            next_coupon = date
            break
    
    print(f"   Previous Coupon: {previous_coupon}")
    print(f"   Settlement Date: {settlement_date}")
    print(f"   Next Coupon: {next_coupon}")
    
    if previous_coupon and next_coupon:
        days_since_coupon = settlement_date - previous_coupon
        days_in_period = next_coupon - previous_coupon
        accrued_fraction = float(days_since_coupon) / float(days_in_period)
        expected_accrued = (coupon_rate / 2) * accrued_fraction * face_value
        print(f"   Days Since Last Coupon: {days_since_coupon}")
        print(f"   Days in Coupon Period: {days_in_period}")
        print(f"   Accrued Fraction: {accrued_fraction:.6f}")
        print(f"   Expected Accrued: ${expected_accrued:.4f}")
    print()
    
    # Create bond
    coupons = [coupon_rate]
    bond = ql.FixedRateBond(0, face_value, schedule, coupons, day_count)
    
    # Set up pricing engine
    bond_engine = ql.DiscountingBondEngine(ql.YieldTermStructureHandle())
    bond.setPricingEngine(bond_engine)
    
    # Calculate yield
    yield_rate = bond.bondYield(price, day_count, ql.Compounded, frequency, settlement_date)
    print(f"💰 Yield: {yield_rate * 100:.5f}%")
    
    # Test different duration calculation methods
    print("\n⏱️  DURATION CALCULATION COMPARISON:")
    
    # Method 1: Using BondFunctions.duration (what we're currently using)
    duration_method1 = ql.BondFunctions.duration(
        bond,
        ql.InterestRate(yield_rate, day_count, ql.Compounded, frequency),
        ql.Duration.Modified,
        settlement_date
    )
    print(f"   Method 1 (BondFunctions): {duration_method1:.5f} years")
    
    # Method 2: Try with ActualActual(ISDA) for comparison
    day_count_isda = ql.ActualActual(ql.ActualActual.ISDA)
    duration_method2 = ql.BondFunctions.duration(
        bond,
        ql.InterestRate(yield_rate, day_count_isda, ql.Compounded, frequency),
        ql.Duration.Modified,
        settlement_date
    )
    print(f"   Method 2 (with ISDA):     {duration_method2:.5f} years")
    
    # Method 3: Manual calculation for verification
    # Get all cash flows
    cashflows = bond.cashflows()
    pv_total = 0.0
    duration_numerator = 0.0
    
    print(f"\n📊 CASH FLOW ANALYSIS:")
    print(f"   Total Cash Flows: {len(cashflows)}")
    
    for i, cf in enumerate(cashflows):
        if i >= 5:  # Show first 5 cash flows
            if i == 5:
                print("   ... (showing first 5 cash flows only)")
            break
            
        date = cf.date()
        amount = cf.amount()
        time_to_payment = day_count.yearFraction(settlement_date, date)
        discount_factor = (1 + yield_rate/2) ** (-2 * time_to_payment)
        pv = amount * discount_factor
        
        pv_total += pv
        duration_numerator += pv * time_to_payment
        
        print(f"   CF {i+1}: {date} | ${amount:.2f} | {time_to_payment:.4f}y | PV: ${pv:.4f}")
    
    # Calculate manual duration
    if pv_total > 0:
        manual_duration = duration_numerator / pv_total
        print(f"\n   Manual Duration Calculation: {manual_duration:.5f} years")
    
    # Test accrued interest calculation
    print(f"\n🧾 ACCRUED INTEREST DEBUG:")
    accrued = bond.accruedAmount(settlement_date)
    print(f"   Bond.accruedAmount(): ${accrued:.4f}")
    
    # Try alternative accrued calculation
    try:
        # Get the coupon from the bond directly
        for cf in bond.cashflows():
            if hasattr(cf, 'accrualPeriod'):
                # This is a coupon
                coupon_cf = ql.as_coupon(cf)
                if coupon_cf.accrualStartDate() <= settlement_date < coupon_cf.accrualEndDate():
                    accrued_alt = coupon_cf.accruedAmount(settlement_date)
                    print(f"   Alternative Calculation: ${accrued_alt:.4f}")
                    break
    except:
        print("   Alternative calculation failed")
    
    print("\n" + "=" * 70)
    print("📋 SUMMARY:")
    print("=" * 70)
    print(f"Yield:             {yield_rate * 100:.5f}% (Expected: 4.89916%)")
    print(f"Duration (Method1): {duration_method1:.5f} (Expected: 16.35658)")
    print(f"Duration (Method2): {duration_method2:.5f} (with ISDA day count)")
    print(f"Accrued Interest:  ${accrued:.4f} (Expected: $1.08)")
    print("=" * 70)

if __name__ == "__main__":
    debug_treasury_detailed()
