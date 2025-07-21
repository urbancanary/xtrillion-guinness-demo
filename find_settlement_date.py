#!/usr/bin/env python3
"""
Test Different Settlement Dates to Match Expected Accrued Interest
================================================================

Find the settlement date that gives us $1.08 accrued interest
"""

import sys
sys.path.append('.')
import QuantLib as ql

def find_correct_settlement_date():
    """Find settlement date that gives $1.08 accrued interest"""
    
    print("🔍 FINDING CORRECT SETTLEMENT DATE")
    print("=" * 50)
    
    # Bond parameters
    coupon_rate = 3.0 / 100.0
    price = 71.66
    face_value = 100.0
    target_accrued = 1.08
    
    # QuantLib setup
    maturity_date = ql.Date(15, 8, 2052)
    
    # US Treasury conventions
    day_count = ql.ActualActual(ql.ActualActual.Bond)
    business_convention = ql.Following
    frequency = ql.Semiannual
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    
    # Test different settlement dates in 2025
    test_dates = [
        ql.Date(30, 6, 2025),  # June 30 (current)
        ql.Date(15, 7, 2025),  # July 15
        ql.Date(30, 7, 2025),  # July 30
        ql.Date(14, 8, 2025),  # August 14 (day before coupon)
    ]
    
    for settlement_date in test_dates:
        print(f"\n📅 Testing Settlement Date: {settlement_date}")
        
        # Set evaluation date
        ql.Settings.instance().evaluationDate = settlement_date
        
        # Create schedule
        schedule = ql.Schedule(
            settlement_date, maturity_date, ql.Period(frequency),
            calendar, business_convention, business_convention,
            ql.DateGeneration.Backward, False
        )
        
        # Create bond
        coupons = [coupon_rate]
        bond = ql.FixedRateBond(0, face_value, schedule, coupons, day_count)
        
        # Set up pricing engine
        bond_engine = ql.DiscountingBondEngine(ql.YieldTermStructureHandle())
        bond.setPricingEngine(bond_engine)
        
        # Calculate accrued interest
        accrued = bond.accruedAmount(settlement_date)
        
        # Calculate yield and duration
        yield_rate = bond.bondYield(price, day_count, ql.Compounded, frequency, settlement_date)
        duration = ql.BondFunctions.duration(
            bond,
            ql.InterestRate(yield_rate, day_count, ql.Compounded, frequency),
            ql.Duration.Modified,
            settlement_date
        )
        
        # Show payment schedule info
        print(f"   First Payment: {schedule[1]}")
        print(f"   Accrued Interest: ${accrued:.4f}")
        print(f"   Yield: {yield_rate * 100:.5f}%")
        print(f"   Duration: {duration:.5f} years")
        
        # Check if this matches expected accrued
        accrued_diff = abs(accrued - target_accrued)
        if accrued_diff < 0.01:  # Within $0.01
            print(f"   🎯 MATCH! This settlement date gives target accrued interest")
            
            # Compare all results
            print(f"\n🏆 RESULTS WITH CORRECT SETTLEMENT DATE:")
            print(f"   Settlement: {settlement_date}")
            print(f"   Yield:      {yield_rate * 100:.5f}% (Expected: 4.89916%)")
            print(f"   Duration:   {duration:.5f} years (Expected: 16.35658)")
            print(f"   Accrued:    ${accrued:.4f} (Expected: $1.08)")
            
            yield_diff = (yield_rate * 100) - 4.89916
            duration_diff = duration - 16.35658
            accrued_diff = accrued - 1.08
            
            print(f"\n📊 DIFFERENCES FROM EXPECTED:")
            print(f"   Yield Diff:    {yield_diff:+.5f}%")
            print(f"   Duration Diff: {duration_diff:+.5f} years")
            print(f"   Accrued Diff:  ${accrued_diff:+.4f}")

if __name__ == "__main__":
    find_correct_settlement_date()
