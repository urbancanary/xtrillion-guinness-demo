#!/usr/bin/env python3
"""
QuantLib Duration Investigation - Target T 3 15/08/52 Bond
===========================================================

This script investigates the exact QuantLib configuration causing the 
massive duration error for T 3 15/08/52:
- Expected: 16.357839 years
- Current: 9.69461 years  
- Error: 6.66 years (41% off!)

This script tests different QuantLib parameter combinations to identify 
the exact cause of the error.
"""

import sys
import os
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

import QuantLib as ql
from datetime import datetime, date

def test_quantlib_configurations():
    """
    Test different QuantLib configurations to find the duration error source
    """
    
    print("🔍 QUANTLIB DURATION INVESTIGATION")
    print("=" * 50)
    print("Target Bond: T 3 15/08/52 at price 71.66")
    print("Expected Duration: 16.357839 years (Bloomberg)")
    print("Current Result: 9.69461 years (6.66 year error)")
    print()
    
    # Bond parameters (matching current implementation)
    coupon_rate = 3.0  # 3% coupon
    price = 71.66
    face_value = 100.0
    
    # Dates (matching current implementation)
    trade_date = date(2025, 6, 30)  # Settlement date from logs
    maturity_date = date(2052, 8, 15)  # Maturity from logs
    
    print(f"📅 Settlement Date: {trade_date}")
    print(f"📅 Maturity Date: {maturity_date}")
    print(f"💰 Coupon Rate: {coupon_rate}%")
    print(f"💰 Price: {price}")
    print()
    
    # Convert to QuantLib dates
    ql_trade_date = ql.Date(trade_date.day, trade_date.month, trade_date.year)
    ql_maturity = ql.Date(maturity_date.day, maturity_date.month, maturity_date.year)
    ql.Settings.instance().evaluationDate = ql_trade_date
    
    # Calendar and conventions (matching current implementation)
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    settlement_date = calendar.advance(ql_trade_date, ql.Period(0, ql.Days))  # T+0
    
    print("🧪 TESTING DIFFERENT ISSUE DATE APPROACHES")
    print("-" * 50)
    
    # Test 1: Current implementation (conservative issue date)
    years_before_maturity = min(35, max(10, int((maturity_date.year - 2000))))
    conservative_issue = calendar.advance(ql_maturity, ql.Period(-years_before_maturity, ql.Years))
    test_issue_date("Conservative Issue Date", conservative_issue, ql_maturity, settlement_date, 
                   coupon_rate, price, calendar)
    
    # Test 2: Try real Treasury issue date (estimate for 30Y bond issued ~2022)
    estimated_real_issue = ql.Date(15, 8, 2022)  # Estimated real issue date
    test_issue_date("Estimated Real Issue Date", estimated_real_issue, ql_maturity, settlement_date,
                   coupon_rate, price, calendar)
    
    # Test 3: Try different schedule generation methods
    print("\n🧪 TESTING DIFFERENT SCHEDULE GENERATION METHODS")
    print("-" * 50)
    
    test_schedule_methods(conservative_issue, ql_maturity, settlement_date, coupon_rate, price, calendar)
    
    # Test 4: Try different day count conventions
    print("\n🧪 TESTING DIFFERENT DAY COUNT CONVENTIONS")
    print("-" * 50)
    
    test_day_count_conventions(conservative_issue, ql_maturity, settlement_date, coupon_rate, price, calendar)

def test_issue_date(description, issue_date, maturity_date, settlement_date, coupon_rate, price, calendar):
    """Test a specific issue date configuration"""
    
    print(f"\n📊 {description}:")
    print(f"   Issue Date: {format_ql_date(issue_date)}")
    
    try:
        # Create schedule (matching current implementation)
        frequency = ql.Semiannual
        schedule = ql.Schedule(
            issue_date, maturity_date, ql.Period(frequency), calendar, 
            ql.Following, ql.Following, ql.DateGeneration.Backward, False
        )
        
        # Create bond (matching current implementation)
        day_counter = ql.ActualActual(ql.ActualActual.ISDA)
        coupon_decimal = coupon_rate / 100.0
        bond = ql.FixedRateBond(0, 100.0, schedule, [coupon_decimal], day_counter)
        
        # Calculate yield (matching current implementation)
        yield_frequency = ql.Semiannual
        bond_yield_decimal = bond.bondYield(price, day_counter, ql.Compounded, yield_frequency)
        
        # Calculate duration (matching current implementation)
        yield_percentage = bond_yield_decimal * 100
        duration_raw = ql.BondFunctions.duration(
            bond, yield_percentage, day_counter, ql.Compounded, 
            yield_frequency, ql.Duration.Modified
        )
        duration_bloomberg = duration_raw * 100
        
        print(f"   ✅ Yield: {bond_yield_decimal*100:.6f}%")
        print(f"   📊 Duration (Raw): {duration_raw:.6f}")
        print(f"   📊 Duration (Bloomberg): {duration_bloomberg:.6f} years")
        print(f"   🎯 Error vs Expected: {abs(16.357839 - duration_bloomberg):.3f} years")
        
        if abs(16.357839 - duration_bloomberg) < 1.0:
            print(f"   🎉 SUCCESS: Duration error < 1 year!")
        else:
            print(f"   ❌ STILL WRONG: Duration error > 1 year")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

