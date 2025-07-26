#!/usr/bin/env python3
"""
Manual QuantLib Test - Diagnose Duration Units Issue
==================================================

Direct QuantLib calculation to compare with expected Bloomberg results
"""

import QuantLib as ql
from datetime import datetime

def manual_quantlib_test():
    """Manual QuantLib calculation to diagnose the units issue"""
    
    print("🧪 MANUAL QUANTLIB DURATION TEST")
    print("=" * 60)
    
    # Set up QuantLib environment
    calculation_date = ql.Date(30, 6, 2025)  # 2025-06-30
    ql.Settings.instance().evaluationDate = calculation_date
    
    # Bond parameters 
    issue_date = calculation_date
    maturity_date = ql.Date(15, 8, 2052)  # 2052-08-15
    coupon_rate = 0.03  # 3%
    clean_price = 71.66
    
    print(f"📅 Calculation Date: {calculation_date}")
    print(f"📅 Maturity Date: {maturity_date}")
    print(f"💰 Coupon Rate: {coupon_rate*100}%")
    print(f"💰 Clean Price: {clean_price}")
    print()
    
    # Test different day count conventions and frequencies
    test_cases = [
        {
            "name": "Current Implementation",
            "day_count": ql.ActualActual(ql.ActualActual.ISDA),
            "frequency": ql.Semiannual,
            "compounding": ql.Compounded
        },
        {
            "name": "Bloomberg Standard",
            "day_count": ql.ActualActual(ql.ActualActual.ISDA),
            "frequency": ql.Semiannual,
            "compounding": ql.Compounded
        },
        {
            "name": "Alternative: 30/360",
            "day_count": ql.Thirty360(ql.Thirty360.BondBasis),
            "frequency": ql.Semiannual,
            "compounding": ql.Compounded
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"🧪 TEST CASE {i+1}: {test_case['name']}")
        print("-" * 50)
        
        try:
            # Create schedule
            schedule = ql.Schedule(
                issue_date, 
                maturity_date,
                ql.Period(test_case['frequency']),
                ql.UnitedStates(ql.UnitedStates.GovernmentBond),
                ql.Following,
                ql.Following,
                ql.DateGeneration.Backward,
                False
            )
            
            # Create bond
            bond = ql.FixedRateBond(
                0,  # settlement days
                100.0,  # face value
                schedule,
                [coupon_rate],
                test_case['day_count']
            )
            
            # Create yield curve (flat)
            yield_curve = ql.FlatForward(calculation_date, 0.03, test_case['day_count'])
            yield_handle = ql.YieldTermStructureHandle(yield_curve)
            
            # Set pricing engine
            engine = ql.DiscountingBondEngine(yield_handle)
            bond.setPricingEngine(engine)
            
            # Calculate yield from price
            bond_yield = bond.bondYield(clean_price, test_case['day_count'], test_case['compounding'], test_case['frequency'])
            
            print(f"✅ Bond Yield: {bond_yield*100:.6f}%")
            
            # Test DIFFERENT duration calculation methods
            print("\n🔍 TESTING DIFFERENT DURATION CALCULATION METHODS:")
            
            # Method 1: BondFunctions.duration with yield rate
            try:
                duration_1 = ql.BondFunctions.duration(
                    bond, 
                    bond_yield,
                    test_case['day_count'],
                    test_case['compounding'],
                    test_case['frequency'],
                    ql.Duration.Modified
                )
                print(f"   Method 1 - BondFunctions.duration: {duration_1:.6f}")
                print(f"   Method 1 - Scaled x100: {duration_1*100:.6f}")
            except Exception as e:
                print(f"   Method 1 - FAILED: {e}")
            
            # Method 2: BondFunctions.duration with InterestRate object
            try:
                interest_rate = ql.InterestRate(bond_yield, test_case['day_count'], test_case['compounding'], test_case['frequency'])
                duration_2 = ql.BondFunctions.duration(bond, interest_rate, ql.Duration.Modified)
                print(f"   Method 2 - With InterestRate object: {duration_2:.6f}")
                print(f"   Method 2 - Scaled x100: {duration_2*100:.6f}")
            except Exception as e:
                print(f"   Method 2 - FAILED: {e}")
            
            # Method 3: Manual calculation check
            try:
                # Calculate modified duration manually for comparison
                # ModDur = MacDur / (1 + YTM/frequency)
                macaulay_duration = ql.BondFunctions.duration(
                    bond,
                    bond_yield, 
                    test_case['day_count'],
                    test_case['compounding'],
                    test_case['frequency'],
                    ql.Duration.Macaulay
                )
                frequency_per_year = 2.0 if test_case['frequency'] == ql.Semiannual else 1.0
                manual_mod_duration = macaulay_duration / (1 + bond_yield/frequency_per_year)
                print(f"   Method 3 - Macaulay Duration: {macaulay_duration:.6f}")
                print(f"   Method 3 - Manual Modified: {manual_mod_duration:.6f}")
            except Exception as e:
                print(f"   Method 3 - FAILED: {e}")
            
            # Calculate convexity
            try:
                convexity = ql.BondFunctions.convexity(
                    bond,
                    bond_yield,
                    test_case['day_count'],
                    test_case['compounding'],
                    test_case['frequency']
                )
                print(f"\n📊 Convexity: {convexity:.6f}")
                print(f"📊 Convexity x100: {convexity*100:.6f}")
                print(f"📊 Convexity x10000: {convexity*10000:.6f}")
            except Exception as e:
                print(f"📊 Convexity - FAILED: {e}")
            
            print()
            
        except Exception as e:
            print(f"❌ TEST CASE FAILED: {e}")
            print()
    
    print("🎯 EXPECTED BLOOMBERG RESULTS FOR COMPARISON:")
    print("   Yield: 4.89960%")
    print("   Modified Duration: 16.35658 years")
    print("   Convexity: 370.22")
    print()
    print("🔍 ANALYSIS:")
    print("   - If any method gives ~16.36, that's the correct approach")
    print("   - If results are ~0.16, multiply by 100")
    print("   - If results are ~0.0016, multiply by 10000")
    print("   - Compare different day count conventions")

if __name__ == "__main__":
    manual_quantlib_test()
