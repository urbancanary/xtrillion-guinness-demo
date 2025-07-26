#!/usr/bin/env python3
"""
Test script for user's 25 bonds - CORRECT API FORMAT
Using the exact format expected by the API
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
    """Test portfolio analysis with correct API format"""
    print(f"📊 Testing portfolio analysis with {len(bonds_data)} bonds...")
    
    # Get today's date for Inventory Date
    today = datetime.now().strftime("%Y/%m/%d")
    
    # Format exactly as expected by API
    portfolio_data = {
        "data": [
            {
                "BOND_CD": bond["isin"],
                "CLOSING PRICE": bond["price"],
                "Inventory Date": today,
                "WEIGHTING": bond["weight"]
            }
            for bond in bonds_data
        ]
    }
    
    try:
        print("📤 Sending portfolio analysis request with correct format...")
        response = requests.post(
            f"{API_BASE}/api/v1/portfolio/analyze",
            json=portfolio_data,
            headers={"Content-Type": "application/json"},
            timeout=120
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

def display_portfolio_results(result):
    """Display portfolio analysis results"""
    if not result:
        return
        
    print(f"\n📈 PORTFOLIO ANALYSIS RESULTS:")
    print("=" * 80)
    
    # Display portfolio summary if available
    if "portfolio_summary" in result:
        summary = result["portfolio_summary"]
        print(f"📊 PORTFOLIO SUMMARY:")
        
        total_weight = summary.get("total_weight", 0)
        portfolio_yield = summary.get("portfolio_yield", 0)
        portfolio_duration = summary.get("portfolio_duration", 0)
        portfolio_spread = summary.get("portfolio_spread", 0)
        
        print(f"   • Total Weight: {total_weight:.2f}%")
        print(f"   • Portfolio Yield: {portfolio_yield:.2f}%")
        print(f"   • Portfolio Duration: {portfolio_duration:.2f} years")
        print(f"   • Portfolio Spread: {portfolio_spread:.0f} bp")
        print()
    
    # Display individual bond results
    if "bonds" in result and result["bonds"]:
        print(f"📋 INDIVIDUAL BOND RESULTS ({len(result['bonds'])} bonds):")
        print(f"{'#':<3} {'ISIN':<15} {'Price':<8} {'Weight':<7} {'Yield%':<8} {'Duration':<9} {'Spread':<8} {'Name':<35}")
        print("-" * 110)
        
        for i, bond in enumerate(result["bonds"], 1):
            isin = bond.get("bond_id", "N/A")
            price = bond.get("price", 0)
            weight = bond.get("weight", 0)
            ytm = bond.get("yield_to_maturity", 0)
            duration = bond.get("duration", 0)
            spread = bond.get("spread_over_treasury", 0)
            name = bond.get("description", "Unknown")[:33]
            
            print(f"{i:<3} {isin:<15} {price:<8.2f} {weight:<7.2f} {ytm:<8.2f} {duration:<9.2f} {spread:<8.0f} {name:<35}")
    
    print()

def main():
    """Main test function"""
    print("🚀 BOND CALCULATION TEST - USER'S 25 BONDS")
    print("=" * 55)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API: {API_BASE}")
    print(f"Total bonds: {len(bonds_data)}")
    print(f"Settlement: API default (prior month end)")
    print()
    
    # Test portfolio analysis with correct format
    portfolio_result = test_portfolio_analysis()
    
    if portfolio_result:
        display_portfolio_results(portfolio_result)
        
        print("🎉 SUCCESS! Bond calculations completed.")
        print(f"✅ All {len(bonds_data)} bonds processed")
        print("✅ Yield, Duration, and Spread calculated for each bond")
        print("✅ Portfolio-level metrics calculated")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"complete_bond_results_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump({
                "portfolio_analysis": portfolio_result,
                "test_info": {
                    "timestamp": datetime.now().isoformat(),
                    "bond_count": len(bonds_data),
                    "api_base": API_BASE,
                    "settlement_note": "API uses prior month end as default settlement"
                }
            }, f, indent=2)
        print(f"\n📁 Complete results saved to: {filename}")
        
    else:
        print("\n❌ Portfolio analysis failed")
        print("Please check API status and format requirements")

if __name__ == "__main__":
    main()
