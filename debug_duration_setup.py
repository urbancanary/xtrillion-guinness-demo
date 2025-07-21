#!/usr/bin/env python3
"""
🔍 QuantLib Duration Debug Script
================================
Debug the Treasury bond duration calculation to find the setup discrepancy
Expected: 16.35 years, Getting: 16.60 years (0.25 year difference = ~3 months)
"""

import QuantLib as ql
from datetime import datetime

def debug_treasury_bond():
    print("🔍 QuantLib Treasury Bond Duration Debug")
    print("=" * 60)
    
    # Bond details from API test
    coupon = 3.0
    maturity = "2052-08-15"
    price = 71.66
    settlement_date_str = "2025-06-30"
    
    print(f"Bond: T 3% 15/08/52")
    print(f"Price: {price}")
    print(f"Settlement: {settlement_date_str}")
    print("-" * 60)
    
    # CRITICAL: Check what evaluation date is being used
    current_eval_date = ql.Settings.instance().evaluationDate
    print(f"❓ Current QuantLib Evaluation Date: {current_eval_date}")
    
    # Set explicit evaluation date to match expected calculation
    # Try the settlement date first
    eval_date = ql.Date(30, 6, 2025)
    ql.Settings.instance().evaluationDate = eval_date
    print(f"✅ Set Evaluation Date to: {eval_date}")
    
    # Create settlement date
    settlement_date = ql.Date(30, 6, 2025)
    print(f"✅ Settlement Date: {settlement_date}")
    
    # Create maturity date
    maturity_date = ql.Date(15, 8, 2052)
    print(f"✅ Maturity Date: {maturity_date}")
    
    # Calculate time to maturity in years
    time_to_maturity = (maturity_date - settlement_date) / 365.25
    print(f"📊 Time to Maturity: {time_to_maturity:.4f} years")
    
    print("\n" + "=" * 60)
    print("🏗️ BOND CONSTRUCTION DEBUG")
    print("=" * 60)
    
    # US Treasury bond setup
    face_amount = 100.0
    issue_date = ql.Date(15, 8, 2022)  # Reasonable issue date
    
    # Treasury conventions
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    business_convention = ql.Unadjusted  # Critical for Treasuries
    settlement_days = 1  # T+1 for Treasuries
    
    print(f"Calendar: US Government Bond")
    print(f"Business Convention: {business_convention}")
    print(f"Settlement Days: {settlement_days}")
    
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
    
    print(f"Schedule Type: Semiannual, Backward generation")
    print(f"Total Coupon Periods: {len(schedule) - 1}")
    
    # Print first few and last few coupon dates
    print(f"\n📅 CASH FLOW SCHEDULE:")
    for i, date in enumerate(schedule):
        if i < 3 or i >= len(schedule) - 3:
            print(f"  {i+1:2d}: {date}")
        elif i == 3:
            print(f"   ... ({len(schedule) - 6} more dates)")
    
    # Create the bond
    fixed_rate_bond = ql.FixedRateBond(
        settlement_days,
        face_amount,
        schedule,
        [coupon / 100],  # Convert to decimal
        ql.ActualActual(ql.ActualActual.Bond),  # Treasury day count
        business_convention,
        100.0  # Redemption
    )
    
    print(f"\n🏛️ BOND OBJECT CREATED")
    print(f"Settlement Date from Bond: {fixed_rate_bond.settlementDate()}")
    print(f"Maturity Date from Bond: {fixed_rate_bond.maturityDate()}")
    
    # Check the settlement date discrepancy
    actual_settlement = fixed_rate_bond.settlementDate()
    if actual_settlement != settlement_date:
        print(f"⚠️  SETTLEMENT DATE MISMATCH!")
        print(f"   Expected: {settlement_date}")
        print(f"   Actual:   {actual_settlement}")
        print(f"   Difference: {actual_settlement - settlement_date} days")
    
    print("\n" + "=" * 60)
    print("💰 CASH FLOW ANALYSIS")
    print("=" * 60)
    
    # Inspect all cash flows
    cashflows = fixed_rate_bond.cashflows()
    print(f"Total Cash Flows: {len(cashflows)}")
    
    print(f"\nFirst 5 Cash Flows:")
    for i, cf in enumerate(cashflows[:5]):
        print(f"  {i+1:2d}: {cf.date()} - Amount: {cf.amount():.6f}")
    
    print(f"\nLast 5 Cash Flows:")
    for i, cf in enumerate(cashflows[-5:], len(cashflows)-4):
        print(f"  {i:2d}: {cf.date()} - Amount: {cf.amount():.6f}")
    
    print("\n" + "=" * 60)
    print("📊 DURATION CALCULATIONS")
    print("=" * 60)
    
    # Calculate yield from price
    day_count = ql.ActualActual(ql.ActualActual.Bond)
    compounding_freq = ql.Semiannual
    
    bond_yield = fixed_rate_bond.bondYield(
        price,
        day_count,
        ql.Compounded,
        compounding_freq,
        settlement_date
    )
    
    print(f"✅ Calculated Yield: {bond_yield * 100:.6f}%")
    
    # Duration calculation with detailed setup
    duration_rate = ql.InterestRate(
        bond_yield, 
        day_count, 
        ql.Compounded, 
        compounding_freq
    )
    
    print(f"Interest Rate Object:")
    print(f"  Rate: {bond_yield * 100:.6f}%")
    print(f"  Day Count: {day_count}")
    print(f"  Compounding: Compounded")
    print(f"  Frequency: {compounding_freq}")
    
    # Calculate modified duration
    bond_duration = ql.BondFunctions.duration(
        fixed_rate_bond, 
        duration_rate, 
        ql.Duration.Modified
    )
    
    print(f"\n🎯 FINAL RESULTS:")
    print(f"Modified Duration: {bond_duration:.6f} years")
    print(f"Expected Duration: 16.35 years")
    print(f"Difference: {bond_duration - 16.35:.6f} years ({(bond_duration - 16.35) * 12:.2f} months)")
    
    # Test with different evaluation dates
    print("\n" + "=" * 60)
    print("🧪 EVALUATION DATE SENSITIVITY TEST")
    print("=" * 60)
    
    test_dates = [
        (ql.Date(30, 6, 2025), "2025-06-30 (Current)"),
        (ql.Date(31, 5, 2025), "2025-05-31 (Prior Month End)"),
        (ql.Date(15, 6, 2025), "2025-06-15 (Mid-Month)"),
        (ql.Date(21, 7, 2025), "2025-07-21 (Today)")
    ]
    
    for test_date, description in test_dates:
        ql.Settings.instance().evaluationDate = test_date
        
        # Recalculate with new evaluation date
        test_yield = fixed_rate_bond.bondYield(
            price, day_count, ql.Compounded, compounding_freq, settlement_date
        )
        test_duration_rate = ql.InterestRate(test_yield, day_count, ql.Compounded, compounding_freq)
        test_duration = ql.BondFunctions.duration(fixed_rate_bond, test_duration_rate, ql.Duration.Modified)
        
        print(f"{description}: Duration = {test_duration:.6f} years")

if __name__ == "__main__":
    debug_treasury_bond()
