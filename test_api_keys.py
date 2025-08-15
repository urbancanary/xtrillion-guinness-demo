#!/usr/bin/env python3
"""
Test API key requirements across all environments
"""

import requests
import json

# Test configurations
ENVIRONMENTS = {
    'RMB Dev': {
        'url': 'https://development-dot-future-footing-414610.uc.r.appspot.com',
        'should_require_key': False
    },
    'Maia Dev': {
        'url': 'https://api-dev.x-trillion.ai',
        'should_require_key': True
    },
    'Production': {
        'url': 'https://api.x-trillion.ai',
        'should_require_key': True  # Will be true after deployment
    }
}

# Maia's API key
MAIA_API_KEY = 'gax10_maia_7k9d2m5p8w1e6r4t3y2x'

# Test endpoint
TEST_ENDPOINT = '/api/v1/bond/analysis'
TEST_DATA = {
    "description": "T 3 15/08/52",
    "price": 71.66
}

def test_environment(name, config):
    """Test an environment with and without API key"""
    print(f"\n{'='*60}")
    print(f"Testing {name}")
    print(f"URL: {config['url']}")
    print(f"Should require API key: {config['should_require_key']}")
    print('-'*60)
    
    # Test without API key
    print("\n1. Testing WITHOUT API key:")
    try:
        response = requests.post(
            f"{config['url']}{TEST_ENDPOINT}",
            json=TEST_DATA,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"   ✅ Success (200) - API key NOT required")
            if config['should_require_key']:
                print(f"   ⚠️  WARNING: This environment SHOULD require API key!")
        elif response.status_code == 401:
            print(f"   ❌ Unauthorized (401) - API key required")
            if not config['should_require_key']:
                print(f"   ⚠️  WARNING: This environment should NOT require API key!")
        else:
            print(f"   ❓ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test with Maia's API key
    print("\n2. Testing WITH Maia's API key:")
    try:
        response = requests.post(
            f"{config['url']}{TEST_ENDPOINT}",
            json=TEST_DATA,
            headers={
                'Content-Type': 'application/json',
                'X-API-Key': MAIA_API_KEY
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"   ✅ Success (200) - Maia's key accepted")
            result = response.json()
            if result.get('status') == 'success':
                analytics = result.get('analytics', {})
                print(f"   📊 YTM: {analytics.get('ytm', 'N/A')}")
        elif response.status_code == 401:
            print(f"   ❌ Unauthorized (401) - Maia's key rejected")
            print(f"   Response: {response.json()}")
        else:
            print(f"   ❓ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    print("API Key Test Suite")
    print("==================")
    print(f"Maia's API Key: {MAIA_API_KEY}")
    
    for name, config in ENVIRONMENTS.items():
        test_environment(name, config)
    
    print(f"\n{'='*60}")
    print("Summary:")
    print("- RMB Dev: Should work WITHOUT key (your playground)")
    print("- Maia Dev: Should REQUIRE key (Maia's test environment)")
    print("- Production: Currently soft auth, will be strict after deployment")

if __name__ == "__main__":
    main()