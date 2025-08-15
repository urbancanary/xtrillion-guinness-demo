#!/usr/bin/env python3
"""
Simulate cache performance to understand the real-world speed benefits
"""

import time
import json
import requests
from datetime import datetime

class CacheSimulator:
    def __init__(self):
        self.cache = {}
        self.api_calls = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
    def get_bond_data(self, bond, price, settlement, use_cache=True):
        """Get bond data with optional caching"""
        cache_key = f"{bond}_{price}_{settlement}"
        
        if use_cache and cache_key in self.cache:
            # Cache hit - just return cached data
            self.cache_hits += 1
            return self.cache[cache_key], 0  # 0ms for cache read (essentially instant)
        
        # Cache miss - make API call
        self.cache_misses += 1
        self.api_calls += 1
        
        start = time.time()
        response = requests.post(
            "https://development-dot-future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": "gax10_dev_4n8s6k2x7p9v5m8p1z"
            },
            json={
                "description": bond,
                "price": price,
                "settlement_date": settlement
            },
            timeout=30
        )
        elapsed = (time.time() - start) * 1000  # Convert to ms
        
        if response.status_code == 200:
            data = response.json()["analytics"]
            result = {
                "ytm": data["ytm"],
                "duration": data["duration"],
                "spread": data["spread"]
            }
            
            if use_cache:
                self.cache[cache_key] = result
            
            return result, elapsed
        
        return None, elapsed

def test_cache_scenarios():
    """Test different caching scenarios"""
    print("🧪 Cache Performance Simulation")
    print("=" * 60)
    
    simulator = CacheSimulator()
    
    # Scenario 1: Single bond called multiple times (best case for cache)
    print("\n📊 Scenario 1: Same bond called 10 times")
    times_cached = []
    times_uncached = []
    
    # With cache
    for i in range(10):
        _, elapsed = simulator.get_bond_data("T 3 15/08/52", 71.66, "2025-06-30", use_cache=True)
        times_cached.append(elapsed)
        if i == 0:
            print(f"  First call (cache miss): {elapsed:.0f}ms")
        elif i == 1:
            print(f"  Second call (cache hit): {elapsed:.0f}ms")
    
    print(f"  Total time with cache: {sum(times_cached):.0f}ms")
    print(f"  Cache hits: {simulator.cache_hits}, misses: {simulator.cache_misses}")
    
    # Reset for uncached test
    simulator2 = CacheSimulator()
    
    # Without cache
    for i in range(10):
        _, elapsed = simulator2.get_bond_data("T 3 15/08/52", 71.66, "2025-06-30", use_cache=False)
        times_uncached.append(elapsed)
    
    print(f"  Total time without cache: {sum(times_uncached):.0f}ms")
    print(f"  Speedup: {sum(times_uncached)/sum(times_cached):.1f}x")
    
    # Scenario 2: Different bonds (worst case for cache)
    print("\n📊 Scenario 2: 10 different bonds")
    simulator3 = CacheSimulator()
    times_different = []
    
    for i in range(10):
        bond = f"T {i+1} 15/08/52"
        price = 70 + i
        _, elapsed = simulator3.get_bond_data(bond, price, "2025-06-30", use_cache=True)
        times_different.append(elapsed)
    
    print(f"  Total time (all cache misses): {sum(times_different):.0f}ms")
    print(f"  Average per bond: {sum(times_different)/10:.0f}ms")
    print(f"  Cache effectiveness: {simulator3.cache_hits}/{simulator3.cache_hits + simulator3.cache_misses} = 0%")
    
    # Scenario 3: Mixed usage (realistic)
    print("\n📊 Scenario 3: Mixed usage (some repeats)")
    simulator4 = CacheSimulator()
    bonds_list = [
        ("T 3 15/08/52", 71.66),
        ("T 2 15/08/51", 70.50),
        ("T 3 15/08/52", 71.66),  # Repeat
        ("T 4 15/08/53", 72.00),
        ("T 2 15/08/51", 70.50),  # Repeat
        ("T 3 15/08/52", 71.66),  # Repeat
        ("T 5 15/08/54", 73.00),
        ("T 3 15/08/52", 71.66),  # Repeat
        ("T 2 15/08/51", 70.50),  # Repeat
        ("T 6 15/08/55", 74.00),
    ]
    
    times_mixed = []
    for bond, price in bonds_list:
        _, elapsed = simulator4.get_bond_data(bond, price, "2025-06-30", use_cache=True)
        times_mixed.append(elapsed)
    
    print(f"  Total time: {sum(times_mixed):.0f}ms")
    print(f"  Cache hits: {simulator4.cache_hits}, misses: {simulator4.cache_misses}")
    print(f"  Hit rate: {simulator4.cache_hits/len(bonds_list)*100:.0f}%")
    print(f"  Time saved: {simulator4.cache_hits * 400:.0f}ms")
    
    # Scenario 4: Settlement date changes (cache invalidation problem)
    print("\n📊 Scenario 4: Same bond, different settlement dates")
    simulator5 = CacheSimulator()
    
    # First call with one date
    data1, time1 = simulator5.get_bond_data("T 3 15/08/52", 71.66, "2025-06-30", use_cache=True)
    print(f"  Call 1 (2025-06-30): Duration = {data1['duration']:.2f}, Time = {time1:.0f}ms")
    
    # Second call with different date (cache key includes date, so cache miss)
    data2, time2 = simulator5.get_bond_data("T 3 15/08/52", 71.66, "2025-07-31", use_cache=True)
    print(f"  Call 2 (2025-07-31): Duration = {data2['duration']:.2f}, Time = {time2:.0f}ms")
    
    # Third call with first date again (cache hit)
    data3, time3 = simulator5.get_bond_data("T 3 15/08/52", 71.66, "2025-06-30", use_cache=True)
    print(f"  Call 3 (2025-06-30): Duration = {data3['duration']:.2f}, Time = {time3:.0f}ms")
    
    print("\n📈 Summary:")
    print("=" * 60)
    print("✅ Cache PROS:")
    print("  - Near-instant (<1ms) for cache hits")
    print("  - Excellent for repeated calculations")
    print("  - Can provide 10x+ speedup for same bonds")
    
    print("\n❌ Cache CONS:")
    print("  - Adds complexity to code")
    print("  - Risk of stale data if not properly keyed")
    print("  - No benefit for unique bond calculations")
    print("  - Settlement date changes invalidate cache")
    
    print("\n🎯 Recommendation:")
    avg_api_time = sum(times_different) / len(times_different)
    if avg_api_time < 500:
        print(f"  With {avg_api_time:.0f}ms API response time:")
        print("  → Consider NO CACHE for simplicity")
        print("  → Use cache only if same bonds calculated repeatedly")
        print("  → MUST include settlement_date in cache key")
    else:
        print(f"  With {avg_api_time:.0f}ms API response time:")
        print("  → Cache recommended for better UX")
        print("  → Implement proper cache invalidation")
        print("  → Include all parameters in cache key")

if __name__ == "__main__":
    test_cache_scenarios()