#!/usr/bin/env python3
"""
Direct Comparison Test - Your Setup vs Manual Setup
=================================================

Run both approaches side-by-side to isolate the difference
"""

import QuantLib as ql
from datetime import datetime

def test_your_setup_vs_manual():
    """Compare your bond setup vs manual setup directly"""
    
    print("🔬 DIRECT COMPARISON TEST")
    print("=" * 80)
    
    # Common parameters
    calculation_date = ql.Date(30, 6, 2025)
    ql.Settings.instance().evaluationDate = calculation_date
    maturity_date = ql.Date(15, 8, 2052)
    coupon_rate = 0.03
    clean_price = 71.66
    
    print("=" * 80)
    print("🧪 TEST 1: YOUR IMPLEMENTATION APPROACH")
    print("=" * 80)
    
    try:
        # YOUR IMPLEMENTATION APPROACH (from logs)
        calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
        settlement_days = 0
        issue_date = calculation_date
        frequency = ql.Semiannual
        day_counter = ql.ActualActual(ql.ActualActual.ISDA)
        
        # Create schedule (your approach)
        schedule_yours = ql.Schedule(
            issue_date, 
            maturity_date, 
            ql.Period(frequency), 
            calendar, 
            ql.Following,  # Updated to Following
            ql.Following,  # Updated to Following
            ql.DateGeneration.Backward, 
            False
        )
        
        # Create bond (your approach)
        bond_yours = ql.FixedRateBond(settlement_days, 100.0, schedule_yours, [coupon_rate], day_counter)
        
        # Create yield curve (your approach)
        yield_curve = ql.FlatForward(calculation_date, 0.03, day_counter)
        yield_handle = ql.YieldTermStructureHandle(yield_curve)
        engine = ql.DiscountingBondEngine(yield_handle)
        bond_yours.setPricingEngine(engine)
        
        # Calculate yield (your approach)
        bond_yield_yours = bond_yours.bondYield(clean_price, day_counter, ql.Compounded, frequency)
        
        # Convert to decimal if needed
        if bond_yield_yours > 1.0:
            bond_yield_yours = bond_yield_yours / 100.0
        
        # Calculate duration (your approach)
        duration_yours = ql.BondFunctions.duration(bond_yours, bond_yield_yours, day_counter, ql.Compounded, frequency, ql.Duration.Modified)
        convexity_yours = ql.BondFunctions.convexity(bond_yours, bond_yield_yours, day_counter, ql.Compounded, frequency)
        
        print(f"✅ YOUR APPROACH RESULTS:")
        print(f"   Yield: {bond_yield_yours*100:.6f}%")
        print(f"   Duration: {duration_yours:.6f}")
        print(f"   Convexity: {convexity_yours:.6f}")
        
    except Exception as e:
        print(f"❌ YOUR APPROACH FAILED: {e}")
    
    print()
    print("=" * 80)
    print("🧪 TEST 2: MANUAL WORKING APPROACH")
    print("=" * 80)
    
    try:
        # MANUAL WORKING APPROACH (from successful test)
        schedule_manual = ql.Schedule(
            calculation_date,  # issue date
            maturity_date,
            ql.Period(ql.Semiannual),
            ql.UnitedStates(ql.UnitedStates.GovernmentBond),
            ql.Following,
            ql.Following,
            ql.DateGeneration.Backward,
            False
        )
        
        # Create bond (manual approach)
        bond_manual = ql.FixedRateBond(
            0,  # settlement days
            100.0,  # face value
            schedule_manual,
            [coupon_rate],
            ql.ActualActual(ql.ActualActual.ISDA)
        )
        
        # Create yield curve (manual approach)
        yield_curve_manual = ql.FlatForward(calculation_date, 0.03, ql.ActualActual(ql.ActualActual.ISDA))
        yield_handle_manual = ql.YieldTermStructureHandle(yield_curve_manual)
        engine_manual = ql.DiscountingBondEngine(yield_handle_manual)
        bond_manual.setPricingEngine(engine_manual)
        
        # Calculate yield (manual approach)
        bond_yield_manual = bond_manual.bondYield(clean_price, ql.ActualActual(ql.ActualActual.ISDA), ql.Compounded, ql.Semiannual)
        
        # Calculate duration (manual approach)
        duration_manual = ql.BondFunctions.duration(bond_manual, bond_yield_manual, ql.ActualActual(ql.ActualActual.ISDA), ql.Compounded, ql.Semiannual, ql.Duration.Modified)
        convexity_manual = ql.BondFunctions.convexity(bond_manual, bond_yield_manual, ql.ActualActual(ql.ActualActual.ISDA), ql.Compounded, ql.Semiannual)
        
        print(f"✅ MANUAL APPROACH RESULTS:")
        print(f"   Yield: {bond_yield_manual*100:.6f}%")
        print(f"   Duration: {duration_manual:.6f}")
        print(f"   Convexity: {convexity_manual:.6f}")
        
    except Exception as e:
        print(f"❌ MANUAL APPROACH FAILED: {e}")
    
    print()
    print("=" * 80)
    print("🧪 TEST 3: ALTERNATIVE - NO PRICING ENGINE")
    print("=" * 80)
    
    try:
        # Try without setting pricing engine at all
        bond_alt = ql.FixedRateBond(
            0,  # settlement days
            100.0,  # face value
            schedule_manual,
            [coupon_rate],
            ql.ActualActual(ql.ActualActual.ISDA)
        )
        
        # Calculate yield without pricing engine
        bond_yield_alt = bond_alt.bondYield(clean_price, ql.ActualActual(ql.ActualActual.ISDA), ql.Compounded, ql.Semiannual)
        
        # Calculate duration
        duration_alt = ql.BondFunctions.duration(bond_alt, bond_yield_alt, ql.ActualActual(ql.ActualActual.ISDA), ql.Compounded, ql.Semiannual, ql.Duration.Modified)
        convexity_alt = ql.BondFunctions.convexity(bond_alt, bond_yield_alt, ql.ActualActual(ql.ActualActual.ISDA), ql.Compounded, ql.Semiannual)
        
        print(f"✅ NO PRICING ENGINE RESULTS:")
        print(f"   Yield: {bond_yield_alt*100:.6f}%")
        print(f"   Duration: {duration_alt:.6f}")
        print(f"   Convexity: {convexity_alt:.6f}")
        
    except Exception as e:
        print(f"❌ NO PRICING ENGINE FAILED: {e}")
    
    print()
    print("📊 EXPECTED BLOOMBERG RESULTS:")
    print("   Yield: 4.89960%")
    print("   Duration: 16.35658")
    print("   Convexity: 370.22")
    
    print()
    print("🔍 ANALYSIS:")
    print("   - Compare which approach gives duration ~16.36")
    print("   - Look for key differences in setup")
    print("   - Check if pricing engine affects duration calculation")

if __name__ == "__main__":
    test_your_setup_vs_manual()
