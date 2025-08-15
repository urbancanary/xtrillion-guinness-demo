#!/usr/bin/env python3
"""
Business Critical: Test ALL documentation examples against BOTH production and development APIs
"""

import subprocess
import json
import time
from datetime import datetime

# API configurations
ENVIRONMENTS = {
    "PRODUCTION": {
        "base_url": "https://api.x-trillion.ai",
        "health_url": "https://api.x-trillion.ai/health",
        "api_key": "gax10_maia_7k9d2m5p8w1e6r4t3y2x"
    },
    "DEVELOPMENT": {
        "base_url": "https://api-dev.x-trillion.ai", 
        "health_url": "https://api-dev.x-trillion.ai/health",
        "api_key": "gax10_maia_7k9d2m5p8w1e6r4t3y2x"
    }
}

def run_curl(command, test_name, env_name):
    """Run curl command and return detailed result"""
    try:
        start_time = time.time()
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=15)
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                if 'error' in response and response['error']:
                    return False, f"API Error: {response.get('error')}", response_time
                elif 'status' in response and response['status'] == 'error':
                    return False, f"API Error: {response.get('message', 'Unknown error')}", response_time
                return True, "Success", response_time
            except json.JSONDecodeError:
                if "<!doctype html>" in result.stdout.lower():
                    return False, "404 Not Found", response_time
                return False, f"Invalid JSON response", response_time
        else:
            return False, f"HTTP Error: {result.returncode}", response_time
    except subprocess.TimeoutExpired:
        return False, "Timeout (>15s)", 15000
    except Exception as e:
        return False, f"Exception: {str(e)}", 0

