#!/usr/bin/env python3
"""
Final test of all documentation examples
"""

import subprocess
import json
import time

def run_curl(command):
    """Run curl command and return result"""
    print(f"\nTesting: {command[:100]}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                if 'error' in response:
                    return False, f"API Error: {response.get('error')}"
                return True, "Success"
            except json.JSONDecodeError:
                return False, f"Invalid JSON: {result.stdout[:100]}"
        else:
            return False, f"HTTP Error: {result.stderr[:100]}"
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)

# Test Quick Start examples
print("="*60)
print("TESTING QUICK START GUIDE EXAMPLES")
print("="*60)

quickstart_tests = [
    # Bond analysis
    '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"description": "T 3 15/08/52", "price": 71.66, "settlement_date": "2025-08-01"}' ''',
    
    # Portfolio context
    '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"description": "T 3 15/08/52", "price": 71.66, "context": "portfolio"}' ''',
    
    # ISIN
    '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"isin": "US912810TJ79", "price": 71.66}' ''',
    
    # Overrides
    '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"description": "AAPL 3.45 02/09/2029", "price": 97.25, "overrides": {"day_count": "Thirty360.BondBasis", "business_convention": "ModifiedFollowing", "end_of_month": false}}' ''',
    
    # Flexible format
    '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis/flexible" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '["T 3 15/08/52", 71.66, "2025-08-01"]' ''',
    
    # Portfolio
    '''curl -X POST "https://api.x-trillion.ai/api/v1/portfolio/analysis" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"settlement_date": "2025-08-01", "data": [{"description": "T 3 15/08/52", "CLOSING PRICE": 71.66, "WEIGHTING": 0.4}, {"description": "PANAMA, 3.87%, 23-Jul-2060", "CLOSING PRICE": 56.60, "WEIGHTING": 0.3}, {"description": "INDONESIA, 3.85%, 15-Oct-2030", "CLOSING PRICE": 90.21, "WEIGHTING": 0.3}]}' ''',
    
    # Cash flow
    '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/cashflow" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"bonds": [{"description": "T 3 15/08/52", "nominal": 1000000}], "filter": "all", "settlement_date": "2025-08-01"}' ''',
    
    # Health check
    '''curl "https://api.x-trillion.ai/api/v1/health" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" ''',
    
    # Version
    '''curl "https://api.x-trillion.ai/api/v1/version" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" '''
]

results = []
for i, test in enumerate(quickstart_tests, 1):
    success, message = run_curl(test)
    results.append((i, success, message))
    time.sleep(0.5)  # Be nice to the API

# Test External doc examples
print("\n" + "="*60)
print("TESTING EXTERNAL API DOCUMENTATION EXAMPLES")
print("="*60)

external_tests = [
    # Standard bond
    '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"description": "T 3 15/08/52", "price": 71.66, "settlement_date": "2025-07-30"}' ''',
    
    # Portfolio with descriptions
    '''curl -X POST "https://api.x-trillion.ai/api/v1/portfolio/analysis" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"data": [{"description": "T 3 15/08/52", "CLOSING PRICE": 71.66, "WEIGHTING": 50.0}, {"description": "T 4.1 02/15/28", "CLOSING PRICE": 99.5, "WEIGHTING": 50.0}]}' ''',
    
    # Cash flow next
    '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/cashflow/next" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"bonds": [{"description": "T 3 15/08/52", "nominal": 1000000}]}' ''',
    
    # Cash flow period
    '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/cashflow/period/180" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"bonds": [{"description": "T 3 15/08/52", "nominal": 1000000}, {"description": "AAPL 3.45 02/09/29", "nominal": 500000}]}' '''
]

external_results = []
for i, test in enumerate(external_tests, 1):
    success, message = run_curl(test)
    external_results.append((i, success, message))
    time.sleep(0.5)

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)

print("\nQuick Start Guide Results:")
for i, success, message in results:
    status = "✅" if success else "❌"
    print(f"  Test {i}: {status} {message}")

print(f"\nQuick Start: {sum(1 for _, s, _ in results if s)}/{len(results)} passed")

print("\nExternal Documentation Results:")
for i, success, message in external_results:
    status = "✅" if success else "❌"
    print(f"  Test {i}: {status} {message}")

print(f"\nExternal Docs: {sum(1 for _, s, _ in external_results if s)}/{len(external_results)} passed")

total_passed = sum(1 for _, s, _ in results if s) + sum(1 for _, s, _ in external_results if s)
total_tests = len(results) + len(external_results)
print(f"\nOVERALL: {total_passed}/{total_tests} tests passed")

if total_passed < total_tests:
    print("\n⚠️  Some tests failed - documentation examples may need updating!")
else:
    print("\n✅ All documentation examples are working correctly!")