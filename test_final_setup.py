#!/usr/bin/env python3
"""
Final API setup verification
"""

import requests
import json

# API Keys
KEYS = {
    'admin': 'gax10_admin_9k3m7p5w2r8t6v4x1z',
    'maia': 'gax10_maia_7k9d2m5p8w1e6r4t3y2x',
    'demo': 'gax10_demo_3j5h8m9k2p6r4t7w1q',
    'invalid': 'invalid_key_12345'
}

# Test configurations
TESTS = [
    {
        'name': 'RMB Dev - No key',
        'url': 'https://development-dot-future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis',
        'key': None,
        'expected': 200
    },
    {
        'name': 'RMB Dev - With admin key',
        'url': 'https://development-dot-future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis',
        'key': 'admin',
        'expected': 200
    },
    {
        'name': 'Maia Dev - No key',
        'url': 'https://api-dev.x-trillion.ai/api/v1/bond/analysis',
        'key': None,
        'expected': 401
    },
    {
        'name': 'Maia Dev - Admin key',
        'url': 'https://api-dev.x-trillion.ai/api/v1/bond/analysis',
        'key': 'admin',
        'expected': 200
    },
    {
        'name': 'Maia Dev - Maia key',
        'url': 'https://api-dev.x-trillion.ai/api/v1/bond/analysis',
        'key': 'maia',
        'expected': 200
    },
    {
        'name': 'Maia Dev - Invalid key',
        'url': 'https://api-dev.x-trillion.ai/api/v1/bond/analysis',
        'key': 'invalid',
        'expected': 401
    },
    {
        'name': 'Production - No key',
        'url': 'https://api.x-trillion.ai/api/v1/bond/analysis',
        'key': None,
        'expected': 401
    },
    {
        'name': 'Production - Admin key',
        'url': 'https://api.x-trillion.ai/api/v1/bond/analysis',
        'key': 'admin',
        'expected': 200
    },
    {
        'name': 'Production - Maia key',
        'url': 'https://api.x-trillion.ai/api/v1/bond/analysis',
        'key': 'maia',
        'expected': 200
    },
    {
        'name': 'Production - Demo key',
        'url': 'https://api.x-trillion.ai/api/v1/bond/analysis',
        'key': 'demo',
        'expected': 200
    }
]

def run_test(test):
    """Run a single test"""
    headers = {'Content-Type': 'application/json'}
    if test['key']:
        headers['X-API-Key'] = KEYS[test['key']]
    
    data = {"description": "T 3 15/08/52", "price": 71.66}
    
    try:
        response = requests.post(test['url'], json=data, headers=headers, timeout=10)
        
        if response.status_code == test['expected']:
            return True, f"✅ {response.status_code}"
        else:
            return False, f"❌ Got {response.status_code}, expected {test['expected']}"
    except Exception as e:
        return False, f"❌ Error: {e}"

def main():
    print("🔍 Final API Setup Verification")
    print("=" * 60)
    
    results = []
    for test in TESTS:
        success, message = run_test(test)
        results.append((test['name'], success, message))
        
        print(f"\n{test['name']}")
        print(f"  Key: {test['key'] or 'None'}")
        print(f"  Result: {message}")
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    
    all_passed = all(r[1] for r in results)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nYour setup is perfect:")
        print("- RMB Dev: No authentication (your playground)")
        print("- Maia Dev & Production: Strict authentication")
        print("- Admin key works everywhere")
        print("- Maia's key works in their environments")
    else:
        print("❌ Some tests failed:")
        for name, success, message in results:
            if not success:
                print(f"  - {name}: {message}")

if __name__ == "__main__":
    main()