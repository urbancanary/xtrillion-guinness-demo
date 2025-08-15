#!/usr/bin/env python3
"""
Test cash flow API endpoint
"""

import requests
import json
import time

# Wait a moment for server to fully start
time.sleep(2)

# Test URL
base_url = "http://localhost:8080"
api_key = "gax10_maia_7k9d2m5p8w1e6r4t3y2x"

# Test 1: Basic cash flow request
print("Test 1: Basic cash flow request")
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
        "settlement_date": "2025-07-30"
    }
)

print(f"Status code: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print("✅ Cash flow endpoint working!")
    print(f"Total cash flows: {result.get('total_cash_flows', 'N/A')}")
    print(f"Next payment date: {result.get('next_payment_date', 'N/A')}")
else:
    print(f"❌ Error: {response.text}")

# Test 2: Next cash flow only
print("\n\nTest 2: Next cash flow only")
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
        "settlement_date": "2025-07-30"
    }
)

print(f"Status code: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print("✅ Next cash flow endpoint working!")
    print(f"Total cash flows: {result.get('total_cash_flows', 'N/A')}")
else:
    print(f"❌ Error: {response.text}")

# Test 3: Period filter (90 days)
print("\n\nTest 3: Period filter (90 days)")
response = requests.post(
    f"{base_url}/api/v1/bond/cashflow/period/90",
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
        "settlement_date": "2025-07-30"
    }
)

print(f"Status code: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print("✅ Period cash flow endpoint working!")
    print(f"Total cash flows: {result.get('total_cash_flows', 'N/A')}")
else:
    print(f"❌ Error: {response.text}")