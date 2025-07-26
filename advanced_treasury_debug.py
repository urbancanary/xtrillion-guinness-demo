#!/usr/bin/env python3
"""
Advanced Treasury Duration Debug
==============================

Tests different approaches to fix the Treasury duration calculation bug.
Focus on yield calculation methods and bond setup.
"""

import QuantLib as ql
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def debug_quantlib_yield_methods():
    """Test different QuantLib yield calculation approaches"""
    
    print("🔬 ADVANCED QUANTLIB YIELD DEBUGGING")
    print("=" * 60)
    
    # Set evaluation date
    settlement_date = ql.Date(30, 6, 2025)
    ql.Settings.instance().evaluationDate = settlement_date
    
    # Bond parameters matching your Treasury
    issue_date = settlement_date
    maturity_date = ql.Date(15, 8, 2052)
    coupon_rate = 0.03  # 3%
    price = 71.66
    face_value = 100.0
    
    print(f"📊 Bond Parameters:")
    print(f"   Settlement: {settlement_date}")
    print(f"   Maturity: {maturity_date}")
    print(f"   Coupon: {coupon_rate*100}%")
    print(f"   Price: {price}")
    print(f"   Expected Duration: 16.35658")
    print()
    
    # Test different day count conventions
    day_counts = [
        ("ActualActual_ISDA", ql.ActualActual(ql.ActualActual.ISDA)),
        ("ActualActual_Bond", ql.ActualActual(ql.ActualActual.Bond)),
        ("Actual365Fixed", ql.Actual365Fixed()),
        ("Thirty360_BondBasis", ql.Thirty360(ql.Thirty360.BondBasis))
    ]
    
    # Test different frequencies
    frequencies = [
        ("Semiannual", ql.Semiannual),
        ("Annual", ql.Annual)
    ]
    
    print("🧪 TESTING DIFFERENT CONVENTIONS:")
    print("-" * 50)
    
    for dc_name, day_counter in day_counts:
        for freq_name, frequency in frequencies:
            try:
                print(f"\n📋 Testing: {dc_name} + {freq_name}")
                
                # Create schedule
                schedule = ql.Schedule(
                    issue_date,
                    maturity_date, 
                    ql.Period(frequency),
                    ql.UnitedStates(ql.UnitedStates.GovernmentBond),
                    ql.Following,
                    ql.Following,
                    ql.DateGeneration.Backward,
                    False
                )
                
                # Create bond
                bond = ql.FixedRateBond(
                    0,  # Settlement days
                    face_value,
                    schedule,
                    [coupon_rate],
                    day_counter
                )
                
                # Calculate yield - TEST DIFFERENT METHODS
                
                # Method 1: Standard bondYield
                yield_decimal = bond.bondYield(price, day_counter, ql.Compounded, frequency)
                
                # Method 2: Direct IRR calculation
                cash_flows = bond.cashflows()
                
                # Calculate durations with different yield approaches
                duration_std = ql.BondFunctions.duration(
                    bond, yield_decimal, day_counter, ql.Compounded, frequency, ql.Duration.Modified
                )
                
                # Test manual yield calculation using clean price instead of dirty price
                clean_price = price  # Assuming price given is clean price
                yield_from_clean = bond.bondYield(clean_price, day_counter, ql.Compounded, frequency)
                
                duration_from_clean = ql.BondFunctions.duration(
                    bond, yield_from_clean, day_counter, ql.Compounded, frequency, ql.Duration.Modified
                )
                
                print(f"   📈 Yield (standard): {yield_decimal:.6f} ({yield_decimal*100:.4f}%)")
                print(f"   📈 Yield (from clean): {yield_from_clean:.6f} ({yield_from_clean*100:.4f}%)")
                print(f"   ⏱️  Duration (standard): {duration_std:.5f}")
                print(f"   ⏱️  Duration (from clean): {duration_from_clean:.5f}")
                
                # Check accuracy
                expected = 16.35658
                error_std = abs(duration_std - expected)
                error_clean = abs(duration_from_clean - expected)
                
                print(f"   📊 Error (standard): {error_std:.5f}")
                print(f"   📊 Error (from clean): {error_clean:.5f}")
                
                if error_std < 0.1:
                    print(f"   ✅ CLOSE MATCH with standard method!")
                if error_clean < 0.1:
                    print(f"   ✅ CLOSE MATCH with clean price method!")
                    
            except Exception as e:
                print(f"   ❌ Failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 TESTING BLOOMBERG-SPECIFIC APPROACH")
    print("=" * 60)
    
    # Bloomberg typically uses:
    # - ActualActual ISDA day count for Treasuries
    # - Semiannual frequency
    # - Clean price for yield calculation
    # - Settlement = T+1 for Treasuries
    
    try:
        # Bloomberg-style setup
        bbg_settlement = ql.Date(1, 7, 2025)  # T+1 settlement
        ql.Settings.instance().evaluationDate = bbg_settlement
        
        bbg_day_counter = ql.ActualActual(ql.ActualActual.ISDA)
        bbg_frequency = ql.Semiannual
        
        # Create Bloomberg-style schedule
        bbg_schedule = ql.Schedule(
            bbg_settlement,
            maturity_date,
            ql.Period(bbg_frequency),
            ql.UnitedStates(ql.UnitedStates.GovernmentBond),
            ql.Following,
            ql.Following, 
            ql.DateGeneration.Backward,
            False
        )
        
        # Bloomberg-style bond
        bbg_bond = ql.FixedRateBond(
            1,  # T+1 settlement for Treasuries
            face_value,
            bbg_schedule,
            [coupon_rate],
            bbg_day_counter
        )
        
        # Bloomberg yield calculation
        bbg_yield = bbg_bond.bondYield(price, bbg_day_counter, ql.Compounded, bbg_frequency)
        bbg_duration = ql.BondFunctions.duration(
            bbg_bond, bbg_yield, bbg_day_counter, ql.Compounded, bbg_frequency, ql.Duration.Modified
        )
        
        print(f"📊 Bloomberg-Style Results:")
        print(f"   Settlement: T+1 ({bbg_settlement})")
        print(f"   Day Count: ActualActual ISDA")
        print(f"   Frequency: Semiannual")
        print(f"   📈 Yield: {bbg_yield:.6f} ({bbg_yield*100:.4f}%)")
        print(f"   ⏱️  Duration: {bbg_duration:.5f}")
        print(f"   📊 Error vs Expected: {abs(bbg_duration - 16.35658):.5f}")
        
        if abs(bbg_duration - 16.35658) < 0.1:
            print(f"   🎯 BLOOMBERG METHOD SUCCESS!")
            
    except Exception as e:
        print(f"❌ Bloomberg test failed: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    debug_quantlib_yield_methods()
