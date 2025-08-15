#!/usr/bin/env python3
"""
Test script to compare API response times with different metric sets.
Measures the performance difference between full metrics and minimal metrics (yield, spread, duration only).
"""

import json
import time
import requests
import statistics
from typing import Dict, List, Tuple

# Configuration
API_BASE_URL = "http://localhost:8080"  # Local testing
API_KEY = "gax10_test_9r4t7w2k5m8p1z6x3v"  # Internal Testing Key
NUM_ITERATIONS = 20  # Number of test iterations for each configuration

# Test bonds
TEST_BONDS = [
    {"description": "T 3 15/08/52", "price": 71.66},
    {"description": "T 4.1 02/15/28", "price": 99.5},
    {"description": "AAPL 3.45 02/09/29", "price": 97.25},
    {"description": "PANAMA 3.87 23/07/60", "price": 56.60},
    {"description": "IBM 4.0 06/20/42", "price": 85.75}
]

def measure_api_call(endpoint: str, payload: Dict, headers: Dict) -> Tuple[float, Dict, int]:
    """
    Make an API call and measure response time.
    Returns: (response_time_ms, response_json, response_size_bytes)
    """
    start_time = time.perf_counter()
    
    response = requests.post(
        f"{API_BASE_URL}{endpoint}",
        headers=headers,
        json=payload
    )
    
    end_time = time.perf_counter()
    response_time_ms = (end_time - start_time) * 1000
    
    response_json = response.json()
    response_size = len(response.text)
    
    return response_time_ms, response_json, response_size

def test_full_metrics(bond: Dict) -> Tuple[float, int, int]:
    """Test with full metrics (current default)."""
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    payload = {
        "description": bond["description"],
        "price": bond["price"],
        "settlement_date": "2025-08-01"
    }
    
    response_time, response_json, response_size = measure_api_call(
        "/api/v1/bond/analysis",
        payload,
        headers
    )
    
    # Count number of metrics returned
    analytics = response_json.get("analytics", {})
    num_metrics = len(analytics)
    
    return response_time, response_size, num_metrics

def test_minimal_metrics(bond: Dict) -> Tuple[float, int, int]:
    """Test with minimal metrics (yield, spread, duration only)."""
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    payload = {
        "description": bond["description"],
        "price": bond["price"],
        "settlement_date": "2025-08-01",
        "context": "minimal"  # This context doesn't exist yet - for testing we'll simulate
    }
    
    # For now, we'll test with portfolio context which is smaller
    payload["context"] = "portfolio"
    
    response_time, response_json, response_size = measure_api_call(
        "/api/v1/bond/analysis",
        payload,
        headers
    )
    
    # Count number of metrics returned
    analytics = response_json.get("analytics", {})
    num_metrics = len(analytics)
    
    return response_time, response_size, num_metrics

def simulate_minimal_response(bond: Dict) -> Tuple[float, int, int]:
    """
    Simulate minimal response by calling full API and extracting only 3 metrics.
    This helps estimate the network transfer savings.
    """
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    payload = {
        "description": bond["description"],
        "price": bond["price"],
        "settlement_date": "2025-08-01"
    }
    
    start_time = time.perf_counter()
    
    response = requests.post(
        f"{API_BASE_URL}/api/v1/bond/analysis",
        headers=headers,
        json=payload
    )
    
    end_time = time.perf_counter()
    response_time_ms = (end_time - start_time) * 1000
    
    # Simulate minimal response
    full_response = response.json()
    if full_response.get("status") == "success":
        minimal_response = {
            "status": "success",
            "analytics": {
                "ytm": full_response["analytics"].get("ytm"),
                "duration": full_response["analytics"].get("duration"),
                "spread": full_response["analytics"].get("spread")
            }
        }
        response_size = len(json.dumps(minimal_response))
        num_metrics = 3
    else:
        response_size = len(response.text)
        num_metrics = 0
    
    return response_time_ms, response_size, num_metrics

