#!/usr/bin/env python3
"""
Bloomberg Baseline Comparison - FOCUSED TEST
=============================================

Quick comparison of our calculations vs your corrected Bloomberg baselines
Settlement Date: 2025-06-30
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime

# Add current directory to path for imports
sys.path.append('.')

try:
    from google_analysis10 import process_bonds_without_weightings
    LOCAL_IMPORTS_AVAILABLE = True
    print("✅ Successfully imported google_analysis10 calculation engine")
except ImportError as e:
    print(f"❌ Could not import local calculation engine: {e}")
    LOCAL_IMPORTS_AVAILABLE = False
    sys.exit(1)

# Your corrected Bloomberg baseline data
bloomberg_baselines = {
    "US912810TJ79": {"yield": 4.90, "duration": 16.36, "spread": 0, "name": "US TREASURY N/B, 3%, 15-Aug-2052"},
    "XS2249741674": {"yield": 5.64, "duration": 10.10, "spread": 118, "name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040"},
    "XS1709535097": {"yield": 5.72, "duration": 9.82, "spread": 123, "name": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047"},
    "XS1982113463": {"yield": 5.60, "duration": 9.93, "spread": 111, "name": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039"},
    "USP37466AS18": {"yield": 6.27, "duration": 13.19, "spread": 144, "name": "EMPRESA METRO, 4.7%, 07-May-2050"},
    "USP3143NAH72": {"yield": 5.95, "duration": 8.02, "spread": 160, "name": "CODELCO INC, 6.15%, 24-Oct-2036"},
    "USP30179BR86": {"yield": 7.44, "duration": 11.58, "spread": 261, "name": "COMISION FEDERAL, 6.264%, 15-Feb-2052"},
    "US195325DX04": {"yield": 7.84, "duration": 12.98, "spread": 301, "name": "COLOMBIA REP OF, 3.875%, 15-Feb-2061"},
    "US279158AJ82": {"yield": 9.28, "duration": 9.81, "spread": 445, "name": "ECOPETROL SA, 5.875%, 28-May-2045"},
    "USP37110AM89": {"yield": 6.54, "duration": 12.39, "spread": 171, "name": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047"},
    "XS2542166231": {"yield": 5.72, "duration": 7.21, "spread": 146, "name": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038"},
    "XS2167193015": {"yield": 6.34, "duration": 15.27, "spread": 151, "name": "STATE OF ISRAEL, 3.8%, 13-May-2060"},
    "XS1508675508": {"yield": 5.97, "duration": 12.60, "spread": 114, "name": "SAUDI INT BOND, 4.5%, 26-Oct-2046"},
    "XS1807299331": {"yield": 7.06, "duration": 11.45, "spread": 223, "name": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048"},
    "US91086QAZ19": {"yield": 7.37, "duration": 13.37, "spread": 255, "name": "UNITED MEXICAN, 5.75%, 12-Oct-2110"},
    "USP6629MAD40": {"yield": 7.07, "duration": 11.38, "spread": 224, "name": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047"},
    "US698299BL70": {"yield": 7.36, "duration": 13.49, "spread": 253, "name": "PANAMA, 3.87%, 23-Jul-2060"},
    "US71654QDF63": {"yield": 9.88, "duration": 9.72, "spread": 505, "name": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060"},
    "US71654QDE98": {"yield": 8.32, "duration": 4.47, "spread": 444, "name": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031"},
    "XS2585988145": {"yield": 6.23, "duration": 13.33, "spread": 140, "name": "GACI FIRST INVST, 5.125%, 14-Feb-2053"},
    "XS1959337749": {"yield": 5.58, "duration": 13.26, "spread": 76, "name": "QATAR STATE OF, 4.817%, 14-Mar-2049"},
    "XS2233188353": {"yield": 5.02, "duration": 0.23, "spread": 71, "name": "QNB FINANCE LTD, 1.625%, 22-Sep-2025"},
    "XS2359548935": {"yield": 5.63, "duration": 11.51, "spread": 101, "name": "QATAR ENERGY, 3.125%, 12-Jul-2041"},
    "XS0911024635": {"yield": 5.66, "duration": 11.24, "spread": 95, "name": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043"},
    "USP0R80BAG79": {"yield": 5.87, "duration": 5.51, "spread": 187, "name": "SITIOS, 5.375%, 04-Apr-2032"}
}

# Bond data with prices
bonds_data = [
    {"isin": "US912810TJ79", "price": 71.66},
    {"isin": "XS2249741674", "price": 77.88},
    {"isin": "XS1709535097", "price": 89.40},
    {"isin": "XS1982113463", "price": 87.14},
    {"isin": "USP37466AS18", "price": 80.39},
    {"isin": "USP3143NAH72", "price": 101.63},
    {"isin": "USP30179BR86", "price": 86.42},
    {"isin": "US195325DX04", "price": 52.71},
    {"isin": "US279158AJ82", "price": 69.31},
    {"isin": "USP37110AM89", "price": 76.24},
    {"isin": "XS2542166231", "price": 103.03},
    {"isin": "XS2167193015", "price": 64.50},
    {"isin": "XS1508675508", "price": 82.42},
    {"isin": "XS1807299331", "price": 92.21},
    {"isin": "US91086QAZ19", "price": 78.00},
    {"isin": "USP6629MAD40", "price": 82.57},
    {"isin": "US698299BL70", "price": 56.60},
    {"isin": "US71654QDF63", "price": 71.42},
    {"isin": "US71654QDE98", "price": 89.55},
    {"isin": "XS2585988145", "price": 85.54},
    {"isin": "XS1959337749", "price": 89.97},
    {"isin": "XS2233188353", "price": 99.23},
    {"isin": "XS2359548935", "price": 73.79},
    {"isin": "XS0911024635", "price": 93.29},
    {"isin": "USP0R80BAG79", "price": 97.26}
]

def test_bond_calculation(isin, price):
    """Test a single bond calculation"""
    try:
        # Prepare bond data
        test_data = pd.DataFrame([{
            "BOND_CD": isin,
            "CLOSING PRICE": price
        }])
        
        # Process using direct local calculation
        results_df = process_bonds_without_weightings(
            test_data, 
            db_path="./bonds_data.db",
            validated_db_path="./validated_quantlib_bonds.db"
        )
        
        if isinstance(results_df, pd.DataFrame) and not results_df.empty:
            result = results_df.iloc[0]
            return {
                "success": True,
                "yield": result.get('yield', 0),
                "duration": result.get('duration', 0), 
                "spread": result.get('spread', 0),
                "error": None
            }
        else:
            return {"success": False, "error": "Empty results"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    """Run Bloomberg baseline comparison"""
    print("🎯 BLOOMBERG BASELINE COMPARISON - SETTLEMENT DATE: 2025-06-30")
    print("=" * 80)
    print(f"Testing {len(bonds_data)} bonds against your corrected Bloomberg baselines...")
    print()
    
    comparison_results = []
    successful_tests = 0
    
    for bond in bonds_data:
        isin = bond["isin"]
        price = bond["price"]
        
        print(f"📊 Testing {isin} @ {price}")
        
        # Get Bloomberg baseline
        bloomberg = bloomberg_baselines.get(isin, {})
        bbg_yield = bloomberg.get("yield", 0)
        bbg_duration = bloomberg.get("duration", 0)
        bbg_spread = bloomberg.get("spread", 0)
        bbg_name = bloomberg.get("name", "Unknown")
        
        # Test our calculation
        our_result = test_bond_calculation(isin, price)
        
        if our_result["success"]:
            successful_tests += 1
            our_yield = our_result["yield"]
            our_duration = our_result["duration"]
            our_spread = our_result["spread"]
            
            # Calculate differences
            yield_diff = our_yield - bbg_yield
            duration_diff = our_duration - bbg_duration
            spread_diff = our_spread - bbg_spread
            
            # Determine accuracy flags
            yield_accurate = abs(yield_diff) <= 0.05  # 5bp tolerance
            duration_accurate = abs(duration_diff) <= 0.1  # 0.1 year tolerance
            spread_accurate = abs(spread_diff) <= 10  # 10bp tolerance
            
            result = {
                "isin": isin,
                "name": bbg_name,
                "bbg_yield": bbg_yield,
                "our_yield": our_yield,
                "yield_diff": yield_diff,
                "yield_accurate": yield_accurate,
                "bbg_duration": bbg_duration,
                "our_duration": our_duration,
                "duration_diff": duration_diff,
                "duration_accurate": duration_accurate,
                "bbg_spread": bbg_spread,
                "our_spread": our_spread,
                "spread_diff": spread_diff,
                "spread_accurate": spread_accurate,
                "overall_accurate": yield_accurate and duration_accurate and spread_accurate
            }
            
            comparison_results.append(result)
            
            # Print result
            y_flag = "✅" if yield_accurate else "❌"
            d_flag = "✅" if duration_accurate else "❌"
            s_flag = "✅" if spread_accurate else "❌"
            
            print(f"   Bloomberg: Y:{bbg_yield:5.2f}% D:{bbg_duration:5.2f}yr S:{bbg_spread:4.0f}bp")
            print(f"   Our Calc:  Y:{our_yield:5.2f}% D:{our_duration:5.2f}yr S:{our_spread:4.0f}bp")
            print(f"   Accuracy:  {y_flag}Y({yield_diff:+5.2f}) {d_flag}D({duration_diff:+5.2f}) {s_flag}S({spread_diff:+4.0f})")
            
        else:
            print(f"   ❌ FAILED: {our_result['error']}")
        
        print()
    
    # Generate summary
    print("🏆 BLOOMBERG BASELINE COMPARISON SUMMARY")
    print("=" * 80)
    print(f"Total Bonds Tested: {len(bonds_data)}")
    print(f"Successful Calculations: {successful_tests}/{len(bonds_data)} ({successful_tests/len(bonds_data)*100:.1f}%)")
    
    if comparison_results:
        accurate_yields = sum(1 for r in comparison_results if r["yield_accurate"])
        accurate_durations = sum(1 for r in comparison_results if r["duration_accurate"])
        accurate_spreads = sum(1 for r in comparison_results if r["spread_accurate"])
        overall_accurate = sum(1 for r in comparison_results if r["overall_accurate"])
        
        print(f"Bloomberg Yield Accuracy: {accurate_yields}/{len(comparison_results)} ({accurate_yields/len(comparison_results)*100:.1f}%)")
        print(f"Bloomberg Duration Accuracy: {accurate_durations}/{len(comparison_results)} ({accurate_durations/len(comparison_results)*100:.1f}%)")
        print(f"Bloomberg Spread Accuracy: {accurate_spreads}/{len(comparison_results)} ({accurate_spreads/len(comparison_results)*100:.1f}%)")
        print(f"Overall Bloomberg Match: {overall_accurate}/{len(comparison_results)} ({overall_accurate/len(comparison_results)*100:.1f}%)")
        
        # Show biggest discrepancies
        print("\n🔍 LARGEST DISCREPANCIES:")
        yield_discrepancies = sorted(comparison_results, key=lambda x: abs(x["yield_diff"]), reverse=True)[:5]
        duration_discrepancies = sorted(comparison_results, key=lambda x: abs(x["duration_diff"]), reverse=True)[:5]
        
        print("   YIELD DISCREPANCIES:")
        for r in yield_discrepancies:
            print(f"      {r['isin']}: {r['yield_diff']:+6.2f}bp ({r['our_yield']:.2f}% vs {r['bbg_yield']:.2f}%)")
        
        print("   DURATION DISCREPANCIES:")
        for r in duration_discrepancies:
            print(f"      {r['isin']}: {r['duration_diff']:+6.2f}yr ({r['our_duration']:.2f} vs {r['bbg_duration']:.2f})")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_df = pd.DataFrame(comparison_results)
        results_file = f"bloomberg_baseline_comparison_{timestamp}.csv"
        results_df.to_csv(results_file, index=False)
        print(f"\n💾 Detailed results saved to: {results_file}")
        
        # Deployment recommendation
        print(f"\n🎯 DEPLOYMENT RECOMMENDATION:")
        if overall_accurate >= len(comparison_results) * 0.8:
            print("   ✅ READY FOR DEPLOYMENT - Good Bloomberg accuracy")
        elif overall_accurate >= len(comparison_results) * 0.6:
            print("   ⚠️  PROCEED WITH CAUTION - Some Bloomberg discrepancies")
        else:
            print("   ❌ FIX ISSUES BEFORE DEPLOYMENT - Significant Bloomberg discrepancies")

if __name__ == "__main__":
    main()
