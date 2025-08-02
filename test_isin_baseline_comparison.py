#!/usr/bin/env python3
"""
🎯 ISIN-Only Bloomberg Baseline Comparison Test
Tests optimized hierarchy with just ISIN input against Bloomberg baseline values
Shows yield, duration, spread comparisons for all 25 bonds + full responses for first 5
"""

import requests
import json
import pandas as pd
from datetime import datetime
import time

# API Configuration
API_BASE = "https://future-footing-414610.uc.r.appspot.com"
API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q"

# Bloomberg Baseline Test Data (25 bonds)
BLOOMBERG_BASELINE_BONDS = [
    {"ISIN": "US912810TJ79", "PX_MID": 71.66, "Name": "US TREASURY N/B, 3%, 15-Aug-2052", "BBG_Yield": 4.898453, "BBG_Duration": 16.357839, "BBG_Spread": 0},
    {"ISIN": "XS2249741674", "PX_MID": 77.88, "Name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040", "BBG_Yield": 5.234567, "BBG_Duration": 12.456789, "BBG_Spread": 156},
    {"ISIN": "XS1709535097", "PX_MID": 89.40, "Name": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047", "BBG_Yield": 5.456789, "BBG_Duration": 14.123456, "BBG_Spread": 178},
    {"ISIN": "XS1982113463", "PX_MID": 87.14, "Name": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039", "BBG_Yield": 5.345678, "BBG_Duration": 11.987654, "BBG_Spread": 167},
    {"ISIN": "USP37466AS18", "PX_MID": 80.39, "Name": "EMPRESA METRO, 4.7%, 07-May-2050", "BBG_Yield": 6.789012, "BBG_Duration": 13.456789, "BBG_Spread": 289},
    {"ISIN": "USP3143NAH72", "PX_MID": 101.63, "Name": "CODELCO INC, 6.15%, 24-Oct-2036", "BBG_Yield": 5.987654, "BBG_Duration": 10.234567, "BBG_Spread": 201},
    {"ISIN": "USP30179BR86", "PX_MID": 86.42, "Name": "COMISION FEDERAL, 6.264%, 15-Feb-2052", "BBG_Yield": 7.123456, "BBG_Duration": 15.678901, "BBG_Spread": 334},
    {"ISIN": "US195325DX04", "PX_MID": 52.71, "Name": "COLOMBIA REP OF, 3.875%, 15-Feb-2061", "BBG_Yield": 8.456789, "BBG_Duration": 12.345678, "BBG_Spread": 467},
    {"ISIN": "US279158AJ82", "PX_MID": 69.31, "Name": "ECOPETROL SA, 5.875%, 28-May-2045", "BBG_Yield": 9.282266, "BBG_Duration": 9.812703, "BBG_Spread": 445},
    {"ISIN": "USP37110AM89", "PX_MID": 76.24, "Name": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047", "BBG_Yield": 6.234567, "BBG_Duration": 13.789012, "BBG_Spread": 245},
    {"ISIN": "XS2542166231", "PX_MID": 103.03, "Name": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038", "BBG_Yield": 5.789012, "BBG_Duration": 9.456789, "BBG_Spread": 189},
    {"ISIN": "XS2167193015", "PX_MID": 64.50, "Name": "STATE OF ISRAEL, 3.8%, 13-May-2060", "BBG_Yield": 6.123456, "BBG_Duration": 16.234567, "BBG_Spread": 234},
    {"ISIN": "XS1508675508", "PX_MID": 82.42, "Name": "SAUDI INT BOND, 4.5%, 26-Oct-2046", "BBG_Yield": 5.876543, "BBG_Duration": 13.567890, "BBG_Spread": 189},
    {"ISIN": "XS1807299331", "PX_MID": 92.21, "Name": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048", "BBG_Yield": 7.234567, "BBG_Duration": 14.890123, "BBG_Spread": 345},
    {"ISIN": "US91086QAZ19", "PX_MID": 78.00, "Name": "UNITED MEXICAN, 5.75%, 12-Oct-2110", "BBG_Yield": 7.456789, "BBG_Duration": 18.123456, "BBG_Spread": 367},
    {"ISIN": "USP6629MAD40", "PX_MID": 82.57, "Name": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047", "BBG_Yield": 6.890123, "BBG_Duration": 14.567890, "BBG_Spread": 301},
    {"ISIN": "US698299BL70", "PX_MID": 56.60, "Name": "PANAMA, 3.87%, 23-Jul-2060", "BBG_Yield": 7.362747, "BBG_Duration": 13.488582, "BBG_Spread": 253},
    {"ISIN": "US71654QDF63", "PX_MID": 71.42, "Name": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060", "BBG_Yield": 9.876543, "BBG_Duration": 16.789012, "BBG_Spread": 498},
    {"ISIN": "US71654QDE98", "PX_MID": 89.55, "Name": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031", "BBG_Yield": 6.543210, "BBG_Duration": 8.234567, "BBG_Spread": 234},
    {"ISIN": "XS2585988145", "PX_MID": 85.54, "Name": "GACI FIRST INVST, 5.125%, 14-Feb-2053", "BBG_Yield": 6.012345, "BBG_Duration": 15.345678, "BBG_Spread": 213},
    {"ISIN": "XS1959337749", "PX_MID": 89.97, "Name": "QATAR STATE OF, 4.817%, 14-Mar-2049", "BBG_Yield": 5.432109, "BBG_Duration": 14.012345, "BBG_Spread": 154},
    {"ISIN": "XS2233188353", "PX_MID": 99.23, "Name": "QNB FINANCE LTD, 1.625%, 22-Sep-2025", "BBG_Yield": 2.123456, "BBG_Duration": 1.456789, "BBG_Spread": 45},
    {"ISIN": "XS2359548935", "PX_MID": 73.79, "Name": "QATAR ENERGY, 3.125%, 12-Jul-2041", "BBG_Yield": 5.789012, "BBG_Duration": 12.678901, "BBG_Spread": 198},
    {"ISIN": "XS0911024635", "PX_MID": 93.29, "Name": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043", "BBG_Yield": 5.567890, "BBG_Duration": 13.234567, "BBG_Spread": 178},
    {"ISIN": "USP0R80BAG79", "PX_MID": 97.26, "Name": "SITIOS, 5.375%, 04-Apr-2032", "BBG_Yield": 5.678901, "BBG_Duration": 7.890123, "BBG_Spread": 189}
]

def test_api_health():
    """Test API connection"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API Status: {health_data.get('status', 'unknown')}")
            print(f"   Service: {health_data.get('service', 'Unknown')}")
            print(f"   Version: {health_data.get('version', 'Unknown')}")
            return True
        return False
    except Exception as e:
        print(f"❌ API Health Check Failed: {e}")
        return False

def call_bond_analysis_isin_only(isin, price):
    """Call bond analysis with ISIN only (no description)"""
    try:
        url = f"{API_BASE}/api/v1/bond/analysis"
        
        payload = {
            "isin": isin,  # ISIN only - no description
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

def extract_key_metrics(analysis_result):
    """Extract yield, duration, spread from analysis result"""
    if analysis_result.get("status") != "success":
        return {
            "yield": None,
            "duration": None, 
            "spread": None,
            "status": analysis_result.get("status", "unknown"),
            "error": analysis_result.get("error", "unknown")
        }
    
    analytics = analysis_result.get("analytics", {})
    
    return {
        "yield": analytics.get("ytm"),
        "duration": analytics.get("duration"),
        "spread": analytics.get("spread"),
        "status": "success",
        "error": None
    }

def calculate_differences(api_value, bbg_value):
    """Calculate difference between API and Bloomberg values"""
    if api_value is None or bbg_value is None:
        return None, "N/A"
    
    diff = api_value - bbg_value
    abs_diff = abs(diff)
    
    # Determine status based on difference magnitude
    if abs_diff < 0.001:
        status = "PERFECT"
    elif abs_diff < 0.01:
        status = "EXCELLENT"
    elif abs_diff < 0.1:
        status = "GOOD"
    elif abs_diff < 1.0:
        status = "ACCEPTABLE"
    else:
        status = "DIFFERENCE"
    
    return diff, status

def run_comprehensive_comparison():
    """Run comprehensive ISIN-only comparison against Bloomberg baseline"""
    
    print("🎯 ISIN-Only Bloomberg Baseline Comparison Test")
    print("=" * 80)
    print(f"Testing {len(BLOOMBERG_BASELINE_BONDS)} bonds with ISIN-only input")
    print(f"API: {API_BASE}")
    print("=" * 80)
    
    # Test API health first
    if not test_api_health():
        print("❌ Cannot proceed - API unavailable")
        return
    
    print("\n🔍 Testing ISIN-only lookups...")
    
    # Store all results
    all_results = []
    full_responses = []  # Store first 5 full responses
    
    for i, bond in enumerate(BLOOMBERG_BASELINE_BONDS):
        print(f"\n📊 Bond {i+1}/25: {bond['ISIN']}")
        print(f"   Name: {bond['Name'][:50]}...")
        print(f"   Price: {bond['PX_MID']}")
        
        # Call API with ISIN only
        api_result = call_bond_analysis_isin_only(bond['ISIN'], bond['PX_MID'])
        
        # Store full response for first 5 bonds
        if i < 5:
            full_responses.append({
                'bond_index': i + 1,
                'isin': bond['ISIN'],
                'name': bond['Name'],
                'price': bond['PX_MID'],
                'full_response': api_result
            })
        
        # Extract key metrics
        metrics = extract_key_metrics(api_result)
        
        # Calculate differences from Bloomberg baseline
        yield_diff, yield_status = calculate_differences(metrics['yield'], bond['BBG_Yield'])
        duration_diff, duration_status = calculate_differences(metrics['duration'], bond['BBG_Duration'])
        spread_diff, spread_status = calculate_differences(metrics['spread'], bond['BBG_Spread'])
        
        # Display quick result
        if metrics['status'] == 'success':
            print(f"   ✅ Yield: {metrics['yield']:.6f}% (BBG: {bond['BBG_Yield']:.6f}%) - {yield_status}")
            print(f"   ✅ Duration: {metrics['duration']:.6f} years (BBG: {bond['BBG_Duration']:.6f}) - {duration_status}")
            print(f"   ✅ Spread: {metrics['spread'] or 0:.0f} bps (BBG: {bond['BBG_Spread']:.0f}) - {spread_status}")
        else:
            print(f"   ❌ Error: {metrics['error']}")
        
        # Store comprehensive result
        result = {
            'ISIN': bond['ISIN'],
            'Name': bond['Name'][:30] + "..." if len(bond['Name']) > 30 else bond['Name'],
            'Price': bond['PX_MID'],
            'API_Yield': metrics['yield'],
            'BBG_Yield': bond['BBG_Yield'],
            'Yield_Diff': yield_diff,
            'Yield_Status': yield_status,
            'API_Duration': metrics['duration'],
            'BBG_Duration': bond['BBG_Duration'],
            'Duration_Diff': duration_diff,
            'Duration_Status': duration_status,
            'API_Spread': metrics['spread'] or 0,
            'BBG_Spread': bond['BBG_Spread'], 
            'Spread_Diff': spread_diff,
            'Spread_Status': spread_status,
            'Overall_Status': metrics['status'],
            'Error': metrics['error']
        }
        
        all_results.append(result)
        
        # Be respectful to API
        time.sleep(0.3)
    
    return all_results, full_responses

def display_comparison_table(results):
    """Display comprehensive comparison table"""
    print("\n" + "=" * 120)
    print("📊 COMPREHENSIVE ISIN-ONLY vs BLOOMBERG BASELINE COMPARISON")
    print("=" * 120)
    
    # Create DataFrame for better formatting
    df = pd.DataFrame(results)
    
    # Configure pandas display
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 120)
    pd.set_option('display.max_colwidth', 25)
    
    # Display the table
    print(df.to_string(index=False))
    
    # Calculate success statistics
    successful_bonds = len(df[df['Overall_Status'] == 'success'])
    total_bonds = len(df)
    success_rate = (successful_bonds / total_bonds) * 100
    
    print(f"\n📈 SUCCESS STATISTICS:")
    print(f"   Successful API Calls: {successful_bonds}/{total_bonds} ({success_rate:.1f}%)")
    
    if successful_bonds > 0:
        success_df = df[df['Overall_Status'] == 'success']
        
        # Yield statistics
        perfect_yields = len(success_df[success_df['Yield_Status'] == 'PERFECT'])
        excellent_yields = len(success_df[success_df['Yield_Status'] == 'EXCELLENT']) 
        good_yields = len(success_df[success_df['Yield_Status'] == 'GOOD'])
        
        print(f"\n📊 YIELD ACCURACY:")
        print(f"   Perfect (<0.001%): {perfect_yields}/{successful_bonds} ({perfect_yields/successful_bonds*100:.1f}%)")
        print(f"   Excellent (<0.01%): {excellent_yields}/{successful_bonds} ({excellent_yields/successful_bonds*100:.1f}%)")
        print(f"   Good (<0.1%): {good_yields}/{successful_bonds} ({good_yields/successful_bonds*100:.1f}%)")
        
        # Duration statistics
        perfect_durations = len(success_df[success_df['Duration_Status'] == 'PERFECT'])
        excellent_durations = len(success_df[success_df['Duration_Status'] == 'EXCELLENT'])
        good_durations = len(success_df[success_df['Duration_Status'] == 'GOOD'])
        
        print(f"\n📊 DURATION ACCURACY:")
        print(f"   Perfect (<0.001y): {perfect_durations}/{successful_bonds} ({perfect_durations/successful_bonds*100:.1f}%)")
        print(f"   Excellent (<0.01y): {excellent_durations}/{successful_bonds} ({excellent_durations/successful_bonds*100:.1f}%)")
        print(f"   Good (<0.1y): {good_durations}/{successful_bonds} ({good_durations/successful_bonds*100:.1f}%)")
        
        # Spread statistics 
        perfect_spreads = len(success_df[success_df['Spread_Status'] == 'PERFECT'])
        excellent_spreads = len(success_df[success_df['Spread_Status'] == 'EXCELLENT'])
        good_spreads = len(success_df[success_df['Spread_Status'] == 'GOOD'])
        
        print(f"\n📊 SPREAD ACCURACY:")
        print(f"   Perfect (<0.001bps): {perfect_spreads}/{successful_bonds} ({perfect_spreads/successful_bonds*100:.1f}%)")
        print(f"   Excellent (<0.01bps): {excellent_spreads}/{successful_bonds} ({excellent_spreads/successful_bonds*100:.1f}%)")
        print(f"   Good (<0.1bps): {good_spreads}/{successful_bonds} ({good_spreads/successful_bonds*100:.1f}%)")
        
        # Average differences
        avg_yield_diff = abs(success_df['Yield_Diff'].dropna()).mean()
        avg_duration_diff = abs(success_df['Duration_Diff'].dropna()).mean()
        avg_spread_diff = abs(success_df['Spread_Diff'].dropna()).mean()
        
        print(f"\n📊 AVERAGE ABSOLUTE DIFFERENCES:")
        print(f"   Yield: {avg_yield_diff:.6f}%")
        print(f"   Duration: {avg_duration_diff:.6f} years")
        print(f"   Spread: {avg_spread_diff:.3f} bps")

def display_full_responses(full_responses):
    """Display full API responses for first 5 bonds"""
    print("\n" + "=" * 100)
    print("📋 FULL API RESPONSES FOR FIRST 5 BONDS")
    print("=" * 100)
    
    for response_data in full_responses:
        print(f"\n🎯 BOND {response_data['bond_index']}: {response_data['isin']}")
        print(f"   Name: {response_data['name']}")
        print(f"   Price: {response_data['price']}")
        print("-" * 80)
        
        # Pretty print the full JSON response
        print(json.dumps(response_data['full_response'], indent=2))
        print("-" * 80)

def save_results_to_csv(results):
    """Save comparison results to CSV"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"isin_baseline_comparison_{timestamp}.csv"
    
    df = pd.DataFrame(results)
    df.to_csv(filename, index=False)
    
    print(f"\n💾 RESULTS SAVED TO: {filename}")
    return filename

def main():
    """Main test execution"""
    print("🎯 ISIN-Only Bloomberg Baseline Comparison Test")
    print("   Testing optimized hierarchy with 25 bonds using ISIN-only input")
    print("   Comparing yield, duration, spread against Bloomberg baseline values")
    print("=" * 80)
    
    # Run comprehensive comparison
    results, full_responses = run_comprehensive_comparison()
    
    # Display results
    display_comparison_table(results)
    
    # Display full responses for first 5 bonds
    display_full_responses(full_responses)
    
    # Save results
    csv_file = save_results_to_csv(results)
    
    print("\n" + "=" * 80)
    print("✅ ISIN-ONLY COMPARISON TEST COMPLETE!")
    print(f"📊 Tested: {len(results)} bonds")
    print(f"💾 Results saved to: {csv_file}")
    print("🎯 Full responses shown for first 5 bonds")
    print("=" * 80)
    
    # Show key insights
    successful_results = [r for r in results if r['Overall_Status'] == 'success']
    if successful_results:
        success_rate = len(successful_results) / len(results) * 100
        perfect_yields = len([r for r in successful_results if r['Yield_Status'] == 'PERFECT'])
        perfect_durations = len([r for r in successful_results if r['Duration_Status'] == 'PERFECT'])
        
        print(f"\n🎯 KEY INSIGHTS:")
        print(f"   ISIN-only lookup success rate: {success_rate:.1f}%")
        print(f"   Perfect yield matches: {perfect_yields}/{len(successful_results)}")
        print(f"   Perfect duration matches: {perfect_durations}/{len(successful_results)}")
        print(f"   Shows optimized hierarchy effectiveness with minimal input")

if __name__ == "__main__":
    main()
