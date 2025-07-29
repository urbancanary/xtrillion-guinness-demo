#!/usr/bin/env python3
"""
Test Context Implementation
==========================

Test the new context-aware response formatting to ensure it works correctly.
"""

import requests
import json
import time

# Test configurations
API_BASE = "http://localhost:8080"  # Local testing
API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q"

def test_context_functionality():
    """Test all context options work as expected"""
    
    test_bond = {
        "description": "T 4.625 02/15/25",
        "price": 99.5
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    print("🧪 Testing Context-Aware Response Formatting")
    print("=" * 50)
    
    # Test 1: Default context (no context parameter)
    print("\n1️⃣ Testing DEFAULT context...")
    default_payload = test_bond.copy()
    
    try:
        response = requests.post(f"{API_BASE}/api/v1/bond/parse-and-calculate", 
                               json=default_payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data.get('status')}")
            print(f"   📊 Context: {data.get('context', 'not set')}")
            print(f"   📈 Analytics fields: {len(data.get('analytics', {}))}")
            print(f"   🔧 Metadata context: {data.get('metadata', {}).get('context_applied', 'not set')}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Portfolio context
    print("\n2️⃣ Testing PORTFOLIO context...")
    portfolio_payload = test_bond.copy()
    portfolio_payload["context"] = "portfolio"
    
    try:
        response = requests.post(f"{API_BASE}/api/v1/bond/parse-and-calculate", 
                               json=portfolio_payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data.get('status')}")
            print(f"   📊 Context: {data.get('context')}")
            print(f"   📈 Analytics fields: {len(data.get('analytics', {}))}")
            print(f"   🎯 Optimization: {data.get('optimization', 'not set')}")
            print(f"   💰 Yield Semi: {data.get('analytics', {}).get('yield_semi')}")
            print(f"   💰 Yield Annual: {data.get('analytics', {}).get('yield_annual')}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Technical context
    print("\n3️⃣ Testing TECHNICAL context...")
    technical_payload = test_bond.copy()
    technical_payload["context"] = "technical"
    
    try:
        response = requests.post(f"{API_BASE}/api/v1/bond/parse-and-calculate", 
                               json=technical_payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data.get('status')}")
            print(f"   📊 Context: {data.get('context')}")
            print(f"   🔧 Debug info available: {'debug_info' in data}")
            print(f"   📈 Analytics fields: {len(data.get('analytics', {}))}")
            if 'debug_info' in data:
                debug = data['debug_info']
                print(f"   🔍 Parsing route: {debug.get('parsing_route')}")
                print(f"   ⚙️ Universal parser: {debug.get('universal_parser_used')}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Context implementation test complete!")

if __name__ == "__main__":
    test_context_functionality()
