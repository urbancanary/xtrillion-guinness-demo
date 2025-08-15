#!/usr/bin/env python3
"""
Response time benchmark for XTrillion API
Tests individual bond analysis and portfolio analysis
"""

import requests
import time
import json
import statistics

BASE_URL = "https://api.x-trillion.ai"
API_KEY = "gax10_maia_7k9d2m5p8w1e6r4t3y2x"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def test_individual_bond(runs=10):
    """Test individual bond analysis response times"""
    print("Testing Individual Bond Analysis (T 3 15/08/52)")
    print("=" * 60)
    
    times = []
    
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
                # Check if response includes timing
                api_time = result.get('metadata', {}).get('response_time_ms')
                
                print(f"Run {i+1:2d}: {response_time:6.0f}ms (API reported: {api_time}ms)" if api_time else f"Run {i+1:2d}: {response_time:6.0f}ms")
                times.append(response_time)
            else:
                print(f"Run {i+1:2d}: ERROR - Status {response.status_code}")
                
        except Exception as e:
            print(f"Run {i+1:2d}: ERROR - {str(e)}")
    
    if times:
        print(f"\nStatistics:")
        print(f"  Average: {statistics.mean(times):.0f}ms")
        print(f"  Median:  {statistics.median(times):.0f}ms")
        print(f"  Min:     {min(times):.0f}ms")
        print(f"  Max:     {max(times):.0f}ms")
        if len(times) > 1:
            print(f"  Std Dev: {statistics.stdev(times):.0f}ms")
    
    return times

def test_portfolio_analysis(runs=10):
    """Test portfolio analysis response times"""
    print("\n\nTesting Portfolio Analysis (2 bonds)")
    print("=" * 60)
    
    times = []
    
    data = {
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
        ],
        "settlement_date": "2025-08-01"
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
                # Check if response includes timing
                api_time = result.get('metadata', {}).get('response_time_ms')
                
                print(f"Run {i+1:2d}: {response_time:6.0f}ms (API reported: {api_time}ms)" if api_time else f"Run {i+1:2d}: {response_time:6.0f}ms")
                times.append(response_time)
            else:
                print(f"Run {i+1:2d}: ERROR - Status {response.status_code}")
                
        except Exception as e:
            print(f"Run {i+1:2d}: ERROR - {str(e)}")
    
    if times:
        print(f"\nStatistics:")
        print(f"  Average: {statistics.mean(times):.0f}ms")
        print(f"  Median:  {statistics.median(times):.0f}ms")
        print(f"  Min:     {min(times):.0f}ms")
        print(f"  Max:     {max(times):.0f}ms")
        if len(times) > 1:
            print(f"  Std Dev: {statistics.stdev(times):.0f}ms")
    
    return times

if __name__ == "__main__":
    print("XTrillion API Response Time Benchmark")
    print("*" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"Testing with 10 runs each\n")
    
    # Test individual bond
    individual_times = test_individual_bond(10)
    
    # Test portfolio
    portfolio_times = test_portfolio_analysis(10)
    
    # Summary comparison
    print("\n\nSUMMARY COMPARISON")
    print("=" * 60)
    if individual_times and portfolio_times:
        print(f"Individual Bond Average: {statistics.mean(individual_times):.0f}ms")
        print(f"Portfolio Average:       {statistics.mean(portfolio_times):.0f}ms")
        print(f"Portfolio/Individual Ratio: {statistics.mean(portfolio_times)/statistics.mean(individual_times):.2f}x")