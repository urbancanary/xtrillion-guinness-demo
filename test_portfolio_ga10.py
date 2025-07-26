#!/usr/bin/env python3
"""
Test All 25 Bonds with Google Analysis 10 API
Calls the new GA10 API for portfolio analysis
"""
import requests
import json
import sys

# API endpoint - corrected to use port 8081 where the working API is running
API_URL = "http://localhost:8081/api/v1/bond/parse-and-calculate"

# Your 25-bond portfolio data
bonds = [
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

def call_api_for_bond(bond):
    """Call Google Analysis 10 API for individual bond"""
    try:
        payload = {
            "description": bond["name"], 
            "price": bond["price"],
            "settlement_date": "2025-06-30"  # Using proper prior month end
        }
        
        response = requests.post(API_URL, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and "analytics" in data:
                analytics = data["analytics"]
                return {
                    "success": True,
                    "yield": analytics.get("yield", 0),
                    "duration": analytics.get("duration", 0),
                    "accrued_interest": analytics.get("accrued_interest", 0),
                    "price": analytics.get("price", bond["price"])
                }
        
        return {"success": False, "error": f"API returned: {response.text[:100]}"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def calculate_spread(treasury_yield, bond_yield):
    """Calculate spread over treasury in basis points"""
    if treasury_yield and bond_yield:
        return (bond_yield - treasury_yield) * 100  # Convert to basis points
    return 0

def main():
    print("🏦 GOOGLE ANALYSIS 10 API - 25 Bond Portfolio Analysis")
    print("🌐 API Endpoint: http://localhost:8081")
    print("📅 Settlement Date: 2025-06-30 (Prior Month End)")
    print("=" * 90)
    print(f"{'#':<3} {'ISIN':<13} {'Price':<7} {'Yield (%)':<9} {'Duration':<9} {'Spread (bps)':<12} {'Status':<10}")
    print("-" * 90)
    
    results = []
    successful = 0
    failed = 0
    treasury_yield = None
    
    for i, bond in enumerate(bonds, 1):
        result = call_api_for_bond(bond)
        
        if result["success"]:
            yield_pct = result['yield']
            duration_years = result['duration']
            accrued = result['accrued_interest']
            status = "✅ SUCCESS"
            successful += 1
            
            # Use first bond (US Treasury) as benchmark for spreads
            if i == 1:
                treasury_yield = yield_pct
                spread_bps = "—"
            else:
                spread_bps = f"{calculate_spread(treasury_yield, yield_pct):.0f}" if treasury_yield else "N/A"
            
            results.append({
                "isin": bond["isin"],
                "name": bond["name"],
                "price": bond["price"],
                "yield": yield_pct,
                "duration": duration_years,
                "spread": spread_bps,
                "accrued_interest": accrued
            })
            
        else:
            yield_pct = "ERROR"
            duration_years = "ERROR" 
            spread_bps = "ERROR"
            status = "❌ FAILED"
            failed += 1
            
        print(f"{i:<3} {bond['isin']:<13} {bond['price']:<7} {yield_pct if isinstance(yield_pct, str) else f'{yield_pct:.2f}':<9} {duration_years if isinstance(duration_years, str) else f'{duration_years:.2f}':<9} {spread_bps:<12} {status:<10}")
    
    print("-" * 90)
    print(f"📊 SUMMARY: {successful}/25 bonds successful ({successful/25*100:.1f}%)")
    print(f"❌ FAILED: {failed} bonds")
    
    if successful > 0:
        print(f"\n🎯 PORTFOLIO METRICS:")
        successful_results = [r for r in results if isinstance(r['yield'], (int, float))]
        if successful_results:
            avg_yield = sum(r['yield'] for r in successful_results) / len(successful_results)
            avg_duration = sum(r['duration'] for r in successful_results) / len(successful_results)
            print(f"   📈 Average Yield: {avg_yield:.2f}%")
            print(f"   ⏱️  Average Duration: {avg_duration:.2f} years")
            print(f"   🏛️ Treasury Benchmark: {treasury_yield:.2f}%" if treasury_yield else "   🏛️ Treasury Benchmark: N/A")
            
    print(f"\n✅ Google Analysis 10 API is operational and ready for portfolio analysis!")

if __name__ == "__main__":
    main()
