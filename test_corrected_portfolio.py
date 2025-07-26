#!/usr/bin/env python3
"""
Test the 25-bond portfolio with NO settlement date specified
Let the system use its default (last month end)
"""

import requests
import json
import pandas as pd
from datetime import datetime
import time

# API endpoint
API_BASE = "http://localhost:8081"

# Portfolio data - NO settlement_date specified
BOND_PORTFOLIO = [
    {"isin": "US912810TJ79", "price": 71.66, "name": "US TREASURY N/B, 3%, 15-Aug-2052"},
    {"isin": "XS2249741674", "price": 77.88, "name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040"},
    {"isin": "XS1709535097", "price": 89.40, "name": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047"},
    {"isin": "XS1982113463", "price": 87.14, "name": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039"},
    {"isin": "USP37466AS18", "price": 80.39, "name": "EMPRESA METRO, 4.7%, 07-May-2050"}
]

def calculate_bond(bond_data):
    """Calculate yield, duration, spread - NO settlement date specified"""
    payload = {
        "description": bond_data["name"],
        "price": bond_data["price"]
        # NO settlement_date parameter - let system default
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
                    "settlement": analytics.get("settlement", "unknown"),
                    "confidence": result.get("processing", {}).get("confidence", "unknown")
                }
        
        return {"success": False, "error": f"HTTP {response.status_code}"}
    
    except Exception as e:
        return {"success": False, "error": str(e)[:100]}

def main():
    print("🧪 TESTING WITH SYSTEM DEFAULT SETTLEMENT DATE")
    print("=" * 60)
    
    for i, bond in enumerate(BOND_PORTFOLIO, 1):
        print(f"\n🔄 [{i}/5] {bond['isin']} - {bond['name']}")
        
        result = calculate_bond(bond)
        
        if result["success"]:
            print(f"   Settlement: {result['settlement']}")
            print(f"   Yield: {result['yield']:.2f}%")
            print(f"   Duration: {result['duration']:.2f} years")
            print(f"   Spread: {result['spread']:+.0f}bp")
        else:
            print(f"   ❌ Error: {result['error']}")
        
        time.sleep(0.3)

if __name__ == "__main__":
    main()
