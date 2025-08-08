#!/usr/bin/env python3
"""
Deep Duration Investigation
============================
Test different settlement dates and configurations
"""

import QuantLib as ql
from datetime import datetime, date

def test_with_different_settings():
    """Test with various settings to find the issue"""
    
    print("🔍 DEEP DURATION INVESTIGATION FOR T 3 15/08/52")
    print("=" * 60)
    
    # Bond parameters
    maturity_date = ql.Date(15, 8, 2052)
    coupon_rate = 0.03  # 3%
    price = 71.66
    
    # Test different evaluation dates
    test_dates = [
        (ql.Date(30, 6, 2025), "June 30, 2025"),
        (ql.Date(27, 6, 2025), "June 27, 2025"),  # Friday
        (ql.Date(2, 7, 2025), "July 2, 2025"),   # T+2 from June 30
        (ql.Date(17, 4, 2025), "April 17, 2025"),  # Date from working calculator
    ]
    
    # Test different day count conventions
    conventions = [
        ("ActualActual.Bond", ql.ActualActual(ql.ActualActual.Bond)),
        ("ActualActual.ISMA", ql.ActualActual(ql.ActualActual.ISMA)),
        ("ActualActual.ISDA", ql.ActualActual(ql.ActualActual.ISDA)),
    ]
    
    print(f"Bond: T 3 15/08/52")
    print(f"Price: {price}")
    print(f"Expected Duration: 16.351196 years")
    print()
    
    for eval_date, date_name in test_dates:
        print(f"\n📅 Testing with Evaluation Date: {date_name}")
        print("-" * 50)
        
        ql.Settings.instance().evaluationDate = eval_date
        
        for conv_name, day_counter in conventions:
            try:
                # Create schedule with backward generation (US Treasury standard)
                schedule = ql.Schedule(
                    eval_date,
                    maturity_date,
                    ql.Period(ql.Semiannual),
                    ql.UnitedStates(ql.UnitedStates.GovernmentBond),
                    ql.Following,
                    ql.Following,
                    ql.DateGeneration.Backward,
                    True  # end of month
                )
                
                # Create bond with 2 settlement days
                bond = ql.FixedRateBond(
                    2,  # settlement days
                    100.0,  # face value
                    schedule,
                    [coupon_rate],
                    day_counter
                )
                
                # Calculate yield and duration
                bond_yield = bond.bondYield(price, day_counter, ql.Compounded, ql.Semiannual)
                duration = ql.BondFunctions.duration(
                    bond, bond_yield, day_counter, ql.Compounded, 
                    ql.Semiannual, ql.Duration.Modified
                )
                
                # Check if this matches expected
                is_correct = abs(duration - 16.351196) < 0.001
                status = "✅" if is_correct else "❌"
                
                print(f"   {conv_name:<20} Duration: {duration:.6f} {status}")
                
            except Exception as e:
                print(f"   {conv_name:<20} ERROR: {str(e)}")

def test_different_schedule_generation():
    """Test with different schedule generation methods"""
    print("\n\n🔧 Testing Different Schedule Generation Methods")
    print("=" * 60)
    
    # Setup
    eval_date = ql.Date(30, 6, 2025)
    ql.Settings.instance().evaluationDate = eval_date
    
    maturity_date = ql.Date(15, 8, 2052)
    issue_date = ql.Date(15, 8, 2022)  # Approximate issue date
    coupon_rate = 0.03
    price = 71.66
    
    # Use ActualActual.Bond (should be correct)
    day_counter = ql.ActualActual(ql.ActualActual.Bond)
    
    print("Testing schedule generation methods:")
    
    # Method 1: From evaluation date
    print("\n1. From Evaluation Date (current method):")
    schedule1 = ql.Schedule(
        eval_date,
        maturity_date,
        ql.Period(ql.Semiannual),
        ql.UnitedStates(ql.UnitedStates.GovernmentBond),
        ql.Following,
        ql.Following,
        ql.DateGeneration.Backward,
        True
    )
    
    bond1 = ql.FixedRateBond(2, 100.0, schedule1, [coupon_rate], day_counter)
    yield1 = bond1.bondYield(price, day_counter, ql.Compounded, ql.Semiannual)
    duration1 = ql.BondFunctions.duration(
        bond1, yield1, day_counter, ql.Compounded, 
        ql.Semiannual, ql.Duration.Modified
    )
    print(f"   Duration: {duration1:.6f}")
    
    # Method 2: From issue date
    print("\n2. From Issue Date (proper full schedule):")
    schedule2 = ql.Schedule(
        issue_date,
        maturity_date,
        ql.Period(ql.Semiannual),
        ql.UnitedStates(ql.UnitedStates.GovernmentBond),
        ql.Following,
        ql.Following,
        ql.DateGeneration.Backward,
        True
    )
    
    bond2 = ql.FixedRateBond(2, 100.0, schedule2, [coupon_rate], day_counter)
    yield2 = bond2.bondYield(price, day_counter, ql.Compounded, ql.Semiannual)
    duration2 = ql.BondFunctions.duration(
        bond2, yield2, day_counter, ql.Compounded, 
        ql.Semiannual, ql.Duration.Modified
    )
    print(f"   Duration: {duration2:.6f}")
    
    # Method 3: Using MakeFixedBond (QuantLib's preferred method)
    print("\n3. Using specific coupon dates:")
    # For T 3 15/08/52, coupons are on Feb 15 and Aug 15
    first_coupon = ql.Date(15, 2, 2025)
    schedule3 = ql.Schedule(
        first_coupon,
        maturity_date,
        ql.Period(ql.Semiannual),
        ql.UnitedStates(ql.UnitedStates.GovernmentBond),
        ql.Following,
        ql.Following,
        ql.DateGeneration.Forward,
        False
    )
    
    bond3 = ql.FixedRateBond(2, 100.0, schedule3, [coupon_rate], day_counter)
    yield3 = bond3.bondYield(price, day_counter, ql.Compounded, ql.Semiannual)
    duration3 = ql.BondFunctions.duration(
        bond3, yield3, day_counter, ql.Compounded, 
        ql.Semiannual, ql.Duration.Modified
    )
    print(f"   Duration: {duration3:.6f}")
    
    print("\n📊 COMPARISON:")
    print(f"   Method 1 (from eval date):  {duration1:.6f}")
    print(f"   Method 2 (from issue date): {duration2:.6f}")
    print(f"   Method 3 (specific dates):  {duration3:.6f}")
    print(f"   Expected (Bloomberg):       16.351196")

if __name__ == "__main__":
    test_with_different_settings()
    test_different_schedule_generation()