def run_performance_tests():
    """Run comprehensive performance tests."""
    print("=" * 80)
    print("API Response Time Comparison: Full Metrics vs. Minimal Metrics")
    print("=" * 80)
    print(f"\nTesting with {NUM_ITERATIONS} iterations per bond...")
    print(f"API: {API_BASE_URL}")
    print()
    
    # Results storage
    full_metrics_times = []
    full_metrics_sizes = []
    portfolio_context_times = []
    portfolio_context_sizes = []
    simulated_minimal_sizes = []
    
    for bond in TEST_BONDS:
        print(f"\nTesting bond: {bond['description']}")
        print("-" * 50)
        
        # Test full metrics
        bond_full_times = []
        bond_full_sizes = []
        for _ in range(NUM_ITERATIONS):
            time_ms, size_bytes, num_metrics = test_full_metrics(bond)
            bond_full_times.append(time_ms)
            bond_full_sizes.append(size_bytes)
        
        avg_full_time = statistics.mean(bond_full_times)
        avg_full_size = statistics.mean(bond_full_sizes)
        full_metrics_times.extend(bond_full_times)
        full_metrics_sizes.extend(bond_full_sizes)
        
        print(f"  Full metrics (13 fields):")
        print(f"    Avg response time: {avg_full_time:.2f} ms")
        print(f"    Response size: {avg_full_size:.0f} bytes")
        print(f"    Metrics returned: {num_metrics}")
        
        # Test portfolio context (currently the most minimal available)
        bond_portfolio_times = []
        bond_portfolio_sizes = []
        for _ in range(NUM_ITERATIONS):
            time_ms, size_bytes, num_metrics = test_minimal_metrics(bond)
            bond_portfolio_times.append(time_ms)
            bond_portfolio_sizes.append(size_bytes)
        
        avg_portfolio_time = statistics.mean(bond_portfolio_times)
        avg_portfolio_size = statistics.mean(bond_portfolio_sizes)
        portfolio_context_times.extend(bond_portfolio_times)
        portfolio_context_sizes.extend(bond_portfolio_sizes)
        
        print(f"  Portfolio context:")
        print(f"    Avg response time: {avg_portfolio_time:.2f} ms")
        print(f"    Response size: {avg_portfolio_size:.0f} bytes")
        print(f"    Metrics returned: {num_metrics}")
        
        # Simulate minimal response
        _, minimal_size, _ = simulate_minimal_response(bond)
        simulated_minimal_sizes.append(minimal_size)
        
        print(f"  Simulated minimal (3 fields only):")
        print(f"    Estimated size: {minimal_size} bytes")
        
        # Calculate improvements
        time_improvement = ((avg_full_time - avg_portfolio_time) / avg_full_time) * 100
        size_reduction = ((avg_full_size - avg_portfolio_size) / avg_full_size) * 100
        minimal_size_reduction = ((avg_full_size - minimal_size) / avg_full_size) * 100
        
        print(f"\n  Performance comparison:")
        print(f"    Portfolio context vs Full: {time_improvement:.1f}% faster, {size_reduction:.1f}% smaller")
        print(f"    Minimal (3 fields) would be: {minimal_size_reduction:.1f}% smaller")
    
    # Overall statistics
    print("\n" + "=" * 80)
    print("OVERALL STATISTICS")
    print("=" * 80)
    
    print("\nFull Metrics (current default):")
    print(f"  Average response time: {statistics.mean(full_metrics_times):.2f} ms")
    print(f"  Median response time: {statistics.median(full_metrics_times):.2f} ms")
    print(f"  P95 response time: {statistics.quantiles(full_metrics_times, n=20)[18]:.2f} ms")
    print(f"  Average size: {statistics.mean(full_metrics_sizes):.0f} bytes")
    
    print("\nPortfolio Context (simplified):")
    print(f"  Average response time: {statistics.mean(portfolio_context_times):.2f} ms")
    print(f"  Median response time: {statistics.median(portfolio_context_times):.2f} ms")
    print(f"  P95 response time: {statistics.quantiles(portfolio_context_times, n=20)[18]:.2f} ms")
    print(f"  Average size: {statistics.mean(portfolio_context_sizes):.0f} bytes")
    
    print("\nSimulated Minimal (3 fields: yield, duration, spread):")
    print(f"  Estimated average size: {statistics.mean(simulated_minimal_sizes):.0f} bytes")
    
    # Calculate overall improvements
    overall_time_improvement = ((statistics.mean(full_metrics_times) - statistics.mean(portfolio_context_times)) / statistics.mean(full_metrics_times)) * 100
    overall_size_reduction = ((statistics.mean(full_metrics_sizes) - statistics.mean(portfolio_context_sizes)) / statistics.mean(full_metrics_sizes)) * 100
    minimal_size_reduction = ((statistics.mean(full_metrics_sizes) - statistics.mean(simulated_minimal_sizes)) / statistics.mean(full_metrics_sizes)) * 100
    
    print("\n" + "=" * 80)
    print("POTENTIAL IMPROVEMENTS")
    print("=" * 80)
    print(f"\nPortfolio context vs Full metrics:")
    print(f"  Response time: {overall_time_improvement:.1f}% faster")
    print(f"  Response size: {overall_size_reduction:.1f}% smaller")
    
    print(f"\nMinimal response (3 fields only) would achieve:")
    print(f"  Response size: {minimal_size_reduction:.1f}% smaller than full")
    print(f"  Estimated size reduction: {statistics.mean(full_metrics_sizes) - statistics.mean(simulated_minimal_sizes):.0f} bytes saved per request")
    
    # Network transfer analysis
    print("\n" + "=" * 80)
    print("NETWORK TRANSFER IMPACT")
    print("=" * 80)
    
    requests_per_second = 100  # Example throughput
    print(f"\nAt {requests_per_second} requests/second:")
    
    full_bandwidth = (statistics.mean(full_metrics_sizes) * requests_per_second) / 1024
    portfolio_bandwidth = (statistics.mean(portfolio_context_sizes) * requests_per_second) / 1024
    minimal_bandwidth = (statistics.mean(simulated_minimal_sizes) * requests_per_second) / 1024
    
    print(f"  Full metrics: {full_bandwidth:.1f} KB/s")
    print(f"  Portfolio context: {portfolio_bandwidth:.1f} KB/s")
    print(f"  Minimal (3 fields): {minimal_bandwidth:.1f} KB/s")
    
    print(f"\nBandwidth savings with minimal response:")
    print(f"  {full_bandwidth - minimal_bandwidth:.1f} KB/s saved")
    print(f"  {((full_bandwidth - minimal_bandwidth) / full_bandwidth) * 100:.1f}% reduction")

if __name__ == "__main__":
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("API is running. Starting performance tests...\n")
            run_performance_tests()
        else:
            print(f"API returned status code {response.status_code}")
            print("Please ensure the API is running properly.")
    except requests.exceptions.RequestException as e:
        print(f"Could not connect to API at {API_BASE_URL}")
        print(f"Error: {e}")
        print("\nPlease start the API with: ./start_ga10_portfolio_api.sh")