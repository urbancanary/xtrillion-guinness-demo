#!/usr/bin/env python3
"""
🔍 BLOOMBERG ACCURACY DIAGNOSTIC
===============================

Diagnoses why there's a huge discrepancy between calculated values 
and Bloomberg baseline data.

Checks:
1. Settlement date consistency
2. Bond specification accuracy  
3. Bloomberg data validity
4. Calculation parameter debugging
"""

import sys
import os
sys.path.insert(0, "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10")

from bond_master_hierarchy import calculate_bond_master
from datetime import datetime

# Test a few key bonds to diagnose the issue
TEST_BONDS = [
    {
        "isin": "US912810TJ79", 
        "px_mid": 71.66, 
        "name": "T 3 15/08/52",
        "bb_yield": 4.898453,
        "bb_duration": 16.357839,
        "description": "US Treasury - Should be most accurate"
    },
    {
        "isin": "XS2249741674", 
        "px_mid": 77.88, 
        "name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040",
        "bb_yield": 5.637570,
        "bb_duration": 10.097620,
        "description": "Corporate bond - Large discrepancy"
    },
    {
        "isin": "USP3143NAH72", 
        "px_mid": 101.63, 
        "name": "CODELCO INC, 6.15%, 24-Oct-2036",
        "bb_yield": 5.949058,
        "bb_duration": 8.024166,
        "description": "Corporate bond - Check conventions"
    }
]

def diagnose_bond_calculation(bond_data):
    """Diagnose a single bond calculation"""
    print(f"\n🔍 DIAGNOSING: {bond_data['description']}")
    print(f"   ISIN: {bond_data['isin']}")
    print(f"   Name: {bond_data['name']}")
    print(f"   Price: ${bond_data['px_mid']}")
    print("   " + "="*60)
    
    # Test calculation with 2025-06-30 settlement
    try:
        result = calculate_bond_master(
            isin=bond_data["isin"],
            description=bond_data["name"],
            price=bond_data["px_mid"],
            settlement_date='2025-06-30'
        )
        
        if result.get("success"):
            calc_yield = result.get("yield")
            calc_duration = result.get("duration")
            
            print(f"   ✅ CALCULATION SUCCESS")
            # Fix display bug: calc_yield is decimal, convert to percentage for display
            calc_yield_pct = calc_yield * 100 if calc_yield < 1 else calc_yield
            print(f"      📊 Calculated Yield:     {calc_yield_pct:.6f}%")
            print(f"      📊 Bloomberg Yield:      {bond_data['bb_yield']:.6f}%")
            
            if calc_yield:
                # Fix calculation: both should be in same units for comparison
                calc_yield_for_diff = calc_yield * 100 if calc_yield < 1 else calc_yield
                yield_diff_bps = abs(calc_yield_for_diff - bond_data['bb_yield']) * 100
                print(f"      📊 Yield Difference:     {yield_diff_bps:.3f} bps")
                
                if yield_diff_bps < 5:
                    print(f"      🎯 YIELD ASSESSMENT:     EXCELLENT")
                elif yield_diff_bps < 25:
                    print(f"      ✅ YIELD ASSESSMENT:     GOOD")
                elif yield_diff_bps < 100:
                    print(f"      ⚠️ YIELD ASSESSMENT:     FAIR")
                else:
                    print(f"      ❌ YIELD ASSESSMENT:     POOR")
            
            print(f"      📊 Calculated Duration:  {calc_duration:.6f} years")
            print(f"      📊 Bloomberg Duration:   {bond_data['bb_duration']:.6f} years")
            
            if calc_duration:
                duration_diff = abs(calc_duration - bond_data['bb_duration'])
                print(f"      📊 Duration Difference:  {duration_diff:.6f} years")
                
                if duration_diff < 0.05:
                    print(f"      🎯 DURATION ASSESSMENT:  EXCELLENT")
                elif duration_diff < 0.2:
                    print(f"      ✅ DURATION ASSESSMENT:  GOOD")
                elif duration_diff < 1.0:
                    print(f"      ⚠️ DURATION ASSESSMENT:  FAIR")
                else:
                    print(f"      ❌ DURATION ASSESSMENT:  POOR")
            
            # Show calculation details
            conventions = result.get("conventions", {})
            print(f"      🔧 CALCULATION DETAILS:")
            print(f"         Settlement Date: {conventions.get('settlement_date', 'N/A')}")
            print(f"         Day Count: {conventions.get('day_count_convention', 'N/A')}")
            print(f"         Payment Freq: {conventions.get('payment_frequency', 'N/A')}")
            print(f"         Bond Type: {conventions.get('bond_type', 'N/A')}")
            
        else:
            print(f"   ❌ CALCULATION FAILED: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   🚨 EXCEPTION: {str(e)}")

def check_bloomberg_data_consistency():
    """Check if Bloomberg data is internally consistent"""
    print(f"\n📊 BLOOMBERG DATA CONSISTENCY CHECK")
    print("="*70)
    
    treasury_yield = 4.898453  # From Bloomberg baseline
    
    print(f"   📈 Treasury Baseline Yield: {treasury_yield:.6f}%")
    print(f"   📅 Settlement Date: 2025-06-30")
    print(f"   🏛️ Bond: US Treasury 3% 08/15/2052")
    
    # Check if this makes sense for a 3% coupon treasury at $71.66 price
    expected_yield_range = (4.5, 5.5)  # Rough estimate
    
    if expected_yield_range[0] <= treasury_yield <= expected_yield_range[1]:
        print(f"   ✅ Treasury yield within expected range {expected_yield_range}")
    else:
        print(f"   ⚠️ Treasury yield outside expected range {expected_yield_range}")
    
    print(f"\n   💡 ANALYSIS:")
    print(f"      • 3% coupon bond trading at $71.66 (71.66% of par)")
    print(f"      • This is a significant discount to par")
    print(f"      • Expected YTM should be > 3% coupon rate")
    print(f"      • Bloomberg YTM of {treasury_yield:.3f}% seems reasonable")

def main():
    """Main diagnostic function"""
    print("🔍 BLOOMBERG ACCURACY DIAGNOSTIC")
    print("=" * 70)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Purpose: Diagnose why Bloomberg comparison is failing")
    print(f"📁 Project: /Users/andyseaman/Notebooks/json_receiver_project/google_analysis10")
    
    # Check Bloomberg data consistency first
    check_bloomberg_data_consistency()
    
    # Test individual bonds
    for bond_data in TEST_BONDS:
        diagnose_bond_calculation(bond_data)
    
    print(f"\n🎯 DIAGNOSTIC SUMMARY")
    print("="*70)
    print(f"📊 Key Questions to Answer:")
    print(f"   1. Are the Bloomberg baseline yields reasonable?")
    print(f"   2. Is the settlement date correct (2025-06-30)?")
    print(f"   3. Are bond specifications (coupon, maturity) accurate?")
    print(f"   4. Are calculation conventions (day count, frequency) right?")
    print(f"   5. Is there a systematic bias in calculations?")
    
    print(f"\n💡 Next Steps Based on Results:")
    print(f"   • If Treasury is close: Basic setup is correct")
    print(f"   • If corporates are far: Convention/specification issues")
    print(f"   • If all are far: Settlement date or systematic error")
    print(f"   • Check Bloomberg data source and date")

if __name__ == "__main__":
    main()
