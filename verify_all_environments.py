#!/usr/bin/env python3
"""
Verify all environments return identical results
"""

import requests
import json

# Test data
test_bond = {
    "description": "T 3 15/08/52",
    "price": 71.66,
    "settlement_date": "2025-08-01"
}

# Environment endpoints
environments = {
    "Production": {
        "url": "https://api.x-trillion.ai/api/v1/bond/analysis",
        "api_key": "gax10_maia_7k9d2m5p8w1e6r4t3y2x"
    },
    "Development": {
        "url": "https://development-dot-future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis",
        "api_key": "gax10_maia_7k9d2m5p8w1e6r4t3y2x"
    },
    "Test": {
        "url": "https://test-minimal-dot-future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis",
        "api_key": "gax10_maia_7k9d2m5p8w1e6r4t3y2x"
    }
}

results = {}

print("Testing all environments with T 3 15/08/52")
print("=" * 80)

for env_name, env_config in environments.items():
    print(f"\n{env_name}:")
    print("-" * 40)
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": env_config["api_key"]
    }
    
    try:
        response = requests.post(
            env_config["url"],
            headers=headers,
            json=test_bond,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Handle different response formats
            if "analytics" in data:
                analytics = data["analytics"]
            elif "data" in data:
                analytics = data["data"]
            else:
                analytics = data
            
            results[env_name] = {
                "ytm": analytics.get("ytm"),
                "duration": analytics.get("duration"),
                "convexity": analytics.get("convexity"),
                "accrued_interest": analytics.get("accrued_interest"),
                "spread": analytics.get("spread"),
                "z_spread": analytics.get("z_spread")
            }
            
            print(f"✅ Success")
            print(f"   YTM: {results[env_name]['ytm']:.6f}%")
            print(f"   Duration: {results[env_name]['duration']:.6f}")
            print(f"   Accrued: {results[env_name]['accrued_interest']:.6f}")
            
        else:
            print(f"❌ Error {response.status_code}: {response.text[:100]}")
            results[env_name] = None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        results[env_name] = None

# Compare results
print("\n" + "=" * 80)
print("COMPARISON:")
print("-" * 80)

if all(results.values()):
    # Get reference values from production
    ref_env = "Production"
    ref_values = results[ref_env]
    
    all_match = True
    for metric in ["ytm", "duration", "convexity", "accrued_interest", "spread", "z_spread"]:
        values = {env: results[env][metric] for env in results if results[env]}
        
        # Check if all values are the same
        unique_values = set(v for v in values.values() if v is not None)
        
        if len(unique_values) <= 1:
            print(f"✅ {metric:<20}: {ref_values[metric]}")
        else:
            print(f"❌ {metric:<20}: MISMATCH")
            for env, val in values.items():
                print(f"   {env}: {val}")
            all_match = False
    
    print("\n" + "=" * 80)
    if all_match:
        print("✅ SUCCESS: All environments return IDENTICAL results!")
    else:
        print("❌ FAILURE: Environments return different results!")
else:
    print("❌ Could not compare - some environments failed")