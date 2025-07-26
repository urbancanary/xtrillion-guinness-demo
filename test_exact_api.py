#!/usr/bin/env python3
"""
🔍 EXACT API QuantLib Setup Test
===============================
Replicate the EXACT QuantLib setup used by the API
"""

import QuantLib as ql

def test_exact_api_setup():
    print("🔍 EXACT API QuantLib Setup Test")
    print("=" * 60)
    
    # STEP 1: Exact API date setup
    trade_date = ql.Date(30, 6, 2025)
    settlement_days = 1
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    settlement_date = calendar.advance(trade_date, ql.Period(settlement_days, ql.Days))
    ql.Settings.instance().evaluationDate = settlement_date
    
    print(f"Settlement Date: {settlement_date}")
    print(f"Evaluation Date: {ql.Settings.instance().evaluationDate}")
    
    # STEP 2: Exact API bond construction
    coupon = 3.0 / 100  # API uses decimal
    price = 71.66
    maturity_date = ql.Date(15, 8, 2052)
    issue_date = ql.Date(15, 8, 2022)
    
    # Day count from API logic
    day_count = ql.ActualActual(ql.ActualActual.Bond)
    business_conv = ql.Unadjusted  # From our fix
    
    # Create schedule (API style)
    schedule = ql.Schedule(
        issue_date,
        maturity_date,
        ql.Period(ql.Semiannual),
        calendar,
        business_conv,
        business_conv,
        ql.DateGeneration.Backward,
        False
    )
    
    # EXACT API FixedRateBond construction (simplified constructor)
    coupon_list = [coupon]
    fixed_rate_bond = ql.FixedRateBond(settlement_days, 100.0, schedule, coupon_list, day_count)
    
    # API uses DiscountingBondEngine with treasury yield curve
    # Create flat yield curve for pricing engine
    flat_curve = ql.FlatForward(settlement_date, 0.04, day_count)  # Approximate rate
    treasury_handle = ql.YieldTermStructureHandle(flat_curve)
    bond_engine = ql.DiscountingBondEngine(treasury_handle)
    fixed_rate_bond.setPricingEngine(bond_engine)
    
    print(f"\n🏛️ BOND SETUP (API Style):")
    print(f"Bond Settlement Date: {fixed_rate_bond.settlementDate()}")
    print(f"Constructor: Simplified (5 params)")
    print(f"Pricing Engine: DiscountingBondEngine")
    
    # STEP 3: Calculate yield (API style)
    clean_price = float(price) / 1
    compounding_freq = ql.Semiannual
    
    bond_yield = fixed_rate_bond.bondYield(
        clean_price,
        day_count,
        ql.Compounded,
        compounding_freq,
        settlement_date
    )
    
    print(f"\n📊 YIELD CALCULATION:")
    print(f"Clean Price: {clean_price}")
    print(f"Calculated Yield: {bond_yield * 100:.6f}%")
    
    # STEP 4: Duration calculation (Treasury logic from API)
    if True:  # Treasury bond logic
        treasury_day_count = ql.ActualActual(ql.ActualActual.Bond)
        duration_rate = ql.InterestRate(bond_yield, treasury_day_count, ql.Compounded, ql.Semiannual)
        bond_duration = ql.BondFunctions.duration(fixed_rate_bond, duration_rate, ql.Duration.Modified)
    
    print(f"\n🎯 DURATION CALCULATION:")
    print(f"Treasury Day Count: {treasury_day_count}")
    print(f"Duration Rate: {bond_yield * 100:.6f}% Semiannual")
    print(f"Calculated Duration: {bond_duration:.6f} years")
    
    print(f"\n📊 FINAL COMPARISON:")
    print(f"API Result:    16.598212 years")
    print(f"This Test:     {bond_duration:.6f} years")
    print(f"Expected:      16.35 years")
    print(f"Difference from API: {abs(bond_duration - 16.598212):.6f} years")
    print(f"Match API? {'✅ YES' if abs(bond_duration - 16.598212) < 0.001 else '❌ NO'}")

if __name__ == "__main__":
    test_exact_api_setup()
