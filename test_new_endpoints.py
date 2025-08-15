#!/usr/bin/env python3
"""
Test script for new /bond/quick endpoint and metrics parameter support
"""

import json
import time
import requests
import statistics

# Configuration
API_BASE_URL = "http://localhost:8080"
API_KEY = "gax10_test_9r4t7w2k5m8p1z6x3v"

def test_endpoint(name, endpoint, payload, expected_metrics=None):
    """Test an endpoint and report results"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Endpoint: {endpoint}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 60)
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    start_time = time.perf_counter()
    response = requests.post(
        f"{API_BASE_URL}{endpoint}",
        headers=headers,
        json=payload
    )
    end_time = time.perf_counter()
    
    response_time_ms = (end_time - start_time) * 1000
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Time: {response_time_ms:.2f} ms")
    print(f"Response Size: {len(response.text)} bytes")
    
    if response.status_code == 200:
        data = response.json()
        
        if 'analytics' in data:
            analytics = data['analytics']
            print(f"Metrics Returned: {list(analytics.keys())}")
            print(f"Number of Metrics: {len(analytics)}")
            
            # Check if expected metrics are present
            if expected_metrics:
                missing = [m for m in expected_metrics if m not in analytics]
                if missing:
                    print(f"⚠️  Missing expected metrics: {missing}")
                else:
                    print(f"✅ All expected metrics present")
            
            # Print sample values
            print("\nSample Values:")
            for key, value in list(analytics.items())[:5]:
                if isinstance(value, float):
                    print(f"  {key}: {value:.4f}")
                else:
                    print(f"  {key}: {value}")
        else:
            print("Response:", json.dumps(data, indent=2))
    else:
        print(f"Error Response: {response.text[:200]}")
    
    return response_time_ms, len(response.text)

def run_all_tests():
    """Run comprehensive tests of new functionality"""
    
    print("=" * 80)
    print("TESTING NEW BOND API ENDPOINTS AND METRICS PARAMETER")
    print("=" * 80)
    
    results = []
    
    # Test 1: /bond/quick with defaults (minimal)
    time_ms, size = test_endpoint(
        "1. /bond/quick - Default (minimal metrics)",
        "/api/v1/bond/quick",
        {
            "description": "T 3 15/08/52",
            "price": 71.66
        },
        expected_metrics=["ytm", "duration", "spread"]
    )
    results.append(("Quick Default", time_ms, size))
    
    # Test 2: /bond/quick with custom metrics
    time_ms, size = test_endpoint(
        "2. /bond/quick - Custom metrics",
        "/api/v1/bond/quick",
        {
            "description": "T 3 15/08/52",
            "price": 71.66,
            "metrics": ["ytm_semi", "ytm_annual", "duration_annual", "convexity"]
        },
        expected_metrics=["ytm_semi", "ytm_annual", "duration_annual", "convexity"]
    )
    results.append(("Quick Custom", time_ms, size))
    
    # Test 3: /bond/analysis with metrics parameter
    time_ms, size = test_endpoint(
        "3. /bond/analysis - With metrics parameter",
        "/api/v1/bond/analysis",
        {
            "description": "T 3 15/08/52",
            "price": 71.66,
            "metrics": ["ytm", "duration", "spread"]
        },
        expected_metrics=["ytm", "duration", "spread"]
    )
    results.append(("Analysis Selective", time_ms, size))
    
    # Test 4: /bond/analysis without metrics (full response)
    time_ms, size = test_endpoint(
        "4. /bond/analysis - Without metrics (full response)",
        "/api/v1/bond/analysis",
        {
            "description": "T 3 15/08/52",
            "price": 71.66
        }
    )
    results.append(("Analysis Full", time_ms, size))
    
    # Test 5: /portfolio/analysis with metrics
    time_ms, size = test_endpoint(
        "5. /portfolio/analysis - With metrics parameter",
        "/api/v1/portfolio/analysis",
        {
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
            "metrics": ["ytm", "duration"]
        }
    )
    results.append(("Portfolio Selective", time_ms, size))
    
    # Test 6: Test convention variants
    time_ms, size = test_endpoint(
        "6. /bond/quick - Convention variants test",
        "/api/v1/bond/quick",
        {
            "description": "T 3 15/08/52",
            "price": 71.66,
            "metrics": ["ytm", "ytm_semi", "ytm_annual", "duration", "duration_semi", "duration_annual"]
        },
        expected_metrics=["ytm", "ytm_semi", "ytm_annual", "duration", "duration_semi", "duration_annual"]
    )
    results.append(("Convention Variants", time_ms, size))
    
    # Summary
    print("\n" + "=" * 80)
    print("PERFORMANCE SUMMARY")
    print("=" * 80)
    
    print(f"\n{'Test Name':<25} {'Response Time':<15} {'Response Size':<15}")
    print("-" * 55)
    
    for name, time_ms, size in results:
        print(f"{name:<25} {time_ms:>8.2f} ms     {size:>8} bytes")
    
    # Calculate improvements
    full_result = next((r for r in results if r[0] == "Analysis Full"), None)
    quick_result = next((r for r in results if r[0] == "Quick Default"), None)
    
    if full_result and quick_result:
        full_time, full_size = full_result[1], full_result[2]
        quick_time, quick_size = quick_result[1], quick_result[2]
        
        time_improvement = ((full_time - quick_time) / full_time) * 100
        size_reduction = ((full_size - quick_size) / full_size) * 100
        
        print("\n" + "=" * 80)
        print("IMPROVEMENT METRICS: /bond/quick vs /bond/analysis (full)")
        print("=" * 80)
        print(f"Response Time: {quick_time:.2f} ms vs {full_time:.2f} ms ({time_improvement:.1f}% faster)")
        print(f"Response Size: {quick_size} bytes vs {full_size} bytes ({size_reduction:.1f}% smaller)")
        print(f"Size Reduction: {full_size - quick_size} bytes saved")

if __name__ == "__main__":
    # Wait a moment for API to be ready
    time.sleep(1)
    
    # Check API health first
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("✅ API is healthy. Starting tests...\n")
            run_all_tests()
        else:
            print(f"⚠️  API returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not connect to API: {e}")
        print("Please ensure the API is running with: ./start_ga10_portfolio_api.sh")