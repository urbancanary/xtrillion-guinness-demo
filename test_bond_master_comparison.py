#!/usr/bin/env python3
"""
🎯 Bond Master Calculation Comparison - ISIN vs No-ISIN Routes
==============================================================

Test calculate_bond_master with your specific bond:
- ISIN: US912810TJ79  
- PX_MID: 71.66
- Name: T 3 15/08/52

Both with and without ISIN to spot discrepancies.
"""

import sys
import os
import pandas as pd
import json
from datetime import datetime
from typing import Dict, Any
import logging

# Setup paths
project_root = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10'
sys.path.append(project_root)
os.chdir(project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Import the master function
try:
    from bond_master_hierarchy import calculate_bond_master
    print("✅ Successfully imported calculate_bond_master")
except ImportError as e:
    print(f"❌ Failed to import calculate_bond_master: {e}")
    sys.exit(1)

def test_bond_both_routes():
    """
    Test the specific bond both with and without ISIN
    
    Bond Details:
    - ISIN: US912810TJ79
    - PX_MID: 71.66  
    - Name: T 3 15/08/52
    """
    
    print("🧪 COMPREHENSIVE BOND MASTER COMPARISON")
    print("=" * 60)
    print(f"🕒 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test bond details
    test_isin = "US912810TJ79"
    test_price = 71.66
    test_description = "T 3 15/08/52"
    
    print(f"🎯 Test Bond Details:")
    print(f"   ISIN: {test_isin}")
    print(f"   Price: {test_price}")
    print(f"   Description: '{test_description}'")
    print()
    
    # Test 1: WITH ISIN (Route 1: ISIN Hierarchy)
    print("📍 Test 1: WITH ISIN - Route 1: ISIN Hierarchy")
    print("-" * 50)
    
    try:
        result_with_isin = calculate_bond_master(
            isin=test_isin,
            description=test_description,
            price=test_price
        )
        
        print(f"✅ Route: {result_with_isin.get('route_used', 'Unknown')}")
        print(f"✅ Success: {result_with_isin.get('success', False)}")
        
        if result_with_isin.get('success'):
            print(f"✅ Yield: {result_with_isin.get('yield', 0):.6f}%")
            print(f"✅ Duration: {result_with_isin.get('duration', 0):.6f}")
            print(f"✅ ISIN Used: {result_with_isin.get('isin', 'None')}")
        else:
            print(f"❌ Error: {result_with_isin.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        result_with_isin = {'success': False, 'error': str(e), 'route_used': 'failed'}
    
    print()
    
    # Test 2: WITHOUT ISIN (Route 2: Parse Hierarchy)
    print("📖 Test 2: WITHOUT ISIN - Route 2: Parse Hierarchy")
    print("-" * 50)
    
    try:
        result_without_isin = calculate_bond_master(
            isin=None,  # No ISIN - force parse hierarchy
            description=test_description,
            price=test_price
        )
        
        print(f"✅ Route: {result_without_isin.get('route_used', 'Unknown')}")
        print(f"✅ Success: {result_without_isin.get('success', False)}")
        
        if result_without_isin.get('success'):
            print(f"✅ Yield: {result_without_isin.get('yield', 0):.6f}%")
            print(f"✅ Duration: {result_without_isin.get('duration', 0):.6f}")
            print(f"✅ ISIN Detected: {result_without_isin.get('isin', 'None')}")
        else:
            print(f"❌ Error: {result_without_isin.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        result_without_isin = {'success': False, 'error': str(e), 'route_used': 'failed'}
    
    print()
    
    # Generate comprehensive comparison table
    generate_comparison_table(result_with_isin, result_without_isin)
    
    # Generate detailed analysis
    generate_detailed_analysis(result_with_isin, result_without_isin)
    
    return result_with_isin, result_without_isin

def generate_comparison_table(with_isin: Dict[str, Any], without_isin: Dict[str, Any]):
    """Generate a detailed side-by-side comparison table"""
    
    print("📊 DETAILED SIDE-BY-SIDE COMPARISON TABLE")
    print("=" * 80)
    
    # Extract all unique keys from both results
    all_keys = set(with_isin.keys()) | set(without_isin.keys())
    
    # Define key ordering for better readability
    priority_keys = [
        'success', 'route_used', 'isin_provided', 'isin', 'description', 
        'price', 'yield', 'duration', 'spread', 'accrued_interest',
        'calculation_method', 'settlement_date', 'conventions', 'error'
    ]
    
    # Sort keys: priority first, then alphabetical
    sorted_keys = []
    for key in priority_keys:
        if key in all_keys:
            sorted_keys.append(key)
            all_keys.remove(key)
    sorted_keys.extend(sorted(all_keys))
    
    # Print table header
    print(f"{'Field':<25} | {'WITH ISIN (Route 1)':<30} | {'WITHOUT ISIN (Route 2)':<30} | {'Match':<8}")
    print("-" * 100)
    
    # Print each field comparison
    for key in sorted_keys:
        val1 = with_isin.get(key, 'N/A')
        val2 = without_isin.get(key, 'N/A')
        
        # Format values for display
        val1_str = format_value_for_display(val1)
        val2_str = format_value_for_display(val2)
        
        # Check if values match
        match_status = check_values_match(val1, val2)
        match_symbol = "✅" if match_status else "❌" if val1 != 'N/A' and val2 != 'N/A' else "⚠️"
        
        print(f"{key:<25} | {val1_str:<30} | {val2_str:<30} | {match_symbol:<8}")
    
    print()

def format_value_for_display(value) -> str:
    """Format a value for nice display in the table"""
    if value is None:
        return "None"
    elif isinstance(value, bool):
        return str(value)
    elif isinstance(value, (int, float)):
        if isinstance(value, float) and abs(value) > 0.001:
            return f"{value:.6f}"
        else:
            return str(value)
    elif isinstance(value, dict):
        return f"Dict({len(value)} items)"
    elif isinstance(value, list):
        return f"List({len(value)} items)"
    elif isinstance(value, str):
        return value[:28] + "..." if len(value) > 28 else value
    else:
        return str(value)[:28]

def check_values_match(val1, val2) -> bool:
    """Check if two values are considered matching"""
    if val1 == val2:
        return True
    
    # Special handling for floats - allow small differences
    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
        try:
            diff = abs(float(val1) - float(val2))
            return diff < 1e-10  # Very small tolerance for floating point
        except:
            return False
    
    return False

def generate_detailed_analysis(with_isin: Dict[str, Any], without_isin: Dict[str, Any]):
    """Generate detailed analysis of the comparison"""
    
    print("🔍 DETAILED ANALYSIS")
    print("=" * 50)
    
    # Check if both routes succeeded
    both_success = with_isin.get('success', False) and without_isin.get('success', False)
    
    if both_success:
        print("✅ BOTH ROUTES SUCCESSFUL")
        
        # Compare key financial metrics
        print("\n📈 Financial Metrics Comparison:")
        
        # Yield comparison
        yield1 = with_isin.get('yield')
        yield2 = without_isin.get('yield')
        if yield1 is not None and yield2 is not None:
            yield_diff = abs(yield1 - yield2)
            yield_diff_bps = yield_diff * 100
            print(f"   Yield WITH ISIN:    {yield1:.6f}%")
            print(f"   Yield WITHOUT ISIN: {yield2:.6f}%")
            print(f"   Difference:         {yield_diff:.6f}% ({yield_diff_bps:.2f} bps)")
            
            if yield_diff_bps < 1:
                print("   ✅ Yields are virtually identical (<1 bp difference)")
            elif yield_diff_bps < 10:
                print("   ⚠️ Small yield difference (1-10 bps)")
            else:
                print("   ❌ Significant yield difference (>10 bps)")
        
        # Duration comparison
        dur1 = with_isin.get('duration')
        dur2 = without_isin.get('duration')
        if dur1 is not None and dur2 is not None:
            dur_diff = abs(dur1 - dur2)
            print(f"\n   Duration WITH ISIN:    {dur1:.6f}")
            print(f"   Duration WITHOUT ISIN: {dur2:.6f}")
            print(f"   Difference:            {dur_diff:.6f}")
            
            if dur_diff < 0.01:
                print("   ✅ Durations are virtually identical")
            elif dur_diff < 0.1:
                print("   ⚠️ Small duration difference")
            else:
                print("   ❌ Significant duration difference")
        
        # ISIN detection comparison
        isin1 = with_isin.get('isin')
        isin2 = without_isin.get('isin')
        print(f"\n🆔 ISIN Handling:")
        print(f"   WITH ISIN route:    {isin1}")
        print(f"   WITHOUT ISIN route: {isin2}")
        
        if isin1 == isin2:
            print("   ✅ Both routes use same ISIN")
        else:
            print("   ⚠️ Routes use different ISINs")
        
        # Route information
        route1 = with_isin.get('route_used')
        route2 = without_isin.get('route_used')
        print(f"\n🛣️ Route Information:")
        print(f"   Route 1: {route1}")
        print(f"   Route 2: {route2}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if yield_diff_bps < 1 and dur_diff < 0.01:
            print("   ✅ EXCELLENT: Both routes produce virtually identical results")
            print("   ✅ The dual hierarchy system is working correctly")
        elif yield_diff_bps < 10 and dur_diff < 0.1:
            print("   ⚠️ GOOD: Routes produce similar results with minor differences")
            print("   ⚠️ Consider investigating small discrepancies")
        else:
            print("   ❌ CONCERNING: Routes produce significantly different results")
            print("   ❌ Investigation required - possible calculation divergence")
    
    elif with_isin.get('success') and not without_isin.get('success'):
        print("⚠️ ROUTE 1 SUCCESS, ROUTE 2 FAILED")
        print(f"   Route 1 (WITH ISIN): ✅ Success")
        print(f"   Route 2 (WITHOUT ISIN): ❌ {without_isin.get('error', 'Failed')}")
        print("   🔍 Investigation needed: Parse hierarchy may have issues")
        
    elif not with_isin.get('success') and without_isin.get('success'):
        print("⚠️ ROUTE 2 SUCCESS, ROUTE 1 FAILED")
        print(f"   Route 1 (WITH ISIN): ❌ {with_isin.get('error', 'Failed')}")
        print(f"   Route 2 (WITHOUT ISIN): ✅ Success")
        print("   🔍 Investigation needed: ISIN hierarchy may have issues")
        
    else:
        print("❌ BOTH ROUTES FAILED")
        print(f"   Route 1 Error: {with_isin.get('error', 'Unknown')}")
        print(f"   Route 2 Error: {without_isin.get('error', 'Unknown')}")
        print("   🚨 Critical issue: Both calculation routes are broken")

def save_results_to_file(with_isin: Dict[str, Any], without_isin: Dict[str, Any]):
    """Save detailed results to JSON file for further analysis"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"bond_master_comparison_{timestamp}.json"
    
    comparison_data = {
        'test_info': {
            'timestamp': datetime.now().isoformat(),
            'test_bond': {
                'isin': 'US912810TJ79',
                'price': 71.66,
                'description': 'T 3 15/08/52'
            }
        },
        'results': {
            'with_isin': with_isin,
            'without_isin': without_isin
        }
    }
    
    try:
        with open(filename, 'w') as f:
            json.dump(comparison_data, f, indent=2, default=str)
        print(f"\n💾 Results saved to: {filename}")
    except Exception as e:
        print(f"\n❌ Failed to save results: {e}")

def main():
    """Main execution function"""
    
    print("🚀 Starting Bond Master Comparison Test")
    print()
    
    # Run the comprehensive test
    result_with, result_without = test_bond_both_routes()
    
    # Save results for further analysis
    save_results_to_file(result_with, result_without)
    
    print("\n🎉 Bond Master Comparison Test Complete!")
    print("\n💡 Next Steps:")
    print("   1. Review the detailed comparison table above")
    print("   2. Check for any significant discrepancies") 
    print("   3. If discrepancies found, investigate the specific route")
    print("   4. Use saved JSON file for further analysis if needed")

if __name__ == "__main__":
    main()
