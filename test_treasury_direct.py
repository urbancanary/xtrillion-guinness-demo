#!/usr/bin/env python3
"""
Direct Treasury Bond Test - Bypass API
=========================================

Test the exact Treasury bond from your document directly:
- US TREASURY N/B, 3%, 15-Aug-2052
- Price: 71.66
- Settlement: 2025-06-30

Expected Results:
- Yield: 4.89916%
- Duration: 16.35658 years
- Accrued Interest: $1.08
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

def test_treasury_direct():
    """Test Treasury bond calculation with exact parameters from your document"""
    
    print("=" * 60)
    print("🏛️  DIRECT TREASURY BOND TEST")
    print("=" * 60)
    
    # Bond parameters from your document
    description = "US TREASURY N/B, 3%, 15-Aug-2052"
    price = 71.66
    settlement_date_str = "2025-06-30"
    
    print(f"📋 Bond: {description}")
    print(f"💰 Price: {price}")
    print(f"📅 Settlement: {settlement_date_str}")
    print()
    
    # Parse parameters
    coupon_rate = 3.0 / 100.0  # 3% as decimal
    maturity_date_str = "2052-08-15"
    face_value = 100.0
    
    # QuantLib setup
    ql.Settings.instance().evaluationDate = ql.Date(30, 6, 2025)
    
    # Create dates
    settlement_date = ql.Date(30, 6, 2025)
    maturity_date = ql.Date(15, 8, 2052)
    
    print("🔧 QuantLib Setup:")
    print(f"   Settlement Date: {settlement_date}")
    print(f"   Maturity Date: {maturity_date}")
    print(f"   Time to Maturity: {(maturity_date - settlement_date) / 365.25:.2f} years")
    print()
    
    # US Treasury conventions (FIXED)
    day_count = ql.ActualActual(ql.ActualActual.Bond)  # ✅ Bond not ISDA
    business_convention = ql.Following
    frequency = ql.Semiannual
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    
    print("📐 US Treasury Conventions:")
    print(f"   Day Count: ActualActual(Bond)")
    print(f"   Frequency: Semiannual")
    print(f"   Business Convention: Following")
    print(f"   Calendar: US Government Bond")
    print()
    
    # Create payment schedule
    schedule = ql.Schedule(
        settlement_date, maturity_date, ql.Period(frequency),
        calendar, business_convention, business_convention,
        ql.DateGeneration.Backward, False
    )
    
    print(f"📅 Payment Schedule: {len(schedule) - 1} payments")
    print(f"   First Payment: {schedule[1]}")
    print(f"   Last Payment: {schedule[-1]}")
    print()
    
    # Create the Treasury bond
    coupons = [coupon_rate]
    bond = ql.FixedRateBond(
        0,  # settlement days
        face_value,
        schedule,
        coupons,
        day_count
    )
    
    print("✅ Treasury Bond Created")
    
    # Set up yield calculation engine
    bond_engine = ql.DiscountingBondEngine(ql.YieldTermStructureHandle())
    bond.setPricingEngine(bond_engine)
    
    # Calculate yield (CRITICAL: Use same conventions)
    yield_rate = bond.bondYield(
        price,                    # Clean price
        day_count,               # Same day count as bond
        ql.Compounded,           # Compounding type
        frequency,               # Same frequency as bond
        settlement_date          # Settlement date
    )
    
    print("💰 YIELD CALCULATION:")
    print(f"   Yield to Maturity: {yield_rate * 100:.5f}%")
    print()
    
    # Calculate duration (CRITICAL: Use same conventions)
    duration = ql.BondFunctions.duration(
        bond,
        ql.InterestRate(yield_rate, day_count, ql.Compounded, frequency),
        ql.Duration.Modified,
        settlement_date
    )
    
    print("⏱️  DURATION CALCULATION:")
    print(f"   Modified Duration: {duration:.5f} years")
    print()
    
    # Calculate accrued interest
    accrued = bond.accruedAmount(settlement_date)
    
    print("🧾 ACCRUED INTEREST:")
    print(f"   Accrued Interest: ${accrued:.2f}")
    print()
    
    # Summary
    print("=" * 60)
    print("📊 FINAL RESULTS vs EXPECTED")
    print("=" * 60)
    
    expected_yield = 4.89916
    expected_duration = 16.35658
    expected_accrued = 1.08
    
    yield_pct = yield_rate * 100
    yield_diff = yield_pct - expected_yield
    duration_diff = duration - expected_duration
    accrued_diff = accrued - expected_accrued
    
    print(f"✅ Yield:     {yield_pct:.5f}% | Expected: {expected_yield:.5f}% | Diff: {yield_diff:+.5f}%")
    print(f"✅ Duration:  {duration:.5f}   | Expected: {expected_duration:.5f}   | Diff: {duration_diff:+.5f}")
    print(f"✅ Accrued:   ${accrued:.2f}      | Expected: ${expected_accrued:.2f}      | Diff: ${accrued_diff:+.2f}")
    print()
    
    # Check if results match
    yield_match = abs(yield_diff) < 0.001  # Within 0.001%
    duration_match = abs(duration_diff) < 0.001  # Within 0.001 years
    accrued_match = abs(accrued_diff) < 0.01  # Within $0.01
    
    if yield_match and duration_match and accrued_match:
        print("🎯 SUCCESS: All results match expected values!")
    else:
        print("❌ MISMATCH: Results don't match expected values")
        if not yield_match:
            print(f"   ❌ Yield mismatch: {yield_diff:+.5f}%")
        if not duration_match:
            print(f"   ❌ Duration mismatch: {duration_diff:+.5f} years")
        if not accrued_match:
            print(f"   ❌ Accrued mismatch: ${accrued_diff:+.2f}")
    
    print("=" * 60)
    
    return {
        'yield': yield_pct,
        'duration': duration,
        'accrued': accrued,
        'yield_match': yield_match,
        'duration_match': duration_match,
        'accrued_match': accrued_match
    }

if __name__ == "__main__":
    results = test_treasury_direct()
