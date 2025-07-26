#!/usr/bin/env python3
"""
Yield Units Diagnostic Test
==========================

Test if the bond.bondYield() method is returning yield in percentage vs decimal
"""

import QuantLib as ql

def test_yield_units():
    """Test if yield units are causing the 100x duration error"""
    
    print("🔍 YIELD UNITS DIAGNOSTIC TEST")
    print("=" * 50)
    
    # Set up QuantLib environment  
    calculation_date = ql.Date(30, 6, 2025)
    ql.Settings.instance().evaluationDate = calculation_date
    
    # Create bond
    issue_date = calculation_date
    maturity_date = ql.Date(15, 8, 2052)
    coupon_rate = 0.03  # 3%
    clean_price = 71.66
    
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
    
    day_count = ql.ActualActual(ql.ActualActual.ISDA)
    bond = ql.FixedRateBond(0, 100.0, schedule, [coupon_rate], day_count)
    
    # Create yield curve
    yield_curve = ql.FlatForward(calculation_date, 0.03, day_count)
    yield_handle = ql.YieldTermStructureHandle(yield_curve)
    engine = ql.DiscountingBondEngine(yield_handle)
    bond.setPricingEngine(engine)
    
    print(f"📅 Setup: Price={clean_price}, Coupon={coupon_rate*100}%")
    print()
    
    # Test different yield calculation methods
    print("🧪 TESTING DIFFERENT YIELD CALCULATION METHODS:")
    print("-" * 50)
    
    # Method 1: bond.bondYield() without settlement_date (like manual test)
    try:
        yield_1 = bond.bondYield(clean_price, day_count, ql.Compounded, ql.Semiannual)
        print(f"Method 1 (no settlement): {yield_1:.10f}")
        print(f"Method 1 as percentage: {yield_1*100:.6f}%")
        
        # Test duration with this yield
        duration_1 = ql.BondFunctions.duration(bond, yield_1, day_count, ql.Compounded, ql.Semiannual, ql.Duration.Modified)
        print(f"Duration with Method 1: {duration_1:.6f}")
    except Exception as e:
        print(f"Method 1 FAILED: {e}")
    
    print()
    
    # Method 2: bond.bondYield() WITH settlement_date (like your implementation)
    try:
        yield_2 = bond.bondYield(clean_price, day_count, ql.Compounded, ql.Semiannual, calculation_date)
        print(f"Method 2 (with settlement): {yield_2:.10f}")
        print(f"Method 2 as percentage: {yield_2*100:.6f}%")
        
        # Test duration with this yield
        duration_2 = ql.BondFunctions.duration(bond, yield_2, day_count, ql.Compounded, ql.Semiannual, ql.Duration.Modified)
        print(f"Duration with Method 2: {duration_2:.6f}")
    except Exception as e:
        print(f"Method 2 FAILED: {e}")
    
    print()
    
    # Method 3: Test what happens if we accidentally pass percentage yield
    try:
        # Simulate passing percentage yield (4.9%) instead of decimal (0.049)
        yield_3_wrong = 4.9  # This would be wrong - percentage instead of decimal
        print(f"Method 3 (WRONG - percentage): {yield_3_wrong:.6f}")
        
        duration_3 = ql.BondFunctions.duration(bond, yield_3_wrong, day_count, ql.Compounded, ql.Semiannual, ql.Duration.Modified)
        print(f"Duration with WRONG percentage yield: {duration_3:.6f}")
        print(f"Duration ratio (wrong/correct): {duration_3/duration_1:.6f}")
    except Exception as e:
        print(f"Method 3 FAILED: {e}")
    
    print()
    print("📊 EXPECTED RESULTS:")
    print("   Bloomberg Yield: 4.89960%")
    print("   Bloomberg Duration: 16.35658 years")
    print()
    print("🔍 DIAGNOSIS:")
    print("   - If Method 1 gives ~16.36 duration, use that approach")
    print("   - If Method 2 gives ~0.16 duration, that's your bug")
    print("   - If Method 3 gives ~0.16 duration, you're passing percentage yield")

if __name__ == "__main__":
    test_yield_units()
