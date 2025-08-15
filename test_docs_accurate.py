#!/usr/bin/env python3
"""
Accurate test of documentation examples - only tests what's actually in the docs
"""

import subprocess
import json
import time

def run_curl(command, test_name):
    """Run curl command and return result"""
    print(f"\n{test_name}")
    print("-" * len(test_name))
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                if 'error' in response and response['error']:
                    return False, f"API Error: {response.get('error')}"
                elif 'status' in response and response['status'] == 'error':
                    return False, f"API Error: {response.get('message', 'Unknown error')}"
                return True, "Success"
            except json.JSONDecodeError:
                # Check if it's HTML (404 error)
                if "<!doctype html>" in result.stdout.lower():
                    return False, "404 Not Found"
                return False, f"Invalid JSON: {result.stdout[:100]}"
        else:
            return False, f"HTTP Error: {result.stderr[:100] if result.stderr else 'Unknown error'}"
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)

# Quick Start Guide examples - exactly as they appear in the documentation
print("="*60)
print("TESTING QUICK START GUIDE EXAMPLES")
print("="*60)

quickstart_tests = [
    ("1. Bond analysis - comprehensive metrics", 
     '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"description": "T 3 15/08/52", "price": 71.66, "settlement_date": "2025-08-01"}' '''),
    
    ("2. Bond analysis - portfolio context", 
     '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"description": "T 3 15/08/52", "price": 71.66, "context": "portfolio"}' '''),
    
    ("3. Bond analysis - using ISIN", 
     '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"isin": "US912810TJ79", "price": 71.66}' '''),
    
    ("4. Bond analysis - with overrides", 
     '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"description": "AAPL 3.45 02/09/2029", "price": 97.25, "overrides": {"day_count": "Thirty360.BondBasis", "business_convention": "ModifiedFollowing", "end_of_month": false}}' '''),
    
    ("5. Flexible analysis - array format", 
     '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis/flexible" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '["T 3 15/08/52", 71.66, "2025-08-01"]' '''),
    
    ("6. Portfolio analysis", 
     '''curl -X POST "https://api.x-trillion.ai/api/v1/portfolio/analysis" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"settlement_date": "2025-08-01", "data": [{"description": "T 3 15/08/52", "CLOSING PRICE": 71.66, "WEIGHTING": 0.4}, {"description": "PANAMA, 3.87%, 23-Jul-2060", "CLOSING PRICE": 56.60, "WEIGHTING": 0.3}, {"description": "INDONESIA, 3.85%, 15-Oct-2030", "CLOSING PRICE": 90.21, "WEIGHTING": 0.3}]}' '''),
    
    ("7. Cash flow - all future", 
     '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/cashflow" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"bonds": [{"description": "T 3 15/08/52", "nominal": 1000000}], "filter": "all", "settlement_date": "2025-08-01"}' '''),
    
    ("8. Cash flow - next only", 
     '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/cashflow/next" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"bonds": [{"description": "T 3 15/08/52", "nominal": 1000000}]}' '''),
    
    ("9. Cash flow - period 90 days", 
     '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/cashflow/period/90" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"bonds": [{"description": "T 3 15/08/52", "nominal": 1000000}, {"description": "AAPL 3.45 02/09/29", "nominal": 500000}]}' '''),
    
    ("10. API version", 
     '''curl "https://api.x-trillion.ai/api/v1/version" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" ''')
]

results = []
for test_name, test_cmd in quickstart_tests:
    success, message = run_curl(test_cmd, test_name)
    results.append((test_name, success, message))
    time.sleep(0.5)  # Be nice to the API

# External API Documentation examples
print("\n" + "="*60)
print("TESTING EXTERNAL API DOCUMENTATION EXAMPLES")
print("="*60)

external_tests = [
    ("1. Health check",
     '''curl -s "https://api.x-trillion.ai/health" '''),
     
    ("2. Standard bond calculation",
     '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"description": "T 3 15/08/52", "price": 71.66, "settlement_date": "2025-07-30"}' '''),
    
    ("3. Flexible format - array",
     '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/analysis/flexible" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '["T 3 15/08/52", 71.66, "2025-07-31"]' '''),
    
    ("4. Portfolio analysis",
     '''curl -X POST "https://api.x-trillion.ai/api/v1/portfolio/analysis" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"data": [{"description": "T 3 15/08/52", "CLOSING PRICE": 71.66, "WEIGHTING": 50.0}, {"description": "T 4.1 02/15/28", "CLOSING PRICE": 99.5, "WEIGHTING": 50.0}]}' '''),
    
    ("5. Cash flow - all",
     '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/cashflow" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"bonds": [{"description": "T 3 15/08/52", "nominal": 1000000}], "filter": "all", "context": "portfolio", "settlement_date": "2025-07-30"}' '''),
    
    ("6. Cash flow - next",
     '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/cashflow/next" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"bonds": [{"description": "T 3 15/08/52", "nominal": 1000000}]}' '''),
    
    ("7. Cash flow - period 180 days",
     '''curl -X POST "https://api.x-trillion.ai/api/v1/bond/cashflow/period/180" -H "Content-Type: application/json" -H "X-API-Key: gax10_maia_7k9d2m5p8w1e6r4t3y2x" -d '{"bonds": [{"description": "T 3 15/08/52", "nominal": 1000000}, {"description": "AAPL 3.45 02/09/29", "nominal": 500000}]}' ''')
]

external_results = []
for test_name, test_cmd in external_tests:
    success, message = run_curl(test_cmd, test_name)
    external_results.append((test_name, success, message))
    time.sleep(0.5)

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)

print("\n📚 Quick Start Guide Results:")
print("-" * 40)
passed = 0
for test_name, success, message in results:
    status = "✅" if success else "❌"
    print(f"{status} {test_name}")
    if not success:
        print(f"   └─ {message}")
    else:
        passed += 1

print(f"\n✨ Quick Start: {passed}/{len(results)} passed ({passed/len(results)*100:.0f}%)")

print("\n📄 External Documentation Results:")
print("-" * 40)
passed_ext = 0
for test_name, success, message in external_results:
    status = "✅" if success else "❌"
    print(f"{status} {test_name}")
    if not success:
        print(f"   └─ {message}")
    else:
        passed_ext += 1

print(f"\n✨ External Docs: {passed_ext}/{len(external_results)} passed ({passed_ext/len(external_results)*100:.0f}%)")

total_passed = passed + passed_ext
total_tests = len(results) + len(external_results)
print(f"\n🎯 OVERALL: {total_passed}/{total_tests} tests passed ({total_passed/total_tests*100:.0f}%)")

if total_passed == total_tests:
    print("\n🎉 SUCCESS! All documentation examples are working correctly!")
else:
    print(f"\n⚠️  {total_tests - total_passed} tests failed - fixing required for 100% success")