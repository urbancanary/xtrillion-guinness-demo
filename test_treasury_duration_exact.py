#!/usr/bin/env python3
"""
Test the EXACT duration calculation with proper Treasury conventions
US TREASURY N/B, 3%, 15-Aug-2052, Price: 71.66
Target: 16.35 duration
"""

import QuantLib as ql
import sys
import os
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

from google_analysis9 import get_correct_quantlib_compounding

def test_treasury_duration_exact():
    print("🔢 EXACT Treasury Duration Test - Spot On Accuracy")
    print("=" * 60)
    
    # Set settlement date 
    settlement_date = ql.Date(30, 7, 2025)
    ql.Settings.instance().evaluationDate = settlement_date
    
    # Treasury bond details
    price = 71.66
    coupon_rate = 0.03  # 3%
    maturity_date = ql.Date(15, 8, 2052)
    isin = "US912810TJ79"
    
    print(f"Bond: US TREASURY N/B, 3%, 15-Aug-2052")
    print(f"ISIN: {isin}")
    print(f"Price: {price}")
    print(f"Settlement: {settlement_date}")
    print(f"Maturity: {maturity_date}")
    print()
    
    # 🏛️ TREASURY CONVENTIONS (EXACT)
    day_count = ql.ActualActual(ql.ActualActual.ISDA)
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    business_convention = ql.Following
    frequency = ql.Semiannual  # Treasury bonds pay semiannually
    compounding_type = ql.Compounded
    settlement_days = 1
    
    print("📊 EXACT TREASURY CONVENTIONS:")
    print(f"Day Count: ActualActual_ISDA")
    print(f"Frequency: Semiannual")
    print(f"Compounding: Compounded")
    print(f"Business Convention: Following")
    print()
    
    # Create the bond schedule
    schedule = ql.Schedule(
        settlement_date, maturity_date, ql.Period(frequency),
        calendar, business_convention, business_convention,
        ql.DateGeneration.Backward, False
    )
    
    # Create the fixed rate bond
    coupons = [coupon_rate]
    fixed_rate_bond = ql.FixedRateBond(
        settlement_days, 100.0, schedule, coupons, day_count
    )
    
    print(f"✅ Bond created with {len(schedule)-1} coupon payments")
    print()
    
    # Calculate yield using EXACT Treasury conventions
    clean_price = price
    bond_yield = fixed_rate_bond.bondYield(clean_price, day_count, compounding_type, frequency)
    
    print(f"💰 YIELD CALCULATION:")
    print(f"Clean Price: {clean_price}")
    print(f"Bond Yield: {bond_yield:.6f} ({bond_yield*100:.4f}%)")
    print()
    
    # 🎯 METHOD 1: Create InterestRate object with EXACT conventions
    print("🎯 DURATION METHOD 1: InterestRate Object")
    interest_rate = ql.InterestRate(bond_yield, day_count, compounding_type, frequency)
    duration_method1 = ql.BondFunctions.duration(fixed_rate_bond, interest_rate, ql.Duration.Modified)
    
    print(f"Interest Rate Object: {bond_yield:.6f}, ActualActual_ISDA, Compounded, Semiannual")
    print(f"Duration Method 1: {duration_method1:.6f} years")
    print()
    
    # 🎯 METHOD 2: Pass conventions directly
    print("🎯 DURATION METHOD 2: Direct Conventions")
    duration_method2 = ql.BondFunctions.duration(
        fixed_rate_bond, bond_yield, day_count, compounding_type, frequency, ql.Duration.Modified
    )
    
    print(f"Duration Method 2: {duration_method2:.6f} years")
    print()
    
    # Compare with target
    target_duration = 16.35
    print("🎯 COMPARISON WITH TARGET:")
    print(f"Target Duration: {target_duration:.2f} years")
    print(f"Method 1 Duration: {duration_method1:.2f} years")
    print(f"Method 2 Duration: {duration_method2:.2f} years")
    print(f"Method 1 Difference: {abs(duration_method1 - target_duration):.4f} years")
    print(f"Method 2 Difference: {abs(duration_method2 - target_duration):.4f} years")
    print()
    
    # Test what the current system uses
    print("🔍 TESTING CURRENT SYSTEM CONVENTIONS:")
    try:
        compounding_freq = get_correct_quantlib_compounding(isin, description=None, issuer=None)
        is_treasury = (compounding_freq == ql.Semiannual)
        
        print(f"System Detection: {'Treasury' if is_treasury else 'Corporate'}")
        print(f"System Compounding: {'Semiannual' if compounding_freq == ql.Semiannual else 'Annual'}")
        
        # This mimics the current system calculation
        system_interest_rate = ql.InterestRate(bond_yield, day_count, compounding_type, compounding_freq)
        system_duration = ql.BondFunctions.duration(fixed_rate_bond, system_interest_rate, ql.Duration.Modified)
        
        print(f"System Duration: {system_duration:.6f} years")
        print(f"System Difference from Target: {abs(system_duration - target_duration):.4f} years")
        
    except Exception as e:
        print(f"Error testing system: {e}")
    
    print()
    print("=" * 60)
    print("SUMMARY:")
    if abs(duration_method1 - target_duration) < 0.01:
        print("✅ METHOD 1 SPOT ON!")
    elif abs(duration_method2 - target_duration) < 0.01:
        print("✅ METHOD 2 SPOT ON!")
    else:
        print("❌ Neither method achieves spot-on accuracy")
        print("   May need different settlement date or curve setup")
    
    return {
        'method1_duration': duration_method1,
        'method2_duration': duration_method2,
        'target_duration': target_duration,
        'yield': bond_yield * 100
    }

if __name__ == "__main__":
    try:
        result = test_treasury_duration_exact()
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
