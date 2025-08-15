#!/usr/bin/env python3
"""
Test examples from External API Documentation
"""

import subprocess
import json

def run_test(name, command):
    """Run a test and show results"""
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print(f"{'='*80}")
    
    # Replace placeholder with actual API key
    command = command.replace("your_api_key_here", "gax10_maia_7k9d2m5p8w1e6r4t3y2x")
    
    print(f"Command: {command[:100]}...")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            response = json.loads(result.stdout)
            print("✅ Success")
            
            # Check for specific fields based on test
            if 'analytics' in response:
                print(f"  YTM: {response['analytics'].get('ytm', 'N/A')}")
                print(f"  Duration: {response['analytics'].get('duration', 'N/A')}")
            
            if 'metadata' in response and 'response_time_ms' in response['metadata']:
                print(f"  Response time: {response['metadata']['response_time_ms']}ms")
                
            if 'overrides_applied' in response:
                print(f"  Overrides: {response['overrides_applied']}")
                
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

# Test 1: Standard Bond Calculation
test1 = '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "description": "T 3 15/08/52",
    "price": 71.66,
    "settlement_date": "2025-07-30"
  }' '''

# Test 2: Scenario analysis with modified coupon
test2 = '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "description": "AAPL 3.45 02/09/2029",
    "price": 97.25,
    "overrides": {
      "coupon": 3.75
    }
  }' '''

# Test 3: Override conventions
test3 = '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "isin": "XS1234567890",
    "price": 98.50,
    "overrides": {
      "day_count": "ActualActual.Bond",
      "frequency": "Annual",
      "business_convention": "ModifiedFollowing"
    }
  }' '''

# Test 4: Portfolio Analysis
test4 = '''curl -X POST "https://api.x-trillion.ai/api/v1/portfolio/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "data": [
      {
        "description": "T 3 15/08/52",
        "CLOSING PRICE": 71.66,
        "WEIGHTING": 50.0
      },
      {
        "description": "T 4.1 02/15/28",
        "CLOSING PRICE": 99.5,
        "WEIGHTING": 50.0
      }
    ]
  }' '''

# Test 5: ISIN-based portfolio (alternative naming)
test5 = '''curl -X POST "https://api.x-trillion.ai/api/v1/portfolio/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "data": [
      {
        "BOND_CD": "US00131MAB90",
        "CLOSING PRICE": 71.66,
        "WEIGHTING": 50.0
      }
    ]
  }' '''

# Test 6: Cash flow analysis
test6 = '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/cashflow" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "bonds": [
      {
        "description": "T 3 15/08/52",
        "nominal": 1000000
      }
    ],
    "filter": "period",
    "days": 90,
    "context": "portfolio",
    "settlement_date": "2025-07-30"
  }' '''

# Test 7: Override example from section 8.2
test7 = '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "description": "IBM 4.0 06/20/2042",
    "price": 85.75,
    "overrides": {
      "coupon": 4.25,
      "maturity": "2042-06-20",
      "day_count": "Thirty360.BondBasis",
      "frequency": "Semiannual",
      "issuer": "International Business Machines Corp"
    }
  }' '''

# Test 8: Flexible format
test8 = '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis/flexible" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '["T 3 15/08/52", 71.66, "2025-07-31"]' '''

# Test 9: Portfolio context
test9 = '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "description": "T 3 15/08/52",
    "price": 71.66,
    "context": "portfolio"
  }' '''

# Test 10: Technical context
test10 = '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "description": "T 3 15/08/52",
    "price": 71.66,
    "context": "technical"
  }' '''

# Run all tests
tests = [
    ("Standard Bond Calculation", test1),
    ("Scenario Analysis - Modified Coupon", test2),
    ("Override Conventions - Unknown ISIN", test3),
    ("Portfolio Analysis", test4),
    ("ISIN-based Portfolio", test5),
    ("Cash Flow Analysis", test6),
    ("IBM Bond with Overrides", test7),
    ("Flexible Format", test8),
    ("Portfolio Context", test9),
    ("Technical Context", test10)
]

success_count = 0
for name, test in tests:
    if run_test(name, test):
        success_count += 1

print(f"\n{'='*80}")
print(f"SUMMARY: {success_count}/{len(tests)} tests passed")
print(f"{'='*80}")