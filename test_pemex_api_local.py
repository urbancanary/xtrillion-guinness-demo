#!/usr/bin/env python3
"""
Test PEMEX bond fix via local API
"""

import requests
import json
import subprocess
import time
import os
import signal

def start_local_api():
    """Start the local API server"""
    print("🚀 Starting local API server...")
    
    # Start the API in the background
    process = subprocess.Popen(
        ['python3', 'google_analysis10_api.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    # Wait for server to start
    time.sleep(5)
    
    return process

def test_pemex_local_api():
    """Test PEMEX bond against local API"""
    print("\n🧪 Testing PEMEX bond against local API")
    print("=" * 60)
    
    url = "http://localhost:8080/api/v1/bond/analysis"
    
    payload = {
        "description": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060",
        "price": 100.0,
        "settlement_date": "2025-04-21"
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "test_api_key"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        result = response.json()
        
        if result.get('status') == 'success':
            analytics = result.get('analytics', {})
            accrued = analytics.get('accrued_interest', 0)
            accrued_per_million = accrued * 10000
            
            print(f"\n📊 Local API Results:")
            print(f"   Accrued interest: {accrued:.6f}%") 
            print(f"   Accrued per million: ${accrued_per_million:,.2f}")
            
            print(f"\n💡 Expected Result:")
            print(f"   Accrued interest: 1.602361%")
            print(f"   Accrued per million: $16,023.61")
            
            # Check if fix worked
            if abs(accrued_per_million - 16023.61) < 1.0:
                print("\n✅ FIX SUCCESSFUL! Values match expected.")
                return True
            else:
                print("\n❌ Fix not working correctly.")
                return False
        else:
            print(f"❌ API Error: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    """Main test function"""
    # Start local API
    api_process = start_local_api()
    
    try:
        # Test the API
        success = test_pemex_local_api()
        
        if success:
            print("\n🎉 PEMEX bond fix is working correctly!")
        else:
            print("\n❌ PEMEX bond fix needs more work.")
            
    finally:
        # Stop the API server
        print("\n🛑 Stopping API server...")
        os.killpg(os.getpgid(api_process.pid), signal.SIGTERM)
        time.sleep(2)

if __name__ == "__main__":
    main()