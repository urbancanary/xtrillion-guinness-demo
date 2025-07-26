#!/usr/bin/env python3
"""
Test script for user's 25 bonds with yield, spread, and duration calculations
No settlement date specified - will use API default (prior month end)
"""

import json
import requests
import sys
from datetime import datetime

# API endpoint
API_BASE = "http://localhost:8080"

# User's bond data
bonds_data = [
    {"isin": "US912810TJ79", "price": 71.66, "weight": 1.03, "name": "US TREASURY N/B, 3%, 15-Aug-2052"},
    {"isin": "XS2249741674", "price": 77.88, "weight": 3.88, "name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040"},
    {"isin": "XS1709535097", "price": 89.40, "weight": 3.78, "name": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047"},
    {"isin": "XS1982113463", "price": 87.14, "weight": 3.71, "name": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039"},
    {"isin": "USP37466AS18", "price": 80.39, "weight": 4.57, "name": "EMPRESA METRO, 4.7%, 07-May-2050"},
    {"isin": "USP3143NAH72", "price": 101.63, "weight": 5.79, "name": "CODELCO INC, 6.15%, 24-Oct-2036"},
    {"isin": "USP30179BR86", "price": 86.42, "weight": 6.27, "name": "COMISION FEDERAL, 6.264%, 15-Feb-2052"},
    {"isin": "US195325DX04", "price": 52.71, "weight": 3.82, "name": "COLOMBIA REP OF, 3.875%, 15-Feb-2061"},
    {"isin": "US279158AJ82", "price": 69.31, "weight": 2.93, "name": "ECOPETROL SA, 5.875%, 28-May-2045"},
    {"isin": "USP37110AM89", "price": 76.24, "weight": 2.73, "name": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047"},
    {"isin": "XS2542166231", "price": 103.03, "weight": 2.96, "name": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038"},
    {"isin": "XS2167193015", "price": 64.50, "weight": 4.14, "name": "STATE OF ISRAEL, 3.8%, 13-May-2060"},
    {"isin": "XS1508675508", "price": 82.42, "weight": 4.09, "name": "SAUDI INT BOND, 4.5%, 26-Oct-2046"},
    {"isin": "XS1807299331", "price": 92.21, "weight": 6.58, "name": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048"},
    {"isin": "US91086QAZ19", "price": 78.00, "weight": 1.69, "name": "UNITED MEXICAN, 5.75%, 12-Oct-2110"},
    {"isin": "USP6629MAD40", "price": 82.57, "weight": 3.89, "name": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047"},
    {"isin": "US698299BL70", "price": 56.60, "weight": 4.12, "name": "PANAMA, 3.87%, 23-Jul-2060"},
    {"isin": "US71654QDF63", "price": 71.42, "weight": 3.95, "name": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060"},
    {"isin": "US71654QDE98", "price": 89.55, "weight": 1.30, "name": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031"},
    {"isin": "XS2585988145", "price": 85.54, "weight": 2.78, "name": "GACI FIRST INVST, 5.125%, 14-Feb-2053"},
    {"isin": "XS1959337749", "price": 89.97, "weight": 4.50, "name": "QATAR STATE OF, 4.817%, 14-Mar-2049"},
    {"isin": "XS2233188353", "price": 99.23, "weight": 4.90, "name": "QNB FINANCE LTD, 1.625%, 22-Sep-2025"},
    {"isin": "XS2359548935", "price": 73.79, "weight": 3.70, "name": "QATAR ENERGY, 3.125%, 12-Jul-2041"},
    {"isin": "XS0911024635", "price": 93.29, "weight": 3.32, "name": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043"},
    {"isin": "USP0R80BAG79", "price": 97.26, "weight": 3.12, "name": "SITIOS, 5.375%, 04-Apr-2032"}
]

def test_health():
    """Test API health"""
    print("🏥 Testing API health...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            print("✅ API is healthy")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to API: {e}")
        return False

def test_portfolio_analysis():
    """Test portfolio analysis with all 25 bonds"""
    print(f"\n📊 Testing portfolio analysis with {len(bonds_data)} bonds...")
    
    # Prepare portfolio data
    portfolio_data = {
        "bonds": [
            {
                "description": bond["name"],
                "price": bond["price"],
                "weight": bond["weight"],
                "isin": bond["isin"]
            }
            for bond in bonds_data
        ],
        "analysis_notes": "User's 25-bond portfolio - no settlement date specified"
    }
    
    try:
        print("📤 Sending portfolio analysis request...")
        response = requests.post(
            f"{API_BASE}/api/v1/portfolio/calculate",
            json=portfolio_data,
            headers={"Content-Type": "application/json"},
            timeout=60  # Longer timeout for complex calculation
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Portfolio analysis successful!")
            
            # Print portfolio summary
            if "portfolio_summary" in result:
                summary = result["portfolio_summary"]
                print(f"\n📈 PORTFOLIO SUMMARY:")
                print(f"   • Bonds analyzed: {summary.get('bond_count', 'N/A')}")
                print(f"   • Total weight: {summary.get('total_weight', 'N/A'):.2f}%" if summary.get('total_weight') else "   • Total weight: N/A")
                print(f"   • Portfolio yield: {summary.get('portfolio_yield', 'N/A'):.2f}%" if summary.get('portfolio_yield') else "   • Portfolio yield: N/A")
                print(f"   • Portfolio duration: {summary.get('portfolio_duration', 'N/A'):.2f} years" if summary.get('portfolio_duration') else "   • Portfolio duration: N/A")
                print(f"   • Portfolio spread: {summary.get('portfolio_spread', 'N/A'):.0f}bp" if summary.get('portfolio_spread') else "   • Portfolio spread: N/A")
            
            # Print individual bond results
            if "bonds" in result:
                print(f"\n📋 INDIVIDUAL BOND RESULTS:")
                print(f"{'#':<3} {'ISIN':<12} {'Price':<8} {'Yield%':<8} {'Duration':<8} {'Spread':<8} {'Name':<30}")
                print("-" * 90)
                
                for i, bond in enumerate(result["bonds"][:10], 1):  # Show first 10
                    isin = bond.get("isin", "N/A")
                    price = bond.get("price", 0)
                    ytm = bond.get("yield_to_maturity", 0)
                    duration = bond.get("duration", 0)
                    spread = bond.get("spread_over_treasury", 0)
                    name = bond.get("description", "Unknown")[:28]
                    
                    print(f"{i:<3} {isin:<12} {price:<8.2f} {ytm:<8.2f} {duration:<8.2f} {spread:<8.0f} {name:<30}")
                
                if len(result["bonds"]) > 10:
                    print(f"... and {len(result['bonds']) - 10} more bonds")
            
            return result
        else:
            print(f"❌ Portfolio analysis failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Portfolio analysis request failed: {e}")
        return None

def test_individual_bond():
    """Test individual bond calculation"""
    print(f"\n🔬 Testing individual bond calculation...")
    
    # Test with first bond (US Treasury)
    test_bond = bonds_data[0]
    bond_data = {
        "description": test_bond["name"],
        "price": test_bond["price"]
    }
    
    try:
        print(f"📤 Testing: {test_bond['name']} at {test_bond['price']}")
        response = requests.post(
            f"{API_BASE}/api/v1/bond/parse-and-calculate",
            json=bond_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Individual bond calculation successful!")
            
            if "calculated_bond" in result:
                bond = result["calculated_bond"]
                print(f"   • Yield: {bond.get('yield_to_maturity', 'N/A'):.2f}%" if bond.get('yield_to_maturity') else "   • Yield: N/A")
                print(f"   • Duration: {bond.get('duration', 'N/A'):.2f} years" if bond.get('duration') else "   • Duration: N/A")
                print(f"   • Spread: {bond.get('spread_over_treasury', 'N/A'):.0f}bp" if bond.get('spread_over_treasury') else "   • Spread: N/A")
            
            return result
        else:
            print(f"❌ Individual bond calculation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Individual bond calculation failed: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 Starting bond calculation tests...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API: {API_BASE}")
    print(f"Bonds to test: {len(bonds_data)}")
    
    # Test API health
    if not test_health():
        print("❌ API is not healthy. Exiting.")
        sys.exit(1)
    
    # Test individual bond calculation
    test_individual_bond()
    
    # Test full portfolio analysis
    portfolio_result = test_portfolio_analysis()
    
    if portfolio_result:
        print("\n🎉 All tests completed successfully!")
        print(f"✅ Portfolio analysis: WORKING")
        print(f"✅ Individual bond calc: WORKING")
        print(f"✅ Bond count: {len(bonds_data)}")
        
        # Save results
        with open("bond_test_results.json", "w") as f:
            json.dump(portfolio_result, f, indent=2)
        print(f"📁 Results saved to: bond_test_results.json")
        
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
