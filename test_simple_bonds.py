#!/usr/bin/env python3
"""
Test script for user's bonds - SIMPLE VERSION
Test with just 3 bonds first to see if API works
"""

import json
import requests
from datetime import datetime

# API endpoint
API_BASE = "http://localhost:8080"

# Test with first 3 bonds only
test_bonds = [
    {"isin": "US912810TJ79", "price": 71.66, "weight": 1.03, "name": "US TREASURY N/B, 3%, 15-Aug-2052"},
    {"isin": "XS2249741674", "price": 77.88, "weight": 3.88, "name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040"},
    {"isin": "XS1982113463", "price": 87.14, "weight": 3.71, "name": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039"}
]

def test_individual_bond(bond):
    """Test individual bond calculation"""
    print(f"🔬 Testing: {bond['isin']} - {bond['name'][:40]}")
    
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
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Response keys: {list(result.keys())}")
            
            # Check for different possible response structures
            bond_calc = None
            if "calculated_bond" in result:
                bond_calc = result["calculated_bond"]
            elif "bond" in result:
                bond_calc = result["bond"]
            elif "result" in result:
                bond_calc = result["result"]
            else:
                # Maybe the data is directly in the result
                bond_calc = result
            
            if bond_calc and isinstance(bond_calc, dict):
                ytm = bond_calc.get("yield_to_maturity", bond_calc.get("yield", bond_calc.get("ytm", "N/A")))
                duration = bond_calc.get("duration", bond_calc.get("modified_duration", "N/A"))
                spread = bond_calc.get("spread_over_treasury", bond_calc.get("spread", "N/A"))
                
                print(f"   ✅ Yield: {ytm}")
                print(f"   ✅ Duration: {duration}")
                print(f"   ✅ Spread: {spread}")
                
                return {
                    "isin": bond["isin"],
                    "price": bond["price"],
                    "yield": ytm,
                    "duration": duration,
                    "spread": spread,
                    "status": "success"
                }
            else:
                print(f"   ❌ No bond calculation data found")
                print(f"   Full response: {json.dumps(result, indent=2)}")
                return {"isin": bond["isin"], "status": "no_data"}
        else:
            print(f"   ❌ Failed: {response.text}")
            return {"isin": bond["isin"], "status": "failed", "error": response.text}
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return {"isin": bond["isin"], "status": "exception", "error": str(e)}

def test_small_portfolio():
    """Test portfolio with just 3 bonds"""
    print(f"\n📊 Testing portfolio with {len(test_bonds)} bonds...")
    
    today = datetime.now().strftime("%Y/%m/%d")
    
    portfolio_data = {
        "data": [
            {
                "BOND_CD": bond["isin"],
                "CLOSING PRICE": bond["price"],
                "Inventory Date": today,
                "WEIGHTING": bond["weight"]
            }
            for bond in test_bonds
        ]
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/portfolio/analyze",
            json=portfolio_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Portfolio analysis successful!")
            print(f"   Response keys: {list(result.keys())}")
            return result
        else:
            print(f"   ❌ Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 SIMPLE BOND TEST - 3 BONDS ONLY")
    print("=" * 40)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API: {API_BASE}")
    
    # Test individual bonds
    individual_results = []
    for bond in test_bonds:
        result = test_individual_bond(bond)
        individual_results.append(result)
        print()
    
    # Test portfolio
    portfolio_result = test_small_portfolio()
    
    # Summary
    print(f"\n📋 SUMMARY:")
    successful = [r for r in individual_results if r.get("status") == "success"]
    print(f"   Individual bonds: {len(successful)}/{len(test_bonds)} successful")
    print(f"   Portfolio analysis: {'✅ Success' if portfolio_result else '❌ Failed'}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"simple_test_results_{timestamp}.json", "w") as f:
        json.dump({
            "individual_results": individual_results,
            "portfolio_result": portfolio_result,
            "timestamp": timestamp
        }, f, indent=2)

if __name__ == "__main__":
    main()
