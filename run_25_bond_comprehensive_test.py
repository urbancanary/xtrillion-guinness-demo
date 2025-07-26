#!/usr/bin/env python3
"""
RUN 25-BOND COMPREHENSIVE TESTING
=================================

Executes the 6-way comprehensive testing framework with the actual 25-bond portfolio
from the corrected analytics table (settlement date: 2025-06-30).

This script:
1. Loads the 25 bonds from the corrected analytics table
2. Runs 6-way testing (Direct Local ±ISIN, Local API ±ISIN, Cloud API ±ISIN)
3. Compares with Bloomberg baseline (from analytics table)
4. Generates comprehensive analysis and deployment recommendations
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to path
sys.path.append('.')

# Import the comprehensive testing framework
from comprehensive_6way_tester import ComprehensiveBondTester

def get_25_bond_portfolio():
    """
    Extract the 25-bond portfolio from the corrected analytics table
    Settlement Date: 2025-06-30 (CORRECTED - prior month end)
    """
    bonds_25_portfolio = [
        {"isin": "US912810TJ79", "price": 71.66, "weighting": 8.09, "description": "US TREASURY N/B, 3%, 15-Aug-2052"},
        {"isin": "XS2249741674", "price": 77.88, "weighting": 3.88, "description": "GALAXY PIPELINE, 3.25%, 30-Sep-2040"},
        {"isin": "XS1709535097", "price": 89.40, "weighting": 4.12, "description": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047"},
        {"isin": "XS1982113463", "price": 87.14, "weighting": 4.12, "description": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039"},
        {"isin": "USP37466AS18", "price": 80.39, "weighting": 4.12, "description": "EMPRESA METRO, 4.7%, 07-May-2050"},
        {"isin": "USP3143NAH72", "price": 101.63, "weighting": 4.05, "description": "CODELCO INC, 6.15%, 24-Oct-2036"},
        {"isin": "USP30179BR86", "price": 86.42, "weighting": 4.05, "description": "COMISION FEDERAL, 6.264%, 15-Feb-2052"},
        {"isin": "US195325DX04", "price": 52.71, "weighting": 4.05, "description": "COLOMBIA REP OF, 3.875%, 15-Feb-2061"},
        {"isin": "US279158AJ82", "price": 69.31, "weighting": 3.95, "description": "ECOPETROL SA, 5.875%, 28-May-2045"},
        {"isin": "USP37110AM89", "price": 76.24, "weighting": 3.95, "description": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047"},
        {"isin": "XS2542166231", "price": 103.03, "weighting": 3.95, "description": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038"},
        {"isin": "XS2167193015", "price": 64.50, "weighting": 3.93, "description": "STATE OF ISRAEL, 3.8%, 13-May-2060"},
        {"isin": "XS1508675508", "price": 82.42, "weighting": 3.93, "description": "SAUDI INT BOND, 4.5%, 26-Oct-2046"},
        {"isin": "XS1807299331", "price": 92.21, "weighting": 3.93, "description": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048"},
        {"isin": "US91086QAZ19", "price": 78.00, "weighting": 3.93, "description": "UNITED MEXICAN, 5.75%, 12-Oct-2110"},
        {"isin": "USP6629MAD40", "price": 82.57, "weighting": 3.90, "description": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047"},
        {"isin": "US698299BL70", "price": 56.60, "weighting": 3.90, "description": "PANAMA, 3.87%, 23-Jul-2060"},
        {"isin": "US71654QDF63", "price": 71.42, "weighting": 3.90, "description": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060"},
        {"isin": "US71654QDE98", "price": 89.55, "weighting": 3.90, "description": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031"},
        {"isin": "XS2585988145", "price": 85.54, "weighting": 3.88, "description": "GACI FIRST INVST, 5.125%, 14-Feb-2053"},
        {"isin": "XS1959337749", "price": 89.97, "weighting": 3.88, "description": "QATAR STATE OF, 4.817%, 14-Mar-2049"},
        {"isin": "XS2233188353", "price": 99.23, "weighting": 3.88, "description": "QNB FINANCE LTD, 1.625%, 22-Sep-2025"},
        {"isin": "XS2359548935", "price": 73.79, "weighting": 3.85, "description": "QATAR ENERGY, 3.125%, 12-Jul-2041"},
        {"isin": "XS0911024635", "price": 93.29, "weighting": 3.85, "description": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043"},
        {"isin": "USP0R80BAG79", "price": 97.26, "weighting": 3.85, "description": "SITIOS, 5.375%, 04-Apr-2032"}
    ]
    
    print(f"📊 Loaded 25-bond portfolio with total weighting: {sum(bond['weighting'] for bond in bonds_25_portfolio):.2f}%")
    return bonds_25_portfolio

def get_bloomberg_baseline():
    """
    Bloomberg baseline results from the corrected analytics table
    These are the "actual" results we should validate against
    """
    bloomberg_actuals = {
        "US912810TJ79": {"yield": 4.89916, "duration": 16.35658, "spread": 39.91632},
        "XS2249741674": {"yield": 5.39556, "duration": 11.22303, "spread": 89.55584},
        "XS1709535097": {"yield": 5.42359, "duration": 13.21138, "spread": 92.35907},
        "XS1982113463": {"yield": 5.59944, "duration": 9.93052, "spread": 109.94388},
        "USP37466AS18": {"yield": 6.26618, "duration": 13.18176, "spread": 176.61783},
        "USP3143NAH72": {"yield": 5.94874, "duration": 8.01689, "spread": 144.87434},
        "USP30179BR86": {"yield": 7.44217, "duration": 11.58710, "spread": 294.21683},
        "US195325DX04": {"yield": 7.83636, "duration": 12.97993, "spread": 333.63631},
        "US279158AJ82": {"yield": 9.28195, "duration": 9.80447, "spread": 478.19491},
        "USP37110AM89": {"yield": 6.54274, "duration": 12.38229, "spread": 204.27423},
        "XS2542166231": {"yield": 5.78691, "duration": 8.61427, "spread": 128.69067},
        "XS2167193015": {"yield": 6.33756, "duration": 15.26825, "spread": 183.75586},
        "XS1508675508": {"yield": 5.96747, "duration": 12.60204, "spread": 146.74727},
        "XS1807299331": {"yield": 7.05978, "duration": 11.44784, "spread": 255.97846},
        "US91086QAZ19": {"yield": 7.37494, "duration": 13.36798, "spread": 287.49419},
        "USP6629MAD40": {"yield": 7.07038, "duration": 11.37892, "spread": 257.03820},
        "US698299BL70": {"yield": 7.32679, "duration": 13.57604, "spread": 282.67859},
        "US71654QDF63": {"yield": 9.87572, "duration": 9.71461, "spread": 537.57173},
        "US71654QDE98": {"yield": 8.32733, "duration": 4.46458, "spread": 382.73346},
        "XS2585988145": {"yield": 6.22763, "duration": 13.33263, "spread": 172.76259},
        "XS1959337749": {"yield": 5.58469, "duration": 13.26146, "spread": 108.46879},
        "XS2233188353": {"yield": 5.02106, "duration": 0.22450, "spread": 52.10619},
        "XS2359548935": {"yield": 5.62805, "duration": 11.51499, "spread": 112.80529},
        "XS0911024635": {"yield": 5.66298, "duration": 11.23839, "spread": 116.29823},
        "USP0R80BAG79": {"yield": 5.86969, "duration": 5.51011, "spread": 136.96853}
    }
    
    print(f"📈 Loaded Bloomberg baseline for {len(bloomberg_actuals)} bonds")
    return bloomberg_actuals

def main():
    """
    Main comprehensive testing execution
    """
    print("🏛️ 25-BOND COMPREHENSIVE TESTING FRAMEWORK")
    print("=" * 80)
    print("🎯 TESTING STRATEGY:")
    print("   • 25 bonds from corrected analytics table")
    print("   • Settlement Date: 2025-06-30 (CORRECTED - prior month end)")
    print("   • 6-way testing: Direct Local ±ISIN, Local API ±ISIN, Cloud API ±ISIN")
    print("   • Bloomberg baseline validation with 5 decimal precision")
    print("   • Database gap analysis and deployment readiness assessment")
    print("=" * 80)
    
    # Load the 25-bond portfolio
    bonds_portfolio = get_25_bond_portfolio()
    
    # Load Bloomberg baseline
    bloomberg_baseline = get_bloomberg_baseline()
    
    # Initialize the comprehensive testing framework
    tester = ComprehensiveBondTester(
        local_api_url="http://localhost:8080",
        cloud_api_url=None  # Will be set when cloud is deployed
    )
    
    # Load Bloomberg baseline for comparison
    tester.load_bloomberg_actuals(bloomberg_baseline)
    
    print(f"\n🚀 STARTING COMPREHENSIVE 6-WAY TESTING...")
    print(f"   📊 Testing {len(bonds_portfolio)} bonds")
    print(f"   📈 Bloomberg baseline loaded for accuracy validation")
    print(f"   🎯 Settlement date: 2025-06-30 (corrected)")
    
    # Run comprehensive tests with corrected settlement date
    settlement_date = "2025-06-30"  # CORRECTED prior month end
    
    results = tester.test_all_bonds(bonds_portfolio, settlement_date=settlement_date)
    
    print(f"\n✅ TESTING COMPLETED for all {len(results)} bonds")
    
    # Generate and save comprehensive reports
    print(f"\n📊 GENERATING COMPREHENSIVE ANALYSIS...")
    results_file, report_file = tester.save_results("bond_25_comprehensive_test")
    
    # Print executive summary with deployment recommendation
    print(f"\n" + "=" * 100)
    tester.print_executive_summary()
    
    # Additional detailed analysis
    print(f"\n📋 DETAILED ANALYSIS:")
    print(f"   📁 Results saved to: {results_file}")
    print(f"   📁 Report saved to: {report_file}")
    
    # Check for specific issues
    report = tester.generate_comprehensive_report()
    
    print(f"\n🔍 DATABASE COVERAGE ANALYSIS:")
    direct_local_success = report["success_rates"].get("direct_local_with_isin", {}).get("rate", 0)
    parser_fallback_success = report["success_rates"].get("direct_local_without_isin", {}).get("rate", 0)
    
    if direct_local_success < 100:
        missing_bonds = 100 - direct_local_success
        print(f"   ⚠️  Database missing {missing_bonds:.0f}% of bonds - parser fallback needed")
        print(f"   📊 Parser fallback success rate: {parser_fallback_success:.1f}%")
    else:
        print(f"   ✅ Database coverage: 100% - all bonds found in database")
    
    print(f"\n🎯 DEPLOYMENT READINESS:")
    bloomberg_accuracy = report.get("bloomberg_comparison", {}).get("method_accuracy", {})
    
    if bloomberg_accuracy:
        best_method = None
        best_accuracy = 0
        for method_key, data in bloomberg_accuracy.items():
            accuracy = data.get("accuracy_rate", 0)
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_method = data.get("name", method_key)
        
        print(f"   🏆 Best performing method: {best_method} ({best_accuracy:.1f}% accuracy)")
        
        if best_accuracy >= 95:
            print(f"   ✅ READY FOR CLOUD DEPLOYMENT - Excellent Bloomberg accuracy")
        elif best_accuracy >= 90:
            print(f"   ⚠️  PROCEED WITH CAUTION - Good but monitor cloud results")
        else:
            print(f"   ❌ FIX ISSUES BEFORE DEPLOYMENT - Low Bloomberg accuracy")
    
    print(f"\n🌟 NEXT STEPS:")
    print(f"   1. Review detailed results in: {results_file}")
    print(f"   2. Analyze discrepancies in: {report_file}")
    print(f"   3. Fix any database coverage gaps identified")
    print(f"   4. Deploy to cloud if readiness criteria met")
    print(f"   5. Repeat testing on cloud deployment")
    
    print("=" * 100)
    
    return tester, results, report

if __name__ == "__main__":
    # Execute comprehensive testing
    tester, results, report = main()
    print(f"\n🎉 COMPREHENSIVE 25-BOND TESTING COMPLETE!")
    print(f"💡 Use returned objects for further analysis:")
    print(f"   - tester: ComprehensiveBondTester instance")
    print(f"   - results: Detailed test results")
    print(f"   - report: Comprehensive analysis report")
