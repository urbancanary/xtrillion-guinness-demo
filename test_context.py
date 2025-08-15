#!/usr/bin/env python3
"""
Test context parameter functionality
"""

import requests
import json

BASE_URL = "http://localhost:8080"
API_KEY = "gax10_maia_7k9d2m5p8w1e6r4t3y2x"

test_bond = {
    "description": "T 3 15/08/52",
    "price": 71.66,
    "settlement_date": "2025-08-01"
}

contexts = ["portfolio", "technical", None]

for context in contexts:
    print(f"\n{'='*60}")
    print(f"Testing context: {context}")
    print(f"{'='*60}")
    
    request_data = test_bond.copy()
    if context:
        request_data["context"] = context
    
    response = requests.post(
        f"{BASE_URL}/api/v1/bond/analysis",
        headers={
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        },
        json=request_data
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success - Response structure:")
        
        # Show top-level keys
        print(f"   Top-level keys: {list(data.keys())}")
        
        # Show analytics keys
        if "analytics" in data:
            print(f"   Analytics keys: {list(data['analytics'].keys())}")
            if context == "portfolio":
                # Check for portfolio-specific fields
                portfolio_fields = ['yield_semi', 'yield_annual', 'duration_semi', 'duration_annual']
                found = [f for f in portfolio_fields if f in data['analytics']]
                print(f"   Portfolio fields found: {found}")
        
        # Show context info
        if "context" in data:
            print(f"   Context: {data['context']}")
        if "optimization" in data:
            print(f"   Optimization: {data['optimization']}")
            
        # Response size
        response_text = json.dumps(data, indent=2)
        print(f"   Response size: {len(response_text)} chars, {len(response_text.split(chr(10)))} lines")
    else:
        print(f"❌ Error {response.status_code}: {response.text[:100]}")