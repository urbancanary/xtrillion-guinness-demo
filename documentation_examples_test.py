#!/usr/bin/env python3
"""
Comprehensive test suite for all examples in the external API documentation
Tests all documented endpoints with proper response time measurements including cold starts
"""

import json
import requests
import time
import datetime
import statistics
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import argparse

# Production API configuration
PRODUCTION_URL = "https://future-footing-414610.uc.r.appspot.com"
DEMO_API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q"

# Response time thresholds (milliseconds)
THRESHOLDS = {
    "health": {"cold": 2000, "warm": 200},
    "bond_analysis": {"cold": 2000, "warm": 500},
    "portfolio_analysis": {"cold": 2000, "warm": 1000},
    "cash_flow": {"cold": 2000, "warm": 500},
    "flexible_analysis": {"cold": 2000, "warm": 500}
}

@dataclass
class TimingResult:
    endpoint: str
    cold_start_ms: float
    warm_times_ms: List[float]
    avg_warm_ms: float
    median_warm_ms: float
    min_warm_ms: float
    max_warm_ms: float
    std_dev_ms: float
    success_rate: float
    errors: List[str]

class DocumentationExamplesTester:
    def __init__(self, base_url: str = PRODUCTION_URL):
        self.base_url = base_url
        self.api_key = DEMO_API_KEY
        self.results = []
        self.all_responses = {}
        
    def measure_request(self, method: str, url: str, headers: Dict = None, 
                       json_data: Dict = None, timeout: int = 30) -> Tuple[Optional[requests.Response], float]:
        """Make request and measure response time"""
        start = time.time()
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                timeout=timeout
            )
            elapsed_ms = (time.time() - start) * 1000
            return response, elapsed_ms
        except Exception as e:
            elapsed_ms = (time.time() - start) * 1000
            print(f"❌ Request failed: {e}")
            return None, elapsed_ms
            
    def test_endpoint_timing(self, name: str, method: str, endpoint: str, 
                           headers: Dict = None, json_data: Dict = None,
                           num_warm_runs: int = 5) -> TimingResult:
        """Test an endpoint with cold start and multiple warm runs"""
        print(f"\n🧪 Testing: {name}")
        print(f"   Endpoint: {method} {endpoint}")
        
        url = f"{self.base_url}{endpoint}"
        errors = []
        warm_times = []
        
        # Cold start measurement
        print("   📊 Cold start test...")
        response, cold_time = self.measure_request(method, url, headers, json_data)
        
        if response and response.status_code == 200:
            print(f"   ✅ Cold start: {cold_time:.0f}ms")
            self.all_responses[name] = response.json()
        else:
            error_msg = f"Cold start failed: {response.status_code if response else 'No response'}"
            print(f"   ❌ {error_msg}")
            errors.append(error_msg)
            cold_time = -1
            
        # Wait a moment before warm runs
        time.sleep(0.5)
        
        # Warm runs
        print(f"   📊 Running {num_warm_runs} warm tests...")
        successful_runs = 0
        
        for i in range(num_warm_runs):
            response, elapsed = self.measure_request(method, url, headers, json_data)
            
            if response and response.status_code == 200:
                warm_times.append(elapsed)
                successful_runs += 1
                print(f"      Run {i+1}: {elapsed:.0f}ms")
            else:
                error_msg = f"Warm run {i+1} failed"
                errors.append(error_msg)
                
            # Small delay between requests
            if i < num_warm_runs - 1:
                time.sleep(0.2)
                
        # Calculate statistics
        if warm_times:
            avg_warm = statistics.mean(warm_times)
            median_warm = statistics.median(warm_times)
            min_warm = min(warm_times)
            max_warm = max(warm_times)
            std_dev = statistics.stdev(warm_times) if len(warm_times) > 1 else 0
        else:
            avg_warm = median_warm = min_warm = max_warm = std_dev = -1
            
        success_rate = (successful_runs + (1 if cold_time > 0 else 0)) / (num_warm_runs + 1) * 100
        
        result = TimingResult(
            endpoint=name,
            cold_start_ms=cold_time,
            warm_times_ms=warm_times,
            avg_warm_ms=avg_warm,
            median_warm_ms=median_warm,
            min_warm_ms=min_warm,
            max_warm_ms=max_warm,
            std_dev_ms=std_dev,
            success_rate=success_rate,
            errors=errors
        )
        
        # Check against thresholds
        endpoint_type = name.split(" - ")[0].lower().replace(" ", "_")
        if endpoint_type in THRESHOLDS:
            thresholds = THRESHOLDS[endpoint_type]
            
            if cold_time > 0 and cold_time > thresholds["cold"]:
                print(f"   ⚠️  Cold start exceeds threshold: {cold_time:.0f}ms > {thresholds['cold']}ms")
                
            if avg_warm > 0 and avg_warm > thresholds["warm"]:
                print(f"   ⚠️  Warm average exceeds threshold: {avg_warm:.0f}ms > {thresholds['warm']}ms")
                
        print(f"   📈 Summary: Avg={avg_warm:.0f}ms, Min={min_warm:.0f}ms, Max={max_warm:.0f}ms")
        
        return result
        
    def test_all_documentation_examples(self):
        """Test all examples from the external documentation"""
        print("🚀 XTrillion API Documentation Examples Test Suite")
        print(f"   Base URL: {self.base_url}")
        print(f"   Timestamp: {datetime.datetime.now().isoformat()}")
        print("=" * 80)
        
        # Common headers
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }
        
        # Test 1: Health Check (Section 4.2)
        result = self.test_endpoint_timing(
            name="Health Check - GET /health",
            method="GET",
            endpoint="/health",
            num_warm_runs=3
        )
        self.results.append(result)
        
        # Test 2: Individual Bond Analysis (Section 4.3)
        result = self.test_endpoint_timing(
            name="Bond Analysis - US Treasury 3% 2052",
            method="POST",
            endpoint="/api/v1/bond/analysis",
            headers=headers,
            json_data={
                "description": "T 3 15/08/52",
                "price": 71.66,
                "settlement_date": "2025-07-30"
            }
        )
        self.results.append(result)
        
        # Test 3: Flexible Bond Analysis (Section 4.3a)
        result = self.test_endpoint_timing(
            name="Flexible Analysis - Array Format",
            method="POST",
            endpoint="/api/v1/bond/analysis/flexible",
            headers=headers,
            json_data=["T 3 15/08/52", 71.66, "2025-07-31"]
        )
        self.results.append(result)
        
        # Test 4: Portfolio Analysis - Two Bonds (Section 4.4)
        result = self.test_endpoint_timing(
            name="Portfolio Analysis - 2 Bonds",
            method="POST",
            endpoint="/api/v1/portfolio/analysis",
            headers=headers,
            json_data={
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
                ]
            }
        )
        self.results.append(result)
        
        # Test 5: Portfolio Analysis - ISIN Approach (Section 4.4)
        result = self.test_endpoint_timing(
            name="Portfolio Analysis - ISIN Format",
            method="POST",
            endpoint="/api/v1/portfolio/analysis",
            headers=headers,
            json_data={
                "data": [
                    {
                        "BOND_CD": "US912810TJ79",  # Real Treasury ISIN
                        "CLOSING PRICE": 99.5,
                        "WEIGHTING": 100.0
                    }
                ]
            }
        )
        self.results.append(result)
        
        # Test 6: Cash Flow Analysis (Section 4.5)
        result = self.test_endpoint_timing(
            name="Cash Flow Analysis - 90 Day Period",
            method="POST",
            endpoint="/api/v1/bond/cashflow",
            headers=headers,
            json_data={
                "bonds": [
                    {
                        "description": "T 3 15/08/52",
                        "nominal": 1000000
                    }
                ],
                "filter": "period",
                "days": 90,
                "context": "portfolio",
                "settlement_date": "2025-07-30"
            }
        )
        self.results.append(result)
        
        # Test 7: Large Portfolio (Performance Test)
        large_portfolio_data = []
        treasuries = [
            ("T 2.875 15/05/32", 89.25, 10.0),
            ("T 3 15/08/52", 71.66, 15.0),
            ("T 4.125 15/11/32", 99.5, 15.0),
            ("T 2.5 15/02/45", 75.8, 10.0),
            ("T 3.625 15/02/44", 90.2, 10.0),
            ("T 3.125 15/11/41", 82.5, 10.0),
            ("T 2.75 15/11/42", 77.3, 10.0),
            ("T 3.375 15/05/44", 88.1, 10.0),
            ("T 2.25 15/08/46", 69.4, 5.0),
            ("T 4.75 15/02/41", 105.6, 5.0)
        ]
        
        for desc, price, weight in treasuries:
            large_portfolio_data.append({
                "description": desc,
                "CLOSING PRICE": price,
                "WEIGHTING": weight
            })
            
        result = self.test_endpoint_timing(
            name="Portfolio Analysis - 10 Bonds (Performance)",
            method="POST",
            endpoint="/api/v1/portfolio/analysis",
            headers=headers,
            json_data={"data": large_portfolio_data},
            num_warm_runs=3
        )
        self.results.append(result)
        
        # Test 8: Bond with No Settlement Date (Tests Default)
        result = self.test_endpoint_timing(
            name="Bond Analysis - Default Settlement",
            method="POST",
            endpoint="/api/v1/bond/analysis",
            headers=headers,
            json_data={
                "description": "T 3 15/08/52",
                "price": 71.66
            }
        )
        self.results.append(result)
        
        # Test 9: Different Bond Types
        test_bonds = [
            ("PEMEX 6.5 13/06/27", 95.75),
            ("PANAMA 3.87 23/07/60", 56.60),
            ("T 4.125 15/11/32", 99.5)
        ]
        
        for bond_desc, price in test_bonds:
            result = self.test_endpoint_timing(
                name=f"Bond Analysis - {bond_desc.split()[0]}",
                method="POST",
                endpoint="/api/v1/bond/analysis",
                headers=headers,
                json_data={
                    "description": bond_desc,
                    "price": price,
                    "settlement_date": "2025-04-18"  # Fixed date for consistency
                },
                num_warm_runs=3
            )
            self.results.append(result)
            
    def generate_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        report = {
            "test_date": datetime.datetime.now().isoformat(),
            "base_url": self.base_url,
            "total_tests": len(self.results),
            "summary": {
                "avg_cold_start_ms": 0,
                "avg_warm_response_ms": 0,
                "overall_success_rate": 0,
                "tests_exceeding_thresholds": 0
            },
            "detailed_results": [],
            "response_samples": self.all_responses
        }
        
        # Calculate summary statistics
        valid_cold_times = [r.cold_start_ms for r in self.results if r.cold_start_ms > 0]
        valid_warm_times = [r.avg_warm_ms for r in self.results if r.avg_warm_ms > 0]
        
        if valid_cold_times:
            report["summary"]["avg_cold_start_ms"] = statistics.mean(valid_cold_times)
            
        if valid_warm_times:
            report["summary"]["avg_warm_response_ms"] = statistics.mean(valid_warm_times)
            
        total_success_rate = statistics.mean([r.success_rate for r in self.results])
        report["summary"]["overall_success_rate"] = total_success_rate
        
        # Add detailed results
        for result in self.results:
            report["detailed_results"].append(asdict(result))
            
        return report
        
    def print_summary(self):
        """Print performance summary"""
        print("\n" + "=" * 80)
        print("📊 PERFORMANCE SUMMARY")
        print("=" * 80)
        
        # Create summary table
        print(f"\n{'Endpoint':<40} {'Cold (ms)':<12} {'Avg (ms)':<12} {'Min (ms)':<12} {'Max (ms)':<12} {'Success':<10}")
        print("-" * 100)
        
        for result in self.results:
            cold_str = f"{result.cold_start_ms:.0f}" if result.cold_start_ms > 0 else "Failed"
            avg_str = f"{result.avg_warm_ms:.0f}" if result.avg_warm_ms > 0 else "N/A"
            min_str = f"{result.min_warm_ms:.0f}" if result.min_warm_ms > 0 else "N/A"
            max_str = f"{result.max_warm_ms:.0f}" if result.max_warm_ms > 0 else "N/A"
            
            print(f"{result.endpoint:<40} {cold_str:<12} {avg_str:<12} {min_str:<12} {max_str:<12} {result.success_rate:.0f}%")
            
        # Overall statistics
        valid_cold_times = [r.cold_start_ms for r in self.results if r.cold_start_ms > 0]
        valid_warm_times = [r.avg_warm_ms for r in self.results if r.avg_warm_ms > 0]
        
        print("\n" + "=" * 80)
        print("📈 OVERALL STATISTICS")
        print("=" * 80)
        
        if valid_cold_times:
            print(f"Average Cold Start: {statistics.mean(valid_cold_times):.0f}ms")
            print(f"Median Cold Start: {statistics.median(valid_cold_times):.0f}ms")
            print(f"Max Cold Start: {max(valid_cold_times):.0f}ms")
            
        if valid_warm_times:
            print(f"\nAverage Warm Response: {statistics.mean(valid_warm_times):.0f}ms")
            print(f"Median Warm Response: {statistics.median(valid_warm_times):.0f}ms")
            print(f"Min Warm Response: {min([r.min_warm_ms for r in self.results if r.min_warm_ms > 0]):.0f}ms")
            print(f"Max Warm Response: {max([r.max_warm_ms for r in self.results if r.max_warm_ms > 0]):.0f}ms")
            
        # Threshold violations
        print("\n⚠️  THRESHOLD VIOLATIONS:")
        violations = 0
        for result in self.results:
            endpoint_type = result.endpoint.split(" - ")[0].lower().replace(" ", "_")
            if endpoint_type in THRESHOLDS:
                thresholds = THRESHOLDS[endpoint_type]
                if result.cold_start_ms > thresholds["cold"]:
                    print(f"   {result.endpoint}: Cold start {result.cold_start_ms:.0f}ms > {thresholds['cold']}ms")
                    violations += 1
                if result.avg_warm_ms > thresholds["warm"]:
                    print(f"   {result.endpoint}: Warm avg {result.avg_warm_ms:.0f}ms > {thresholds['warm']}ms")
                    violations += 1
                    
        if violations == 0:
            print("   ✅ All response times within acceptable thresholds")
            
        # Errors
        print("\n❌ ERRORS:")
        error_count = 0
        for result in self.results:
            if result.errors:
                print(f"   {result.endpoint}:")
                for error in result.errors:
                    print(f"      - {error}")
                    error_count += 1
                    
        if error_count == 0:
            print("   ✅ No errors encountered")

def main():
    parser = argparse.ArgumentParser(description='Test all API documentation examples with timing')
    parser.add_argument('--warm-runs', type=int, default=5, 
                       help='Number of warm runs per endpoint (default: 5)')
    parser.add_argument('--save-report', action='store_true',
                       help='Save detailed JSON report')
    parser.add_argument('--base-url', type=str, default=PRODUCTION_URL,
                       help='Override base URL for testing')
    
    args = parser.parse_args()
    
    # Run tests
    tester = DocumentationExamplesTester(base_url=args.base_url)
    tester.test_all_documentation_examples()
    
    # Print summary
    tester.print_summary()
    
    # Save detailed report
    if args.save_report:
        report = tester.generate_performance_report()
        filename = f"documentation_test_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📄 Detailed report saved to: {filename}")
        
    # Exit with error if any tests failed
    total_success = all(r.success_rate == 100 for r in tester.results)
    sys.exit(0 if total_success else 1)

if __name__ == "__main__":
    main()