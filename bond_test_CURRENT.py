#!/usr/bin/env python3
"""
PRECISION Bloomberg Test - 6 Decimal Accuracy
============================================

Tests against EXACT Bloomberg terminal values (6 decimal places)
to show TRUE accuracy of calculation engine vs Bloomberg.

Uses actual BB terminal data with full precision:
- Yields to 6 decimal places (e.g., 4.898453%)
- Duration to 6 decimal places (e.g., 16.357839 years) 
- Spreads to basis points (e.g., 118 bps)

This eliminates artificial rounding errors and shows REAL accuracy.
"""

import sys
import os
from datetime import datetime

# Add the google_analysis10 directory to Python path
PROJECT_ROOT = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10"
sys.path.insert(0, PROJECT_ROOT)

from bond_master_hierarchy import calculate_bond_master

# EXACT Bloomberg Terminal Data - 6 Decimal Precision
BLOOMBERG_PRECISION_DATA = [
    {"isin": "US912810TJ79", "px_mid": 71.66, "name": "T 3 15/08/52", 
     "bb_duration": 16.357839, "bb_yield": 4.898453, "bb_spread": None},  # Treasury - no spread
    
    {"isin": "XS2249741674", "px_mid": 77.88, "name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040",
     "bb_duration": 10.097620, "bb_yield": 5.637570, "bb_spread": 118},
    
    {"isin": "XS1709535097", "px_mid": 89.40, "name": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047",
     "bb_duration": 9.815219, "bb_yield": 5.717451, "bb_spread": 123},
    
    {"isin": "XS1982113463", "px_mid": 87.14, "name": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039",
     "bb_duration": 9.927596, "bb_yield": 5.599746, "bb_spread": 111},
    
    {"isin": "USP37466AS18", "px_mid": 80.39, "name": "EMPRESA METRO, 4.7%, 07-May-2050",
     "bb_duration": 13.189567, "bb_yield": 6.265800, "bb_spread": 144},
    
    {"isin": "USP3143NAH72", "px_mid": 101.63, "name": "CODELCO INC, 6.15%, 24-Oct-2036",
     "bb_duration": 8.024166, "bb_yield": 5.949058, "bb_spread": 160},
    
    {"isin": "USP30179BR86", "px_mid": 86.42, "name": "COMISION FEDERAL, 6.264%, 15-Feb-2052",
     "bb_duration": 11.583500, "bb_yield": 7.442306, "bb_spread": 261},
    
    {"isin": "US195325DX04", "px_mid": 52.71, "name": "COLOMBIA REP OF, 3.875%, 15-Feb-2061",
     "bb_duration": 12.975798, "bb_yield": 7.836133, "bb_spread": 301},
    
    {"isin": "US279158AJ82", "px_mid": 69.31, "name": "ECOPETROL SA, 5.875%, 28-May-2045",
     "bb_duration": 9.812703, "bb_yield": 9.282266, "bb_spread": 445},
    
    {"isin": "USP37110AM89", "px_mid": 76.24, "name": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047",
     "bb_duration": 12.389556, "bb_yield": 6.542351, "bb_spread": 171},
    
    {"isin": "XS2542166231", "px_mid": 103.03, "name": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038",
     "bb_duration": 7.207705, "bb_yield": 5.720213, "bb_spread": 146},
    
    {"isin": "XS2167193015", "px_mid": 64.50, "name": "STATE OF ISRAEL, 3.8%, 13-May-2060",
     "bb_duration": 15.269052, "bb_yield": 6.337460, "bb_spread": 151},
    
    {"isin": "XS1508675508", "px_mid": 82.42, "name": "SAUDI INT BOND, 4.5%, 26-Oct-2046",
     "bb_duration": 12.598517, "bb_yield": 5.967150, "bb_spread": 114},
    
    {"isin": "XS1807299331", "px_mid": 92.21, "name": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048",
     "bb_duration": 11.446459, "bb_yield": 7.059957, "bb_spread": 223},
    
    {"isin": "US91086QAZ19", "px_mid": 78.00, "name": "UNITED MEXICAN, 5.75%, 12-Oct-2110",
     "bb_duration": 13.370728, "bb_yield": 7.374879, "bb_spread": 255},
    
    {"isin": "USP6629MAD40", "px_mid": 82.57, "name": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047",
     "bb_duration": 11.382487, "bb_yield": 7.070132, "bb_spread": 224},
    
    {"isin": "US698299BL70", "px_mid": 56.60, "name": "PANAMA, 3.87%, 23-Jul-2060",
     "bb_duration": 13.488582, "bb_yield": 7.362747, "bb_spread": 253},
    
    {"isin": "US71654QDF63", "px_mid": 71.42, "name": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060",
     "bb_duration": 9.719713, "bb_yield": 9.875691, "bb_spread": 505},
    
    {"isin": "US71654QDE98", "px_mid": 89.55, "name": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031",
     "bb_duration": 4.469801, "bb_yield": 8.324595, "bb_spread": 444},
    
    {"isin": "XS2585988145", "px_mid": 85.54, "name": "GACI FIRST INVST, 5.125%, 14-Feb-2053",
     "bb_duration": 13.327227, "bb_yield": 6.228001, "bb_spread": 140},
    
    {"isin": "XS1959337749", "px_mid": 89.97, "name": "QATAR STATE OF, 4.817%, 14-Mar-2049",
     "bb_duration": 13.261812, "bb_yield": 5.584981, "bb_spread": 76},
    
    {"isin": "XS2233188353", "px_mid": 99.23, "name": "QNB FINANCE LTD, 1.625%, 22-Sep-2025",
     "bb_duration": 0.225205, "bb_yield": 5.015259, "bb_spread": 71},
    
    {"isin": "XS2359548935", "px_mid": 73.79, "name": "QATAR ENERGY, 3.125%, 12-Jul-2041",
     "bb_duration": 11.512115, "bb_yield": 5.628065, "bb_spread": 101},
    
    {"isin": "XS0911024635", "px_mid": 93.29, "name": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043",
     "bb_duration": 11.237819, "bb_yield": 5.663334, "bb_spread": 95},
    
    {"isin": "USP0R80BAG79", "px_mid": 97.26, "name": "SITIOS, 5.375%, 04-Apr-2032",
     "bb_duration": 5.514383, "bb_yield": 5.870215, "bb_spread": 187}
]

