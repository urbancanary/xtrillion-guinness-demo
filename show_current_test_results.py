#!/usr/bin/env python3
"""
Show current test results in a formatted way
"""

import json
import requests
from pathlib import Path
from datetime import datetime

def show_test_results():
    """Display test results"""
    print("="*80)
    print("🧪 XTrillion API Test Results Dashboard")
    print("="*80)
    
    # 1. Show latest test results
    result_files = list(Path('.').glob('test_results_production_*.json'))
    if result_files:
        latest_file = max(result_files, key=lambda f: f.stat().st_mtime)
        with open(latest_file, 'r') as f:
            test_data = json.load(f)
        
        print(f"\n📊 Latest Test Run: {test_data['timestamp']}")
        print(f"Environment: {test_data['environment']}")
        print(f"Success Rate: {test_data['success_rate']:.1f}% ({test_data['passed']}/{test_data['total_tests']})")
        print(f"Duration: {test_data['duration_seconds']:.1f} seconds")
        
        print("\nTest Results:")
        print("-"*60)
        for result in test_data['results']:
            status = "✅" if result['passed'] else "❌"
            print(f"{status} {result['test_name']}")
            if result.get('details'):
                print(f"   {result['details'][:80]}...")
    
    # 2. Show baseline values
    print("\n📈 Baseline Values (Settlement: 2025-06-30)")
    print("-"*60)
    
    baseline_file = Path('calculation_baseline.json')
    if baseline_file.exists():
        with open(baseline_file, 'r') as f:
            baseline = json.load(f)
        
        print(f"{'Bond':<30} {'YTM':<10} {'Duration':<10} {'Accrued'}")
        print("-"*60)
        for key, value in baseline.items():
            bond_name = value['name']
            ytm = value['metrics']['ytm']
            duration = value['metrics']['duration']
            accrued = value['metrics']['accrued_interest']
            print(f"{bond_name:<30} {ytm:<10.6f} {duration:<10.6f} ${accrued:.6f}")
    
    # 3. Live API test
    print("\n🔄 Live API Test - US Treasury 3% 15/08/52")
    print("-"*60)
    
    api_url = "https://future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis"
    api_key = "gax10_demo_3j5h8m9k2p6r4t7w1q"
    
    payload = {
        "description": "T 3 15/08/52",
        "price": 71.66,
        "settlement_date": "2025-06-30"
    }
    
    try:
        response = requests.post(
            api_url,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key
            },
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            analytics = data.get('analytics', {})
            
            print(f"Settlement Date: {analytics.get('settlement_date')}")
            print(f"Clean Price: ${analytics.get('clean_price')}")
            print(f"Dirty Price: ${analytics.get('dirty_price'):.6f}")
            print(f"Accrued Interest: ${analytics.get('accrued_interest'):.6f}")
            print(f"YTM: {analytics.get('ytm'):.6f}%")
            print(f"Modified Duration: {analytics.get('duration'):.6f}")
            print(f"Convexity: {analytics.get('convexity'):.6f}")
            print(f"PVBP: ${analytics.get('pvbp'):.6f}")
            
            # Check against expected values
            expected_ytm = 4.898837
            expected_duration = 16.350751
            
            ytm_match = abs(analytics.get('ytm', 0) - expected_ytm) < 0.000001
            dur_match = abs(analytics.get('duration', 0) - expected_duration) < 0.000001
            
            print(f"\n✅ YTM matches expected: {expected_ytm:.6f}" if ytm_match else f"\n❌ YTM mismatch!")
            print(f"✅ Duration matches expected: {expected_duration:.6f}" if dur_match else f"❌ Duration mismatch!")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error calling API: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    show_test_results()