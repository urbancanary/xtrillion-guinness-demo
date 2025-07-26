#!/usr/bin/env python3
"""
🎯 Individual Bond Test - All 25 Bonds
======================================

Since portfolio analysis has database issues, let's test all 25 bonds individually
using the working XTrillion GA10 enhanced API with convexity and OAD calculations.
"""

import requests
import json
import time
from datetime import datetime
import pandas as pd

# =============================================================================
# 🎯 25-BOND TEST DATASET (Real Market Data)
# =============================================================================

BOND_DATASET = [
    {"ISIN": "US912810TJ79", "PX_MID": 71.66, "Name": "US TREASURY N/B, 3%, 15-Aug-2052", "Weight": 1.03},
    {"ISIN": "XS2249741674", "PX_MID": 77.88, "Name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040", "Weight": 3.88},
    {"ISIN": "XS1709535097", "PX_MID": 89.40, "Name": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047", "Weight": 3.78},
    {"ISIN": "XS1982113463", "PX_MID": 87.14, "Name": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039", "Weight": 3.71},
    {"ISIN": "USP37466AS18", "PX_MID": 80.39, "Name": "EMPRESA METRO, 4.7%, 07-May-2050", "Weight": 4.57},
    {"ISIN": "USP3143NAH72", "PX_MID": 101.63, "Name": "CODELCO INC, 6.15%, 24-Oct-2036", "Weight": 5.79},
    {"ISIN": "USP30179BR86", "PX_MID": 86.42, "Name": "COMISION FEDERAL, 6.264%, 15-Feb-2052", "Weight": 6.27},
    {"ISIN": "US195325DX04", "PX_MID": 52.71, "Name": "COLOMBIA REP OF, 3.875%, 15-Feb-2061", "Weight": 3.82},
    {"ISIN": "US279158AJ82", "PX_MID": 69.31, "Name": "ECOPETROL SA, 5.875%, 28-May-2045", "Weight": 2.93},
    {"ISIN": "USP37110AM89", "PX_MID": 76.24, "Name": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047", "Weight": 2.73},
    {"ISIN": "XS2542166231", "PX_MID": 103.03, "Name": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038", "Weight": 2.96},
    {"ISIN": "XS2167193015", "PX_MID": 64.50, "Name": "STATE OF ISRAEL, 3.8%, 13-May-2060", "Weight": 4.14},
    {"ISIN": "XS1508675508", "PX_MID": 82.42, "Name": "SAUDI INT BOND, 4.5%, 26-Oct-2046", "Weight": 4.09},
    {"ISIN": "XS1807299331", "PX_MID": 92.21, "Name": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048", "Weight": 6.58},
    {"ISIN": "US91086QAZ19", "PX_MID": 78.00, "Name": "UNITED MEXICAN, 5.75%, 12-Oct-2110", "Weight": 1.69},
    {"ISIN": "USP6629MAD40", "PX_MID": 82.57, "Name": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047", "Weight": 3.89},
    {"ISIN": "US698299BL70", "PX_MID": 56.60, "Name": "PANAMA, 3.87%, 23-Jul-2060", "Weight": 4.12},
    {"ISIN": "US71654QDF63", "PX_MID": 71.42, "Name": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060", "Weight": 3.95},
    {"ISIN": "US71654QDE98", "PX_MID": 89.55, "Name": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031", "Weight": 1.30},
    {"ISIN": "XS2585988145", "PX_MID": 85.54, "Name": "GACI FIRST INVST, 5.125%, 14-Feb-2053", "Weight": 2.78},
    {"ISIN": "XS1959337749", "PX_MID": 89.97, "Name": "QATAR STATE OF, 4.817%, 14-Mar-2049", "Weight": 4.50},
    {"ISIN": "XS2233188353", "PX_MID": 99.23, "Name": "QNB FINANCE LTD, 1.625%, 22-Sep-2025", "Weight": 4.90},
    {"ISIN": "XS2359548935", "PX_MID": 73.79, "Name": "QATAR ENERGY, 3.125%, 12-Jul-2041", "Weight": 3.70},
    {"ISIN": "XS0911024635", "PX_MID": 93.29, "Name": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043", "Weight": 3.32},
    {"ISIN": "USP0R80BAG79", "PX_MID": 97.26, "Name": "SITIOS, 5.375%, 04-Apr-2032", "Weight": 3.12}
]

# Working API endpoint 
API_BASE_URL = "https://xtrillion-ga10-44056503414.us-central1.run.app"
API_KEY = "gax9_test_9r4t7w2k5m8p1z6x3v"

def test_individual_bond(bond_data):
    """Test individual bond calculation with enhanced metrics"""
    try:
        url = f"{API_BASE_URL}/api/v1/bond/parse-and-calculate-enhanced"
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        }
        
        # Test data
        test_bond = {
            "description": bond_data["Name"],
            "isin": bond_data["ISIN"],
            "price": bond_data["PX_MID"],
            "settlement_date": "2025-07-30",
            "include_oas": True
        }
        
        response = requests.post(url, headers=headers, json=test_bond, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            analytics = result.get('analytics', {})
            
            return {
                'success': True,
                'isin': bond_data["ISIN"],
                'name': bond_data["Name"],
                'price': bond_data["PX_MID"],
                'weight': bond_data["Weight"],
                'yield': analytics.get('yield', 0),
                'duration': analytics.get('duration', 0),
                'spread': analytics.get('spread', 0),
                'convexity': analytics.get('convexity', 0),
                'oad': analytics.get('option_adjusted_duration', 0),
                'oas': analytics.get('option_adjusted_spread', 0),
                'accrued': analytics.get('accrued_interest', 0),
                'settlement': analytics.get('settlement', ''),
                'processing': result.get('processing', {})
            }
        else:
            return {
                'success': False,
                'isin': bond_data["ISIN"],
                'name': bond_data["Name"],
                'error': f"HTTP {response.status_code}",
                'details': response.text[:200] if response.text else 'No error details'
            }
            
    except Exception as e:
        return {
            'success': False,
            'isin': bond_data["ISIN"],
            'name': bond_data["Name"],
            'error': str(e)
        }

def calculate_portfolio_metrics(successful_results):
    """Calculate portfolio-level metrics from individual bond results"""
    if not successful_results:
        return {}
    
    total_weight = sum(bond['weight'] for bond in successful_results)
    
    # Weighted averages
    portfolio_yield = sum(bond['yield'] * bond['weight'] for bond in successful_results) / total_weight
    portfolio_duration = sum(bond['duration'] * bond['weight'] for bond in successful_results) / total_weight
    portfolio_spread = sum(bond['spread'] * bond['weight'] for bond in successful_results) / total_weight
    portfolio_convexity = sum(bond['convexity'] * bond['weight'] for bond in successful_results) / total_weight
    portfolio_oad = sum(bond['oad'] * bond['weight'] for bond in successful_results) / total_weight
    
    # Statistics
    avg_price = sum(bond['price'] * bond['weight'] for bond in successful_results) / total_weight
    yield_range = (min(bond['yield'] for bond in successful_results), 
                   max(bond['yield'] for bond in successful_results))
    duration_range = (min(bond['duration'] for bond in successful_results),
                      max(bond['duration'] for bond in successful_results))
    
    return {
        'portfolio_yield': portfolio_yield,
        'portfolio_duration': portfolio_duration, 
        'portfolio_spread': portfolio_spread,
        'portfolio_convexity': portfolio_convexity,
        'portfolio_oad': portfolio_oad,
        'avg_price': avg_price,
        'total_weight': total_weight,
        'yield_range': yield_range,
        'duration_range': duration_range,
        'bond_count': len(successful_results)
    }

def run_individual_bond_test():
    """Run comprehensive individual bond test"""
    print("🎯 INDIVIDUAL BOND TEST - ALL 25 BONDS")
    print("=" * 70)
    print(f"📅 Test timestamp: {datetime.now().isoformat()}")
    print(f"🌐 Using XTrillion GA10 Enhanced API: {API_BASE_URL}")
    print(f"⭐ Features: Yield, Duration, Spread, Convexity, OAD, OAS")
    
    results = []
    successful_results = []
    failed_results = []
    
    print(f"\n🔄 Processing {len(BOND_DATASET)} bonds individually...")
    
    for i, bond in enumerate(BOND_DATASET, 1):
        print(f"\n📊 Bond {i:2d}/{len(BOND_DATASET)}: {bond['ISIN']}")
        print(f"    💰 {bond['Name'][:50]}...")
        print(f"    💵 Price: {bond['PX_MID']}, Weight: {bond['Weight']}%")
        
        result = test_individual_bond(bond)
        results.append(result)
        
        if result['success']:
            successful_results.append(result)
            print(f"    ✅ SUCCESS: Yield={result['yield']:.2f}%, Duration={result['duration']:.2f}yrs")
            print(f"       ⭐ Convexity={result['convexity']:.2f}, OAD={result['oad']:.2f}")
        else:
            failed_results.append(result)
            print(f"    ❌ FAILED: {result['error']}")
        
        # Small delay to be respectful to API
        time.sleep(0.5)
    
    # Calculate portfolio metrics
    portfolio_metrics = calculate_portfolio_metrics(successful_results)
    
    # =============================================================================
    # 📊 RESULTS SUMMARY
    # =============================================================================
    print(f"\n📊 COMPREHENSIVE RESULTS SUMMARY")
    print("=" * 70)
    
    print(f"✅ Successful bonds: {len(successful_results)}/{len(BOND_DATASET)} ({len(successful_results)/len(BOND_DATASET)*100:.1f}%)")
    print(f"❌ Failed bonds: {len(failed_results)}")
    
    if portfolio_metrics:
        print(f"\n🎯 PORTFOLIO METRICS (Enhanced):")
        print(f"   💰 Portfolio Yield: {portfolio_metrics['portfolio_yield']:.2f}%")
        print(f"   ⏱️  Portfolio Duration: {portfolio_metrics['portfolio_duration']:.2f} years")
        print(f"   📈 Portfolio Spread: {portfolio_metrics['portfolio_spread']:.0f}bp")
        print(f"   ⭐ Portfolio Convexity: {portfolio_metrics['portfolio_convexity']:.2f}")
        print(f"   ⭐ Portfolio OAD: {portfolio_metrics['portfolio_oad']:.2f}")
        print(f"   💵 Average Price: {portfolio_metrics['avg_price']:.2f}")
        print(f"   📊 Total Weight: {portfolio_metrics['total_weight']:.2f}%")
        
        print(f"\n📈 RANGES:")
        print(f"   Yield Range: {portfolio_metrics['yield_range'][0]:.2f}% - {portfolio_metrics['yield_range'][1]:.2f}%")
        print(f"   Duration Range: {portfolio_metrics['duration_range'][0]:.2f} - {portfolio_metrics['duration_range'][1]:.2f} years")
    
    # Show failures if any
    if failed_results:
        print(f"\n❌ FAILED BONDS:")
        for failure in failed_results:
            print(f"   {failure['isin']}: {failure['error']}")
    
    # =============================================================================
    # 💾 SAVE DETAILED RESULTS
    # =============================================================================
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save to JSON
    detailed_results = {
        'test_info': {
            'timestamp': datetime.now().isoformat(),
            'api_endpoint': API_BASE_URL,
            'total_bonds': len(BOND_DATASET),
            'successful_bonds': len(successful_results),
            'success_rate': len(successful_results)/len(BOND_DATASET)*100
        },
        'portfolio_metrics': portfolio_metrics,
        'individual_results': results
    }
    
    json_file = f"individual_bond_results_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(detailed_results, f, indent=2, default=str)
    print(f"\n💾 Detailed results saved to: {json_file}")
    
    # Save to CSV for easy analysis
    if successful_results:
        df = pd.DataFrame(successful_results)
        csv_file = f"individual_bond_results_{timestamp}.csv"
        df.to_csv(csv_file, index=False)
        print(f"📈 CSV results saved to: {csv_file}")
    
    return detailed_results

if __name__ == "__main__":
    # Run the individual bond test
    results = run_individual_bond_test()
    print(f"\n🎉 INDIVIDUAL BOND TEST COMPLETED!")
    print(f"⭐ Enhanced metrics (Convexity, OAD) successfully calculated for working bonds")