def test_schedule_methods(issue_date, maturity_date, settlement_date, coupon_rate, price, calendar):
    """Test different schedule generation methods"""
    
    methods = [
        ("Backward Generation", ql.DateGeneration.Backward),
        ("Forward Generation", ql.DateGeneration.Forward),
    ]
    
    for method_name, generation_rule in methods:
        print(f"\n📊 {method_name}:")
        
        try:
            frequency = ql.Semiannual
            schedule = ql.Schedule(
                issue_date, maturity_date, ql.Period(frequency), calendar,
                ql.Following, ql.Following, generation_rule, False
            )
            
            # Quick duration test
            day_counter = ql.ActualActual(ql.ActualActual.ISDA)
            coupon_decimal = coupon_rate / 100.0
            bond = ql.FixedRateBond(0, 100.0, schedule, [coupon_decimal], day_counter)
            
            yield_frequency = ql.Semiannual
            bond_yield_decimal = bond.bondYield(price, day_counter, ql.Compounded, yield_frequency)
            yield_percentage = bond_yield_decimal * 100
            duration_raw = ql.BondFunctions.duration(
                bond, yield_percentage, day_counter, ql.Compounded, 
                yield_frequency, ql.Duration.Modified
            )
            duration_bloomberg = duration_raw * 100
            
            print(f"   📊 Duration: {duration_bloomberg:.6f} years")
            print(f"   🎯 Error: {abs(16.357839 - duration_bloomberg):.3f} years")
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")

def test_day_count_conventions(issue_date, maturity_date, settlement_date, coupon_rate, price, calendar):
    """Test different day count conventions"""
    
    conventions = [
        ("ActualActual ISDA (Current)", ql.ActualActual(ql.ActualActual.ISDA)),
        ("ActualActual Bond", ql.ActualActual(ql.ActualActual.Bond)),
        ("ActualActual ISMA", ql.ActualActual(ql.ActualActual.ISMA)),
        ("30/360 Bond Basis", ql.Thirty360(ql.Thirty360.BondBasis)),
        ("Actual/360", ql.Actual360()),
        ("Actual/365 Fixed", ql.Actual365Fixed()),
    ]
    
    frequency = ql.Semiannual
    schedule = ql.Schedule(
        issue_date, maturity_date, ql.Period(frequency), calendar,
        ql.Following, ql.Following, ql.DateGeneration.Backward, False
    )
    
    for convention_name, day_counter in conventions:
        print(f"\n📊 {convention_name}:")
        
        try:
            coupon_decimal = coupon_rate / 100.0
            bond = ql.FixedRateBond(0, 100.0, schedule, [coupon_decimal], day_counter)
            
            yield_frequency = ql.Semiannual  
            bond_yield_decimal = bond.bondYield(price, day_counter, ql.Compounded, yield_frequency)
            yield_percentage = bond_yield_decimal * 100
            duration_raw = ql.BondFunctions.duration(
                bond, yield_percentage, day_counter, ql.Compounded,
                yield_frequency, ql.Duration.Modified
            )
            duration_bloomberg = duration_raw * 100
            
            print(f"   💰 Yield: {bond_yield_decimal*100:.6f}%")
            print(f"   📊 Duration: {duration_bloomberg:.6f} years")
            print(f"   🎯 Error: {abs(16.357839 - duration_bloomberg):.3f} years")
            
            if abs(16.357839 - duration_bloomberg) < 0.5:
                print(f"   🎉 EXCELLENT: Duration very close to Bloomberg!")
            elif abs(16.357839 - duration_bloomberg) < 1.0:
                print(f"   ✅ GOOD: Duration error < 1 year")
            else:
                print(f"   ❌ POOR: Duration error > 1 year")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")

def format_ql_date(ql_date):
    """Format QuantLib date for display"""
    return f"{ql_date.dayOfMonth():02d}-{ql_date.month():02d}-{ql_date.year()}"

if __name__ == "__main__":
    print("🚀 Starting comprehensive QuantLib duration investigation...")
    print("This will systematically test different configurations to find the error source.")
    print()
    
    try:
        test_quantlib_configurations()
        
        print(f"\n🎯 INVESTIGATION COMPLETE!")
        print("=" * 50)
        print("Review the results above to identify which configuration")
        print("produces duration closest to Bloomberg's 16.357839 years.")
        print()
        print("Key things to look for:")
        print("1. Issue date method that reduces error significantly")
        print("2. Day count convention that matches Bloomberg expectations")
        print("3. Schedule generation method differences")
        print()
        print("The configuration with the smallest error should be adopted")
        print("in the main google_analysis10.py calculation engine.")
        
    except Exception as e:
        print(f"❌ ERROR: Investigation failed: {e}")
        import traceback
        traceback.print_exc()
