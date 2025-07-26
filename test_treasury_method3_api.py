#!/usr/bin/env python3
"""
Test the Treasury Method 3 API
"""

import requests
import json
import subprocess
import time
import signal
import os

def start_treasury_api():
    """Start the Treasury Method 3 API"""
    return subprocess.Popen(['python3', 'treasury_method3_api.py'], 
                           cwd='/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

def test_treasury_api():
    """Test the Treasury API with your Bloomberg data"""
    
    # Test data matching your Bloomberg expectations
    test_data = {
        "description": "US TREASURY N/B 3 15/08/2052",
        "price": 71.66,
        "settlement_date": "2025-06-30"
    }
    
    api_url = "http://localhost:8081/api/v1/treasury/calculate"
    
    print("🏛️ Testing Treasury Method 3 API...")
    print(f"Input: {test_data}")
    print()
    
    try:
        response = requests.post(api_url, json=test_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! Treasury Method 3 Results:")
            print(json.dumps(result, indent=2))
            
            # Highlight key metrics
            if 'results' in result:
                results = result['results']
                print()
                print("🎯 KEY METRICS:")
                print(f"  Yield: {results['yield_percent']}%")
                print(f"  Duration: {results['duration_years']} years")
                print(f"  Days Accrued: {results['days_accrued']} days")
                print(f"  Accrued per Million: {results['accrued_per_million']}")
                
            if 'bloomberg_comparison' in result:
                bbg = result['bloomberg_comparison']
                print()
                print("📊 VS YOUR BLOOMBERG DATA:")
                print(f"  Duration Diff: {bbg['duration_diff']} years")
                print(f"  Accrued per Million Diff: {bbg['accrued_per_million_diff']}")
                print()
                print("✅ Method 3 is working with proper debug info!")
        else:
            print(f"❌ API Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    # Start the Treasury API
    print("🚀 Starting Treasury Method 3 API...")
    api_process = start_treasury_api()
    
    try:
        # Give it time to start
        time.sleep(3)
        
        # Test the API
        test_treasury_api()
        
    finally:
        # Clean up
        print()
        print("🛑 Stopping API...")
        api_process.terminate()
        time.sleep(1)
        if api_process.poll() is None:
            api_process.kill()
