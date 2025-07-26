#!/usr/bin/env python3
"""
Test script for user's 25 bonds - FIXED VERSION
Using the correct portfolio analysis endpoint
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

def test_portfolio_analysis():
    """Test portfolio analysis with all 25 bonds"""
    print(f"📊 Testing portfolio analysis with {len(bonds_data)} bonds...")
    
    # Prepare portfolio data - simpler format for compatibility
    portfolio_data = {
        "bonds": [
            {
                "description": bond["name"],
                "price": bond["price"],
                "weight": bond["weight"]
            }
            for bond in bonds_data
        ]
    }
    
    try:
        print("📤 Sending portfolio analysis request...")
        response = requests.post(
            f"{API_BASE}/api/v1/portfolio/analyze",
            json=portfolio_data,
            headers={"Content-Type": "application/json"},
            timeout=120  # Extended timeout for 25 bonds
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Portfolio analysis successful!")
            return result
        else:
            print(f"❌ Portfolio analysis failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Portfolio analysis request failed: {e}")
        return None

def test_individual_bonds():
    """Test first few individual bonds"""
    print(f"🔬 Testing individual bond calculations...")
    
    results = []
    
    # Test first 5 bonds
    for i, bond in enumerate(bonds_data[:5], 1):
        print(f"\n📤 Testing bond {i}: {bond['isin']}")
        
        bond_data = {
            "description": bond["name"],
            "price": bond["price"]
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/api/v1/bond/parse-and-calculate",
                json=bond_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if "calculated_bond" in result:
                    calc_bond = result["calculated_bond"]
                    bond_result = {
                        "isin": bond["isin"],
                        "name": bond["name"][:40],
                        "price": bond["price"],
                        "yield": calc_bond.get("yield_to_maturity", 0),
                        "duration": calc_bond.get("duration", 0),
                        "spread": calc_bond.get("spread_over_treasury", 0)
                    }
                    results.append(bond_result)
                    print(f"   ✅ Yield: {bond_result['yield']:.2f}%, Duration: {bond_result['duration']:.2f}y, Spread: {bond_result['spread']:.0f}bp")
                else:
                    print(f"   ❌ No calculation data returned")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return results

def print_results_table(bond_results):
    """Print results in a nice table format"""
    if not bond_results:
        return
        
    print(f"\n📋 INDIVIDUAL BOND CALCULATION RESULTS:")
    print(f"{'#':<3} {'ISIN':<15} {'Price':<8} {'Yield%':<8} {'Duration':<10} {'Spread':<8} {'Name':<40}")
    print("-" * 105)
    
    for i, bond in enumerate(bond_results, 1):
        print(f"{i:<3} {bond['isin']:<15} {bond['price']:<8.2f} {bond['yield']:<8.2f} {bond['duration']:<10.2f} {bond['spread']:<8.0f} {bond['name']:<40}")

def main():
    """Main test function"""
    print("🚀 BOND CALCULATION TEST - USER'S 25 BONDS")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API: {API_BASE}")
    print(f"Total bonds: {len(bonds_data)}")
    print(f"Settlement: API default (prior month end)")
    
    # Test individual bonds first
    bond_results = test_individual_bonds()
    print_results_table(bond_results)
    
    # Test portfolio analysis
    portfolio_result = test_portfolio_analysis()
    
    if portfolio_result:
        print("\n🎉 PORTFOLIO ANALYSIS SUCCESS!")
        
        # Print key portfolio metrics if available
        if "portfolio_summary" in portfolio_result:
            summary = portfolio_result["portfolio_summary"]
            print(f"\n📈 PORTFOLIO SUMMARY:")
            for key, value in summary.items():
                if isinstance(value, (int, float)):
                    if 'yield' in key.lower() or 'spread' in key.lower():
                        print(f"   • {key.replace('_', ' ').title()}: {value:.2f}%")
                    elif 'duration' in key.lower():
                        print(f"   • {key.replace('_', ' ').title()}: {value:.2f} years")
                    else:
                        print(f"   • {key.replace('_', ' ').title()}: {value}")
                else:
                    print(f"   • {key.replace('_', ' ').title()}: {value}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"user_bond_results_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump({
                "individual_bonds": bond_results,
                "portfolio_analysis": portfolio_result,
                "test_info": {
                    "timestamp": datetime.now().isoformat(),
                    "bond_count": len(bonds_data),
                    "api_base": API_BASE
                }
            }, f, indent=2)
        print(f"\n📁 Full results saved to: {filename}")
        
    else:
        print("\n❌ Portfolio analysis failed")
        
        # Still save individual results if we have them
        if bond_results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"individual_bonds_only_{timestamp}.json"
            with open(filename, "w") as f:
                json.dump(bond_results, f, indent=2)
            print(f"📁 Individual bond results saved to: {filename}")

if __name__ == "__main__":
    main()