def test_precision_bond(bond_data):
    """Test a single bond with exact Bloomberg precision comparison"""
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
            calc_spread = result.get("spread")
            
            # Calculate precision differences
            yield_diff_bps = abs(calc_yield - bond_data["bb_yield"]) * 100 if calc_yield else None
            duration_diff = abs(calc_duration - bond_data["bb_duration"]) if calc_duration else None
            spread_diff = abs(calc_spread - bond_data["bb_spread"]) if (calc_spread and bond_data["bb_spread"]) else None
            
            return {
                "success": True,
                "calc_yield": calc_yield,
                "calc_duration": calc_duration,
                "calc_spread": calc_spread,
                "yield_diff_bps": yield_diff_bps,
                "duration_diff": duration_diff,
                "spread_diff": spread_diff,
                "conventions": result.get("conventions", {})
            }
        else:
            return {"success": False, "error": result.get("error", "Unknown error")}
            
    except Exception as e:
        return {"success": False, "error": f"Exception: {str(e)}"}

def format_precision_result(bond_data, result, bond_num):
    """Format precision test result with exact Bloomberg comparison"""
    
    isin = bond_data["isin"]
    name = bond_data["name"][:60]
    price = bond_data["px_mid"]
    
    # Bloomberg values (6 decimal precision)
    bb_yield = bond_data["bb_yield"]
    bb_duration = bond_data["bb_duration"]
    bb_spread = bond_data["bb_spread"]
    
    if result["success"]:
        # Calculated values
        calc_yield = result["calc_yield"]
        calc_duration = result["calc_duration"]
        calc_spread = result["calc_spread"]
        
        # Precision differences
        yield_diff_bps = result["yield_diff_bps"]
        duration_diff = result["duration_diff"]
        spread_diff = result["spread_diff"]
        
        # Accuracy assessment
        yield_accuracy = "🎯 EXCELLENT" if yield_diff_bps < 1 else "✅ GOOD" if yield_diff_bps < 5 else "⚠️ FAIR" if yield_diff_bps < 15 else "❌ POOR"
        duration_accuracy = "🎯 EXCELLENT" if duration_diff < 0.01 else "✅ GOOD" if duration_diff < 0.05 else "⚠️ FAIR" if duration_diff < 0.2 else "❌ POOR"
        
        if bb_spread and calc_spread:
            spread_accuracy = "🎯 EXCELLENT" if spread_diff < 2 else "✅ GOOD" if spread_diff < 10 else "⚠️ FAIR" if spread_diff < 25 else "❌ POOR"
        else:
            spread_accuracy = "N/A (Treasury)"
            spread_diff = None
        
        card = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                          BOND #{bond_num:02d}: {name[:80]:<80}                                                          ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ ISIN: {isin:<15} │ Price: ${price:>8.2f} │ Settlement: 2025-06-30                                                                                                          ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                    📊 PRECISION BLOOMBERG COMPARISON                                                                                                ║
