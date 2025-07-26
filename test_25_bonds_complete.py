#!/usr/bin/env python3
"""
🏛️ Complete 25-Bond Portfolio Analytics Test
===========================================
Calculate yield, duration, and spread for all 25 bonds using Google Analysis 10 API
Settlement Date: 2025-06-30 (Prior Month End)
"""

import requests
import json
import time
from typing import Dict, List, Tuple

# API Configuration
API_BASE = "http://localhost:8081"
SETTLEMENT_DATE = "2025-06-30"

# 25-Bond Portfolio Data
BONDS = [
    ("US912810TJ79", 71.66, "US TREASURY N/B, 3%, 15-Aug-2052"),
    ("XS2249741674", 77.88, "GALAXY PIPELINE, 3.25%, 30-Sep-2040"),
    ("XS1709535097", 89.40, "ABU DHABI CRUDE, 4.6%, 02-Nov-2047"),
    ("XS1982113463", 87.14, "SAUDI ARAB OIL, 4.25%, 16-Apr-2039"),
    ("USP37466AS18", 80.39, "EMPRESA METRO, 4.7%, 07-May-2050"),
    ("USP3143NAH72", 101.63, "CODELCO INC, 6.15%, 24-Oct-2036"),
    ("USP30179BR86", 86.42, "COMISION FEDERAL, 6.264%, 15-Feb-2052"),
    ("US195325DX04", 52.71, "COLOMBIA REP OF, 3.875%, 15-Feb-2061"),
    ("US279158AJ82", 69.31, "ECOPETROL SA, 5.875%, 28-May-2045"),
    ("USP37110AM89", 76.24, "EMPRESA NACIONAL, 4.5%, 14-Sep-2047"),
    ("XS2542166231", 103.03, "GREENSAIF PIPELI, 6.129%, 23-Feb-2038"),
    ("XS2167193015", 64.50, "STATE OF ISRAEL, 3.8%, 13-May-2060"),
    ("XS1508675508", 82.42, "SAUDI INT BOND, 4.5%, 26-Oct-2046"),
    ("XS1807299331", 92.21, "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048"),
    ("US91086QAZ19", 78.00, "UNITED MEXICAN, 5.75%, 12-Oct-2110"),
    ("USP6629MAD40", 82.57, "MEXICO CITY ARPT, 5.5%, 31-Jul-2047"),
    ("US698299BL70", 56.60, "PANAMA, 3.87%, 23-Jul-2060"),
    ("US71654QDF63", 71.42, "PETROLEOS MEXICA, 6.95%, 28-Jan-2060"),
    ("US71654QDE98", 89.55, "PETROLEOS MEXICA, 5.95%, 28-Jan-2031"),
    ("XS2585988145", 85.54, "GACI FIRST INVST, 5.125%, 14-Feb-2053"),
    ("XS1959337749", 89.97, "QATAR STATE OF, 4.817%, 14-Mar-2049"),
    ("XS2233188353", 99.23, "QNB FINANCE LTD, 1.625%, 22-Sep-2025"),
    ("XS2359548935", 73.79, "QATAR ENERGY, 3.125%, 12-Jul-2041"),
    ("XS0911024635", 93.29, "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043"),
    ("USP0R80BAG79", 97.26, "SITIOS, 5.375%, 04-Apr-2032"),
]

