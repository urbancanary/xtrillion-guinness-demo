import requests
import json

API_KEY = "gax10_maia_7k9d2m5p8w1e6r4t3y2x"
BASE_URL = "https://api.x-trillion.ai"

def analyze_bond(description, price, settlement_date=None, overrides=None):
    """Analyze a single bond with optional parameter overrides"""
    
    url = f"{BASE_URL}/api/v1/bond/analysis"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    data = {
        "description": description,
        "price": price
    }
    
    if settlement_date:
        data["settlement_date"] = settlement_date
    
    if overrides:
        data["overrides"] = overrides
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        analytics = result["analytics"]
        print(f"Bond: {description}")
        print(f"YTM: {analytics['ytm']:.2f}%")
        print(f"Duration: {analytics['duration']:.2f} years")
        print(f"Spread: {analytics['spread']:.0f} bps")
        
        # Show overrides if applied
        if result.get("overrides_applied"):
            print(f"Overrides: {result['overrides_applied']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

# Example usage
analyze_bond("T 3 15/08/52", 71.66, "2025-08-01")

# Example with overrides - scenario analysis with different coupon
analyze_bond("AAPL 3.45 02/09/2029", 97.25, 
             overrides={"coupon": 3.75})  # What-if with higher coupon