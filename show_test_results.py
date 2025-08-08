#!/usr/bin/env python3
"""
Display test results in a formatted way
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def format_test_results(filename=None):
    """Format and display test results"""
    
    # If no filename provided, find the latest
    if not filename:
        result_files = list(Path('.').glob('test_results_production_*.json'))
        if not result_files:
            print("❌ No test results found. Run daily_test_suite.py first.")
            return
        filename = max(result_files, key=lambda f: f.stat().st_mtime)
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    # Header
    print("\n" + "="*80)
    print(f"📊 XTrillion API Test Results - {data['environment']}")
    print("="*80)
    
    # Summary
    success_emoji = "✅" if data['success_rate'] == 100 else "⚠️" if data['success_rate'] >= 80 else "❌"
    print(f"\n{success_emoji} Success Rate: {data['success_rate']:.1f}% ({data['passed']}/{data['total_tests']} passed)")
    print(f"⏱️  Total Duration: {data['duration_seconds']:.1f} seconds")
    print(f"🌐 API URL: {data['url']}")
    print(f"📅 Test Date: {datetime.fromisoformat(data['timestamp']).strftime('%B %d, %Y at %I:%M %p')}")
    
    # Detailed Results
    print("\n" + "-"*80)
    print("DETAILED TEST RESULTS:")
    print("-"*80)
    
    for i, result in enumerate(data['results'], 1):
        status = "✅ PASSED" if result['passed'] else "❌ FAILED"
        response_time = f"{result['response_time']*1000:.0f}ms" if result['response_time'] > 0 else "N/A"
        
        print(f"\n{i}. {result['test_name']} - {status}")
        print(f"   Response Time: {response_time}")
        print(f"   Details: {result['details'][:100]}{'...' if len(result['details']) > 100 else ''}")
    
    # Performance Summary
    print("\n" + "-"*80)
    print("PERFORMANCE SUMMARY:")
    print("-"*80)
    
    perf_tests = [r for r in data['results'] if r['response_time'] > 0]
    if perf_tests:
        avg_time = sum(r['response_time'] for r in perf_tests) / len(perf_tests) * 1000
        max_time = max(r['response_time'] for r in perf_tests) * 1000
        min_time = min(r['response_time'] for r in perf_tests) * 1000
        
        print(f"Average Response Time: {avg_time:.0f}ms")
        print(f"Fastest Response: {min_time:.0f}ms")
        print(f"Slowest Response: {max_time:.0f}ms")
    
    # Key Findings
    print("\n" + "-"*80)
    print("KEY FINDINGS:")
    print("-"*80)
    
    # Check baseline
    baseline_test = next((r for r in data['results'] if 'Baseline' in r['test_name']), None)
    if baseline_test and baseline_test['passed']:
        print("✅ All calculations are stable - no changes detected from baseline")
    elif baseline_test and not baseline_test['passed']:
        print("⚠️  CALCULATION CHANGES DETECTED - Review baseline comparison")
    
    # Check performance
    perf_test = next((r for r in data['results'] if 'Performance' in r['test_name']), None)
    if perf_test:
        if "810ms" in perf_test['details']:
            print("⚠️  API performance is acceptable but could be improved (810ms average)")
        elif perf_test['passed']:
            print("✅ API performance is within acceptable limits")
        else:
            print("❌ API performance is degraded")
    
    # Failed tests
    failed_tests = [r for r in data['results'] if not r['passed']]
    if failed_tests:
        print(f"\n❌ {len(failed_tests)} tests failed:")
        for test in failed_tests:
            print(f"   - {test['test_name']}: {test['details'][:50]}...")
    
    print("\n" + "="*80)
    print()

def main():
    """Main function"""
    if len(sys.argv) > 1:
        format_test_results(sys.argv[1])
    else:
        format_test_results()

if __name__ == "__main__":
    main()