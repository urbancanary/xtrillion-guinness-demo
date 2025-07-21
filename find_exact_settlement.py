#!/usr/bin/env python3
"""
Find the exact settlement date that gives 16.35 duration
"""

import QuantLib as ql
from datetime import datetime, timedelta

def find_exact_settlement_for_target_duration():
    print("🎯 Finding EXACT Settlement Date for 16.35 Duration")
    print("=" * 55)
    
    # Bond parameters (fixed)
    price = 71.66
    coupon_rate = 0.03  # 3%
    maturity_date = ql.Date(15, 8, 2052)
    target_duration = 16.35
    
    # Treasury conventions (fixed)
    day_count = ql.ActualActual(ql.ActualActual.ISDA)
    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    business_convention = ql.Following
    frequency = ql.Semiannual
    compounding_type = ql.Compounded
    settlement_days = 1
    
    print(f"Target Duration: {target_duration:.2f} years")
    print(f"Testing different settlement dates...")
    print()
    
    # Test different settlement dates
    base_date = datetime(2025, 7, 1)  # Start from July 1, 2025
    best_match = None
    best_diff = float('inf')
    
    for days_offset in range(-30, 31):  # Test ±30 days
        test_date = base_date + timedelta(days=days_offset)
        settlement_date = ql.Date(test_date.day, test_date.month, test_date.year)
        
        try:
            ql.Settings.instance().evaluationDate = settlement_date
            
            # Create bond
            schedule = ql.Schedule(
                settlement_date, maturity_date, ql.Period(frequency),
                calendar, business_convention, business_convention,
                ql.DateGeneration.Backward, False
            )
            
            coupons = [coupon_rate]
            fixed_rate_bond = ql.FixedRateBond(
                settlement_days, 100.0, schedule, coupons, day_count
            )
            
            # Calculate yield and duration
            bond_yield = fixed_rate_bond.bondYield(price, day_count, compounding_type, frequency)
            interest_rate = ql.InterestRate(bond_yield, day_count, compounding_type, frequency)
            duration = ql.BondFunctions.duration(fixed_rate_bond, interest_rate, ql.Duration.Modified)
            
            # Check if this is closer to target
            diff = abs(duration - target_duration)
            if diff < best_diff:
                best_diff = diff
                best_match = {
                    'settlement_date': settlement_date,
                    'duration': duration,
                    'yield': bond_yield * 100,
                    'difference': diff,
                    'date_str': test_date.strftime('%Y-%m-%d')
                }
            
            # Print if very close
            if diff < 0.05:
                print(f"📅 {test_date.strftime('%Y-%m-%d')}: Duration {duration:.4f}, Diff {diff:.4f}")
                
        except Exception as e:
            continue
    
    print()
    print("🏆 BEST MATCH FOUND:")
    if best_match:
        print(f"Settlement Date: {best_match['date_str']} ({best_match['settlement_date']})")
        print(f"Duration: {best_match['duration']:.6f} years")
        print(f"Yield: {best_match['yield']:.4f}%")
        print(f"Difference from Target: {best_match['difference']:.6f} years")
        
        if best_match['difference'] < 0.01:
            print("✅ SPOT-ON MATCH FOUND!")
        elif best_match['difference'] < 0.05:
            print("✅ VERY CLOSE MATCH!")
        else:
            print("⚠️ Close but not spot-on")
            
        return best_match
    else:
        print("❌ No good match found")
        return None

def test_bloomberg_settlement_dates():
    """Test common Bloomberg settlement conventions"""
    print("\n" + "=" * 55)
    print("🔍 Testing Common Bloomberg Settlement Dates")
    print("=" * 55)
    
    # Common Bloomberg settlement dates
    test_dates = [
        '2025-07-18',  # Recent business day
        '2025-07-17',  # Previous business day  
        '2025-07-21',  # Monday
        '2025-07-31',  # Month end
        '2025-06-30',  # Previous month end
        '2025-08-01',  # Next month start
    ]
    
    for date_str in test_dates:
        test_date = datetime.strptime(date_str, '%Y-%m-%d')
        settlement_date = ql.Date(test_date.day, test_date.month, test_date.year)
        
        try:
            ql.Settings.instance().evaluationDate = settlement_date
            
            # Standard Treasury setup
            maturity_date = ql.Date(15, 8, 2052)
            day_count = ql.ActualActual(ql.ActualActual.ISDA)
            calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
            business_convention = ql.Following
            frequency = ql.Semiannual
            compounding_type = ql.Compounded
            settlement_days = 1
            
            schedule = ql.Schedule(
                settlement_date, maturity_date, ql.Period(frequency),
                calendar, business_convention, business_convention,
                ql.DateGeneration.Backward, False
            )
            
            fixed_rate_bond = ql.FixedRateBond(
                settlement_days, 100.0, schedule, [0.03], day_count
            )
            
            bond_yield = fixed_rate_bond.bondYield(71.66, day_count, compounding_type, frequency)
            interest_rate = ql.InterestRate(bond_yield, day_count, compounding_type, frequency)
            duration = ql.BondFunctions.duration(fixed_rate_bond, interest_rate, ql.Duration.Modified)
            
            diff = abs(duration - 16.35)
            status = "✅" if diff < 0.01 else "⚠️" if diff < 0.05 else "❌"
            
            print(f"{status} {date_str}: Duration {duration:.4f}, Yield {bond_yield*100:.4f}%, Diff {diff:.4f}")
            
        except Exception as e:
            print(f"❌ {date_str}: Error - {e}")

if __name__ == "__main__":
    result = find_exact_settlement_for_target_duration()
    test_bloomberg_settlement_dates()
    
    if result and result['difference'] < 0.01:
        print(f"\n🎉 SOLUTION: Use settlement date {result['date_str']} for spot-on accuracy!")
    else:
        print(f"\n🤔 The 16.35 target may use different parameters (curve, pricing date, etc.)")
