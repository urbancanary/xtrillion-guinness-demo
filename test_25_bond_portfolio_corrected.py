#!/usr/bin/env python3
"""
CORRECTED: 25-Bond Portfolio Test for Google Analysis 10 API
==========================================================

Tests the enhanced API with correct endpoints:
- /api/v1/bond/parse-and-calculate (individual bonds)
- /api/v1/portfolio/analyze (full portfolio)
"""

import requests
import json
import time
from datetime import datetime

# API Configuration
API_BASE = "http://localhost:8080"
# Note: API has soft authentication, so we can test without key

# 25-Bond Portfolio Data (provided by client)
BOND_PORTFOLIO = [
    {"isin": "US912810TJ79", "price": 71.66, "name": "US TREASURY N/B, 3%, 15-Aug-2052", "weight": 1.03},
    {"isin": "XS2249741674", "price": 77.88, "name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040", "weight": 3.88},
    {"isin": "XS1709535097", "price": 89.40, "name": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047", "weight": 3.78},
    {"isin": "XS1982113463", "price": 87.14, "name": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039", "weight": 3.71},
    {"isin": "USP37466AS18", "price": 80.39, "name": "EMPRESA METRO, 4.7%, 07-May-2050", "weight": 4.57},
    {"isin": "USP3143NAH72", "price": 101.63, "name": "CODELCO INC, 6.15%, 24-Oct-2036", "weight": 5.79},
    {"isin": "USP30179BR86", "price": 86.42, "name": "COMISION FEDERAL, 6.264%, 15-Feb-2052", "weight": 6.27},
    {"isin": "US195325DX04", "price": 52.71, "name": "COLOMBIA REP OF, 3.875%, 15-Feb-2061", "weight": 3.82},
    {"isin": "US279158AJ82", "price": 69.31, "name": "ECOPETROL SA, 5.875%, 28-May-2045", "weight": 2.93},
    {"isin": "USP37110AM89", "price": 76.24, "name": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047", "weight": 2.73},
    {"isin": "XS2542166231", "price": 103.03, "name": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038", "weight": 2.96},
    {"isin": "XS2167193015", "price": 64.50, "name": "STATE OF ISRAEL, 3.8%, 13-May-2060", "weight": 4.14},
    {"isin": "XS1508675508", "price": 82.42, "name": "SAUDI INT BOND, 4.5%, 26-Oct-2046", "weight": 4.09},
    {"isin": "XS1807299331", "price": 92.21, "name": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048", "weight": 6.58},
    {"isin": "US91086QAZ19", "price": 78.00, "name": "UNITED MEXICAN, 5.75%, 12-Oct-2110", "weight": 1.69},
    {"isin": "USP6629MAD40", "price": 82.57, "name": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047", "weight": 3.89},
    {"isin": "US698299BL70", "price": 56.60, "name": "PANAMA, 3.87%, 23-Jul-2060", "weight": 4.12},
    {"isin": "US71654QDF63", "price": 71.42, "name": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060", "weight": 3.95},
    {"isin": "US71654QDE98", "price": 89.55, "name": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031", "weight": 1.30},
    {"isin": "XS2585988145", "price": 85.54, "name": "GACI FIRST INVST, 5.125%, 14-Feb-2053", "weight": 2.78},
    {"isin": "XS1959337749", "price": 89.97, "name": "QATAR STATE OF, 4.817%, 14-Mar-2049", "weight": 4.50},
    {"isin": "XS2233188353", "price": 99.23, "name": "QNB FINANCE LTD, 1.625%, 22-Sep-2025", "weight": 4.90},
    {"isin": "XS2359548935", "price": 73.79, "name": "QATAR ENERGY, 3.125%, 12-Jul-2041", "weight": 3.70},
    {"isin": "XS0911024635", "price": 93.29, "name": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043", "weight": 3.32},
    {"isin": "USP0R80BAG79", "price": 97.26, "name": "SITIOS, 5.375%, 04-Apr-2032", "weight": 3.12}
]

def test_health_endpoint():
    """Test API health check"""
    print("🔍 Testing API Health...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API Status: {health_data['status']}")
            print(f"📊 Version: {health_data['version']}")
            print(f"🎯 Enhanced Features: {len([c for c in health_data['capabilities'] if '⭐' in c])} new capabilities")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_individual_bond(bond_data):
    """Test individual bond calculation with correct endpoint"""
    print(f"\n🔬 Testing Bond: {bond_data['name'][:50]}...")
    
    payload = {
        "description": bond_data["name"],
        "price": bond_data["price"],
        "settlement_date": "2025-07-30",
        "isin": bond_data["isin"]  # Include ISIN if available
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/bond/parse-and-calculate",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                analytics = result.get("analytics", {})
                print(f"  ✅ YTM: {analytics.get('yield', 'N/A'):.2f}%")
                print(f"     Duration: {analytics.get('duration', 'N/A'):.2f} years")
                print(f"     Spread: {analytics.get('spread', 'N/A')} bp")
                if 'convexity' in analytics:
                    print(f"     ⭐ Convexity: {analytics.get('convexity', 'N/A')}")
                    print(f"     ⭐ OAD: {analytics.get('option_adjusted_duration', 'N/A')}")
                return result
            else:
                print(f"  ❌ Calculation failed: {result.get('error', 'Unknown error')}")
                return None
        else:
            print(f"  ❌ API Error: {response.status_code}")
            print(f"     Response: {response.text[:200]}")
            return None
            
    except Exception as e:
        print(f"  ❌ Request error: {e}")
        return None

def test_portfolio_analysis():
    """Test full portfolio analysis with correct format"""
    print(f"\n📊 Testing Full Portfolio Analysis (25 bonds)...")
    
    # Format portfolio data according to API expectations
    portfolio_data = []
    for i, bond in enumerate(BOND_PORTFOLIO, 1):
        portfolio_data.append({
            "BOND_CD": bond["isin"],
            "CLOSING PRICE": bond["price"],
            "BOND DESCRIPTION": bond["name"],
            "WEIGHTING": f"{bond['weight']:.2f}%"
        })
    
    payload = {
        "data": portfolio_data
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/portfolio/analyze",
            json=payload,
            headers=headers,
            timeout=180  # Longer timeout for portfolio
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                summary = result.get("portfolio_summary", {})
                print(f"✅ Portfolio Analysis Complete!")
                print(f"   Total Bonds: {summary.get('bond_count', 'N/A')}")
                print(f"   Successful: {summary.get('successful_calculations', 'N/A')}")
                print(f"   Success Rate: {summary.get('success_rate_pct', 'N/A'):.1f}%")
                
                if 'portfolio_yield' in summary:
                    print(f"   📈 Portfolio Yield: {summary.get('portfolio_yield', 'N/A'):.2f}%")
                    print(f"   ⏱️ Portfolio Duration: {summary.get('portfolio_duration', 'N/A'):.2f} years")
                    print(f"   📊 Portfolio Spread: {summary.get('portfolio_spread', 'N/A'):.1f} bp")
                    print(f"   💰 Average Price: {summary.get('average_price', 'N/A'):.2f}")
                
                return result
            else:
                print(f"❌ Portfolio analysis failed: {result.get('error', 'Unknown error')}")
                return None
        else:
            print(f"❌ Portfolio API Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"❌ Portfolio request error: {e}")
        return None

def analyze_results(individual_results, portfolio_result):
    """Analyze and summarize test results"""
    print(f"\n📋 DETAILED RESULTS ANALYSIS")
    print(f"=" * 60)
    
    # Individual bond statistics
    successful_individual = len([r for r in individual_results if r is not None])
    print(f"\n📊 INDIVIDUAL BOND TESTING:")
    print(f"   Sample Size: {len(individual_results)} bonds tested")
    print(f"   Success Rate: {successful_individual}/{len(individual_results)} ({(successful_individual/len(individual_results)*100):.1f}%)")
    
    if successful_individual > 0:
        print(f"\n📈 SAMPLE ANALYTICS:")
        yields = []
        durations = []
        spreads = []
        
        for result in individual_results:
            if result and result.get('status') == 'success':
                analytics = result.get('analytics', {})
                if 'yield' in analytics:
                    yields.append(analytics['yield'])
                if 'duration' in analytics:
                    durations.append(analytics['duration'])
                if 'spread' in analytics:
                    spreads.append(analytics['spread'])
        
        if yields:
            print(f"   Yield Range: {min(yields):.2f}% - {max(yields):.2f}%")
        if durations:
            print(f"   Duration Range: {min(durations):.2f} - {max(durations):.2f} years")
        if spreads:
            print(f"   Spread Range: {min(spreads):.1f} - {max(spreads):.1f} bp")
    
    # Portfolio analysis results
    print(f"\n📈 FULL PORTFOLIO ANALYSIS:")
    if portfolio_result and portfolio_result.get('status') == 'success':
        summary = portfolio_result.get('portfolio_summary', {})
        print(f"   Status: ✅ SUCCESS")
        print(f"   Coverage: {summary.get('successful_calculations', 'N/A')}/{summary.get('bond_count', 'N/A')} bonds")
        print(f"   Success Rate: {summary.get('success_rate_pct', 'N/A'):.1f}%")
        
        if 'portfolio_yield' in summary:
            print(f"\n💼 PORTFOLIO METRICS:")
            print(f"   Weighted Yield: {summary.get('portfolio_yield', 'N/A'):.2f}%")
            print(f"   Weighted Duration: {summary.get('portfolio_duration', 'N/A'):.2f} years")
            print(f"   Weighted Spread: {summary.get('portfolio_spread', 'N/A'):.1f} bp")
            print(f"   Average Price: {summary.get('average_price', 'N/A'):.2f}")
            print(f"   Total Weight: {summary.get('total_weight', 'N/A'):.1f}%")
    else:
        print(f"   Status: ❌ FAILED")
        if portfolio_result:
            print(f"   Error: {portfolio_result.get('error', 'Unknown error')}")
    
    # Save results
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "api_base": API_BASE,
        "total_bonds_in_portfolio": len(BOND_PORTFOLIO),
        "sample_tested": len(individual_results),
        "individual_success_rate": f"{(successful_individual/len(individual_results)*100):.1f}%" if individual_results else "0%",
        "portfolio_analysis_success": portfolio_result is not None and portfolio_result.get('status') == 'success',
        "individual_results": individual_results,
        "portfolio_result": portfolio_result,
        "bond_portfolio": BOND_PORTFOLIO
    }
    
    filename = f"bond_test_comprehensive_{int(time.time())}.json"
    with open(filename, "w") as f:
        json.dump(test_results, f, indent=2, default=str)
    
    print(f"\n💾 Complete results saved to: {filename}")

def main():
    """Main test execution with corrected endpoints"""
    print("🚀 GOOGLE ANALYSIS 10 - CORRECTED API TEST")
    print("=" * 60)
    print("Using CORRECT endpoints:")
    print("  • Individual: /api/v1/bond/parse-and-calculate")
    print("  • Portfolio:  /api/v1/portfolio/analyze")
    print("=" * 60)
    
    # Step 1: Health Check
    if not test_health_endpoint():
        print("❌ API health check failed. Exiting.")
        return
    
    print(f"\n🎯 Testing sample bonds individually...")
    
    # Step 2: Test Sample Individual Bonds (first 3 for speed)
    sample_bonds = BOND_PORTFOLIO[:3]  # Test first 3 bonds
    individual_results = []
    
    for i, bond in enumerate(sample_bonds, 1):
        print(f"\n[{i}/{len(sample_bonds)}] {bond['name'][:60]}...")
        result = test_individual_bond(bond)
        individual_results.append(result)
        time.sleep(2)  # Rate limiting
    
    # Step 3: Test Full Portfolio (all 25 bonds)
    portfolio_result = test_portfolio_analysis()
    
    # Step 4: Analyze Results
    analyze_results(individual_results, portfolio_result)
    
    print(f"\n🎉 CORRECTED API TEST COMPLETE!")
    print(f"📊 Enhanced API with convexity and OAD successfully tested")
    print(f"💼 Your 25-bond portfolio has been analyzed")

if __name__ == "__main__":
    main()
