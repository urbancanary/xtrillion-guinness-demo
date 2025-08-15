#!/usr/bin/env python3
"""
Test all documentation examples with Maia's API key
"""

import subprocess
import json
import time

# Maia's API key
MAIA_KEY = "gax10_maia_7k9d2m5p8w1e6r4t3y2x"

# Test cases from documentation
TESTS = [
    {
        "name": "1. Health Check (No API Key)",
        "command": 'curl -s "https://api.x-trillion.ai/api/v1/health"',
        "check_field": "status",
        "expected_value": "healthy"
    },
    {
        "name": "2. Basic Bond Analysis",
        "command": f'''curl -s -X POST "https://api.x-trillion.ai/api/v1/bond/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {MAIA_KEY}" \
  -d '{{"description": "T 3 15/08/52", "price": 71.66}}'
''',
        "check_field": "status",
        "expected_value": "success"
    },
    {
        "name": "3. Flexible Analysis with Settlement Date",
        "command": f'''curl -s -X POST "https://api.x-trillion.ai/api/v1/bond/analysis/flexible" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {MAIA_KEY}" \
  -d '["T 3 15/08/52", 71.66, "2025-07-31"]'
''',
        "check_field": "status",
        "expected_value": "success"
    },
    {
        "name": "4. Portfolio Analysis",
        "command": f'''curl -s -X POST "https://api.x-trillion.ai/api/v1/portfolio/analysis" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {MAIA_KEY}" \
  -d '{{
    "settlement_date": "2025-08-01",
    "data": [
      {{"BOND_CD": "T 3 15/08/52", "CLOSING PRICE": 71.66, "WEIGHTING": 0.4}},
      {{"BOND_CD": "PANAMA, 3.87%, 23-Jul-2060", "CLOSING PRICE": 56.60, "WEIGHTING": 0.3}},
      {{"BOND_CD": "INDONESIA, 3.85%, 15-Oct-2030", "CLOSING PRICE": 90.21, "WEIGHTING": 0.3}}
    ]
  }}'
''',
        "check_field": "status",
        "expected_value": "success"
    },
    {
        "name": "5. Cash Flow Analysis",
        "command": f'''curl -s -X POST "https://api.x-trillion.ai/api/v1/bond/cashflow" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {MAIA_KEY}" \
  -d '{{
    "isin": "US912810SV23",
    "price": 71.66,
    "settlement_date": "2025-08-01"
  }}'
''',
        "check_field": "status",
        "expected_value": "success"
    },
    {
        "name": "6. Next Cash Flow",
        "command": f'''curl -s -X POST "https://api.x-trillion.ai/api/v1/bond/cashflow/next" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {MAIA_KEY}" \
  -d '{{
    "description": "T 3 15/08/52",
    "price": 71.66
  }}'
''',
        "check_field": "status",
        "expected_value": "success"
    },
    {
        "name": "7. Cash Flows for Period",
        "command": f'''curl -s -X POST "https://api.x-trillion.ai/api/v1/bond/cashflow/period/365" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {MAIA_KEY}" \
  -d '{{
    "description": "T 3 15/08/52",
    "price": 71.66,
    "settlement_date": "2025-08-01"
  }}'
''',
        "check_field": "status",
        "expected_value": "success"
    }
]

def run_test(test):
    """Run a single test and return results"""
    print(f"\n{'='*60}")
    print(f"Testing: {test['name']}")
    print(f"{'='*60}")
    
    # Show command (abbreviated for display)
    cmd_display = test['command'].replace('\n', ' ').replace('  ', ' ')
    if len(cmd_display) > 100:
        cmd_display = cmd_display[:100] + "..."
    print(f"Command: {cmd_display}")
    
    try:
        # Run the command
        start_time = time.time()
        result = subprocess.run(test['command'], shell=True, capture_output=True, text=True)
        elapsed_time = (time.time() - start_time) * 1000  # milliseconds
        
        if result.returncode != 0:
            print(f"❌ FAILED: Command returned non-zero exit code")
            print(f"Error: {result.stderr}")
            return False, elapsed_time
        
        # Parse JSON response
        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError:
            print(f"❌ FAILED: Invalid JSON response")
            print(f"Response: {result.stdout[:200]}...")
            return False, elapsed_time
        
        # Check expected field
        if test['check_field'] in response and response[test['check_field']] == test['expected_value']:
            print(f"✅ SUCCESS: {test['check_field']} = {test['expected_value']}")
            
            # Show key metrics if available
            if 'analytics' in response:
                analytics = response['analytics']
                print(f"   YTM: {analytics.get('ytm', 'N/A')}")
                print(f"   Duration: {analytics.get('duration', 'N/A')}")
            elif 'portfolio_metrics' in response:
                metrics = response['portfolio_metrics']
                print(f"   Portfolio YTM: {metrics.get('portfolio_yield', 'N/A')}")
                print(f"   Portfolio Duration: {metrics.get('portfolio_duration', 'N/A')}")
            elif 'cash_flows' in response:
                print(f"   Cash flows found: {len(response['cash_flows'])}")
            
            print(f"   Response time: {elapsed_time:.0f}ms")
            return True, elapsed_time
        else:
            print(f"❌ FAILED: Expected {test['check_field']}={test['expected_value']}")
            print(f"   Got: {response.get(test['check_field'], 'field not found')}")
            if response.get('status') == 'error':
                print(f"   Error: {response.get('message', 'Unknown error')}")
            return False, elapsed_time
            
    except Exception as e:
        print(f"❌ FAILED: Exception occurred")
        print(f"   Error: {str(e)}")
        return False, 0

def main():
    print("🧪 Testing Documentation Examples with Maia's API Key")
    print(f"API Key: {MAIA_KEY}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    total_time = 0
    
    for test in TESTS:
        success, elapsed = run_test(test)
        results.append((test['name'], success))
        total_time += elapsed
        time.sleep(0.5)  # Small delay between tests
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⏱️  Total Time: {total_time:.0f}ms")
    print(f"⚡ Avg Response: {total_time/len(results):.0f}ms per request")
    
    if failed > 0:
        print("\nFailed Tests:")
        for name, success in results:
            if not success:
                print(f"  - {name}")
    
    print(f"\n{'='*60}")
    if failed == 0:
        print("🎉 ALL DOCUMENTATION EXAMPLES WORKING!")
        print("Maia's API key is properly configured and functional.")
    else:
        print("⚠️  Some examples failed. Please check the errors above.")

if __name__ == "__main__":
    main()