#!/usr/bin/env python3
"""
Debug script to see what the API is actually returning
"""

import json
import requests
from datetime import datetime

API_BASE = "http://localhost:8080"

def debug_bond_response():
    """See exactly what the API returns"""
    
    bond_data = {
        "description": "US TREASURY N/B, 3%, 15-Aug-2052",
        "price": 71.66
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/bond/parse-and-calculate",
            json=bond_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Full response:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    debug_bond_response()
