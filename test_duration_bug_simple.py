#!/usr/bin/env python3
"""
Direct Test of Duration Bug in google_analysis10.py
====================================================
Tests the actual calculation engine to demonstrate the duration bug.
"""

import sys
import os
import QuantLib as ql
from datetime import datetime, date

# Add project to path
sys.path.insert(0, '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

def test_simple_quantlib_duration():
    """Test QuantLib directly to show the bug"""
    
    print("🎯 Direct QuantLib Test - Showing ISMA vs Bond Convention")
    print("=" * 60)
    
    # Setup
    calculation_date = ql.Date(30, 6, 2025)
    ql.Settings.instance().evaluationDate = calculation_date
    
    # Bond parameters for T 3 15/08/52
    maturity_date = ql.Date(15, 8, 2052)
    issue_date = ql.Date(15, 8, 2022)  # Approximate issue
    coupon_rate = 0.03  # 3%
    price = 71.66
    
    # Create schedule
    schedule = ql.Schedule(
        issue_date,
        maturity_date,
        ql.Period(ql.Semiannual),
        ql.UnitedStates(ql.UnitedStates.GovernmentBond),
        ql.Following,
        ql.Following,
        ql.DateGeneration.Backward,
        False
    )
    
    print(f"\n📋 TEST BOND: T 3 15/08/52")
    print(f"   Price: {price}")
    print(f"   Coupon: {coupon_rate*100}%")
    print(f"   Maturity: {maturity_date}")
    
    print("\n📊 TESTING DIFFERENT CONVENTIONS:")
    print("-" * 60)
    
    # Test 1: ISMA (Current bug)
    print("\n1️⃣ ActualActual.ISMA (CURRENT BUG):")
    day_counter_isma = ql.ActualActual(ql.ActualActual.ISMA)
    bond_isma = ql.FixedRateBond(2, 100.0, schedule, [coupon_rate], day_counter_isma)
    
    yield_isma = bond_isma.bondYield(price, day_counter_isma, ql.Compounded, ql.Semiannual)
    duration_isma = ql.BondFunctions.duration(
        bond_isma, yield_isma, day_counter_isma, ql.Compounded, 
        ql.Semiannual, ql.Duration.Modified
    )
    
    print(f"   Yield: {yield_isma * 100:.5f}%")
    print(f"   Duration: {duration_isma:.6f} years")
    
    # Test 2: Bond (The fix)
    print("\n2️⃣ ActualActual.Bond (THE FIX):")
    day_counter_bond = ql.ActualActual(ql.ActualActual.Bond)
    bond_bond = ql.FixedRateBond(2, 100.0, schedule, [coupon_rate], day_counter_bond)
    
    yield_bond = bond_bond.bondYield(price, day_counter_bond, ql.Compounded, ql.Semiannual)
    duration_bond = ql.BondFunctions.duration(
        bond_bond, yield_bond, day_counter_bond, ql.Compounded, 
        ql.Semiannual, ql.Duration.Modified
    )
    
    print(f"   Yield: {yield_bond * 100:.5f}%")
    print(f"   Duration: {duration_bond:.6f} years")
    
    # Show the difference
    print("\n📊 COMPARISON:")
    print(f"   Expected Duration (Bloomberg): 16.351196 years")
    print(f"   ISMA Duration (Bug):           {duration_isma:.6f} years")
    print(f"   Bond Duration (Fix):           {duration_bond:.6f} years")
    print(f"   ISMA Error:                    {abs(duration_isma - 16.351196):.6f} years")
    print(f"   Bond Error:                    {abs(duration_bond - 16.351196):.6f} years")
    
    # Verdict
    print("\n✅ VERDICT:")
    if abs(duration_bond - 16.351196) < abs(duration_isma - 16.351196):
        print("   ActualActual.Bond is CORRECT!")
        print("   The fix will restore accurate duration calculations.")
    else:
        print("   Unexpected result - needs further investigation.")
    
    return duration_isma, duration_bond

def check_file_for_bug():
    """Check the actual code for the bug"""
    print("\n📄 Checking google_analysis10.py for the bug...")
    
    file_path = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/google_analysis10.py'
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Find the bug
    for i, line in enumerate(lines, 1):
        if "day_count_str == 'ActualActual_Bond'" in line:
            print(f"\n   Line {i}: {line.strip()}")
            if i < len(lines):
                next_line = lines[i]
                print(f"   Line {i+1}: {next_line.strip()}")
                
                if 'ql.ActualActual.ISMA' in next_line:
                    print("\n   ❌ BUG CONFIRMED: Using ISMA instead of Bond!")
                    print("\n   TO FIX:")
                    print("   Change line {}: ".format(i+1))
                    print("   FROM: day_counter = ql.ActualActual(ql.ActualActual.ISMA)")
                    print("   TO:   day_counter = ql.ActualActual(ql.ActualActual.Bond)")
                    return True
                elif 'ql.ActualActual.Bond' in next_line:
                    print("\n   ✅ Already fixed! Using Bond convention.")
                    return False
    
    print("   ⚠️ Could not find the relevant code section")
    return None

if __name__ == "__main__":
    print("🔍 DURATION BUG INVESTIGATION")
    print("=" * 60)
    
    # Check if bug exists
    has_bug = check_file_for_bug()
    
    # Run the test
    print("\n" + "=" * 60)
    isma_dur, bond_dur = test_simple_quantlib_duration()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 FINAL SUMMARY:")
    
    if has_bug:
        print("   ❌ Bug is present in code (using ISMA)")
        print(f"   Current duration: {isma_dur:.6f} years")
        print(f"   After fix: {bond_dur:.6f} years")
        print(f"   This will improve accuracy by {abs(isma_dur - bond_dur):.6f} years")
    elif has_bug is False:
        print("   ✅ Code already fixed (using Bond)")
        print(f"   Current duration should be: {bond_dur:.6f} years")
    else:
        print("   ⚠️ Could not determine bug status")