║ ┌─────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────┐                                     ║
║ │                      📈 YIELD TO MATURITY                           │                        ⏱️ MODIFIED DURATION                         │                                     ║
║ ├─────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────┤                                     ║
║ │ Bloomberg (6-decimal):  {bb_yield:>8.6f}%                          │ Bloomberg (6-decimal):  {bb_duration:>8.6f} yrs                    │                                     ║
║ │ Calculated:             {calc_yield:>8.6f}%                         │ Calculated:             {calc_duration:>8.6f} yrs                   │                                     ║
║ │ Difference:             {yield_diff_bps:>8.3f} bps                  │ Difference:             {duration_diff:>8.6f} yrs                   │                                     ║
║ │ Accuracy:               {yield_accuracy:<25}                        │ Accuracy:               {duration_accuracy:<25}                     │                                     ║
║ └─────────────────────────────────────────────────────────────────────┴─────────────────────────────────────────────────────────────────────┘                                     ║
║                                                                                                                                                                                      ║
║ ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐   ║
║ │                                                          💰 TREASURY SPREAD vs BLOOMBERG                                                                                      │   ║
║ ├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤   ║"""

        if bb_spread and calc_spread:
            card += f"""
║ │ Bloomberg Spread:       {bb_spread:>8.0f} bps                                                Calculated Spread:      {calc_spread:>8.1f} bps                             │   ║
║ │ Difference:             {spread_diff:>8.1f} bps                                                Accuracy:                {spread_accuracy:<25}                     │   ║"""
        else:
            card += f"""
║ │ Treasury Bond - No spread vs Treasury (this IS the Treasury benchmark)                                                                                              │   ║"""

        card += f"""
║ └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝"""

    else:
        # Failed calculation
        error = result.get("error", "Unknown error")
        card = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                          BOND #{bond_num:02d}: {name[:80]:<80}                                                          ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ ISIN: {isin:<15} │ Price: ${price:>8.2f} │ Settlement: 2025-06-30                                                                                                          ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                    ❌ CALCULATION FAILED                                                                                            ║
║ Error: {error[:130]:<130}                                                                                                                                                 ║
║                                                                                                                                                                                      ║
║ Bloomberg Reference Values:                                                                                                                                                          ║
║ • Yield: {bb_yield:.6f}%                                                                                                                                                           ║
║ • Duration: {bb_duration:.6f} years                                                                                                                                                ║
║ • Spread: {bb_spread if bb_spread else 'N/A (Treasury)'} bps                                                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝"""

    return card

