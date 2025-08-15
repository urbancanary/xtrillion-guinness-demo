#!/usr/bin/env python3
"""
Test and compare context responses
"""

import requests
import json

BASE_URL = "https://test-minimal-dot-future-footing-414610.uc.r.appspot.com"
API_KEY = "gax10_maia_7k9d2m5p8w1e6r4t3y2x"

test_bond = {
    "description": "T 3 15/08/52",
    "price": 71.66,
    "settlement_date": "2025-08-01"
}

print("Testing context parameter functionality")
print("=" * 80)

# Test 1: Default (no context)
print("\n1. DEFAULT (no context):")
print("-" * 60)
response = requests.post(
    f"{BASE_URL}/api/v1/bond/analysis",
    headers={"Content-Type": "application/json", "X-API-Key": API_KEY},
    json=test_bond
)
if response.status_code == 200:
    data = response.json()
    print(f"✅ Success")
    print(f"   Response size: {len(json.dumps(data))} chars")
    print(f"   Top-level keys: {list(data.keys())}")
    print(f"   Analytics fields: {len(data.get('analytics', {}))}")
else:
    print(f"❌ Error: {response.status_code}")

# Test 2: Portfolio context
print("\n2. PORTFOLIO context:")
print("-" * 60)
portfolio_request = test_bond.copy()
portfolio_request["context"] = "portfolio"
response = requests.post(
    f"{BASE_URL}/api/v1/bond/analysis",
    headers={"Content-Type": "application/json", "X-API-Key": API_KEY},
    json=portfolio_request
)
if response.status_code == 200:
    data = response.json()
    print(f"✅ Success")
    print(f"   Response size: {len(json.dumps(data))} chars")
    print(f"   Top-level keys: {list(data.keys())}")
    print(f"   Analytics fields: {len(data.get('analytics', {}))}")
    print(f"   Context: {data.get('context')}")
    print(f"   Optimization: {data.get('optimization')}")
    
    # Show analytics structure
    if 'analytics' in data:
        analytics = data['analytics']
        print("\n   Portfolio-optimized fields:")
        for key in sorted(analytics.keys()):
            print(f"     - {key}: {analytics[key]}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.json())

# Test 3: Technical context
print("\n3. TECHNICAL context:")
print("-" * 60)
technical_request = test_bond.copy()
technical_request["context"] = "technical"
response = requests.post(
    f"{BASE_URL}/api/v1/bond/analysis",
    headers={"Content-Type": "application/json", "X-API-Key": API_KEY},
    json=technical_request
)
if response.status_code == 200:
    data = response.json()
    print(f"✅ Success")
    print(f"   Response size: {len(json.dumps(data))} chars")
    print(f"   Top-level keys: {list(data.keys())}")
    print(f"   Analytics fields: {len(data.get('analytics', {}))}")
    print(f"   Context: {data.get('context')}")
    
    # Show debug info
    if 'debug_info' in data:
        print("\n   Debug info:")
        for key, value in data['debug_info'].items():
            print(f"     - {key}: {value}")
else:
    print(f"❌ Error: {response.status_code}")

print("\n" + "=" * 80)
print("SUMMARY: Context parameter provides optimized responses for different use cases")