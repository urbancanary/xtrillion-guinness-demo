#!/usr/bin/env python3
"""
Test all examples from Quick Start Guide
"""

import subprocess
import json
import time

def run_curl_command(command):
    """Run a curl command and return the response"""
    print(f"\n{'='*80}")
    print(f"Running: {command[:100]}...")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            response = json.loads(result.stdout)
            print(json.dumps(response, indent=2))
            return response
        else:
            print(f"Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

# Test 1: Default format (should be fast ~25ms)
print("\n### TEST 1: Bond Analysis - Default (Fast) Format ###")
cmd1 = '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '{
    "description": "T 3 15/08/52",
    "price": 71.66,
    "settlement_date": "2025-08-01"
  }' '''
response1 = run_curl_command(cmd1)

# Test 2: Full analytics format (should be slower ~450ms)
print("\n### TEST 2: Bond Analysis - Full Format ###")
cmd2 = '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '{
    "description": "T 3 15/08/52",
    "price": 71.66,
    "format": "full"
  }' '''
response2 = run_curl_command(cmd2)

# Test 3: Using ISIN
print("\n### TEST 3: Bond Analysis - Using ISIN ###")
cmd3 = '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '{
    "isin": "US912810TJ79",
    "price": 71.66
  }' '''
response3 = run_curl_command(cmd3)

# Test 4: Corporate bond with override
print("\n### TEST 4: Bond Analysis - With Override ###")
cmd4 = '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '{
    "description": "AAPL 3.45 02/09/2029",
    "price": 97.25,
    "overrides": {
      "day_count": "Thirty360.BondBasis",
      "business_convention": "ModifiedFollowing",
      "end_of_month": false
    }
  }' '''
response4 = run_curl_command(cmd4)

# Test 5: Flexible format
print("\n### TEST 5: Flexible Bond Analysis ###")
cmd5 = '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis/flexible" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '["T 3 15/08/52", 71.66, "2025-08-01"]' '''
response5 = run_curl_command(cmd5)

# Test 6: Portfolio Analysis
print("\n### TEST 6: Portfolio Analysis ###")
cmd6 = '''curl -X POST "https://api.x-trillion.ai/api/v1/portfolio/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '{
    "settlement_date": "2025-08-01",
    "data": [
      {
        "ISIN": "T 3 15/08/52",
        "CLOSING PRICE": 71.66,
        "WEIGHTING": 0.4
      },
      {
        "ISIN": "PANAMA, 3.87%, 23-Jul-2060",
        "CLOSING PRICE": 56.60,
        "WEIGHTING": 0.3
      },
      {
        "ISIN": "INDONESIA, 3.85%, 15-Oct-2030",
        "CLOSING PRICE": 90.21,
        "WEIGHTING": 0.3
      }
    ]
  }' '''
response6 = run_curl_command(cmd6)

# Test 7: Override with scenario analysis
print("\n### TEST 7: Override - Scenario Analysis ###")
cmd7 = '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '{
    "description": "MSFT 2.4 08/08/2026",
    "price": 96.50,
    "overrides": {
      "coupon": 2.75
    }
  }' '''
response7 = run_curl_command(cmd7)

# Test 8: Override with ISIN
print("\n### TEST 8: Override - ISIN with conventions ###")
cmd8 = '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" \
  -d '{
    "isin": "US912810TJ79",
    "price": 71.66,
    "overrides": {
      "coupon": 3.125,
      "maturity": "2052-08-15"
    }
  }' '''
response8 = run_curl_command(cmd8)

# Test 9: API Version
print("\n### TEST 9: API Version ###")
cmd9 = '''curl "https://api.x-trillion.ai/api/v1/version" \
  -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" '''
response9 = run_curl_command(cmd9)

# Summary
print("\n" + "="*80)
print("SUMMARY OF TESTS")
print("="*80)

tests = [
    ("Default Bond Analysis", response1),
    ("Full Format Analysis", response2),
    ("ISIN Analysis", response3),
    ("Corporate with Override", response4),
    ("Flexible Format", response5),
    ("Portfolio Analysis", response6),
    ("Scenario Override", response7),
    ("ISIN Override", response8),
    ("API Version", response9)
]

for name, resp in tests:
    if resp:
        if 'metadata' in resp and 'response_time_ms' in resp['metadata']:
            time_ms = resp['metadata']['response_time_ms']
            print(f"✓ {name}: {time_ms}ms")
        elif 'status' in resp and resp['status'] == 'success':
            print(f"✓ {name}: Success")
        else:
            print(f"✓ {name}: Response received")
    else:
        print(f"✗ {name}: Failed")