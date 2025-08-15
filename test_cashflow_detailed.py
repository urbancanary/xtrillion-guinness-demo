#!/usr/bin/env python3
"""
Detailed test of cash flow functionality
"""

import requests
import json

# Test URL
base_url = "http://localhost:8080"
api_key = "gax10_maia_7k9d2m5p8w1e6r4t3y2x"

# Test 1: Get all cash flows for a treasury bond
print("=== Test 1: All cash flows for T 3 15/08/52 ===")
response = requests.post(
    f"{base_url}/api/v1/bond/cashflow",
    headers={
        "Content-Type": "application/json",
        "X-API-Key": api_key
    },
    json={
        "bonds": [
            {
                "description": "T 3 15/08/52",
                "nominal": 1000000
            }
        ],
        "filter": "all",
        "context": "portfolio",
        "settlement_date": "2025-08-01"
    }
)

if response.status_code == 200:
    result = response.json()
    print(json.dumps(result, indent=2))
else:
    print(f"Error: {response.status_code} - {response.text}")

# Test 2: Get next cash flow only
print("\n\n=== Test 2: Next cash flow only ===")
response = requests.post(
    f"{base_url}/api/v1/bond/cashflow/next",
    headers={
        "Content-Type": "application/json",
        "X-API-Key": api_key
    },
    json={
        "bonds": [
            {
                "description": "T 3 15/08/52",
                "nominal": 1000000
            }
        ],
        "settlement_date": "2025-08-01"
    }
)

if response.status_code == 200:
    result = response.json()
    print(json.dumps(result, indent=2))
else:
    print(f"Error: {response.status_code} - {response.text}")

# Test 3: Get cash flows for next 180 days
print("\n\n=== Test 3: Cash flows for next 180 days ===")
response = requests.post(
    f"{base_url}/api/v1/bond/cashflow/period/180",
    headers={
        "Content-Type": "application/json",
        "X-API-Key": api_key
    },
    json={
        "bonds": [
            {
                "description": "T 3 15/08/52",
                "nominal": 1000000
            },
            {
                "description": "AAPL 3.45 02/09/29",
                "nominal": 500000
            }
        ],
        "settlement_date": "2025-08-01"
    }
)

if response.status_code == 200:
    result = response.json()
    print(json.dumps(result, indent=2))
else:
    print(f"Error: {response.status_code} - {response.text}")