def calculate_bond(isin: str, price: float, description: str) -> Dict:
    """Calculate bond metrics using Google Analysis 10 API"""
    
    payload = {
        "description": description,
        "price": price,
        "settlement_date": SETTLEMENT_DATE
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/bond/parse-and-calculate",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                analytics = data.get("analytics", {})
                return {
                    "isin": isin,
                    "price": price,
                    "description": description,
                    "yield": analytics.get("yield", 0.0),
                    "duration": analytics.get("duration", 0.0),
                    "spread": analytics.get("spread", 0.0),
                    "success": True
                }
            else:
                print(f"❌ API Error for {isin}: {data.get('error', 'Unknown error')}")
                return {"isin": isin, "success": False, "error": data.get('error')}
        else:
            print(f"❌ HTTP Error {response.status_code} for {isin}")
            return {"isin": isin, "success": False, "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"❌ Exception for {isin}: {e}")
        return {"isin": isin, "success": False, "error": str(e)}

def main():
    print("🚀 Starting 25-Bond Portfolio Analytics Calculation")
    print(f"📅 Settlement Date: {SETTLEMENT_DATE}")
    print(f"🌐 API Base: {API_BASE}")
    print(f"📊 Total Bonds: {len(BONDS)}")
    print("-" * 80)
    
    results = []
    treasury_yield = None
    
    # Calculate each bond
    for i, (isin, price, description) in enumerate(BONDS, 1):
        print(f"📊 [{i:2d}/25] Processing {isin}...")
        
        result = calculate_bond(isin, price, description)
        results.append(result)
        
        # Save Treasury yield for spread calculations
        if "US TREASURY" in description and result.get("success"):
            treasury_yield = result["yield"]
            print(f"✅ Treasury Benchmark: {treasury_yield:.2f}%")
        
        # Brief pause to avoid overwhelming the API
        time.sleep(0.1)
    
    # Calculate success rate
    successful = [r for r in results if r.get("success")]
    success_rate = len(successful) / len(results) * 100
    
    print("\n" + "=" * 80)
    print(f"📊 CALCULATION COMPLETE - Success Rate: {success_rate:.1f}% ({len(successful)}/25)")
    print("=" * 80)
    
    # Display results table
    print("\n🏛️ 25-Bond Portfolio Analytics Results")
    print(f"Settlement Date: {SETTLEMENT_DATE} | Treasury Benchmark: {treasury_yield:.2f}%")
    print("-" * 120)
    print(f"{'#':<3} {'ISIN':<15} {'Price':<8} {'Description':<35} {'Yield (%)':<9} {'Duration':<9} {'Spread (bps)':<12}")
    print("-" * 120)
    
    portfolio_yield = 0
    portfolio_duration = 0
    portfolio_spread = 0
    
    for i, result in enumerate(results, 1):
        if result.get("success"):
            yield_val = result["yield"]
            duration_val = result["duration"]
            spread_val = result.get("spread", 0)
            
            # If spread not provided, calculate vs Treasury
            if spread_val == 0 and treasury_yield:
                spread_val = (yield_val - treasury_yield) * 100  # Convert to basis points
            
            portfolio_yield += yield_val
            portfolio_duration += duration_val
            portfolio_spread += spread_val
            
            print(f"{i:<3} {result['isin']:<15} {result['price']:<8.2f} {result['description'][:35]:<35} "
                  f"{yield_val:<9.2f} {duration_val:<9.2f} {spread_val:<12.0f}")
        else:
            print(f"{i:<3} {result['isin']:<15} {'ERROR':<8} {result.get('error', 'Unknown')[:35]:<35} "
                  f"{'---':<9} {'---':<9} {'---':<12}")
    
    print("-" * 120)
    
    if successful:
        avg_yield = portfolio_yield / len(successful)
        avg_duration = portfolio_duration / len(successful)
        avg_spread = portfolio_spread / len(successful)
        
        print(f"📊 Portfolio Averages:")
        print(f"   Average Yield: {avg_yield:.2f}%")
        print(f"   Average Duration: {avg_duration:.2f} years")
        print(f"   Average Spread: {avg_spread:.0f} bps")
        
        # Export to JSON
        export_data = {
            "calculation_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "settlement_date": SETTLEMENT_DATE,
            "treasury_benchmark": treasury_yield,
            "portfolio_summary": {
                "total_bonds": len(BONDS),
                "successful_calculations": len(successful),
                "success_rate": success_rate,
                "average_yield": avg_yield,
                "average_duration": avg_duration,
                "average_spread": avg_spread
            },
            "bond_results": results
        }
        
        filename = f"portfolio_analytics_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"\n💾 Results exported to: {filename}")

if __name__ == "__main__":
    main()
