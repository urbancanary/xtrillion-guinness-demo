#!/usr/bin/env python3
"""
Bond Master Calculation Test
===========================

Tests both ISIN-based and description-based calculations side by side
to verify semi-annual duration consistency and accuracy.
"""

import sys
import json
from datetime import datetime
import logging

# Add path for google_analysis10 module
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

from google_analysis10 import process_bond_portfolio

# Set up logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise for cleaner output

def create_test_portfolio():
    """Create test portfolio with both ISIN and description versions"""
    
    bonds = [
        {
            "name": "🏛️ US Treasury 3% 2052",
            "isin": "US912810TJ79",
            "description": "US TREASURY N/B, 3%, 15-Aug-2052",
            "price": 71.66,
            "bloomberg_yield": 4.89960,
            "bloomberg_duration": 16.35658,
            "bloomberg_convexity": 370.22
        },
        {
            "name": "🌎 Panama 3.87% 2060", 
            "isin": "US698299BL70",
            "description": "PANAMA, 3.87%, 23-Jul-2060",
            "price": 56.60,
            "bloomberg_yield": 7.36000,
            "bloomberg_duration": 13.57604,
            "bloomberg_convexity": 245.89
        },
        {
            "name": "🛢️ Ecopetrol 5.875% 2045",
            "isin": "US279158AJ82", 
            "description": "ECOPETROL SA, 5.875%, 28-May-2045",
            "price": 69.31,
            "bloomberg_yield": 9.28000,
            "bloomberg_duration": 9.80447,
            "bloomberg_convexity": 123.45
        },
        {
            "name": "🏗️ Galaxy Pipeline 3.25% 2040",
            "isin": "XS2249741674",
            "description": "GALAXY PIPELINE, 3.25%, 30-Sep-2040", 
            "price": 77.88,
            "bloomberg_yield": 5.64000,
            "bloomberg_duration": 11.22303,
            "bloomberg_convexity": 156.78
        },
        {
            "name": "🇸🇦 Saudi Aramco 4.25% 2039",
            "isin": "XS1982113463",
            "description": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039",
            "price": 87.14,
            "bloomberg_yield": 5.60000,
            "bloomberg_duration": 9.93052,
            "bloomberg_convexity": 134.56
        }
    ]
    
    return bonds

def run_calculations(bond, method_type, include_isin=True):
    """Run calculation for a bond with or without ISIN"""
    
    portfolio_data = {
        "data": [
            {
                "isin": bond["isin"] if include_isin else "",
                "description": bond["description"],
                "price": bond["price"],
                "weighting": 1.0
            }
        ]
    }
    
    try:
        results = process_bond_portfolio(
            portfolio_data,
            db_path="/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/portfolio_database.db",
            validated_db_path="/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bloomberg_index.db",
            bloomberg_db_path="/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bloomberg_index.db",
            settlement_date="2025-06-30"
        )
        
        if results and len(results) > 0:
            result = results[0]
            return {
                "method": method_type,
                "success": True,
                "yield": result.get('yield', None),
                "duration": result.get('duration', None),
                "convexity": result.get('convexity', None),
                "isin": result.get('isin', 'N/A'),
                "conventions": result.get('conventions', {}),
                "settlement_date": result.get('settlement_date_str', 'N/A')
            }
        else:
            return {
                "method": method_type,
                "success": False,
                "error": "No results returned"
            }
            
    except Exception as e:
        return {
            "method": method_type,
            "success": False,
            "error": str(e)
        }

def format_number(value, decimals=6):
    """Format number with specified decimals or return N/A"""
    if value is None:
        return "N/A"
    if isinstance(value, (int, float)):
        return f"{value:.{decimals}f}"
    return str(value)

def calculate_difference(actual, expected):
    """Calculate difference and status"""
    if actual is None or expected is None:
        return "N/A", "❌"
    
    diff = abs(actual - expected)
    
    # Status based on difference thresholds
    if diff < 0.01:
        status = "✅"
    elif diff < 0.05:
        status = "🟡"
    else:
        status = "❌"
        
    return f"{diff:.4f}", status

