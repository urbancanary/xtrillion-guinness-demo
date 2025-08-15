#!/usr/bin/env python3
"""
Compare single bond analysis vs portfolio with 1 bond
"""

import requests
import time
import statistics
import json

BASE_URL = "https://api.x-trillion.ai"
API_KEY = "gax10_maia_7k9d2m5p8w1e6r4t3y2x"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def test_individual_bond(runs=10):
    """Test individual bond endpoint"""
    print("Testing Individual Bond Endpoint")
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
            response_time = (end_time - start_time) * 1000
            
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
    
    return times, api_times

def test_portfolio_single_bond(runs=10):
    """Test portfolio endpoint with 1 bond"""
    print("\n\nTesting Portfolio Endpoint (1 bond)")
    print("=" * 60)
    
    times = []
    api_times = []
    
    data = {
        "settlement_date": "2025-08-01",
        "data": [
            {
                "description": "T 3 15/08/52",
                "CLOSING PRICE": 71.66,
                "WEIGHTING": 100.0
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
            response_time = (end_time - start_time) * 1000
            
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
    
    return times, api_times

def test_portfolio_multiple_bonds(runs=10):
    """Test portfolio endpoint with 3 bonds"""
    print("\n\nTesting Portfolio Endpoint (3 bonds)")
    print("=" * 60)
    
    times = []
    api_times = []
    
    data = {
        "settlement_date": "2025-08-01",
        "data": [
            {
                "description": "T 3 15/08/52",
                "CLOSING PRICE": 71.66,
                "WEIGHTING": 40.0
            },
            {
                "description": "T 4.1 02/15/28",
                "CLOSING PRICE": 99.5,
                "WEIGHTING": 30.0
            },
            {
                "description": "T 2.5 05/31/2024",
                "CLOSING PRICE": 98.2,
                "WEIGHTING": 30.0
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
            response_time = (end_time - start_time) * 1000
            
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
    
    return times, api_times

if __name__ == "__main__":
    print("Single Bond vs Portfolio Comparison")
    print("*" * 60)
    
    # Test individual bond
    ind_times, ind_api = test_individual_bond(10)
    
    # Test portfolio with 1 bond
    port1_times, port1_api = test_portfolio_single_bond(10)
    
    # Test portfolio with 3 bonds
    port3_times, port3_api = test_portfolio_multiple_bonds(10)
    
    # Summary
    print("\n\nSUMMARY")
    print("=" * 60)
    print(f"Individual bond:          {statistics.mean(ind_times):6.0f}ms total ({statistics.mean(ind_api):3.0f}ms API)")
    print(f"Portfolio (1 bond):       {statistics.mean(port1_times):6.0f}ms total ({statistics.mean(port1_api):3.0f}ms API)")
    print(f"Portfolio (3 bonds):      {statistics.mean(port3_times):6.0f}ms total ({statistics.mean(port3_api):3.0f}ms API)")
    
    print(f"\nAPI Processing Time Comparison:")
    print(f"Portfolio (1 bond) is {statistics.mean(ind_api)/statistics.mean(port1_api):.2f}x faster than individual")
    print(f"Portfolio (3 bonds) is {statistics.mean(ind_api)/statistics.mean(port3_api):.2f}x faster than individual")
    print(f"Portfolio (3 bonds) takes {statistics.mean(port3_api)/statistics.mean(port1_api):.2f}x longer than 1 bond")