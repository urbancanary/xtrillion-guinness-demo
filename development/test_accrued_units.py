#!/usr/bin/env python3
"""
Test accrued interest calculation to verify units
"""

import sys
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis9')

import QuantLib as ql
from datetime import datetime, timedelta

def test_accrued_interest_units():
    """Test what units QuantLib accruedAmount() returns"""
    
    print("🧪 Testing QuantLib accruedAmount() units")
    print("=" * 50)
    
    # Create a simple 3% semiannual bond
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    settlement_date = ql.Date(15, 7, 2025)  # July 15, 2025
    issue_date = ql.Date(15, 8, 2024)       # August 15, 2024 (last coupon)
    maturity_date = ql.Date(15, 8, 2052)    # August 15, 2052
    
    # Set evaluation date
    ql.Settings.instance().evaluationDate = settlement_date
    
    # Create schedule for semiannual payments
    schedule = ql.Schedule(
        issue_date, maturity_date, 
        ql.Period(ql.Semiannual),  # Every 6 months
        calendar, 
        ql.Unadjusted, ql.Unadjusted,
        ql.DateGeneration.Forward, False
    )
    
    # 3% annual coupon = 1.5% semiannual
    coupon_rate = 0.03  # 3% annual
    face_value = 100.0
    day_count = ql.Thirty360(ql.Thirty360.ISMA)
    
    # Create the bond
    bond = ql.FixedRateBond(
        1,              # settlement days
        face_value,     # face value 
        schedule,       # payment schedule
        [coupon_rate],  # coupon rates
        day_count       # day count convention
    )
    
    # Calculate accrued interest
    accrued = bond.accruedAmount(settlement_date)
    
    print(f"📊 Bond Details:")
    print(f"   Face Value: {face_value}")
    print(f"   Annual Coupon: {coupon_rate*100:.1f}%")
    print(f"   Semiannual Coupon: {coupon_rate*face_value/2:.2f} (per 100 face value)")
    print(f"   Settlement Date: {settlement_date}")
    print(f"   Last Coupon Date: ~{issue_date} (Aug 15)")
    print(f"   Next Coupon Date: ~Feb 15, 2025")
    
    print(f"\n📊 Accrued Interest Calculation:")
    print(f"   Raw accruedAmount(): {accrued:.6f}")
    
    # Manual calculation for verification
    # Days from Aug 15 to July 15 = about 11 months = ~334 days
    # Semiannual period = ~182 days  
    # But we need to be more precise...
    
    # Get the actual coupon dates from the schedule
    coupon_dates = []
    for i in range(len(schedule)):
        coupon_dates.append(schedule[i])
    
    print(f"   Schedule dates: {[str(d) for d in coupon_dates[:5]]}...")
    
    # Find the last coupon before settlement
    last_coupon = None
    next_coupon = None
    for i in range(len(coupon_dates)-1):
        if coupon_dates[i] <= settlement_date < coupon_dates[i+1]:
            last_coupon = coupon_dates[i]
            next_coupon = coupon_dates[i+1]
            break
    
    if last_coupon and next_coupon:
        print(f"   Last Coupon: {last_coupon}")
        print(f"   Next Coupon: {next_coupon}")
        
        # Calculate days
        days_since_coupon = settlement_date - last_coupon
        days_in_period = next_coupon - last_coupon
        
        print(f"   Days since last coupon: {days_since_coupon}")
        print(f"   Days in coupon period: {days_in_period}")
        
        # Manual accrued calculation
        accrued_fraction = float(days_since_coupon) / float(days_in_period)
        semiannual_coupon = coupon_rate * face_value / 2  # 1.5 for 3% bond
        manual_accrued = accrued_fraction * semiannual_coupon
        
        print(f"   Accrued fraction: {accrued_fraction:.4f}")
        print(f"   Semiannual coupon amount: {semiannual_coupon:.3f}")
        print(f"   Manual calculation: {manual_accrued:.6f}")
        print(f"   Manual as %: {manual_accrued:.6f}%")
        
    print(f"\n🔍 Units Analysis:")
    print(f"   QuantLib accrued: {accrued:.6f}")
    
    if accrued > 2.0:
        print(f"   ❌ This looks like it's already multiplied by 100 (percentage)")
        print(f"   ✅ Correct value would be: {accrued/100:.6f}%")
        units = "percentage"
        correct_value = accrued / 100
    elif 0.01 <= accrued <= 2.0:
        print(f"   ✅ This looks like it's in percentage units (0.X%)")
        print(f"   ❌ DON'T multiply by 100")
        units = "percentage"
        correct_value = accrued
    else:
        print(f"   ❓ Unclear units - value seems too small")
        units = "unclear"
        correct_value = accrued
    
    print(f"\n🎯 CONCLUSION:")
    print(f"   QuantLib accruedAmount() returns: {units}")
    if units == "percentage":
        print(f"   For display: {correct_value:.3f}%")
        print(f"   BUG: Current code multiplies by 100 → {accrued*100:.1f}% (WRONG!)")
        print(f"   FIX: Use value directly → {correct_value:.3f}% (CORRECT!)")
    
    return accrued, correct_value

if __name__ == "__main__":
    test_accrued_interest_units()