def main():
    """Run precision Bloomberg comparison test"""
    
    print("🎯 PRECISION BLOOMBERG COMPARISON TEST")
    print("=" * 150)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Project: {PROJECT_ROOT}")
    print(f"📊 Testing: {len(BLOOMBERG_PRECISION_DATA)} bonds")
    print(f"📅 Settlement: 2025-06-30")
    print("🔍 Baseline: EXACT Bloomberg Terminal Values (6 decimal precision)")
    print("💎 Purpose: Show TRUE calculation accuracy vs Bloomberg")
    print("=" * 150)
    
    # Statistics tracking
    total_bonds = len(BLOOMBERG_PRECISION_DATA)
    successful_calcs = 0
    yield_excellent = 0  # <1bp
    yield_good = 0       # <5bp  
    yield_fair = 0       # <15bp
    duration_excellent = 0  # <0.01yr
    duration_good = 0       # <0.05yr
    duration_fair = 0       # <0.2yr
    spread_excellent = 0    # <2bp
    spread_good = 0         # <10bp
    spread_fair = 0         # <25bp
    
    yield_differences = []
    duration_differences = []
    spread_differences = []
    
    # Test each bond
    for i, bond_data in enumerate(BLOOMBERG_PRECISION_DATA, 1):
        print(f"\n🧪 Testing Bond {i}/{total_bonds}: {bond_data['isin']} - {bond_data['name'][:50]}...")
        
        result = test_precision_bond(bond_data)
        
        if result["success"]:
            successful_calcs += 1
            
            # Yield accuracy tracking
            yield_diff_bps = result["yield_diff_bps"]
            yield_differences.append(yield_diff_bps)
            
            if yield_diff_bps < 1:
                yield_excellent += 1
            elif yield_diff_bps < 5:
                yield_good += 1
            elif yield_diff_bps < 15:
                yield_fair += 1
            
            # Duration accuracy tracking
            duration_diff = result["duration_diff"]
            duration_differences.append(duration_diff)
            
            if duration_diff < 0.01:
                duration_excellent += 1
            elif duration_diff < 0.05:
                duration_good += 1
            elif duration_diff < 0.2:
                duration_fair += 1
            
            # Spread accuracy tracking (if applicable)
            if result["spread_diff"] is not None:
                spread_diff = result["spread_diff"]
                spread_differences.append(spread_diff)
                
                if spread_diff < 2:
                    spread_excellent += 1
                elif spread_diff < 10:
                    spread_good += 1
                elif spread_diff < 25:
                    spread_fair += 1
        
        # Print formatted result
        card = format_precision_result(bond_data, result, i)
        print(card)
    
    # Calculate statistics
    avg_yield_diff = sum(yield_differences) / len(yield_differences) if yield_differences else 0
    avg_duration_diff = sum(duration_differences) / len(duration_differences) if duration_differences else 0
    avg_spread_diff = sum(spread_differences) / len(spread_differences) if spread_differences else 0
    
    max_yield_diff = max(yield_differences) if yield_differences else 0
    max_duration_diff = max(duration_differences) if duration_differences else 0
    max_spread_diff = max(spread_differences) if spread_differences else 0
    
    # Print comprehensive summary
    print("\n" + "=" * 150)
    print("📈 PRECISION BLOOMBERG COMPARISON SUMMARY")
    print("=" * 150)
    print(f"📊 Total Bonds Tested: {total_bonds}")
    print(f"✅ Successful Calculations: {successful_calcs}/{total_bonds} ({successful_calcs/total_bonds*100:.1f}%)")
    
    print(f"\n🎯 YIELD ACCURACY vs BLOOMBERG (6-decimal precision):")
    print(f"   🎯 EXCELLENT (<1bp):   {yield_excellent}/{successful_calcs} ({yield_excellent/successful_calcs*100:.1f}%)")
    print(f"   ✅ GOOD (<5bp):        {yield_good}/{successful_calcs} ({yield_good/successful_calcs*100:.1f}%)")
    print(f"   ⚠️ FAIR (<15bp):       {yield_fair}/{successful_calcs} ({yield_fair/successful_calcs*100:.1f}%)")
    print(f"   📊 Average Difference: {avg_yield_diff:.3f} bps")
    print(f"   📊 Maximum Difference: {max_yield_diff:.3f} bps")
    
    print(f"\n⏱️ DURATION ACCURACY vs BLOOMBERG (6-decimal precision):")
    print(f"   🎯 EXCELLENT (<0.01yr): {duration_excellent}/{successful_calcs} ({duration_excellent/successful_calcs*100:.1f}%)")
    print(f"   ✅ GOOD (<0.05yr):      {duration_good}/{successful_calcs} ({duration_good/successful_calcs*100:.1f}%)")
    print(f"   ⚠️ FAIR (<0.2yr):       {duration_fair}/{successful_calcs} ({duration_fair/successful_calcs*100:.1f}%)")
    print(f"   📊 Average Difference: {avg_duration_diff:.6f} years")
    print(f"   📊 Maximum Difference: {max_duration_diff:.6f} years")
    
    if spread_differences:
        print(f"\n💰 SPREAD ACCURACY vs BLOOMBERG:")
        print(f"   🎯 EXCELLENT (<2bp):   {spread_excellent}/{len(spread_differences)} ({spread_excellent/len(spread_differences)*100:.1f}%)")
        print(f"   ✅ GOOD (<10bp):       {spread_good}/{len(spread_differences)} ({spread_good/len(spread_differences)*100:.1f}%)")
        print(f"   ⚠️ FAIR (<25bp):       {spread_fair}/{len(spread_differences)} ({spread_fair/len(spread_differences)*100:.1f}%)")
        print(f"   📊 Average Difference: {avg_spread_diff:.1f} bps")
        print(f"   📊 Maximum Difference: {max_spread_diff:.1f} bps")
    
    # Overall assessment with institutional standards
    yield_institutional_score = (yield_excellent + yield_good) / successful_calcs * 100 if successful_calcs > 0 else 0
    duration_institutional_score = (duration_excellent + duration_good) / successful_calcs * 100 if successful_calcs > 0 else 0
    
    print(f"\n🏛️ INSTITUTIONAL GRADE ASSESSMENT:")
    print(f"   📊 Yield Precision Score: {yield_institutional_score:.1f}% (Excellent + Good)")
    print(f"   📊 Duration Precision Score: {duration_institutional_score:.1f}% (Excellent + Good)")
    
    if yield_institutional_score >= 90 and duration_institutional_score >= 90:
        print("   🏆 VERDICT: INSTITUTIONAL GRADE - Production ready for Bloomberg alternative")
    elif yield_institutional_score >= 80 and duration_institutional_score >= 80:
        print("   ✅ VERDICT: PROFESSIONAL GRADE - Suitable for most trading applications")
    elif yield_institutional_score >= 70 and duration_institutional_score >= 70:
        print("   ⚠️ VERDICT: ACCEPTABLE - Good for analysis, may need improvement for critical trading")
    else:
        print("   ❌ VERDICT: NEEDS IMPROVEMENT - Not suitable for production trading")
    
    print(f"\n⏰ Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("💎 Note: This test uses EXACT Bloomberg terminal values with 6-decimal precision")
    print("🎯 Any differences shown are TRUE calculation differences vs Bloomberg")
    print("=" * 150)

if __name__ == "__main__":
    # Change to the correct directory
    os.chdir(PROJECT_ROOT)
    
    # Run the precision test
    main()
