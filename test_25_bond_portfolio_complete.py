#!/usr/bin/env python3
"""
Test all 25 bonds from the user's portfolio using the restored GitHub API
Returns yield, spread, and duration for each bond
"""

import requests
import json
import pandas as pd
from datetime import datetime
import time

# API endpoint
API_BASE = "http://localhost:8081"

# Portfolio data
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

def test_api_health():
    """Test if API is running"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def calculate_bond(bond_data):
    """Calculate yield, duration, spread for a single bond"""
    payload = {
        "description": bond_data["name"],
        "price": bond_data["price"]
        # NO settlement_date - let system use default (last month end)
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/bond/parse-and-calculate",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                analytics = result.get("analytics", {})
                return {
                    "success": True,
                    "yield": analytics.get("yield", 0),
                    "duration": analytics.get("duration", 0),
                    "spread": analytics.get("spread", 0),
                    "confidence": result.get("processing", {}).get("confidence", "unknown")
                }
        
        return {"success": False, "error": f"HTTP {response.status_code}: {response.text[:200]}"}
    
    except Exception as e:
        return {"success": False, "error": str(e)[:100]}

def main():
    print("🧪 TESTING ALL 25 BONDS WITH RESTORED GITHUB API")
    print("=" * 80)
    
    # Check API health
    if not test_api_health():
        print("❌ API is not responding. Please start the API first.")
        print("Run: python3 google_analysis9_api.py")
        return
    
    print("✅ API is healthy and responding")
    print()
    
    # Process all bonds
    results = []
    successful = 0
    failed = 0
    
    print("Processing bonds...")
    
    for i, bond in enumerate(BOND_PORTFOLIO, 1):
        print(f"🔄 [{i:2d}/25] {bond['isin']} - {bond['name'][:40]}...")
        
        result = calculate_bond(bond)
        
        if result["success"]:
            successful += 1
            status = "✅"
            yield_str = f"{result['yield']:.2f}%"
            duration_str = f"{result['duration']:.2f}"
            spread_str = f"{result['spread']:+.0f}bp"
        else:
            failed += 1
            status = "❌"
            yield_str = "FAILED"
            duration_str = "FAILED"  
            spread_str = "FAILED"
            print(f"    ⚠️  Error: {result['error']}")
        
        results.append({
            "Rank": i,
            "ISIN": bond["isin"],
            "Name": bond["name"][:50],
            "Price": bond["price"],
            "Yield": yield_str,
            "Duration": duration_str,
            "Spread": spread_str,
            "Status": status
        })
        
        # Small delay to be respectful to API
        time.sleep(0.2)
    
    print()
    print("📊 COMPLETE PORTFOLIO RESULTS")
    print("=" * 120)
    
    # Create DataFrame for nice formatting
    df = pd.DataFrame(results)
    
    # Print results table
    print(df.to_string(index=False, max_colwidth=50))
    
    print()
    print("📈 PORTFOLIO SUMMARY")
    print("-" * 40)
    print(f"✅ Successful calculations: {successful}/25 ({successful/25*100:.1f}%)")
    print(f"❌ Failed calculations: {failed}/25 ({failed/25*100:.1f}%)")
    
    if successful > 0:
        # Calculate portfolio-level statistics
        successful_results = [r for r in results if "%" in str(r["Yield"])]
        
        if successful_results:
            yields = [float(r["Yield"].replace("%", "")) for r in successful_results]
            durations = [float(r["Duration"]) for r in successful_results if r["Duration"] != "FAILED"]
            
            print()
            print("🎯 PORTFOLIO ANALYTICS")
            print("-" * 40)
            print(f"Average Yield: {sum(yields)/len(yields):.2f}%")
            print(f"Yield Range: {min(yields):.2f}% - {max(yields):.2f}%")
            if durations:
                print(f"Average Duration: {sum(durations)/len(durations):.2f} years")
                print(f"Duration Range: {min(durations):.2f} - {max(durations):.2f} years")
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"portfolio_test_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump({
            "test_metadata": {
                "timestamp": timestamp,
                "api_endpoint": API_BASE,
                "total_bonds": len(BOND_PORTFOLIO),
                "successful": successful,
                "failed": failed
            },
            "results": results
        }, f, indent=2)
    
    print(f"💾 Results saved to: {filename}")
    
    print()
    if successful == 25:
        print("🎉 PERFECT! All 25 bonds calculated successfully!")
    elif successful >= 20:
        print("🎯 EXCELLENT! Most bonds calculated successfully!")
    elif successful >= 15:
        print("👍 GOOD! Majority of bonds calculated successfully!")
    else:
        print("⚠️  NEEDS WORK! Many bond calculations failed.")

if __name__ == "__main__":
    main()
