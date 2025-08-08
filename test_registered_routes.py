#!/usr/bin/env python3
"""
Check registered routes in the API
"""

import requests

# Test URL
base_url = "http://localhost:8080"

# Try to access a known endpoint first
print("Testing known endpoint /health...")
response = requests.get(f"{base_url}/health")
print(f"Health endpoint status: {response.status_code}")

# Also test the cash flow endpoint path structure
print("\nTesting various cash flow paths:")
paths = [
    "/v1/bond/cashflow",
    "/api/v1/bond/cashflow",
    "/bond/cashflow",
    "/cashflow"
]

for path in paths:
    response = requests.post(f"{base_url}{path}", json={})
    print(f"{path} - Status: {response.status_code}")