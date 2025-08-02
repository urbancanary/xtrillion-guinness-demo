#!/usr/bin/env python3
"""
Bloomberg ISIN Baseline Test - Comprehensive Comparison
========================================================
Tests our local API against Bloomberg baseline values for bonds with ISINs.
Compares Duration, Yield, and Spread metrics.
"""

import requests
import json
import pandas as pd
import time
from datetime import datetime
from typing import Dict, List, Optional

# Local API Configuration
LOCAL_API_URL = "http://localhost:8080"  # Local google_analysis10 API
API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q"

# Bloomberg Baseline Data
BLOOMBERG_BASELINE = [
    {"ISIN": "US912810TJ79", "PX_MID": 71.66, "Name": "US TREASURY N/B, 3%, 15-Aug-2052", "Duration": 16.357839, "Yield": 4.898453, "Spread": None},
    {"ISIN": "XS2249741674", "PX_MID": 77.88, "Name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040", "Duration": 10.097620, "Yield": 5.637570, "Spread": 118},
    {"ISIN": "XS1709535097", "PX_MID": 89.40, "Name": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047", "Duration": 9.815219, "Yield": 5.717451, "Spread": 123},
    {"ISIN": "XS1982113463", "PX_MID": 87.14, "Name": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039", "Duration": 9.927596, "Yield": 5.599746, "Spread": 111},
    {"ISIN": "USP37466AS18", "PX_MID": 80.39, "Name": "EMPRESA METRO, 4.7%, 07-May-2050", "Duration": 13.189567, "Yield": 6.265800, "Spread": 144},
    {"ISIN": "USP3143NAH72", "PX_MID": 101.63, "Name": "CODELCO INC, 6.15%, 24-Oct-2036", "Duration": 8.024166, "Yield": 5.949058, "Spread": 160},
    {"ISIN": "USP30179BR86", "PX_MID": 86.42, "Name": "COMISION FEDERAL, 6.264%, 15-Feb-2052", "Duration": 11.583500, "Yield": 7.442306, "Spread": 261},
    {"ISIN": "US195325DX04", "PX_MID": 52.71, "Name": "COLOMBIA REP OF, 3.875%, 15-Feb-2061", "Duration": 12.975798, "Yield": 7.836133, "Spread": 301},
    {"ISIN": "US279158AJ82", "PX_MID": 69.31, "Name": "ECOPETROL SA, 5.875%, 28-May-2045", "Duration": 9.812703, "Yield": 9.282266, "Spread": 445},
    {"ISIN": "USP37110AM89", "PX_MID": 76.24, "Name": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047", "Duration": 12.389556, "Yield": 6.542351, "Spread": 171},
    {"ISIN": "XS2542166231", "PX_MID": 103.03, "Name": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038", "Duration": 7.207705, "Yield": 5.720213, "Spread": 146},
    {"ISIN": "XS2167193015", "PX_MID": 64.50, "Name": "STATE OF ISRAEL, 3.8%, 13-May-2060", "Duration": 15.269052, "Yield": 6.337460, "Spread": 151},
    {"ISIN": "XS1508675508", "PX_MID": 82.42, "Name": "SAUDI INT BOND, 4.5%, 26-Oct-2046", "Duration": 12.598517, "Yield": 5.967150, "Spread": 114},
    {"ISIN": "XS1807299331", "PX_MID": 92.21, "Name": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048", "Duration": 11.446459, "Yield": 7.059957, "Spread": 223},
    {"ISIN": "US91086QAZ19", "PX_MID": 78.00, "Name": "UNITED MEXICAN, 5.75%, 12-Oct-2110", "Duration": 13.370728, "Yield": 7.374879, "Spread": 255},
    {"ISIN": "USP6629MAD40", "PX_MID": 82.57, "Name": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047", "Duration": 11.382487, "Yield": 7.070132, "Spread": 224},
    {"ISIN": "US698299BL70", "PX_MID": 56.60, "Name": "PANAMA, 3.87%, 23-Jul-2060", "Duration": 13.488582, "Yield": 7.362747, "Spread": 253},
    {"ISIN": "US71654QDF63", "PX_MID": 71.42, "Name": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060", "Duration": 9.719713, "Yield": 9.875691, "Spread": 505},
    {"ISIN": "US71654QDE98", "PX_MID": 89.55, "Name": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031", "Duration": 4.469801, "Yield": 8.324595, "Spread": 444},
    {"ISIN": "XS2585988145", "PX_MID": 85.54, "Name": "GACI FIRST INVST, 5.125%, 14-Feb-2053", "Duration": 13.327227, "Yield": 6.228001, "Spread": 140},
    {"ISIN": "XS1959337749", "PX_MID": 89.97, "Name": "QATAR STATE OF, 4.817%, 14-Mar-2049", "Duration": 13.261812, "Yield": 5.584981, "Spread": 76},
    {"ISIN": "XS2233188353", "PX_MID": 99.23, "Name": "QNB FINANCE LTD, 1.625%, 22-Sep-2025", "Duration": 0.225205, "Yield": 5.015259, "Spread": 71},
    {"ISIN": "XS2359548935", "PX_MID": 73.79, "Name": "QATAR ENERGY, 3.125%, 12-Jul-2041", "Duration": 11.512115, "Yield": 5.628065, "Spread": 101},
    {"ISIN": "XS0911024635", "PX_MID": 93.29, "Name": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043", "Duration": 11.237819, "Yield": 5.663334, "Spread": 95},
    {"ISIN": "USP0R80BAG79", "PX_MID": 97.26, "Name": "SITIOS, 5.375%, 04-Apr-2032", "Duration": 5.514383, "Yield": 5.870215, "Spread": 187}
]

def test_local_api_health():
    """Test if local API is running"""
    try:
        response = requests.get(f"{LOCAL_API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Local API is healthy")
            return True
        else:
            print(f"❌ Local API returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to local API: {e}")
        print("💡 Make sure to start local API: python3 google_analysis10_api.py")
        return False

def call_local_bond_api(isin: str, price: float) -> Dict:
    """Call local bond analysis API"""
    try:
        url = f"{LOCAL_API_URL}/api/v1/bond/analysis"
        
        payload = {
            "isin": isin,
            "price": price
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "status": "error",
                "error": f"API returned {response.status_code}",
                "details": response.text[:200]
            }
            
    except Exception as e:
        return {"status": "error", "error": str(e)}

def analyze_bond_comparison(bloomberg_bond: Dict, api_result: Dict) -> Dict:
    """Analyze differences between Bloomberg and API results"""
    
    if api_result.get("status") != "success":
        return {
            "status": "API_ERROR",
            "error": api_result.get("error", "Unknown error"),
            "yield_diff": None,
            "duration_diff": None,
            "spread_diff": None
        }
    
    analytics = api_result.get("analytics", {})
    
    # Extract values
    api_yield = analytics.get("ytm", 0)
    api_duration = analytics.get("duration", 0)
    api_spread = analytics.get("spread")
    
    bbg_yield = bloomberg_bond["Yield"]
    bbg_duration = bloomberg_bond["Duration"]
    bbg_spread = bloomberg_bond["Spread"]
    
    # Calculate differences
    yield_diff = api_yield - bbg_yield if api_yield and bbg_yield else None
    duration_diff = api_duration - bbg_duration if api_duration and bbg_duration else None
    spread_diff = (api_spread or 0) - (bbg_spread or 0) if bbg_spread is not None else None
    
    # Determine match quality
    yield_match = abs(yield_diff) < 0.01 if yield_diff is not None else False  # 1bp tolerance
    duration_match = abs(duration_diff) < 0.01 if duration_diff is not None else False  # 0.01 year tolerance
    spread_match = abs(spread_diff) < 5 if spread_diff is not None else (api_spread is None and bbg_spread is None)  # 5bp tolerance
    
    if yield_match and duration_match and spread_match:
        match_quality = "PERFECT"
    elif yield_match and duration_match:
        match_quality = "EXCELLENT"
    elif abs(yield_diff or 0) < 0.05 and abs(duration_diff or 0) < 0.1:
        match_quality = "GOOD"
    else:
        match_quality = "POOR"
    
    return {
        "status": "SUCCESS",
        "match_quality": match_quality,
        "api_yield": api_yield,
        "api_duration": api_duration,
        "api_spread": api_spread,
        "yield_diff": yield_diff,
        "duration_diff": duration_diff,
        "spread_diff": spread_diff,
        "yield_match": yield_match,
        "duration_match": duration_match,
        "spread_match": spread_match,
        "route_used": api_result.get("bond", {}).get("route_used", "unknown")
    }

def run_comprehensive_test():
    """Run comprehensive test against Bloomberg baseline"""
    
    print("🎯 Bloomberg ISIN Baseline Test - Comprehensive Comparison")
    print("=" * 80)
    print(f"📊 Testing {len(BLOOMBERG_BASELINE)} bonds with ISINs")
    print(f"🌐 Local API: {LOCAL_API_URL}")
    print()
    
    # Test API health
    if not test_local_api_health():
        return
    
    print()
    print("🚀 Starting bond analysis comparison...")
    print("-" * 80)
    
    results = []
    success_count = 0
    perfect_matches = 0
    excellent_matches = 0
    good_matches = 0
    
    for i, bloomberg_bond in enumerate(BLOOMBERG_BASELINE, 1):
        isin = bloomberg_bond["ISIN"]
        price = bloomberg_bond["PX_MID"]
        name = bloomberg_bond["Name"]
        
        print(f"\n📊 Bond {i:2d}/{len(BLOOMBERG_BASELINE)}: {name[:40]}...")
        print(f"   ISIN: {isin} | Price: {price}")
        
        # Call API
        api_result = call_local_bond_api(isin, price)
        
        # Analyze comparison
        comparison = analyze_bond_comparison(bloomberg_bond, api_result)
        
        # Display results
        if comparison["status"] == "SUCCESS":
            success_count += 1
            
            print(f"   ✅ Status: {comparison['match_quality']}")
            print(f"   📈 Yield:    BBG: {bloomberg_bond['Yield']:7.4f}% | API: {comparison['api_yield']:7.4f}% | Diff: {comparison['yield_diff']:+7.4f}%")
            print(f"   ⏱️  Duration: BBG: {bloomberg_bond['Duration']:7.4f}y | API: {comparison['api_duration']:7.4f}y | Diff: {comparison['duration_diff']:+7.4f}y")
            
            if bloomberg_bond['Spread'] is not None:
                print(f"   📊 Spread:   BBG: {bloomberg_bond['Spread']:7.0f}bp | API: {comparison['api_spread'] or 0:7.0f}bp | Diff: {comparison['spread_diff']:+7.0f}bp")
            else:
                print(f"   📊 Spread:   BBG: Treasury    | API: {comparison['api_spread'] or 0:7.0f}bp | (Treasury baseline)")
            
            print(f"   🛤️  Route: {comparison['route_used']}")
            
            # Count match quality
            if comparison['match_quality'] == 'PERFECT':
                perfect_matches += 1
            elif comparison['match_quality'] == 'EXCELLENT':
                excellent_matches += 1
            elif comparison['match_quality'] == 'GOOD':
                good_matches += 1
        else:
            print(f"   ❌ Error: {comparison.get('error', 'Unknown error')}")
        
        # Store result
        result = {
            "Bond": name[:30] + "..." if len(name) > 30 else name,
            "ISIN": isin,
            "Price": price,
            "BBG_Yield": bloomberg_bond["Yield"],
            "API_Yield": comparison.get("api_yield", "ERROR"),
            "Yield_Diff": comparison.get("yield_diff", "N/A"),
            "BBG_Duration": bloomberg_bond["Duration"],
            "API_Duration": comparison.get("api_duration", "ERROR"),
            "Duration_Diff": comparison.get("duration_diff", "N/A"),
            "BBG_Spread": bloomberg_bond["Spread"],
            "API_Spread": comparison.get("api_spread", "ERROR"),
            "Spread_Diff": comparison.get("spread_diff", "N/A"),
            "Match_Quality": comparison.get("match_quality", "ERROR"),
            "Route": comparison.get("route_used", "N/A")
        }
        results.append(result)
        
        # Small delay to be respectful
        time.sleep(0.2)
    
    # Summary Statistics
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
    print("=" * 80)
    
    print(f"📈 Total Bonds Tested: {len(BLOOMBERG_BASELINE)}")
    print(f"✅ Successful Calculations: {success_count} ({success_count/len(BLOOMBERG_BASELINE)*100:.1f}%)")
    print(f"🎯 Perfect Matches: {perfect_matches} ({perfect_matches/len(BLOOMBERG_BASELINE)*100:.1f}%)")
    print(f"⭐ Excellent Matches: {excellent_matches} ({excellent_matches/len(BLOOMBERG_BASELINE)*100:.1f}%)")
    print(f"👍 Good Matches: {good_matches} ({good_matches/len(BLOOMBERG_BASELINE)*100:.1f}%)")
    
    total_good_or_better = perfect_matches + excellent_matches + good_matches
    print(f"🚀 Overall Success Rate: {total_good_or_better}/{len(BLOOMBERG_BASELINE)} ({total_good_or_better/len(BLOOMBERG_BASELINE)*100:.1f}%)")
    
    # Save detailed results to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"bloomberg_isin_baseline_comparison_{timestamp}.csv"
    
    df = pd.DataFrame(results)
    df.to_csv(csv_filename, index=False)
    
    print(f"\n💾 Detailed results saved to: {csv_filename}")
    
    # Display summary table
    print("\n📋 DETAILED COMPARISON TABLE")
    print("-" * 120)
    
    # Configure pandas display
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 120)
    pd.set_option('display.max_colwidth', 25)
    
    # Show key columns
    summary_df = df[['Bond', 'ISIN', 'BBG_Yield', 'API_Yield', 'Yield_Diff', 
                     'BBG_Duration', 'API_Duration', 'Duration_Diff', 'Match_Quality']].copy()
    
    print(summary_df.to_string(index=False))
    
    return results

if __name__ == "__main__":
    print("🎯 Starting Bloomberg ISIN Baseline Test...")
    print("💡 Make sure local API is running: python3 google_analysis10_api.py")
    print()
    
    results = run_comprehensive_test()
    
    print("\n🎉 Test Complete!")
    print("📊 Check the CSV file for detailed analysis")
    print("🔍 Review any POOR matches for potential improvements")
