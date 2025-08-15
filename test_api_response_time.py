#!/usr/bin/env python3
"""
Test API response time with and without caching to determine if caching is worth it
"""

import requests
import time
import statistics

def test_api_speed():
    """Test API response times for bond calculations"""
    
    base_url = "https://development-dot-future-footing-414610.uc.r.appspot.com"
    api_key = "gax10_dev_4n8s6k2x7p9v5m8p1z"
    
    # Test bond with settlement date
    payload = {
        "description": "T 3 15/08/52",
        "price": 71.66,
        "settlement_date": "2025-06-30"
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    
    print("🧪 Testing API Response Times")
    print("=" * 50)
    
    # Warm up the API
    print("Warming up API...")
    for _ in range(2):
        requests.post(f"{base_url}/api/v1/bond/analysis", headers=headers, json=payload, timeout=30)
    
    # Test multiple requests
    times = []
    for i in range(10):
        start = time.time()
        response = requests.post(
            f"{base_url}/api/v1/bond/analysis",
            headers=headers,
            json=payload,
            timeout=30
        )
        end = time.time()
        
        elapsed = (end - start) * 1000  # Convert to milliseconds
        times.append(elapsed)
        
        if response.status_code == 200:
            data = response.json()
            duration = data.get("analytics", {}).get("duration", "N/A")
            print(f"Request {i+1}: {elapsed:.0f}ms - Duration: {duration}")
        else:
            print(f"Request {i+1}: {elapsed:.0f}ms - Error: {response.status_code}")
    
    print("\n📊 Statistics:")
    print(f"Average: {statistics.mean(times):.0f}ms")
    print(f"Median: {statistics.median(times):.0f}ms")
    print(f"Min: {min(times):.0f}ms")
    print(f"Max: {max(times):.0f}ms")
    print(f"Std Dev: {statistics.stdev(times):.0f}ms")
    
    print("\n💡 Analysis:")
    avg_time = statistics.mean(times)
    if avg_time < 500:
        print(f"✅ API is fast ({avg_time:.0f}ms avg) - caching may not be necessary")
        print("   Caching adds complexity and stale data issues")
    elif avg_time < 1000:
        print(f"⚠️  API is moderate ({avg_time:.0f}ms avg) - optional caching")
        print("   Consider caching with short TTL (5-10 minutes)")
    else:
        print(f"🔴 API is slow ({avg_time:.0f}ms avg) - caching recommended")
        print("   Use caching with appropriate TTL")
    
    # Test batch request
    print("\n🔬 Testing Batch Request (10 bonds):")
    batch_payload = {
        "bonds": [
            {"description": f"T {i} 15/08/{52-i}", "price": 70 + i, "settlement_date": "2025-06-30"}
            for i in range(1, 11)
        ]
    }
    
    start = time.time()
    response = requests.post(
        f"{base_url}/api/v1/portfolio/batch",
        headers=headers,
        json=batch_payload,
        timeout=30
    )
    end = time.time()
    batch_time = (end - start) * 1000
    
    if response.status_code == 200:
        print(f"Batch request (10 bonds): {batch_time:.0f}ms")
        print(f"Per bond: {batch_time/10:.0f}ms")
    else:
        # Try alternative endpoint
        print("Batch endpoint not available, testing sequential...")
        start = time.time()
        for i in range(10):
            requests.post(f"{base_url}/api/v1/bond/analysis", headers=headers, json=payload, timeout=30)
        end = time.time()
        seq_time = (end - start) * 1000
        print(f"Sequential (10 bonds): {seq_time:.0f}ms")
        print(f"Per bond: {seq_time/10:.0f}ms")

if __name__ == "__main__":
    test_api_speed()