#!/usr/bin/env python3
"""
🔧 SIMPLE FIX: Remove complex Treasury issue date logic
Let QuantLib handle schedule creation with defaults
"""

import sys
import os
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

import QuantLib as ql
from datetime import datetime, date

def test_simple_quantlib_approach():
    print("🔧 TESTING SIMPLE QUANTLIB APPROACH (NO CUSTOM ISSUE DATES)")
    print("=" * 70)
    
    # Set evaluation date
    trade_date = date(2025, 7, 29)
    calculation_date = ql.Date(trade_date.day, trade_date.month, trade_date.year)
    ql.Settings.instance().evaluationDate = calculation_date
    
    # Bond parameters
    coupon = 3.0  # 3% coupon
    price = 71.66
    maturity_date = datetime(2052, 8, 15)
    ql_maturity = ql.Date(maturity_date.day, maturity_date.month, maturity_date.year)
    
    # Calendar and conventions
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    day_counter = ql.ActualActual(ql.ActualActual.ISDA)
    frequency = ql.Semiannual
    settlement_date = calculation_date  # No settlement days
    
    print(f"Settlement Date: {settlement_date}")
    print(f"Maturity Date: {ql_maturity}")
    print(f"Years to Maturity: {(maturity_date.year - trade_date.year):.1f}")
    print()
    
    # 🎯 SIMPLE APPROACH: Just use settlement to maturity schedule
    print("🎯 SIMPLE SCHEDULE: Settlement → Maturity (Let QuantLib handle details)")
    simple_schedule = ql.Schedule(
        settlement_date,  # Start from settlement 
        ql_maturity,      # End at maturity
        ql.Period(frequency),  # Semiannual
        calendar,
        ql.Following,     # Business day convention
        ql.Following,     # End of month convention
        ql.DateGeneration.Backward,  # Generate backward from maturity
        False             # End of month adjustment
    )
    
    simple_bond = ql.FixedRateBond(
        0,                    # Settlement days
        100.0,               # Face value  
        simple_schedule,     # Simple schedule
        [coupon/100.0],      # Coupon rates in decimal
        day_counter          # Day count convention
    )
    
    print("🧮 CALCULATING WITH SIMPLE APPROACH...")
    
    try:
        # Calculate yield 
        yield_simple = simple_bond.bondYield(price, day_counter, ql.Compounded, frequency)
        
        # Calculate duration
        duration_simple = ql.BondFunctions.duration(
            simple_bond, 
            yield_simple * 100,  # Convert to percentage for QuantLib 
            day_counter, 
            ql.Compounded, 
            frequency, 
            ql.Duration.Modified
        )
        
        # Calculate convexity
        convexity_simple = ql.BondFunctions.convexity(
            simple_bond, 
            yield_simple * 100, 
            day_counter, 
            ql.Compounded, 
            frequency
        )
        
        # Accrued interest
        accrued_simple = simple_bond.accruedAmount()
        
        print("📊 SIMPLE RESULTS:")
        print(f"   Yield: {yield_simple*100:.4f}%")
        print(f"   Duration: {duration_simple:.2f} years") 
        print(f"   Convexity: {convexity_simple:.2f}")
        print(f"   Accrued: {accrued_simple:.6f}")
        print()
        
        # 🎯 VALIDATION CHECK
        print("🔍 VALIDATION:")
        if 15 <= duration_simple <= 25:
            print("✅ Duration looks reasonable for 27-year bond!")
        else:
            print(f"❌ Duration {duration_simple:.2f} still problematic")
            
        if 4.0 <= yield_simple*100 <= 7.0:
            print("✅ Yield looks reasonable for deep discount!")
        else:
            print(f"❌ Yield {yield_simple*100:.4f}% seems off")
            
        print()
        print("🎯 **RECOMMENDED FIX**: Replace complex Treasury schedule logic with this simple approach")
        print("   - Remove all custom issue date calculations")
        print("   - Use settlement_date → maturity_date schedule")
        print("   - Let QuantLib handle the details with backward generation")
        
    except Exception as e:
        print(f"❌ Simple calculation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_quantlib_approach()
