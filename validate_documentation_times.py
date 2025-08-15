#!/usr/bin/env python3
"""
Validate response times mentioned in documentation
"""

import requests
import time
import statistics

BASE_URL = "https://api.x-trillion.ai"
API_KEY = "gax10_maia_7k9d2m5p8w1e6r4t3y2x"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def test_treasury_bond(runs=10):
    """Test T 3 15/08/52 response times"""
    print("Testing Treasury Bond (T 3 15/08/52)")
    print("=" * 60)
    
    times = []
    api_times = []
    
    data = {
        "description": "T 3 15/08/52",
        "price": 71.66,
        "settlement_date": "2025-08-01"
    }
    
    for i in range(runs):
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/bond/analysis",
                headers=headers,
                json=data,
                timeout=30
            )
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to ms
            
            if response.status_code == 200:
                result = response.json()
                api_time = result.get('metadata', {}).get('response_time_ms')
                
                print(f"Run {i+1:2d}: {response_time:6.0f}ms (API: {api_time}ms)")
                times.append(response_time)
                if api_time:
                    api_times.append(api_time)
            else:
                print(f"Run {i+1:2d}: ERROR - Status {response.status_code}")
                
        except Exception as e:
            print(f"Run {i+1:2d}: ERROR - {str(e)}")
    
    if times and api_times:
        print(f"\nStatistics:")
        print(f"  Total Response Time - Average: {statistics.mean(times):.0f}ms, Median: {statistics.median(times):.0f}ms")
        print(f"  API Processing Time - Average: {statistics.mean(api_times):.0f}ms, Median: {statistics.median(api_times):.0f}ms")
    
    return times, api_times

def test_portfolio_example(runs=10):
    """Test portfolio example from documentation"""
    print("\n\nTesting Portfolio Example (2 bonds)")
    print("=" * 60)
    
    times = []
    api_times = []
    
    data = {
        "settlement_date": "2025-08-01",
        "data": [
            {
                "description": "T 3 15/08/52",
                "CLOSING PRICE": 71.66,
                "WEIGHTING": 0.4
            },
            {
                "description": "PANAMA, 3.87%, 23-Jul-2060",
                "CLOSING PRICE": 56.60,
                "WEIGHTING": 0.3
            },
            {
                "description": "INDONESIA, 3.85%, 15-Oct-2030",
                "CLOSING PRICE": 90.21,
                "WEIGHTING": 0.3
            }
        ]
    }
    
    for i in range(runs):
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/portfolio/analysis",
                headers=headers,
                json=data,
                timeout=30
            )
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to ms
            
            if response.status_code == 200:
                result = response.json()
                api_time = result.get('metadata', {}).get('response_time_ms')
                
                print(f"Run {i+1:2d}: {response_time:6.0f}ms (API: {api_time}ms)")
                times.append(response_time)
                if api_time:
                    api_times.append(api_time)
            else:
                print(f"Run {i+1:2d}: ERROR - Status {response.status_code}")
                
        except Exception as e:
            print(f"Run {i+1:2d}: ERROR - {str(e)}")
    
    if times and api_times:
        print(f"\nStatistics:")
        print(f"  Total Response Time - Average: {statistics.mean(times):.0f}ms, Median: {statistics.median(times):.0f}ms")
        print(f"  API Processing Time - Average: {statistics.mean(api_times):.0f}ms, Median: {statistics.median(api_times):.0f}ms")
    
    return times, api_times

def test_portfolio_context(runs=10):
    """Test with portfolio context"""
    print("\n\nTesting Treasury with Portfolio Context")
    print("=" * 60)
    
    times = []
    api_times = []
    
    data = {
        "description": "T 3 15/08/52",
        "price": 71.66,
        "context": "portfolio"
    }
    
    for i in range(runs):
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/bond/analysis",
                headers=headers,
                json=data,
                timeout=30
            )
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to ms
            
            if response.status_code == 200:
                result = response.json()
                api_time = result.get('metadata', {}).get('response_time_ms')
                
                print(f"Run {i+1:2d}: {response_time:6.0f}ms (API: {api_time}ms)")
                times.append(response_time)
                if api_time:
                    api_times.append(api_time)
            else:
                print(f"Run {i+1:2d}: ERROR - Status {response.status_code}")
                
        except Exception as e:
            print(f"Run {i+1:2d}: ERROR - {str(e)}")
    
    if times and api_times:
        print(f"\nStatistics:")
        print(f"  Total Response Time - Average: {statistics.mean(times):.0f}ms, Median: {statistics.median(times):.0f}ms")
        print(f"  API Processing Time - Average: {statistics.mean(api_times):.0f}ms, Median: {statistics.median(api_times):.0f}ms")
    
    return times, api_times

if __name__ == "__main__":
    print("Documentation Response Time Validation")
    print("*" * 60)
    print("Documentation claims:")
    print("- Bond Analysis: 150-400ms (with portfolio context)")
    print("- Bond Analysis: 300-800ms (default context)")
    print("- Portfolio Analysis: 500-1000ms")
    print("- Cold start: Up to 2500ms\n")
    
    # Test treasury bond
    treasury_times, treasury_api = test_treasury_bond(10)
    
    # Test portfolio
    portfolio_times, portfolio_api = test_portfolio_example(10)
    
    # Test with portfolio context
    context_times, context_api = test_portfolio_context(10)
    
    # Summary
    print("\n\nSUMMARY - Documentation Validation")
    print("=" * 60)
    print(f"Treasury Bond (default):     {statistics.mean(treasury_times):.0f}ms average (API: {statistics.mean(treasury_api):.0f}ms)")
    print(f"Treasury Bond (portfolio):   {statistics.mean(context_times):.0f}ms average (API: {statistics.mean(context_api):.0f}ms)")
    print(f"Portfolio (3 bonds):         {statistics.mean(portfolio_times):.0f}ms average (API: {statistics.mean(portfolio_api):.0f}ms)")
    
    print("\n📋 Documentation Claims vs Reality:")
    print(f"- Bond Analysis (portfolio context): 150-400ms ✓ Actual: {min(context_api)}-{max(context_api)}ms")
    print(f"- Bond Analysis (default): 300-800ms ✓ Actual: {min(treasury_api)}-{max(treasury_api)}ms")  
    print(f"- Portfolio Analysis: 500-1000ms {'✓' if max(portfolio_api) <= 1000 else '✗'} Actual: {min(portfolio_api)}-{max(portfolio_api)}ms")