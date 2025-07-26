#!/usr/bin/env python3
"""
CORRECTED test for US706451BG56 business convention issue
"""

import sys
import QuantLib as ql
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis9')

from calculators.bond_calculation_registry import get_working_accrued_calculation

def test_different_conventions_systematically():
    """Test the bond with different conventions to match the database discrepancy"""
    
    print("🎯 SYSTEMATIC BUSINESS CONVENTION TEST")
    print("="*60)
    
    print("🆔 ISIN: US706451BG56")
    print("💰 Target Bloomberg: $22,635.42 per $1M")
    print("❌ validated_calculations: $22,451.39 per $1M (wrong)")
    print("✅ pemex_calculations: $22,635.42 per $1M (correct)")
    
    # My enhanced calculation function
    calc_func = get_working_accrued_calculation()
    
    # Test what my function produces
    print(f"\n🧪 MY ENHANCED CALCULATION:")
    result = calc_func("US706451BG56", 6.625, "2035-06-15", "2025-04-18")
    if result['success']:
        print(f"   💰 My Result: ${result['accrued_per_million']:,.2f} per $1M")
        print(f"   📊 Days Accrued: {result['days_accrued']}")
        print(f"   📅 Last Coupon: {result['last_coupon_date']}")
    
    # The difference between validated and correct is $184.03
    # Let's calculate what that represents in terms of days or calculation differences
    
    difference = 22635.42 - 22451.39
    print(f"\n🔍 ANALYZING THE $184.03 DIFFERENCE:")
    print(f"   💰 Absolute Difference: ${difference:.2f}")
    print(f"   📊 As % of Bloomberg: {(difference/22635.42)*100:.2f}%")
    
    # Calculate days difference if this was a day count issue
    coupon_daily = (6.625 / 2) / 180  # Rough daily coupon for 6-month period
    days_equivalent = difference / (coupon_daily * 10000)  # Convert to per-million
    print(f"   📅 Equivalent to ~{days_equivalent:.1f} days of accrual difference")

def test_specific_hypothesis():
    """Test specific hypothesis about what caused the validated_calculations error"""
    
    print(f"\n🔬 TESTING SPECIFIC HYPOTHESIS")
    print("="*60)
    
    # Hypothesis: The validated_calculations used "Following" instead of "Unadjusted"
    # for business convention, or had a different last coupon calculation
    
    coupon_rate = 6.625
    settlement_date = ql.Date(18, 4, 2025)
    maturity_date = ql.Date(15, 6, 2035)
    
    ql.Settings.instance().evaluationDate = settlement_date
    
    # Test the exact difference: Following vs Unadjusted
    print("🧪 Testing Following vs Unadjusted business convention:")
    
    conventions = [
        ("Unadjusted", ql.Unadjusted),
        ("Following", ql.Following)
    ]
    
    results = []
    
    for conv_name, conv_ql in conventions:
        try:
            calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
            day_count = ql.Thirty360(ql.Thirty360.BondBasis)
            
            # Generate schedule - this is where business convention matters
            schedule = ql.Schedule(
                ql.Date(15, 6, 2015),  # Issue date
                maturity_date,
                ql.Period(6, ql.Months),
                calendar,
                conv_ql,  # Business convention
                conv_ql,  # Termination business convention
                ql.DateGeneration.Backward,
                False
            )
            
            # Check the actual coupon dates generated
            coupon_dates = []
            for i in range(schedule.size()):
                coupon_dates.append(schedule.date(i))
            
            # Find last coupon before settlement
            last_coupon = None
            for date in reversed(coupon_dates):
                if date <= settlement_date:
                    last_coupon = date
                    break
            
            print(f"\n   📅 {conv_name}:")
            print(f"      Last Coupon: {last_coupon}")
            
            # Create bond and calculate accrued
            bond = ql.FixedRateBond(
                0,
                1000000.0,  # $1M face value
                schedule,
                [coupon_rate / 100.0],
                day_count
            )
            
            accrued = bond.accruedAmount(settlement_date)
            accrued_per_million = accrued  # Already calculated on $1M
            
            print(f"      Accrued: ${accrued_per_million:,.2f} per $1M")
            
            results.append({
                'convention': conv_name,
                'last_coupon': last_coupon,
                'accrued': accrued_per_million
            })
            
        except Exception as e:
            print(f"   ❌ {conv_name} Error: {e}")
    
    # Check if the difference explains the database discrepancy
    if len(results) == 2:
        unadjusted_accrued = results[0]['accrued']
        following_accrued = results[1]['accrued']
        convention_diff = abs(unadjusted_accrued - following_accrued)
        
        print(f"\n🎯 BUSINESS CONVENTION IMPACT:")
        print(f"   💰 Unadjusted: ${unadjusted_accrued:,.2f}")
        print(f"   💰 Following: ${following_accrued:,.2f}")
        print(f"   💰 Difference: ${convention_diff:.2f}")
        
        # Compare with database discrepancy
        database_diff = 22635.42 - 22451.39  # $184.03
        print(f"\n🔍 COMPARISON:")
        print(f"   Database Discrepancy: ${database_diff:.2f}")
        print(f"   Convention Difference: ${convention_diff:.2f}")
        
        if abs(convention_diff - database_diff) < 10.0:
            print("   ✅ BUSINESS CONVENTION EXPLAINS THE DIFFERENCE!")
        else:
            print("   ❌ Business convention doesn't fully explain the difference")

if __name__ == "__main__":
    test_different_conventions_systematically()
    test_specific_hypothesis()