def test_environment(env_name, env_config):
    """Test all examples against a specific environment"""
    print(f"\n{'='*80}")
    print(f"TESTING {env_name} ENVIRONMENT")
    print(f"Base URL: {env_config['base_url']}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    
    # Update URLs for this environment
    base_url = env_config['base_url']
    health_url = env_config['health_url']
    api_key = env_config['api_key']
    
    all_tests = []
    
    # Quick Start Guide Examples
    quickstart_tests = [
        ("QS1: Bond analysis - comprehensive", 
         f'''curl -X POST "{base_url}/api/v1/bond/analysis" -H "Content-Type: application/json" -H "X-API-Key: {api_key}" -d '{{"description": "T 3 15/08/52", "price": 71.66, "settlement_date": "2025-08-01"}}' '''),
        
        ("QS2: Bond analysis - portfolio context", 
         f'''curl -X POST "{base_url}/api/v1/bond/analysis" -H "Content-Type: application/json" -H "X-API-Key: {api_key}" -d '{{"description": "T 3 15/08/52", "price": 71.66, "context": "portfolio"}}' '''),
        
        ("QS3: Bond analysis - ISIN", 
         f'''curl -X POST "{base_url}/api/v1/bond/analysis" -H "Content-Type: application/json" -H "X-API-Key: {api_key}" -d '{{"isin": "US912810TJ79", "price": 71.66}}' '''),
        
        ("QS4: Bond analysis - overrides", 
         f'''curl -X POST "{base_url}/api/v1/bond/analysis" -H "Content-Type: application/json" -H "X-API-Key: {api_key}" -d '{{"description": "AAPL 3.45 02/09/2029", "price": 97.25, "overrides": {{"day_count": "Thirty360.BondBasis", "business_convention": "ModifiedFollowing", "end_of_month": false}}}}' '''),
        
        ("QS5: Flexible analysis", 
         f'''curl -X POST "{base_url}/api/v1/bond/analysis/flexible" -H "Content-Type: application/json" -H "X-API-Key: {api_key}" -d '["T 3 15/08/52", 71.66, "2025-08-01"]' '''),
        
        ("QS6: Portfolio analysis", 
         f'''curl -X POST "{base_url}/api/v1/portfolio/analysis" -H "Content-Type: application/json" -H "X-API-Key: {api_key}" -d '{{"settlement_date": "2025-08-01", "data": [{{"description": "T 3 15/08/52", "CLOSING PRICE": 71.66, "WEIGHTING": 0.4}}, {{"description": "PANAMA, 3.87%, 23-Jul-2060", "CLOSING PRICE": 56.60, "WEIGHTING": 0.3}}, {{"description": "INDONESIA, 3.85%, 15-Oct-2030", "CLOSING PRICE": 90.21, "WEIGHTING": 0.3}}]}}' '''),
        
        ("QS7: Cash flow - all", 
         f'''curl -X POST "{base_url}/api/v1/bond/cashflow" -H "Content-Type: application/json" -H "X-API-Key: {api_key}" -d '{{"bonds": [{{"description": "T 3 15/08/52", "nominal": 1000000}}], "filter": "all", "settlement_date": "2025-08-01"}}' '''),
        
        ("QS8: Cash flow - next", 
         f'''curl -X POST "{base_url}/api/v1/bond/cashflow/next" -H "Content-Type: application/json" -H "X-API-Key: {api_key}" -d '{{"bonds": [{{"description": "T 3 15/08/52", "nominal": 1000000}}]}}' '''),
        
        ("QS9: Cash flow - 90 days", 
         f'''curl -X POST "{base_url}/api/v1/bond/cashflow/period/90" -H "Content-Type: application/json" -H "X-API-Key: {api_key}" -d '{{"bonds": [{{"description": "T 3 15/08/52", "nominal": 1000000}}, {{"description": "AAPL 3.45 02/09/29", "nominal": 500000}}]}}' '''),
        
        ("QS10: Version", 
         f'''curl "{base_url}/api/v1/version" -H "X-API-Key: {api_key}" ''')
    ]
    
    # External Documentation Examples
    external_tests = [
        ("EX1: Health check",
         f'''curl -s "{health_url}" '''),
         
        ("EX2: Bond calculation",
         f'''curl -X POST "{base_url}/api/v1/bond/analysis" -H "Content-Type: application/json" -H "X-API-Key: {api_key}" -d '{{"description": "T 3 15/08/52", "price": 71.66, "settlement_date": "2025-07-30"}}' '''),
        
        ("EX3: Flexible array",
         f'''curl -X POST "{base_url}/api/v1/bond/analysis/flexible" -H "Content-Type: application/json" -H "X-API-Key: {api_key}" -d '["T 3 15/08/52", 71.66, "2025-07-31"]' '''),
        
        ("EX4: Portfolio",
         f'''curl -X POST "{base_url}/api/v1/portfolio/analysis" -H "Content-Type: application/json" -H "X-API-Key: {api_key}" -d '{{"data": [{{"description": "T 3 15/08/52", "CLOSING PRICE": 71.66, "WEIGHTING": 50.0}}, {{"description": "T 4.1 02/15/28", "CLOSING PRICE": 99.5, "WEIGHTING": 50.0}}]}}' '''),
        
        ("EX5: Cash flow - all",
         f'''curl -X POST "{base_url}/api/v1/bond/cashflow" -H "Content-Type: application/json" -H "X-API-Key: {api_key}" -d '{{"bonds": [{{"description": "T 3 15/08/52", "nominal": 1000000}}], "filter": "all", "context": "portfolio", "settlement_date": "2025-07-30"}}' '''),
        
        ("EX6: Cash flow - next",
         f'''curl -X POST "{base_url}/api/v1/bond/cashflow/next" -H "Content-Type: application/json" -H "X-API-Key: {api_key}" -d '{{"bonds": [{{"description": "T 3 15/08/52", "nominal": 1000000}}]}}' '''),
        
        ("EX7: Cash flow - 180 days",
         f'''curl -X POST "{base_url}/api/v1/bond/cashflow/period/180" -H "Content-Type: application/json" -H "X-API-Key: {api_key}" -d '{{"bonds": [{{"description": "T 3 15/08/52", "nominal": 1000000}}, {{"description": "AAPL 3.45 02/09/29", "nominal": 500000}}]}}' ''')
    ]
    
    # Run all tests
    print("\n📚 Quick Start Guide Tests:")
    print("-" * 40)
    quickstart_results = []
    for test_name, test_cmd in quickstart_tests:
        success, message, response_time = run_curl(test_cmd, test_name, env_name)
        quickstart_results.append((test_name, success, message, response_time))
        status = "✅" if success else "❌"
        print(f"{status} {test_name} ({response_time:.0f}ms)")
        if not success:
            print(f"   └─ {message}")
        time.sleep(0.3)  # Be nice to the API
    
    print("\n📄 External Documentation Tests:")
    print("-" * 40)
    external_results = []
    for test_name, test_cmd in external_tests:
        success, message, response_time = run_curl(test_cmd, test_name, env_name)
        external_results.append((test_name, success, message, response_time))
        status = "✅" if success else "❌"
        print(f"{status} {test_name} ({response_time:.0f}ms)")
        if not success:
            print(f"   └─ {message}")
        time.sleep(0.3)
    
    # Calculate statistics
    all_results = quickstart_results + external_results
    total = len(all_results)
    passed = sum(1 for _, success, _, _ in all_results if success)
    failed = total - passed
    avg_response_time = sum(rt for _, _, _, rt in all_results) / total if total > 0 else 0
    
    return {
        'environment': env_name,
        'total': total,
        'passed': passed,
        'failed': failed,
        'success_rate': (passed/total*100) if total > 0 else 0,
        'avg_response_time': avg_response_time,
        'quickstart_results': quickstart_results,
        'external_results': external_results
    }

def main():
    """Run tests on all environments"""
    print("\n" + "="*80)
    print("BUSINESS CRITICAL: API DOCUMENTATION VALIDATION")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    results = {}
    
    # Test each environment
    for env_name, env_config in ENVIRONMENTS.items():
        results[env_name] = test_environment(env_name, env_config)
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    
    all_passed = True
    for env_name, result in results.items():
        print(f"\n{env_name}:")
        print(f"  Total Tests: {result['total']}")
        print(f"  Passed: {result['passed']}")
        print(f"  Failed: {result['failed']}")
        print(f"  Success Rate: {result['success_rate']:.1f}%")
        print(f"  Avg Response Time: {result['avg_response_time']:.0f}ms")
        
        if result['failed'] > 0:
            all_passed = False
            print(f"\n  ⚠️  Failed tests in {env_name}:")
            for test_name, success, message, _ in result['quickstart_results'] + result['external_results']:
                if not success:
                    print(f"    - {test_name}: {message}")
    
    if all_passed:
        print("\n✅ SUCCESS: 100% of documentation examples working in ALL environments!")
        print("🎉 Ready for production use!")
    else:
        print("\n❌ FAILURE: Some tests failed - NOT ready for production!")
        print("⚠️  Fix all issues before proceeding!")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)