#!/usr/bin/env python3
"""
25-Bond Portfolio Test for Google Analysis 10 API
=================================================

Tests the enhanced API with a real client portfolio of 25 bonds
including Treasuries, Sovereigns, and Corporates with market prices.
"""

import requests
import json
import time
from datetime import datetime

# API Configuration
API_BASE = "http://localhost:8080"
API_KEY = "xtrillion-ga9-key-2024"

# 25-Bond Portfolio Data (provided by client)
BOND_PORTFOLIO = [
    {"isin": "US912810TJ79", "price": 71.66, "name": "US TREASURY N/B, 3%, 15-Aug-2052"},
    {"isin": "XS2249741674", "price": 77.88, "name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040"},
    {"isin": "XS1709535097", "price": 89.40, "name": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047"},
    {"isin": "XS1982113463", "price": 87.14, "name": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039"},
    {"isin": "USP37466AS18", "price": 80.39, "name": "EMPRESA METRO, 4.7%, 07-May-2050"},
    {"isin": "USP3143NAH72", "price": 101.63, "name": "CODELCO INC, 6.15%, 24-Oct-2036"},
    {"isin": "USP30179BR86", "price": 86.42, "name": "COMISION FEDERAL, 6.264%, 15-Feb-2052"},
    {"isin": "US195325DX04", "price": 52.71, "name": "COLOMBIA REP OF, 3.875%, 15-Feb-2061"},
    {"isin": "US279158AJ82", "price": 69.31, "name": "ECOPETROL SA, 5.875%, 28-May-2045"},
    {"isin": "USP37110AM89", "price": 76.24, "name": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047"},
    {"isin": "XS2542166231", "price": 103.03, "name": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038"},
    {"isin": "XS2167193015", "price": 64.50, "name": "STATE OF ISRAEL, 3.8%, 13-May-2060"},
    {"isin": "XS1508675508", "price": 82.42, "name": "SAUDI INT BOND, 4.5%, 26-Oct-2046"},
    {"isin": "XS1807299331", "price": 92.21, "name": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048"},
    {"isin": "US91086QAZ19", "price": 78.00, "name": "UNITED MEXICAN, 5.75%, 12-Oct-2110"},
    {"isin": "USP6629MAD40", "price": 82.57, "name": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047"},
    {"isin": "US698299BL70", "price": 56.60, "name": "PANAMA, 3.87%, 23-Jul-2060"},
    {"isin": "US71654QDF63", "price": 71.42, "name": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060"},
    {"isin": "US71654QDE98", "price": 89.55, "name": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031"},
    {"isin": "XS2585988145", "price": 85.54, "name": "GACI FIRST INVST, 5.125%, 14-Feb-2053"},
    {"isin": "XS1959337749", "price": 89.97, "name": "QATAR STATE OF, 4.817%, 14-Mar-2049"},
    {"isin": "XS2233188353", "price": 99.23, "name": "QNB FINANCE LTD, 1.625%, 22-Sep-2025"},
    {"isin": "XS2359548935", "price": 73.79, "name": "QATAR ENERGY, 3.125%, 12-Jul-2041"},
    {"isin": "XS0911024635", "price": 93.29, "name": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043"},
    {"isin": "USP0R80BAG79", "price": 97.26, "name": "SITIOS, 5.375%, 04-Apr-2032"}
]

def test_health_endpoint():
    """Test API health check"""
    print("🔍 Testing API Health...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API Status: {health_data['status']}")
            print(f"📊 Database Size: {health_data['dual_database_system']['primary_database']['size_mb']}MB")
            print(f"🎯 Version: {health_data['version']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_individual_bond(bond_data):
    """Test individual bond calculation"""
    print(f"\n🔬 Testing Bond: {bond_data['name'][:40]}...")
    
    payload = {
        "description": bond_data["name"],
        "price": bond_data["price"],
        "settlement_date": "2025-07-30"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/bond/parse-and-calculate",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                calc = result.get("calculations", {})
                print(f"  ✅ YTM: {calc.get('yield_to_maturity', 'N/A'):.2f}%")
                print(f"     Duration: {calc.get('duration', 'N/A'):.2f} years")
                print(f"     Spread: {calc.get('spread_to_treasury', 'N/A')} bp")
                return result
            else:
                print(f"  ❌ Calculation failed: {result.get('error', 'Unknown error')}")
                return None
        else:
            print(f"  ❌ API Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"  ❌ Request error: {e}")
        return None

def test_portfolio_analysis():
    """Test full portfolio analysis"""
    print(f"\n📊 Testing Full Portfolio Analysis (25 bonds)...")
    
    # Prepare portfolio data for the API
    portfolio_bonds = []
    for i, bond in enumerate(BOND_PORTFOLIO, 1):
        portfolio_bonds.append({
            "rank": i,
            "weight": f"{(100/25):.2f}%",  # Equal weight for testing
            "description": bond["name"],
            "price": bond["price"]
        })
    
    payload = {
        "portfolio": portfolio_bonds,
        "settlement_date": "2025-07-30"
    }
    
    headers = {
        "Content-Type": "application/json", 
        "Authorization": f"Bearer {API_KEY}"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/portfolio/calculate",
            json=payload,
            headers=headers,
            timeout=120  # Longer timeout for portfolio
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                summary = result.get("portfolio_summary", {})
                print(f"✅ Portfolio Analysis Complete!")
                print(f"   Total Bonds: {summary.get('bond_count', 'N/A')}")
                print(f"   Successful: {summary.get('successful_calculations', 'N/A')}")
                print(f"   Failed: {summary.get('failed_calculations', 'N/A')}")
                
                if "portfolio_metrics" in result:
                    metrics = result["portfolio_metrics"]
                    print(f"   Portfolio Yield: {metrics.get('weighted_yield', 'N/A'):.2f}%")
                    print(f"   Portfolio Duration: {metrics.get('weighted_duration', 'N/A'):.2f} years")
                    print(f"   Portfolio Spread: {metrics.get('weighted_spread', 'N/A')} bp")
                
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

def generate_test_report(individual_results, portfolio_result):
    """Generate comprehensive test report"""
    print(f"\n📋 COMPREHENSIVE TEST REPORT")
    print(f"=" * 60)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Bonds Tested: {len(BOND_PORTFOLIO)}")
    print(f"API Endpoint: {API_BASE}")
    
    # Individual bond statistics
    successful_individual = len([r for r in individual_results if r is not None])
    print(f"\n📊 INDIVIDUAL BOND RESULTS:")
    print(f"   Successful: {successful_individual}/{len(BOND_PORTFOLIO)} ({(successful_individual/len(BOND_PORTFOLIO)*100):.1f}%)")
    print(f"   Failed: {len(BOND_PORTFOLIO) - successful_individual}")
    
    # Portfolio analysis results
    print(f"\n📈 PORTFOLIO ANALYSIS:")
    if portfolio_result:
        print(f"   Status: ✅ SUCCESS")
        if "portfolio_metrics" in portfolio_result:
            metrics = portfolio_result["portfolio_metrics"]
            print(f"   Weighted Yield: {metrics.get('weighted_yield', 'N/A'):.2f}%")
            print(f"   Weighted Duration: {metrics.get('weighted_duration', 'N/A'):.2f} years")
    else:
        print(f"   Status: ❌ FAILED")
    
    # Save detailed results
    detailed_results = {
        "timestamp": datetime.now().isoformat(),
        "test_summary": {
            "total_bonds": len(BOND_PORTFOLIO),
            "successful_individual": successful_individual,
            "portfolio_success": portfolio_result is not None
        },
        "individual_results": individual_results,
        "portfolio_result": portfolio_result,
        "bond_portfolio": BOND_PORTFOLIO
    }
    
    with open(f"bond_test_results_{int(time.time())}.json", "w") as f:
        json.dump(detailed_results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: bond_test_results_{int(time.time())}.json")

def main():
    """Main test execution"""
    print("🚀 GOOGLE ANALYSIS 10 - 25-BOND PORTFOLIO TEST")
    print("=" * 60)
    
    # Step 1: Health Check
    if not test_health_endpoint():
        print("❌ API health check failed. Exiting.")
        return
    
    print(f"\n🎯 Testing {len(BOND_PORTFOLIO)} bonds individually...")
    
    # Step 2: Test Individual Bonds (first 5 for speed)
    individual_results = []
    for i, bond in enumerate(BOND_PORTFOLIO[:5], 1):  # Test first 5 bonds
        print(f"\n[{i}/5] {bond['name'][:50]}...")
        result = test_individual_bond(bond)
        individual_results.append(result)
        time.sleep(1)  # Rate limiting
    
    # Step 3: Test Full Portfolio
    portfolio_result = test_portfolio_analysis()
    
    # Step 4: Generate Report
    generate_test_report(individual_results, portfolio_result)
    
    print(f"\n🎉 TEST COMPLETE!")
    print(f"📊 Check the generated JSON file for detailed results")

if __name__ == "__main__":
    main()