def print_comparison_table(bonds, results_with_isin, results_without_isin):
    """Print detailed comparison table"""
    
    print("🔬 BOND MASTER CALCULATION RESULTS - ISIN vs NON-ISIN COMPARISON")
    print("=" * 120)
    print(f"📅 Settlement Date: 2025-06-30")
    print(f"🎯 Testing semi-annual duration consistency for US Treasuries")
    print("=" * 120)
    print()
    
    # Header
    header = "Bond".ljust(25) + "Method".ljust(15) + "Yield (%)".ljust(12) + "Duration".ljust(12) + "Convexity".ljust(12) + "vs Bloomberg".ljust(15) + "Status".ljust(8)
    print(header)
    print("-" * 120)
    
    for i, bond in enumerate(bonds):
        bond_name = bond["name"][:24]
        
        # Results with ISIN
        result_isin = results_with_isin[i]
        # Results without ISIN  
        result_no_isin = results_without_isin[i]
        
        # Bloomberg baseline
        bbg_yield = bond["bloomberg_yield"]
        bbg_duration = bond["bloomberg_duration"] 
        bbg_convexity = bond["bloomberg_convexity"]
        
        # Print ISIN method results
        if result_isin["success"]:
            yield_val = format_number(result_isin["yield"], 5)
            duration_val = format_number(result_isin["duration"], 5)
            convexity_val = format_number(result_isin["convexity"], 2)
            
            # Calculate vs Bloomberg
            if result_isin["yield"]:
                yield_diff, yield_status = calculate_difference(result_isin["yield"], bbg_yield)
                duration_diff, duration_status = calculate_difference(result_isin["duration"], bbg_duration)
                vs_bbg = f"Y:{yield_diff} D:{duration_diff}"
                status = yield_status if yield_status == duration_status else "🟡"
            else:
                vs_bbg = "N/A"
                status = "❌"
                
            print(f"{bond_name.ljust(25)}{'+ ISIN'.ljust(15)}{yield_val.ljust(12)}{duration_val.ljust(12)}{convexity_val.ljust(12)}{vs_bbg.ljust(15)}{status}")
        else:
            print(f"{bond_name.ljust(25)}{'+ ISIN'.ljust(15)}{'FAILED'.ljust(12)}{'FAILED'.ljust(12)}{'FAILED'.ljust(12)}{'ERROR'.ljust(15)}{'❌'}")
        
        # Print non-ISIN method results
        if result_no_isin["success"]:
            yield_val = format_number(result_no_isin["yield"], 5)
            duration_val = format_number(result_no_isin["duration"], 5)
            convexity_val = format_number(result_no_isin["convexity"], 2)
            
            # Calculate vs Bloomberg
            if result_no_isin["yield"]:
                yield_diff, yield_status = calculate_difference(result_no_isin["yield"], bbg_yield)
                duration_diff, duration_status = calculate_difference(result_no_isin["duration"], bbg_duration)
                vs_bbg = f"Y:{yield_diff} D:{duration_diff}"
                status = yield_status if yield_status == duration_status else "🟡"
            else:
                vs_bbg = "N/A"
                status = "❌"
                
            print(f"{''.ljust(25)}{'- ISIN'.ljust(15)}{yield_val.ljust(12)}{duration_val.ljust(12)}{convexity_val.ljust(12)}{vs_bbg.ljust(15)}{status}")
        else:
            print(f"{''.ljust(25)}{'- ISIN'.ljust(15)}{'FAILED'.ljust(12)}{'FAILED'.ljust(12)}{'FAILED'.ljust(12)}{'ERROR'.ljust(15)}{'❌'}")
        
        # Bloomberg baseline
        bbg_yield_str = format_number(bbg_yield, 5)
        bbg_duration_str = format_number(bbg_duration, 5) 
        bbg_convexity_str = format_number(bbg_convexity, 2)
        print(f"{''.ljust(25)}{'Bloomberg'.ljust(15)}{bbg_yield_str.ljust(12)}{bbg_duration_str.ljust(12)}{bbg_convexity_str.ljust(12)}{'BASELINE'.ljust(15)}{'📊'}")
        
        print()  # Blank line between bonds

