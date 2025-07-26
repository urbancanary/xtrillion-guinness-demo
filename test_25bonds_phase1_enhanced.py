#!/usr/bin/env python3
"""
🚀 COMPREHENSIVE 25-BOND PHASE 1 ENHANCED TEST
=============================================

Tests all 25 bonds using the ENHANCED calculate_bond_master function with:
- All original outputs (yield, duration, spread)
- 6 NEW Phase 1 outputs (mac_dur_semi, clean_price, dirty_price, ytm_annual, mod_dur_annual, mac_dur_annual)

Shows full results in professional card format with Phase 1 enhancement tracking.
"""

import sys
import os
import json
from datetime import datetime

# Add the google_analysis10 directory to Python path
PROJECT_ROOT = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10"
sys.path.insert(0, PROJECT_ROOT)

# ✅ ENHANCED FUNCTION - Uses Phase 1 with 6 additional outputs
from bond_master_hierarchy_enhanced import calculate_bond_master

# 25-bond test portfolio
BONDS_25 = [
    {"isin": "US912810TJ79", "px_mid": 71.66, "name": "T 3 15/08/52"},
    {"isin": "XS2249741674", "px_mid": 77.88, "name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040"},
    {"isin": "XS1709535097", "px_mid": 89.40, "name": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047"},
    {"isin": "XS1982113463", "px_mid": 87.14, "name": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039"},
    {"isin": "USP37466AS18", "px_mid": 80.39, "name": "EMPRESA METRO, 4.7%, 07-May-2050"},
    {"isin": "USP3143NAH72", "px_mid": 101.63, "name": "CODELCO INC, 6.15%, 24-Oct-2036"},
    {"isin": "USP30179BR86", "px_mid": 86.42, "name": "COMISION FEDERAL, 6.264%, 15-Feb-2052"},
    {"isin": "US195325DX04", "px_mid": 52.71, "name": "COLOMBIA REP OF, 3.875%, 15-Feb-2061"},
    {"isin": "US279158AJ82", "px_mid": 69.31, "name": "ECOPETROL SA, 5.875%, 28-May-2045"},
    {"isin": "USP37110AM89", "px_mid": 76.24, "name": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047"},
    {"isin": "XS2542166231", "px_mid": 103.03, "name": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038"},
    {"isin": "XS2167193015", "px_mid": 64.50, "name": "STATE OF ISRAEL, 3.8%, 13-May-2060"},
    {"isin": "XS1508675508", "px_mid": 82.42, "name": "SAUDI INT BOND, 4.5%, 26-Oct-2046"},
    {"isin": "XS1807299331", "px_mid": 92.21, "name": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048"},
    {"isin": "US91086QAZ19", "px_mid": 78.00, "name": "UNITED MEXICAN, 5.75%, 12-Oct-2110"},
    {"isin": "USP6629MAD40", "px_mid": 82.57, "name": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047"},
    {"isin": "US698299BL70", "px_mid": 56.60, "name": "PANAMA, 3.87%, 23-Jul-2060"},
    {"isin": "US71654QDF63", "px_mid": 71.42, "name": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060"},
    {"isin": "US71654QDE98", "px_mid": 89.55, "name": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031"},
    {"isin": "XS2585988145", "px_mid": 85.54, "name": "GACI FIRST INVST, 5.125%, 14-Feb-2053"},
    {"isin": "XS1959337749", "px_mid": 89.97, "name": "QATAR STATE OF, 4.817%, 14-Mar-2049"},
    {"isin": "XS2233188353", "px_mid": 99.23, "name": "QNB FINANCE LTD, 1.625%, 22-Sep-2025"},
    {"isin": "XS2359548935", "px_mid": 73.79, "name": "QATAR ENERGY, 3.125%, 12-Jul-2041"},
    {"isin": "XS0911024635", "px_mid": 93.29, "name": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043"},
    {"isin": "USP0R80BAG79", "px_mid": 97.26, "name": "SITIOS, 5.375%, 04-Apr-2032"}
]

def test_single_bond_enhanced(bond, bond_num):
    """Test a single bond with detailed Phase 1 enhancement tracking"""
    try:
        result = calculate_bond_master(
            isin=bond["isin"],
            description=bond["name"],
            price=bond["px_mid"],
            settlement_date='2025-06-30'
        )
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Exception: {str(e)}",
            "isin": bond.get("isin"),
            "description": bond["name"]
        }

def format_enhanced_result_card(bond, result, bond_num):
    """Format enhanced results as a card showing both original + Phase 1 outputs"""
    
    # Extract key data
    isin = bond["isin"]
    name = bond["name"]
    price = bond["px_mid"]
    
    # Original outputs
    success = result.get("success", False)
    yield_val = result.get("yield", "N/A")
    duration = result.get("duration", "N/A")
    spread = result.get("spread", "N/A")
    error = result.get("error", "None")
    
    # Phase 1 enhanced outputs
    mac_dur_semi = result.get("mac_dur_semi", "N/A")
    clean_price = result.get("clean_price", "N/A")
    dirty_price = result.get("dirty_price", "N/A")
    ytm_annual = result.get("ytm_annual", "N/A")
    mod_dur_annual = result.get("mod_dur_annual", "N/A")
    mac_dur_annual = result.get("mac_dur_annual", "N/A")
    
    # Check if Phase 1 outputs were added
    phase1_added = result.get("phase1_outputs_added", False)
    
    # Status indicators
    status = "✅ SUCCESS" if success else "❌ FAILED"
    phase1_status = "🚀 ENHANCED" if phase1_added else "❌ NOT ENHANCED"
    
    # Bond type detection
    bond_type = "🏛️ TREASURY" if "TREASURY" in name.upper() or name.startswith("T ") else "🏢 CORPORATE"
    
    card = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                           BOND #{bond_num:02d}: {name[:85]:<85}                                           ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ {bond_type} │ ISIN: {isin:<15} │ Price: ${price:>8.2f} │ Settlement: 2025-06-30 │ Status: {status:<12} │ Phase 1: {phase1_status:<12}     ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                              📊 ORIGINAL OUTPUTS vs 🚀 PHASE 1 ENHANCED OUTPUTS                                                                    ║
║ ┌────────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────┐                                  ║
║ │                        📈 ORIGINAL OUTPUTS                            │                         🚀 PHASE 1 NEW OUTPUTS                         │                                  ║
║ ├────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────┤                                  ║"""

    if success:
        # Format yield and duration display
        yield_display = f"{yield_val*100:.2f}%" if isinstance(yield_val, (int, float)) else str(yield_val)
        duration_display = f"{duration:.2f} yrs" if isinstance(duration, (int, float)) else str(duration)
        spread_display = f"{spread:.1f} bps" if isinstance(spread, (int, float)) else "N/A (Treasury)"
        
        # Format Phase 1 outputs
        mac_dur_semi_display = f"{mac_dur_semi:.2f} yrs" if isinstance(mac_dur_semi, (int, float)) else str(mac_dur_semi)
        clean_price_display = f"${clean_price:.2f}" if isinstance(clean_price, (int, float)) else str(clean_price)
        dirty_price_display = f"${dirty_price:.2f}" if isinstance(dirty_price, (int, float)) else str(dirty_price)
        ytm_annual_display = f"{ytm_annual:.2f}%" if isinstance(ytm_annual, (int, float)) else str(ytm_annual)
        mod_dur_annual_display = f"{mod_dur_annual:.2f} yrs" if isinstance(mod_dur_annual, (int, float)) else str(mod_dur_annual)
        mac_dur_annual_display = f"{mac_dur_annual:.2f} yrs" if isinstance(mac_dur_annual, (int, float)) else str(mac_dur_annual)
        
        card += f"""
║ │ 📊 Yield to Maturity:  {yield_display:<25}                           │ 🚀 Macaulay Duration (Semi): {mac_dur_semi_display:<25}                │                                  ║
║ │ 📊 Modified Duration:  {duration_display:<25}                           │ 🚀 Clean Price:             {clean_price_display:<25}                │                                  ║
║ │ 📊 Treasury Spread:    {spread_display:<25}                           │ 🚀 Dirty Price:             {dirty_price_display:<25}                │                                  ║
║ │                                                                        │ 🚀 Yield (Annual):          {ytm_annual_display:<25}                │                                  ║
║ │                                                                        │ 🚀 Modified Duration (Ann): {mod_dur_annual_display:<25}                │                                  ║
║ │                                                                        │ 🚀 Macaulay Duration (Ann): {mac_dur_annual_display:<25}                │                                  ║"""
    else:
        # Error case
        error_short = error[:40] + "..." if len(error) > 40 else error
        card += f"""
║ │ ❌ CALCULATION FAILED                                                   │ ❌ PHASE 1 OUTPUTS NOT AVAILABLE                                       │                                  ║
║ │ Error: {error_short:<25}                                                  │ Reason: Original calculation failed                                     │                                  ║
║ │                                                                        │                                                                         │                                  ║
║ │                                                                        │                                                                         │                                  ║
║ │                                                                        │                                                                         │                                  ║
║ │                                                                        │                                                                         │                                  ║"""

    card += f"""
║ └────────────────────────────────────────────────────────────────────────┴─────────────────────────────────────────────────────────────────────────┘                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""
    
    return card

def main():
    """Run comprehensive Phase 1 enhanced test on all 25 bonds"""
    
    print("🚀 COMPREHENSIVE 25-BOND PHASE 1 ENHANCED TEST")
    print("=" * 150)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Project: {PROJECT_ROOT}")
    print(f"📊 Testing: {len(BONDS_25)} bonds")
    print(f"📅 Settlement: 2025-06-30")
    print("🔍 Function: bond_master_hierarchy_enhanced.py")
    print("🚀 Enhancement: Phase 1 - 6 additional XTrillion outputs")
    print("=" * 150)
    
    # Summary counters
    total_bonds = len(BONDS_25)
    successful_calcs = 0
    phase1_enhanced = 0
    treasury_bonds = 0
    corporate_bonds = 0
    
    results_summary = []
    
    # Test each bond
    for i, bond in enumerate(BONDS_25, 1):
        print(f"\n🧪 Testing Bond {i}/{total_bonds}: {bond['isin']} - {bond['name'][:50]}...")
        
        # Test with enhanced function
        result = test_single_bond_enhanced(bond, i)
        
        # Track success rates
        if result.get("success"):
            successful_calcs += 1
            
        # Track Phase 1 enhancement
        if result.get("phase1_outputs_added"):
            phase1_enhanced += 1
        
        # Track bond types
        if "TREASURY" in bond["name"].upper() or bond["name"].startswith("T "):
            treasury_bonds += 1
        else:
            corporate_bonds += 1
        
        # Store for summary
        results_summary.append({
            "bond": bond,
            "result": result
        })
        
        # Print card
        card = format_enhanced_result_card(bond, result, i)
        print(card)
    
    # Print final summary
    print("\n" + "=" * 150)
    print("📈 PHASE 1 ENHANCED FINAL SUMMARY")
    print("=" * 150)
    print(f"📊 Total Bonds Tested: {total_bonds}")
    print(f"✅ Successful Calculations: {successful_calcs}/{total_bonds} ({successful_calcs/total_bonds*100:.1f}%)")
    print(f"🚀 Phase 1 Enhanced: {phase1_enhanced}/{total_bonds} ({phase1_enhanced/total_bonds*100:.1f}%)")
    print(f"🏛️ Treasury Bonds: {treasury_bonds}")
    print(f"🏢 Corporate Bonds: {corporate_bonds}")
    print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Enhanced success criteria analysis
    print("\n🎯 PHASE 1 ENHANCEMENT SUCCESS CRITERIA:")
    if successful_calcs >= total_bonds * 0.95:  # 95% success rate
        print(f"✅ Calculation Success: EXCELLENT ({successful_calcs/total_bonds*100:.1f}% success)")
    elif successful_calcs >= total_bonds * 0.8:  # 80% success rate
        print(f"⚠️ Calculation Success: GOOD ({successful_calcs/total_bonds*100:.1f}% success)")
    else:
        print(f"❌ Calculation Success: NEEDS WORK ({successful_calcs/total_bonds*100:.1f}% success)")
    
    if phase1_enhanced >= total_bonds * 0.95:  # 95% enhancement rate
        print(f"✅ Phase 1 Enhancement: EXCELLENT ({phase1_enhanced/total_bonds*100:.1f}% enhanced)")
    elif phase1_enhanced >= total_bonds * 0.8:  # 80% enhancement rate
        print(f"⚠️ Phase 1 Enhancement: GOOD ({phase1_enhanced/total_bonds*100:.1f}% enhanced)")
    else:
        print(f"❌ Phase 1 Enhancement: NEEDS WORK ({phase1_enhanced/total_bonds*100:.1f}% enhanced)")
    
    # XTrillion compatibility progress
    if phase1_enhanced == successful_calcs:
        print(f"🎯 XTrillion Compatibility: Phase 1 complete - 8/15 total outputs available")
        print(f"📈 Overall Progress: 53.3% towards full XTrillion compatibility")
    
    # Overall assessment
    overall_score = (successful_calcs + phase1_enhanced) / (total_bonds * 2) * 100
    print(f"\n🏆 OVERALL PHASE 1 SCORE: {overall_score:.1f}%")
    
    if overall_score >= 95:
        print("🎉 PHASE 1 COMPLETE! Ready for Phase 2 development!")
    elif overall_score >= 85:
        print("⚠️ PHASE 1 NEARLY COMPLETE - Minor fixes needed")
    elif overall_score >= 70:
        print("🔧 PHASE 1 IN PROGRESS - Good foundation, needs improvement")
    else:
        print("🚨 PHASE 1 ISSUES - Significant work needed")
    
    # Next steps
    if phase1_enhanced >= total_bonds * 0.9:
        print("\n🚀 READY FOR NEXT STEPS:")
        print("   1. ✅ Phase 1 is working excellently!")
        print("   2. 🎯 Ready to implement Phase 2 (7 remaining XTrillion outputs)")
        print("   3. 📊 Consider documenting Phase 1 success and planning Phase 2")
        print("   4. 🔄 Update your main bond calculation workflows to use enhanced function")
    
    return results_summary

if __name__ == "__main__":
    # Change to the correct directory
    os.chdir(PROJECT_ROOT)
    
    # Run the comprehensive enhanced test
    results = main()
