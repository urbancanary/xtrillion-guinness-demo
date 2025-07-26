#!/usr/bin/env python3
"""
🔍 QuantLib Duration Debug - API Matching Test
==============================================
Test with EXACT same setup as the API: T+1 settlement evaluation date
"""

import QuantLib as ql
from datetime import datetime

def test_api_matching_setup():
    print("🔍 API-Matching QuantLib Treasury Bond Setup")
    print("=" * 60)
    
    # Bond details from API test
    coupon = 3.0
    price = 71.66
    
    # STEP 1: Set up dates exactly like the API
    trade_date = ql.Date(30, 6, 2025)  # Settlement input date
    settlement_days = 1  # T+1 settlement
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    
    # Calculate settlement date using calendar advance (like API)
    settlement_date = calendar.advance(trade_date, ql.Period(settlement_days, ql.Days))
    
    # Set evaluation date to settlement date (like API)
    ql.Settings.instance().evaluationDate = settlement_date
    
    print(f"Trade Date: {trade_date}")
    print(f"Settlement Days: {settlement_days}")
    print(f"Calculated Settlement Date: {settlement_date}")
    print(f"Evaluation Date Set To: {ql.Settings.instance().evaluationDate}")
    
    # STEP 2: Create bond exactly like API
    maturity_date = ql.Date(15, 8, 2052)
    issue_date = ql.Date(15, 8, 2022)  # Reasonable issue date
    face_amount = 100.0
    
    # API uses Unadjusted business convention for Treasuries (after our fix)
    business_convention = ql.Unadjusted
    
    # Create schedule
    schedule = ql.Schedule(
        issue_date,
        maturity_date,
        ql.Period(ql.Semiannual),
        calendar,
        business_convention,
        business_convention,
        ql.DateGeneration.Backward,
        False
    )
    
    # Create the bond
    fixed_rate_bond = ql.FixedRateBond(
        settlement_days,
        face_amount,
        schedule,
        [coupon / 100],
        ql.ActualActual(ql.ActualActual.Bond),
        business_convention,
        100.0
    )
    
    print(f"\n🏛️ BOND DETAILS:")
    print(f"Bond Settlement Date: {fixed_rate_bond.settlementDate()}")
    print(f"Bond Maturity: {fixed_rate_bond.maturityDate()}")
    print(f"Evaluation Date: {ql.Settings.instance().evaluationDate}")
    
    # STEP 3: Calculate yield and duration exactly like API
    day_count = ql.ActualActual(ql.ActualActual.Bond)
    compounding_freq = ql.Semiannual
    
    # Calculate yield
    bond_yield = fixed_rate_bond.bondYield(
        price,
        day_count,
        ql.Compounded,
        compounding_freq,
        settlement_date
    )
    
    print(f"\n📊 CALCULATIONS:")
    print(f"Yield: {bond_yield * 100:.6f}%")
    
    # Calculate duration (Treasury-specific logic from API)
    treasury_day_count = ql.ActualActual(ql.ActualActual.Bond)
    duration_rate = ql.InterestRate(bond_yield, treasury_day_count, ql.Compounded, ql.Semiannual)
    bond_duration = ql.BondFunctions.duration(fixed_rate_bond, duration_rate, ql.Duration.Modified)
    
    print(f"Duration: {bond_duration:.6f} years")
    print(f"\n🎯 COMPARISON:")
    print(f"API Result: 16.598212 years")
    print(f"This Test: {bond_duration:.6f} years")
    print(f"Expected: 16.35 years")
    print(f"Difference from API: {abs(bond_duration - 16.598212):.6f} years")
    print(f"Difference from Expected: {abs(bond_duration - 16.35):.6f} years")

if __name__ == "__main__":
    test_api_matching_setup()