def print_summary_analysis(bonds, results_with_isin, results_without_isin):
    """Print summary analysis"""
    
    print("📊 SUMMARY ANALYSIS")
    print("=" * 60)
    
    total_bonds = len(bonds)
    success_with_isin = sum(1 for r in results_with_isin if r["success"])
    success_without_isin = sum(1 for r in results_without_isin if r["success"])
    
    print(f"Total Bonds Tested: {total_bonds}")
    print(f"Success with ISIN: {success_with_isin}/{total_bonds} ({success_with_isin/total_bonds*100:.1f}%)")
    print(f"Success without ISIN: {success_without_isin}/{total_bonds} ({success_without_isin/total_bonds*100:.1f}%)")
    print()
    
    # Duration consistency check
    print("🎯 SEMI-ANNUAL DURATION CONSISTENCY CHECK:")
    print("-" * 50)
    
    for i, bond in enumerate(bonds):
        if bond["name"].startswith("🏛️"):  # US Treasury
            result_isin = results_with_isin[i]
            result_no_isin = results_without_isin[i]
            expected_duration = bond["bloomberg_duration"]
            
            if result_isin["success"] and result_isin["duration"]:
                duration_isin = result_isin["duration"]
                diff_isin = abs(duration_isin - expected_duration)
                status_isin = "✅" if diff_isin < 1.0 else "❌"
                print(f"  {bond['name'][:30]} (ISIN): {duration_isin:.5f} vs {expected_duration:.5f} = {diff_isin:.4f} {status_isin}")
                
                # Check if duration is in the correct range (should be ~16 for this Treasury, not ~10)
                if duration_isin > 15.0:
                    print(f"    ✅ Duration in semi-annual range (>15 years)")
                elif duration_isin < 12.0:
                    print(f"    ❌ Duration too low - likely annual basis or calculation error")
                else:
                    print(f"    🟡 Duration in middle range - check calculation")
            
            if result_no_isin["success"] and result_no_isin["duration"]:
                duration_no_isin = result_no_isin["duration"]
                diff_no_isin = abs(duration_no_isin - expected_duration)
                status_no_isin = "✅" if diff_no_isin < 1.0 else "❌"
                print(f"  {bond['name'][:30]} (Desc): {duration_no_isin:.5f} vs {expected_duration:.5f} = {diff_no_isin:.4f} {status_no_isin}")
                
                # Check if duration is in the correct range
                if duration_no_isin > 15.0:
                    print(f"    ✅ Duration in semi-annual range (>15 years)")
                elif duration_no_isin < 12.0:
                    print(f"    ❌ Duration too low - likely annual basis or calculation error")
                else:
                    print(f"    🟡 Duration in middle range - check calculation")
    
    print()
    print("🔍 KEY INSIGHTS:")
    print("-" * 40)
    print("• US Treasury duration should be ~16.36 years (semi-annual basis)")
    print("• If getting ~8.18 years, it's using annual basis")  
    print("• If getting ~10-11 years, there's a calculation inconsistency")
    print("• Both ISIN and description methods should give identical results")

def main():
    """Main calculation and comparison"""
    
    print("🚀 Starting Bond Master Calculation Test...")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Create test portfolio
    bonds = create_test_portfolio()
    
    print(f"📋 Testing {len(bonds)} bonds with both ISIN and description methods")
    print()
    
    # Run calculations with ISIN
    print("🔍 Running calculations WITH ISIN...")
    results_with_isin = []
    for bond in bonds:
        result = run_calculations(bond, "WITH_ISIN", include_isin=True)
        results_with_isin.append(result)
    
    # Run calculations without ISIN
    print("🔍 Running calculations WITHOUT ISIN...")
    results_without_isin = []
    for bond in bonds:
        result = run_calculations(bond, "WITHOUT_ISIN", include_isin=False)
        results_without_isin.append(result)
    
    print()
    
    # Print comparison table
    print_comparison_table(bonds, results_with_isin, results_without_isin)
    
    # Print summary analysis
    print_summary_analysis(bonds, results_with_isin, results_without_isin)
    
    print()
    print("✅ Bond Master Calculation Test Complete!")

if __name__ == "__main__":
    main()
