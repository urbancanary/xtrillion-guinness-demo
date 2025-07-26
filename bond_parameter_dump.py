#!/usr/bin/env python3
"""
Bond Parameter Dump Test
========================

Dump exact bond parameters being used in your implementation
"""

import QuantLib as ql
import sys
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

def test_exact_parameters():
    """Test with exact parameters from your implementation logs"""
    
    print("🔍 EXACT PARAMETER REPRODUCTION TEST")
    print("=" * 80)
    
    # Set evaluation date
    calculation_date = ql.Date(30, 6, 2025)
    ql.Settings.instance().evaluationDate = calculation_date
    print(f"📅 Evaluation Date: {calculation_date}")
    
    # Exact parameters from your logs
    maturity_date = ql.Date(15, 8, 2052)  # From logs: "Maturity: 2052-08-15"
    coupon_rate = 0.03  # From logs: "Coupon: 3.0"
    clean_price = 71.66  # From logs: "price 71.66"
    settlement_days = 0  # From logs: "SettlementDays: 0"
    
    print(f"📊 Bond Parameters:")
    print(f"   Maturity: {maturity_date}")
    print(f"   Coupon: {coupon_rate*100}%")
    print(f"   Clean Price: {clean_price}")
    print(f"   Settlement Days: {settlement_days}")
    
    # Test different approaches
    approaches = [
        {
            "name": "Exact Your Implementation",
            "issue_date": calculation_date,  # From logs: "Issue: 30-Jun-2025"
            "day_count": ql.ActualActual(ql.ActualActual.ISDA),  # From logs: "ActualActual_Bond"
            "calendar": ql.UnitedStates(ql.UnitedStates.GovernmentBond),
            "frequency": ql.Semiannual
        },
        {
            "name": "Alternative: Issue = Settlement",
            "issue_date": calculation_date,
            "day_count": ql.ActualActual(ql.ActualActual.ISDA),
            "calendar": ql.UnitedStates(ql.UnitedStates.GovernmentBond),
            "frequency": ql.Semiannual
        },
        {
            "name": "Alternative: Different Day Count",
            "issue_date": calculation_date,
            "day_count": ql.ActualActual(ql.ActualActual.Bond),  # Different variant
            "calendar": ql.UnitedStates(ql.UnitedStates.GovernmentBond),
            "frequency": ql.Semiannual
        }
    ]
    
    for approach in approaches:
        print(f"\n" + "="*60)
        print(f"🧪 TESTING: {approach['name']}")
        print("="*60)
        
        try:
            # Create schedule
            schedule = ql.Schedule(
                approach['issue_date'],
                maturity_date,
                ql.Period(approach['frequency']),
                approach['calendar'],
                ql.Following,
                ql.Following,
                ql.DateGeneration.Backward,
                False
            )
            
            # Create bond
            bond = ql.FixedRateBond(
                settlement_days,
                100.0,  # Face value
                schedule,
                [coupon_rate],
                approach['day_count']
            )
            
            # Calculate yield (no pricing engine)
            bond_yield = bond.bondYield(
                clean_price, 
                approach['day_count'], 
                ql.Compounded, 
                approach['frequency']
            )
            
            # Calculate duration
            duration = ql.BondFunctions.duration(
                bond, 
                bond_yield, 
                approach['day_count'], 
                ql.Compounded, 
                approach['frequency'], 
                ql.Duration.Modified
            )
            
            print(f"✅ Results:")
            print(f"   Yield: {bond_yield*100:.6f}%")
            print(f"   Duration: {duration:.6f}")
            print(f"   First payment: {schedule[0]}")
            print(f"   Last payment: {schedule[-1]}")
            print(f"   Total payments: {len(schedule)}")
            
            # Check if this matches your implementation
            your_yield = 4.935783
            your_duration = 10.737312
            
            yield_diff = abs(bond_yield*100 - your_yield)
            duration_diff = abs(duration - your_duration)
            
            print(f"   Yield vs yours: {yield_diff:.6f}% diff")
            print(f"   Duration vs yours: {duration_diff:.6f} diff")
            
            if yield_diff < 0.001:
                print("   🎯 YIELD MATCH! This might be the issue!")
                
            if duration_diff < 0.001:
                print("   🎯 DURATION MATCH! This might be the issue!")
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
    
    print(f"\n" + "="*80)
    print("🔍 DEBUGGING SUMMARY")
    print("="*80)
    print("Your Implementation Results:")
    print("   Yield: 4.935783%")
    print("   Duration: 10.737312")
    print("Expected Results:")
    print("   Yield: 4.899718%") 
    print("   Duration: 16.600282")
    print("\nLook for which test case matches your implementation!")

if __name__ == "__main__":
    test_exact_parameters()
