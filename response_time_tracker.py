#!/usr/bin/env python3
"""
Response Time Tracker for XTrillion API
Tracks response times over multiple runs to identify performance trends
"""

import json
import requests
import time
import datetime
import statistics
import os
from typing import Dict, List
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class ResponseTimeTracker:
    def __init__(self):
        self.history_file = "response_time_history.json"
        self.base_url = "https://future-footing-414610.uc.r.appspot.com"
        self.api_key = "gax10_demo_3j5h8m9k2p6r4t7w1q"
        
    def load_history(self) -> List[Dict]:
        """Load historical response time data"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []
        
    def save_history(self, history: List[Dict]):
        """Save response time history"""
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
            
    def measure_endpoint(self, name: str, method: str, endpoint: str, 
                        headers: Dict = None, json_data: Dict = None,
                        runs: int = 10) -> Dict:
        """Measure response times for an endpoint"""
        url = f"{self.base_url}{endpoint}"
        times = []
        errors = 0
        
        print(f"📊 Measuring {name} ({runs} runs)...")
        
        for i in range(runs):
            start = time.time()
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data,
                    timeout=10
                )
                elapsed_ms = (time.time() - start) * 1000
                
                if response.status_code == 200:
                    times.append(elapsed_ms)
                    print(f"   Run {i+1}: {elapsed_ms:.0f}ms")
                else:
                    errors += 1
                    print(f"   Run {i+1}: Failed (HTTP {response.status_code})")
                    
            except Exception as e:
                errors += 1
                print(f"   Run {i+1}: Error - {str(e)}")
                
            # Small delay between requests
            if i < runs - 1:
                time.sleep(0.5)
                
        # Calculate statistics
        if times:
            result = {
                "endpoint": name,
                "timestamp": datetime.datetime.now().isoformat(),
                "runs": runs,
                "successful": len(times),
                "errors": errors,
                "avg_ms": statistics.mean(times),
                "median_ms": statistics.median(times),
                "min_ms": min(times),
                "max_ms": max(times),
                "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
                "p95_ms": sorted(times)[int(len(times) * 0.95)] if times else 0,
                "all_times": times
            }
        else:
            result = {
                "endpoint": name,
                "timestamp": datetime.datetime.now().isoformat(),
                "runs": runs,
                "successful": 0,
                "errors": errors,
                "avg_ms": -1
            }
            
        return result
        
    def track_performance(self):
        """Run performance tracking for key endpoints"""
        print("🚀 XTrillion API Response Time Tracking")
        print(f"   Timestamp: {datetime.datetime.now()}")
        print("=" * 60)
        
        # Load history
        history = self.load_history()
        
        # Test endpoints
        test_cases = [
            {
                "name": "Health Check",
                "method": "GET",
                "endpoint": "/health",
                "runs": 5
            },
            {
                "name": "Bond Analysis (Fixed Date)",
                "method": "POST",
                "endpoint": "/api/v1/bond/analysis",
                "headers": {
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                },
                "json_data": {
                    "description": "T 3 15/08/52",
                    "price": 71.66,
                    "settlement_date": "2025-06-30"
                },
                "runs": 10
            },
            {
                "name": "Portfolio Analysis (2 Bonds)",
                "method": "POST",
                "endpoint": "/api/v1/portfolio/analysis",
                "headers": {
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                },
                "json_data": {
                    "data": [
                        {"description": "T 3 15/08/52", "CLOSING PRICE": 71.66, "WEIGHTING": 50.0},
                        {"description": "T 4.125 15/11/32", "CLOSING PRICE": 99.5, "WEIGHTING": 50.0}
                    ]
                },
                "runs": 10
            }
        ]
        
        # Current session results
        session_results = []
        
        for test in test_cases:
            result = self.measure_endpoint(
                name=test["name"],
                method=test["method"],
                endpoint=test["endpoint"],
                headers=test.get("headers"),
                json_data=test.get("json_data"),
                runs=test.get("runs", 10)
            )
            session_results.append(result)
            print()
            
        # Add to history
        history.append({
            "session_timestamp": datetime.datetime.now().isoformat(),
            "results": session_results
        })
        
        # Keep only last 30 days of data
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=30)
        history = [h for h in history 
                  if datetime.datetime.fromisoformat(h["session_timestamp"]) > cutoff_date]
        
        # Save updated history
        self.save_history(history)
        
        # Print summary
        self.print_summary(session_results)
        
        # Check for performance degradation
        self.check_degradation(history)
        
    def print_summary(self, results: List[Dict]):
        """Print session summary"""
        print("=" * 60)
        print("📊 SESSION SUMMARY")
        print("=" * 60)
        
        print(f"\n{'Endpoint':<30} {'Avg (ms)':<10} {'P95 (ms)':<10} {'Min':<8} {'Max':<8} {'Success'}")
        print("-" * 76)
        
        for result in results:
            if result["avg_ms"] > 0:
                success_rate = f"{result['successful']}/{result['runs']}"
                print(f"{result['endpoint']:<30} {result['avg_ms']:<10.0f} "
                      f"{result.get('p95_ms', 0):<10.0f} {result['min_ms']:<8.0f} "
                      f"{result['max_ms']:<8.0f} {success_rate}")
            else:
                print(f"{result['endpoint']:<30} {'Failed':<10} {'-':<10} {'-':<8} {'-':<8} 0/{result['runs']}")
                
    def check_degradation(self, history: List[Dict]):
        """Check for performance degradation over time"""
        if len(history) < 2:
            return
            
        print("\n" + "=" * 60)
        print("📈 PERFORMANCE TREND ANALYSIS")
        print("=" * 60)
        
        # Group by endpoint
        endpoint_history = {}
        
        for session in history:
            for result in session["results"]:
                endpoint = result["endpoint"]
                if endpoint not in endpoint_history:
                    endpoint_history[endpoint] = []
                    
                if result["avg_ms"] > 0:
                    endpoint_history[endpoint].append({
                        "timestamp": session["session_timestamp"],
                        "avg_ms": result["avg_ms"],
                        "p95_ms": result.get("p95_ms", result["avg_ms"])
                    })
                    
        # Analyze trends
        for endpoint, data in endpoint_history.items():
            if len(data) < 2:
                continue
                
            # Get recent vs older performance
            recent = data[-5:]  # Last 5 measurements
            older = data[:-5] if len(data) > 5 else data[:1]
            
            recent_avg = statistics.mean([d["avg_ms"] for d in recent])
            older_avg = statistics.mean([d["avg_ms"] for d in older])
            
            change_pct = ((recent_avg - older_avg) / older_avg) * 100
            
            print(f"\n{endpoint}:")
            print(f"   Historical Avg: {older_avg:.0f}ms")
            print(f"   Recent Avg: {recent_avg:.0f}ms")
            print(f"   Change: {change_pct:+.1f}%")
            
            if change_pct > 20:
                print(f"   ⚠️  WARNING: Significant performance degradation detected!")
            elif change_pct > 10:
                print(f"   ⚠️  Minor performance degradation")
            elif change_pct < -10:
                print(f"   ✅ Performance improvement!")
                
    def generate_trend_chart(self, days: int = 7):
        """Generate performance trend chart"""
        history = self.load_history()
        
        if not history:
            print("No historical data available for charting")
            return
            
        # Prepare data for plotting
        endpoint_data = {}
        
        for session in history:
            session_date = datetime.datetime.fromisoformat(session["session_timestamp"])
            
            # Only include recent data
            if (datetime.datetime.now() - session_date).days > days:
                continue
                
            for result in session["results"]:
                endpoint = result["endpoint"]
                if result["avg_ms"] > 0:
                    if endpoint not in endpoint_data:
                        endpoint_data[endpoint] = {"dates": [], "times": []}
                        
                    endpoint_data[endpoint]["dates"].append(session_date)
                    endpoint_data[endpoint]["times"].append(result["avg_ms"])
                    
        # Create plot
        plt.figure(figsize=(12, 6))
        
        for endpoint, data in endpoint_data.items():
            plt.plot(data["dates"], data["times"], marker='o', label=endpoint)
            
        plt.xlabel("Date")
        plt.ylabel("Response Time (ms)")
        plt.title(f"API Response Time Trends (Last {days} Days)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Format x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        plt.gcf().autofmt_xdate()
        
        # Save chart
        filename = f"response_time_trend_{datetime.date.today()}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"\n📊 Trend chart saved to: {filename}")
        plt.close()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Track API response times over time')
    parser.add_argument('--runs', type=int, default=10,
                       help='Number of runs per endpoint (default: 10)')
    parser.add_argument('--chart', action='store_true',
                       help='Generate trend chart')
    parser.add_argument('--days', type=int, default=7,
                       help='Days of history for chart (default: 7)')
    
    args = parser.parse_args()
    
    tracker = ResponseTimeTracker()
    
    if args.chart:
        tracker.generate_trend_chart(days=args.days)
    else:
        tracker.track_performance()

if __name__ == "__main__":
    main()