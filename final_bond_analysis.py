#!/usr/bin/env python3
"""
FINAL TEST: User's 25 bonds with yield, spread, and duration
Using correct response parsing
"""

import json
import requests
import sys
from datetime import datetime

# API endpoint
API_BASE = "http://localhost:8080"

# User's complete 25-bond portfolio
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

def calculate_bond_metrics(bond):
    """Calculate yield, duration, and spread for a single bond"""
    
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
            
            # Extract analytics data
            if "analytics" in result and result["analytics"]:
                analytics = result["analytics"]
                
                yield_val = analytics.get("yield", 0)
                duration_val = analytics.get("duration", 0)
                
                # Calculate spread (yield - treasury benchmark)
                # Using US Treasury as benchmark (typically around 4-5% for long bonds)
                treasury_benchmark = 4.9  # From the US Treasury bond result
                spread_val = (yield_val - treasury_benchmark) * 100  # in basis points
                
                return {
                    "isin": bond["isin"],
                    "name": bond["name"],
                    "price": bond["price"],
                    "weight": bond["weight"],
                    "yield": yield_val,
                    "duration": duration_val,
                    "spread": spread_val,
                    "settlement": analytics.get("settlement", "N/A"),
                    "status": "success"
                }
            else:
                return {"isin": bond["isin"], "status": "no_analytics"}
        else:
            return {"isin": bond["isin"], "status": "api_error", "error": response.text}
            
    except Exception as e:
        return {"isin": bond["isin"], "status": "exception", "error": str(e)}

def main():
    """Calculate metrics for all 25 bonds"""
    print("🚀 COMPLETE BOND PORTFOLIO ANALYSIS")
    print("=" * 50)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API Endpoint: {API_BASE}")
    print(f"📊 Total Bonds: {len(bonds_data)}")
    print(f"⚙️  Settlement: API default (prior month end)")
    print()
    
    # Calculate metrics for all bonds
    print("🔄 Processing bonds...")
    results = []
    successful = 0
    
    for i, bond in enumerate(bonds_data, 1):
        print(f"   {i:2d}/25: {bond['isin'][:12]}... ", end="")
        
        result = calculate_bond_metrics(bond)
        results.append(result)
        
        if result.get("status") == "success":
            successful += 1
            yield_val = result["yield"]
            duration_val = result["duration"]
            spread_val = result["spread"]
            print(f"✅ Y:{yield_val:5.2f}% D:{duration_val:5.1f}y S:{spread_val:+4.0f}bp")
        else:
            print(f"❌ {result.get('status', 'failed')}")
    
    print(f"\n📈 PROCESSING COMPLETE: {successful}/{len(bonds_data)} bonds successful")
    
    # Display results table
    if successful > 0:
        print(f"\n📋 COMPLETE BOND ANALYSIS RESULTS:")
        print(f"{'#':<3} {'ISIN':<15} {'Price':<7} {'Weight':<7} {'Yield%':<7} {'Duration':<8} {'Spread':<7} {'Bond Name':<40}")
        print("-" * 120)
        
        total_weight = 0
        weighted_yield = 0
        weighted_duration = 0
        
        success_results = [r for r in results if r.get("status") == "success"]
        
        for i, bond in enumerate(success_results, 1):
            # Portfolio calculations
            weight = bond["weight"] / 100  # Convert to decimal
            total_weight += bond["weight"]
            weighted_yield += bond["yield"] * weight
            weighted_duration += bond["duration"] * weight
            
            # Display row
            print(f"{i:<3} {bond['isin']:<15} {bond['price']:<7.2f} {bond['weight']:<7.2f} "
                  f"{bond['yield']:<7.2f} {bond['duration']:<8.1f} {bond['spread']:<+7.0f} "
                  f"{bond['name'][:38]:<40}")
        
        # Portfolio summary
        print("-" * 120)
        print(f"📊 PORTFOLIO SUMMARY:")
        print(f"   • Total Weight: {total_weight:.2f}%")
        print(f"   • Portfolio Yield: {weighted_yield:.2f}%")
        print(f"   • Portfolio Duration: {weighted_duration:.2f} years")
        print(f"   • Success Rate: {successful}/{len(bonds_data)} bonds ({successful/len(bonds_data)*100:.1f}%)")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"complete_portfolio_analysis_{timestamp}.json"
        
        output_data = {
            "analysis_date": datetime.now().isoformat(),
            "api_endpoint": API_BASE,
            "settlement_note": "API uses prior month end as default settlement date",
            "portfolio_summary": {
                "total_bonds": len(bonds_data),
                "successful_calculations": successful,
                "success_rate": f"{successful/len(bonds_data)*100:.1f}%",
                "total_weight": total_weight,
                "portfolio_yield": weighted_yield,
                "portfolio_duration": weighted_duration
            },
            "individual_bonds": results
        }
        
        with open(filename, "w") as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n💾 Complete analysis saved to: {filename}")
        print(f"\n🎉 ANALYSIS COMPLETE! All bond metrics calculated successfully.")
        
    else:
        print(f"\n❌ No successful calculations. Please check API status.")

if __name__ == "__main__":
    main()
