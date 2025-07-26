#!/usr/bin/env python3
"""
Test different business conventions for US706451BG56 to find the root cause
"""

import sys
import QuantLib as ql
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis9')

def test_business_convention_impact():
    """Test US706451BG56 with different business conventions"""
    
    print("🔧 TESTING BUSINESS CONVENTION IMPACT")
    print("="*60)
    
    print("🆔 ISIN: US706451BG56 (PEMEX 6⅝ 06/15/35)")
    print("💰 Coupon: 6.625%")
    print("📅 Maturity: 2035-06-15")
    print("📅 Settlement: 2025-04-18")
    
    # Bond parameters
    coupon_rate = 6.625
    maturity_date = ql.Date(15, 6, 2035)
    settlement_date = ql.Date(18, 4, 2025)
    
    # Set evaluation date
    ql.Settings.instance().evaluationDate = settlement_date
    
    # Test different business conventions
    conventions = [
        ("Unadjusted", ql.Unadjusted),
        ("Following", ql.Following),
        ("ModifiedFollowing", ql.ModifiedFollowing),
        ("Preceding", ql.Preceding),
        ("ModifiedPreceding", ql.ModifiedPreceding)
    ]
    
    results = []
    
    for conv_name, conv_enum in conventions:
        print(f"\n🧪 Testing: {conv_name}")
        
        try:
            # Calendar and day count
            calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
            day_count = ql.Thirty360(ql.Thirty360.BondBasis)
            
            # Create bond schedule
            schedule = ql.Schedule(
                ql.Date(15, 6, 2015),  # Issue date (estimated)
                maturity_date,
                ql.Period(6, ql.Months),  # Semiannual
                calendar,
                conv_enum,  # Business convention
                conv_enum,  # Termination business convention  
                ql.DateGeneration.Backward,
                False  # End of month
            )
            
            # Create fixed rate bond
            bond = ql.FixedRateBond(
                0,  # Settlement days
                1000000.0,  # Face value ($1M for per-million calculation)
                schedule,
                [coupon_rate / 100.0],  # Convert to decimal
                day_count
            )
            
            # Calculate accrued interest
            accrued = bond.accruedAmount(settlement_date)
            
            print(f"   💰 Accrued: ${accrued:,.4f} per $1M")
            
            results.append({
                'convention': conv_name,
                'accrued': accrued
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results.append({
                'convention': conv_name,
                'accrued': None,
                'error': str(e)
            })
    
    # Compare with known values
    print(f"\n🎯 COMPARISON WITH DATABASE VALUES:")
    print("="*60)
    
    bloomberg_target = 22635.42
    pemex_calc_value = 22635.42
    validated_calc_value = 22451.39
    
    print(f"📊 Bloomberg Target: ${bloomberg_target:,.2f}")
    print(f"📊 pemex_calculations: ${pemex_calc_value:,.2f}")
    print(f"📊 validated_calculations: ${validated_calc_value:,.2f}")
    
    print(f"\n🔍 BUSINESS CONVENTION RESULTS:")
    for result in results:
        if result['accrued'] is not None:
            diff_bloomberg = abs(result['accrued'] - bloomberg_target)
            diff_validated = abs(result['accrued'] - validated_calc_value)
            
            match_type = ""
            if diff_bloomberg < 1.0:
                match_type += "✅ MATCHES BLOOMBERG "
            if diff_validated < 1.0:
                match_type += "🔍 MATCHES VALIDATED "
            
            print(f"   {result['convention']}: ${result['accrued']:,.2f} {match_type}")
        else:
            print(f"   {result['convention']}: ERROR - {result.get('error', 'Unknown')}")

def test_date_interpretation_issue():
    """Test if the issue is in the date interpretation within validated_quantlib_bonds.db"""
    
    print(f"\n🗓️ TESTING DATE INTERPRETATION IN VALIDATED DB")
    print("="*60)
    
    # The validated_calculations shows 2035-06-15 but maybe the original calculation used wrong date?
    
    dates_to_test = [
        ("Correct: 2035-06-15", ql.Date(15, 6, 2035)),
        ("Wrong: 1935-06-15", ql.Date(15, 6, 1935)),  # If 35 was interpreted as 1935
        ("Edge: 2025-06-15", ql.Date(15, 6, 2025)),   # Current year typo?
    ]
    
    settlement_date = ql.Date(18, 4, 2025)
    ql.Settings.instance().evaluationDate = settlement_date
    
    for date_name, maturity_date in dates_to_test:
        print(f"\n🧪 Testing: {date_name}")
        print(f"   📅 Maturity: {maturity_date}")
        
        try:
            if maturity_date <= settlement_date:
                print(f"   ⚠️  Maturity before settlement - bond would be expired")
                continue
                
            # Create bond with this maturity
            calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
            day_count = ql.Thirty360(ql.Thirty360.BondBasis)
            
            schedule = ql.Schedule(
                ql.Date(15, 6, 2015),  # Issue date
                maturity_date,
                ql.Period(6, ql.Months),
                calendar,
                ql.Unadjusted,
                ql.Unadjusted,
                ql.DateGeneration.Backward,
                False
            )
            
            bond = ql.FixedRateBond(
                0,
                1000000.0,
                schedule,
                [6.625 / 100.0],
                day_count
            )
            
            accrued = bond.accruedAmount(settlement_date)
            print(f"   💰 Accrued: ${accrued:,.4f} per $1M")
            
            # Check if this matches the validated_calculations value
            validated_target = 22451.39
            diff = abs(accrued - validated_target)
            
            if diff < 1.0:
                print(f"   ✅ MATCHES validated_calculations (${validated_target:,.2f})")
                print(f"   🎯 FOUND THE ISSUE! This is likely what happened.")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_business_convention_impact()
    test_date_interpretation_issue()
