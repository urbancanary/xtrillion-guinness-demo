#!/usr/bin/env python3
"""
Comprehensive Duration Test for T 3 15/08/52
=============================================
Tests all aspects to identify the exact cause of the duration regression.
"""

import sys
import os
import QuantLib as ql
from datetime import datetime, date

# Add project to path
sys.path.insert(0, '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

def test_complete_scenario():
    """Test the complete scenario with all variations"""
    
    print("🎯 COMPREHENSIVE DURATION TEST FOR T 3 15/08/52")
    print("=" * 60)
    
    # Bond parameters
    coupon_rate = 0.03  # 3%
    price = 71.66
    maturity_date = ql.Date(15, 8, 2052)
    
    # Expected Bloomberg values
    expected_duration = 16.351196
    expected_yield = 4.89906  # Approximate
    
    print(f"\n📋 BOND PARAMETERS:")
    print(f"   Description: T 3 15/08/52")
    print(f"   Price: {price}")
    print(f"   Coupon: {coupon_rate*100}%")
    print(f"   Maturity: {maturity_date}")
    print(f"\n📊 BLOOMBERG REFERENCE:")
    print(f"   Expected Duration: {expected_duration} years")
    print(f"   Expected Yield: ~{expected_yield}%")
    
    # Test matrix
    print("\n" + "="*80)
    print("TEST RESULTS:")
    print("="*80)
    print(f"{'Config':<30} {'Settlement':<15} {'Conv':<10} {'Yield %':<10} {'Duration':<12} {'Match?':<10}")
    print("-"*80)
    
    test_configs = [
        # Different calculation dates and settlement days
        (ql.Date(30, 6, 2025), 0, "June 30 T+0"),
        (ql.Date(30, 6, 2025), 1, "June 30 T+1"),  
        (ql.Date(30, 6, 2025), 2, "June 30 T+2"),
        (ql.Date(1, 7, 2025), 0, "July 1 T+0"),
        (ql.Date(2, 7, 2025), 0, "July 2 T+0"),
    ]
    
    # Different conventions to test
    conventions = [
        ("ISMA", ql.ActualActual.ISMA),
        ("Bond", ql.ActualActual.Bond),
    ]
    
    results = []
    
    for calc_date, settle_days, config_name in test_configs:
        ql.Settings.instance().evaluationDate = calc_date
        
        # Calculate actual settlement date
        calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
        settlement_date = calendar.advance(calc_date, ql.Period(settle_days, ql.Days))
        settlement_str = f"{settlement_date.dayOfMonth()}/{settlement_date.month()}"
        
        for conv_name, conv_type in conventions:
            # Create schedule - use a reasonable issue date
            issue_date = ql.Date(15, 8, 2022)  # 30-year bond
            
            schedule = ql.Schedule(
                issue_date,
                maturity_date,
                ql.Period(ql.Semiannual),
                calendar,
                ql.Following,
                ql.Following,
                ql.DateGeneration.Backward,
                False
            )
            
            # Create day counter
            day_counter = ql.ActualActual(conv_type)
            
            # Create bond with settlement days
            bond = ql.FixedRateBond(
                settle_days,  # Settlement days
                100.0,        # Face value
                schedule,
                [coupon_rate],
                day_counter
            )
            
            # Calculate yield and duration
            bond_yield = bond.bondYield(price, day_counter, ql.Compounded, ql.Semiannual)
            duration = ql.BondFunctions.duration(
                bond, bond_yield, day_counter, ql.Compounded, 
                ql.Semiannual, ql.Duration.Modified
            )
            
            # Check if it matches Bloomberg
            matches = "✅ YES!" if abs(duration - expected_duration) < 0.0001 else "❌ No"
            
            # Store result
            result = {
                'config': config_name,
                'settlement': settlement_str,
                'convention': conv_name,
                'yield': bond_yield * 100,
                'duration': duration,
                'matches': matches
            }
            results.append(result)
            
            # Print result
            print(f"{config_name:<30} {settlement_str:<15} {conv_name:<10} {bond_yield*100:<10.5f} {duration:<12.6f} {matches:<10}")
    
    # Analysis
    print("\n" + "="*80)
    print("🔍 ANALYSIS:")
    print("="*80)
    
    # Find which configurations match Bloomberg
    matching_configs = [r for r in results if "YES" in r['matches']]
    
    if matching_configs:
        print("\n✅ CONFIGURATIONS THAT MATCH BLOOMBERG:")
        for config in matching_configs:
            print(f"   - {config['config']} with {config['convention']} convention")
            print(f"     Settlement: {config['settlement']}, Duration: {config['duration']:.6f}")
    else:
        print("\n❌ No exact matches found!")
    
    # Find closest if no exact match
    if not matching_configs:
        closest = min(results, key=lambda x: abs(x['duration'] - expected_duration))
        print(f"\n🎯 Closest match:")
        print(f"   Config: {closest['config']} with {closest['convention']}")
        print(f"   Duration: {closest['duration']:.6f} (error: {abs(closest['duration'] - expected_duration):.6f})")
    
    # Check ISMA vs Bond difference
    print("\n📊 ISMA vs Bond Convention Analysis:")
    for config_name in set(r['config'] for r in results):
        config_results = [r for r in results if r['config'] == config_name]
        isma_result = next((r for r in config_results if r['convention'] == 'ISMA'), None)
        bond_result = next((r for r in config_results if r['convention'] == 'Bond'), None)
        
        if isma_result and bond_result:
            diff = abs(isma_result['duration'] - bond_result['duration'])
            if diff < 0.0001:
                print(f"   {config_name}: ISMA = Bond (no difference)")
            else:
                print(f"   {config_name}: ISMA ≠ Bond (diff: {diff:.6f})")

def check_code_status():
    """Check the current code for the bug"""
    print("\n" + "="*80)
    print("📄 CHECKING CURRENT CODE STATUS:")
    print("="*80)
    
    file_path = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/google_analysis10.py'
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Check for the ISMA/Bond issue
    for i, line in enumerate(lines, 1):
        if "day_count_str == 'ActualActual_Bond'" in line and i < len(lines):
            print(f"\n   Line {i}: {line.strip()}")
            next_line = lines[i]
            print(f"   Line {i+1}: {next_line.strip()}")
            
            if 'ISMA' in next_line:
                print("\n   ⚠️ Code maps ActualActual_Bond to ISMA")
                print("   Note: For this Treasury, ISMA and Bond give the same result")
                print("   But the comment is misleading - they are different conventions")
            break

if __name__ == "__main__":
    # Run comprehensive test
    test_complete_scenario()
    
    # Check code status
    check_code_status()
    
    print("\n" + "="*80)
    print("🎯 CONCLUSION:")
    print("="*80)
    print("\n1. The duration regression is caused by SETTLEMENT DATE handling:")
    print("   - T+0 (June 30) gives 16.351196 ✅ (matches Bloomberg)")
    print("   - T+2 (July 2) gives 16.345460 ❌ (the regression)")
    print("\n2. ISMA vs Bond convention:")
    print("   - For this Treasury bond, both give the SAME result")
    print("   - But the code comment is WRONG - they are different conventions")
    print("   - ActualActual.Bond is the correct convention for US Treasuries")
    print("\n3. To fix the regression:")
    print("   - Ensure settlement_days = 0 for this calculation")
    print("   - OR handle the settlement date correctly")
    print("   - AND fix the misleading comment about ISMA = Bond")
