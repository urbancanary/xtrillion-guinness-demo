#!/usr/bin/env python3
"""
Test Current Duration Calculation
==================================
Tests what duration we're ACTUALLY getting with the current code
"""

import sys
import os
sys.path.insert(0, '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

import QuantLib as ql
from datetime import datetime, date

def test_current_actual_code():
    """Test with the ACTUAL current code logic"""
    print("🔍 Testing with CURRENT CODE (ISMA for ActualActual_Bond):")
    print("=" * 60)
    
    # Setup dates exactly as in google_analysis10.py
    calculation_date = ql.Date(30, 6, 2025)  # June 30, 2025
    ql.Settings.instance().evaluationDate = calculation_date
    
    # Bond parameters for T 3 15/08/52
    maturity_date = ql.Date(15, 8, 2052)
    coupon_rate = 0.03  # 3%
    price = 71.66
    
    # Create schedule (semiannual for US Treasury)
    schedule = ql.Schedule(
        calculation_date,
        maturity_date,
        ql.Period(ql.Semiannual),
        ql.UnitedStates(ql.UnitedStates.GovernmentBond),
        ql.Following,
        ql.Following,
        ql.DateGeneration.Backward,
        True
    )
    
    # THIS IS WHAT'S IN THE CURRENT CODE (line 458-459)
    day_count_str = 'ActualActual_Bond'  # This is what Treasury bonds use
    if day_count_str == 'ActualActual_Bond':
        day_counter = ql.ActualActual(ql.ActualActual.ISMA)  # ← CURRENT CODE
    
    # Create bond
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
    
    print(f"📊 CURRENT RESULTS (using ISMA):")
    print(f"   Yield:     {bond_yield * 100:.6f}%")
    print(f"   Duration:  {duration:.6f} years")
    print()
    
    return bond_yield * 100, duration

def test_fixed_code():
    """Test with the FIXED code (using Bond convention)"""
    print("✅ Testing with FIXED CODE (Bond for ActualActual_Bond):")
    print("=" * 60)
    
    # Setup dates
    calculation_date = ql.Date(30, 6, 2025)
    ql.Settings.instance().evaluationDate = calculation_date
    
    # Bond parameters for T 3 15/08/52
    maturity_date = ql.Date(15, 8, 2052)
    coupon_rate = 0.03  # 3%
    price = 71.66
    
    # Create schedule
    schedule = ql.Schedule(
        calculation_date,
        maturity_date,
        ql.Period(ql.Semiannual),
        ql.UnitedStates(ql.UnitedStates.GovernmentBond),
        ql.Following,
        ql.Following,
        ql.DateGeneration.Backward,
        True
    )
    
    # THIS IS THE FIX
    day_count_str = 'ActualActual_Bond'
    if day_count_str == 'ActualActual_Bond':
        day_counter = ql.ActualActual(ql.ActualActual.Bond)  # ← THE FIX
    
    # Create bond
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
    
    print(f"📊 FIXED RESULTS (using Bond):")
    print(f"   Yield:     {bond_yield * 100:.6f}%")
    print(f"   Duration:  {duration:.6f} years")
    print()
    
    return bond_yield * 100, duration

def main():
    print("🎯 ACTUAL Duration Test for T 3 15/08/52")
    print("=" * 60)
    print("Bond: US Treasury 3% Aug 15, 2052")
    print("Price: 71.66")
    print("Settlement: June 30, 2025")
    print()
    
    # Test current code
    current_yield, current_duration = test_current_actual_code()
    
    # Test fixed code
    fixed_yield, fixed_duration = test_fixed_code()
    
    # Bloomberg expected values
    expected_yield = 4.899064
    expected_duration = 16.351196
    
    print("📊 COMPARISON SUMMARY:")
    print("=" * 60)
    print(f"{'Metric':<20} {'Current (ISMA)':<20} {'Fixed (Bond)':<20} {'Bloomberg Expected':<20}")
    print("-" * 80)
    print(f"{'Yield (%):':<20} {current_yield:<20.6f} {fixed_yield:<20.6f} {expected_yield:<20.6f}")
    print(f"{'Duration (years):':<20} {current_duration:<20.6f} {fixed_duration:<20.6f} {expected_duration:<20.6f}")
    print()
    
    # Calculate differences
    current_diff = abs(current_duration - expected_duration)
    fixed_diff = abs(fixed_duration - expected_duration)
    
    print("📈 ACCURACY CHECK:")
    print(f"   Current code error: {current_diff:.6f} years {'❌ WRONG!' if current_diff > 0.001 else '✅'}")
    print(f"   Fixed code error:   {fixed_diff:.6f} years {'✅ CORRECT!' if fixed_diff < 0.001 else '❌'}")
    print()
    
    if current_diff > 0.001:
        print("⚠️  CONFIRMED: Current code has a duration regression!")
        print(f"   The duration is off by {current_diff:.6f} years")
        print(f"   This is caused by using ISMA instead of Bond convention")
    
    if fixed_diff < 0.001:
        print("✅ CONFIRMED: The fix will restore correct duration!")
        print(f"   Changing ISMA to Bond will fix the issue")

if __name__ == "__main__":
    main()
