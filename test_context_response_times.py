#!/usr/bin/env python3
"""
Test response times with different contexts
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

def test_with_context(context=None, runs=10):
    """Test individual bond with different contexts"""
    context_name = context if context else "default"
    print(f"\nTesting Individual Bond - {context_name} context")
    print("=" * 60)
    
    times = []
    api_times = []
    
    data = {
        "description": "T 3 15/08/52",
        "price": 71.66,
        "settlement_date": "2025-08-01"
    }
    
    if context:
        data["context"] = context
    
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
                
                print(f"Run {i+1:2d}: Total: {response_time:6.0f}ms | API: {api_time:4d}ms")
                times.append(response_time)
                if api_time:
                    api_times.append(api_time)
            else:
                print(f"Run {i+1:2d}: ERROR - Status {response.status_code}")
                
        except Exception as e:
            print(f"Run {i+1:2d}: ERROR - {str(e)}")
    
    if times:
        print(f"\nTotal Response Time Statistics:")
        print(f"  Average: {statistics.mean(times):.0f}ms")
        print(f"  Median:  {statistics.median(times):.0f}ms")
        print(f"  Min:     {min(times):.0f}ms")
        print(f"  Max:     {max(times):.0f}ms")
        
        if api_times:
            print(f"\nAPI Processing Time Statistics:")
            print(f"  Average: {statistics.mean(api_times):.0f}ms")
            print(f"  Median:  {statistics.median(api_times):.0f}ms")
            print(f"  Min:     {min(api_times):.0f}ms")
            print(f"  Max:     {max(api_times):.0f}ms")
    
    return times, api_times

if __name__ == "__main__":
    print("XTrillion API Context Performance Comparison")
    print("*" * 60)
    
    # Test default context
    default_times, default_api = test_with_context(None, 10)
    
    # Test portfolio context
    portfolio_times, portfolio_api = test_with_context("portfolio", 10)
    
    # Summary
    print("\n\nSUMMARY - Context Performance Comparison")
    print("=" * 60)
    if default_times and portfolio_times:
        print(f"Default context average:   {statistics.mean(default_times):.0f}ms (API: {statistics.mean(default_api):.0f}ms)")
        print(f"Portfolio context average: {statistics.mean(portfolio_times):.0f}ms (API: {statistics.mean(portfolio_api):.0f}ms)")
        print(f"\nPortfolio context is {statistics.mean(default_times)/statistics.mean(portfolio_times):.2f}x faster overall")
        print(f"Portfolio context API processing is {statistics.mean(default_api)/statistics.mean(portfolio_api):.2f}x faster")