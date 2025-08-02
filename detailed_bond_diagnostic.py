#!/usr/bin/env python3
"""
🔍 DETAILED BOND DIAGNOSTIC TEST
Shows exactly what's happening with each bond - no summaries, just raw results
"""

import requests
import json
import time
from datetime import datetime

# API Configuration
API_BASE = "http://localhost:8080"  # Local development server
API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q"

# Bloomberg baseline bonds with expected results
BLOOMBERG_BONDS = [
    {
        "ISIN": "US912810TJ79",
        "Name": "US TREASURY N/B, 3%, 15-Aug-2052",
        "Price": 71.66,
        "BBG_Yield": 4.898453,
        "BBG_Duration": 16.357839,
        "BBG_Spread": 0
    },
    {
        "ISIN": "XS2249741674", 
        "Name": "GALAXY PIPELINE, 3.25%, 30-Sep-2040",
        "Price": 77.88,
        "BBG_Yield": 4.836434,
        "BBG_Duration": 14.832630,
        "BBG_Spread": 190
    },
    {
        "ISIN": "US279158AJ82",
        "Name": "ECOPETROL SA, 5.875%, 28-May-2045", 
        "Price": 69.31,
        "BBG_Yield": 9.282266,
        "BBG_Duration": 9.812703,
        "BBG_Spread": 445
    },
    {
        "ISIN": "US195325DX04",
        "Name": "COLOMBIA REP OF, 3.875%, 15-Feb-2061",
        "Price": 52.71,
        "BBG_Yield": 8.190110,
        "BBG_Duration": 10.893064,
        "BBG_Spread": 253
    },
    {
        "ISIN": "US698299BL70",
        "Name": "PANAMA, 3.87%, 23-Jul-2060",
        "Price": 56.60,
        "BBG_Yield": 7.362747,
        "BBG_Duration": 13.488582,
        "BBG_Spread": 253
    },
    {
        "ISIN": "US71654QDF63",
        "Name": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060",
        "Price": 71.42,
        "BBG_Yield": 10.175438,
        "BBG_Duration": 8.878621,
        "BBG_Spread": 529
    },
    {
        "ISIN": "XS1959337749",
        "Name": "QATAR STATE OF, 4.817%, 14-Mar-2049",
        "Price": 89.97,
        "BBG_Yield": 5.638068,
        "BBG_Duration": 18.521951,
        "BBG_Spread": 165
    }
]

def call_api_with_isin(isin, price):
    """Test API call using ISIN"""
    try:
        url = f"{API_BASE}/api/v1/bond/analysis"
        payload = {
            "isin": isin,
            "price": price
        }
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        return {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else {"error": response.text[:500]},
            "method": "ISIN"
        }
        
    except Exception as e:
        return {
            "status_code": "ERROR",
            "response": {"error": str(e)},
            "method": "ISIN"
        }

def call_api_with_description(description, price):
    """Test API call using description"""
    try:
        url = f"{API_BASE}/api/v1/bond/analysis"
        payload = {
            "description": description,
            "price": price
        }
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        return {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else {"error": response.text[:500]},
            "method": "DESCRIPTION"
        }
        
    except Exception as e:
        return {
            "status_code": "ERROR", 
            "response": {"error": str(e)},
            "method": "DESCRIPTION"
        }

def test_both_methods(bond):
    """Test both ISIN and description methods for a bond"""
    print(f"\n{'='*80}")
    print(f"🔍 TESTING: {bond['Name'][:60]}")
    print(f"   ISIN: {bond['ISIN']}")
    print(f"   Price: {bond['Price']}")
    print(f"   Expected Yield: {bond['BBG_Yield']:.6f}%")
    print(f"   Expected Duration: {bond['BBG_Duration']:.6f} years")
    print(f"   Expected Spread: {bond['BBG_Spread']} bps")
    print(f"{'='*80}")
    
    results = {}
    
    # Test 1: ISIN Method
    print(f"\n📊 TEST 1: ISIN METHOD")
    print(f"   Calling API with ISIN: {bond['ISIN']}")
    
    isin_result = call_api_with_isin(bond['ISIN'], bond['Price'])
    results['isin'] = isin_result
    
    print(f"   Status Code: {isin_result['status_code']}")
    
    if isin_result['status_code'] == 200:
        response = isin_result['response']
        if response.get('status') == 'success':
            analytics = response.get('analytics', {})
            bond_info = response.get('bond', {})
            
            print(f"   ✅ SUCCESS!")
            print(f"   Route Used: {bond_info.get('route_used', 'Unknown')}")
            print(f"   API Yield: {analytics.get('ytm', 'N/A'):.6f}%")
            print(f"   API Duration: {analytics.get('duration', 'N/A'):.6f} years")
            print(f"   API Spread: {analytics.get('spread', 'N/A')} bps")
            print(f"   Yield Difference: {abs(analytics.get('ytm', 0) - bond['BBG_Yield']):.6f}%")
            print(f"   Duration Difference: {abs(analytics.get('duration', 0) - bond['BBG_Duration']):.6f} years")
        else:
            print(f"   ❌ API ERROR: {response.get('error', 'Unknown error')}")
            print(f"   Full Response: {json.dumps(response, indent=2)}")
    else:
        print(f"   ❌ HTTP ERROR: {isin_result['status_code']}")
        print(f"   Error Details: {isin_result['response']}")
    
    # Test 2: Description Method
    print(f"\n📋 TEST 2: DESCRIPTION METHOD")
    print(f"   Calling API with Description: {bond['Name'][:50]}...")
    
    desc_result = call_api_with_description(bond['Name'], bond['Price'])
    results['description'] = desc_result
    
    print(f"   Status Code: {desc_result['status_code']}")
    
    if desc_result['status_code'] == 200:
        response = desc_result['response']
        if response.get('status') == 'success':
            analytics = response.get('analytics', {})
            bond_info = response.get('bond', {})
            
            print(f"   ✅ SUCCESS!")
            print(f"   Route Used: {bond_info.get('route_used', 'Unknown')}")
            print(f"   API Yield: {analytics.get('ytm', 'N/A'):.6f}%")
            print(f"   API Duration: {analytics.get('duration', 'N/A'):.6f} years")
            print(f"   API Spread: {analytics.get('spread', 'N/A')} bps")
            print(f"   Yield Difference: {abs(analytics.get('ytm', 0) - bond['BBG_Yield']):.6f}%")
            print(f"   Duration Difference: {abs(analytics.get('duration', 0) - bond['BBG_Duration']):.6f} years")
        else:
            print(f"   ❌ API ERROR: {response.get('error', 'Unknown error')}")
            print(f"   Full Response: {json.dumps(response, indent=2)}")
    else:
        print(f"   ❌ HTTP ERROR: {desc_result['status_code']}")
        print(f"   Error Details: {desc_result['response']}")
    
    # Test 3: Enhanced Hierarchy Test - both in one payload
    print(f"\n🔄 TEST 3: ENHANCED HIERARCHY TEST")
    print(f"   Calling API with BOTH ISIN and Description to test fallback")
    
    try:
        url = f"{API_BASE}/api/v1/bond/analysis"
        payload = {
            "isin": bond['ISIN'],
            "description": bond['Name'],
            "price": bond['Price']
        }
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        results['both'] = {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else {"error": response.text[:500]},
            "method": "BOTH"
        }
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                analytics = result.get('analytics', {})
                bond_info = result.get('bond', {})
                
                print(f"   ✅ SUCCESS!")
                print(f"   Route Used: {bond_info.get('route_used', 'Unknown')}")
                print(f"   Which Input Used: ISIN='{bond_info.get('isin', 'None')}', Description='{bond_info.get('description', 'None')[:30]}...'")
                print(f"   API Yield: {analytics.get('ytm', 'N/A'):.6f}%")
                print(f"   API Duration: {analytics.get('duration', 'N/A'):.6f} years")
                print(f"   API Spread: {analytics.get('spread', 'N/A')} bps")
            else:
                print(f"   ❌ API ERROR: {result.get('error', 'Unknown error')}")
                print(f"   Full Response: {json.dumps(result, indent=2)}")
        else:
            print(f"   ❌ HTTP ERROR: {response.status_code}")
            print(f"   Error Details: {response.text[:500]}")
            
    except Exception as e:
        print(f"   ❌ EXCEPTION: {str(e)}")
        results['both'] = {
            "status_code": "ERROR",
            "response": {"error": str(e)},
            "method": "BOTH"
        }
    
    # Summary for this bond
    print(f"\n📊 BOND SUMMARY:")
    isin_success = results['isin']['status_code'] == 200 and results['isin']['response'].get('status') == 'success'
    desc_success = results['description']['status_code'] == 200 and results['description']['response'].get('status') == 'success'
    both_success = results.get('both', {}).get('status_code') == 200 and results.get('both', {}).get('response', {}).get('status') == 'success'
    
    print(f"   ISIN Method: {'✅ SUCCESS' if isin_success else '❌ FAILED'}")
    print(f"   Description Method: {'✅ SUCCESS' if desc_success else '❌ FAILED'}")
    print(f"   Both Method: {'✅ SUCCESS' if both_success else '❌ FAILED'}")
    
    # Wait between bonds to be respectful to API
    time.sleep(1.5)
    
    return results

def main():
    """Run detailed diagnostic on all bonds"""
    print("🔍 DETAILED BOND DIAGNOSTIC TEST")
    print("="*80)
    print("Testing each bond individually with ISIN, Description, and Both methods")
    print("This will show exactly what's happening with each API call")
    print("="*80)
    
    # Test API health first
    try:
        health_response = requests.get(f"{API_BASE}/health", timeout=10)
        if health_response.status_code == 200:
            health = health_response.json()
            print(f"✅ API Health: {health.get('status', 'unknown')}")
            print(f"   Service: {health.get('service', 'unknown')}")
            print(f"   Version: {health.get('version', 'unknown')}")
        else:
            print(f"⚠️ API Health Check Warning: {health_response.status_code}")
    except Exception as e:
        print(f"❌ API Health Check Failed: {e}")
        return
    
    all_results = {}
    
    # Test each bond individually
    for i, bond in enumerate(BLOOMBERG_BONDS, 1):
        print(f"\n🎯 BOND {i}/{len(BLOOMBERG_BONDS)}")
        all_results[bond['ISIN']] = test_both_methods(bond)
    
    # Final summary
    print(f"\n{'='*80}")
    print("🎯 FINAL DIAGNOSTIC SUMMARY")
    print(f"{'='*80}")
    
    isin_successes = 0
    desc_successes = 0
    both_successes = 0
    
    for isin, results in all_results.items():
        bond_name = next(b['Name'] for b in BLOOMBERG_BONDS if b['ISIN'] == isin)
        
        isin_success = results['isin']['status_code'] == 200 and results['isin']['response'].get('status') == 'success'
        desc_success = results['description']['status_code'] == 200 and results['description']['response'].get('status') == 'success'
        both_success = results.get('both', {}).get('status_code') == 200 and results.get('both', {}).get('response', {}).get('status') == 'success'
        
        if isin_success: isin_successes += 1
        if desc_success: desc_successes += 1
        if both_success: both_successes += 1
        
        print(f"{isin}: {bond_name[:40]}")
        print(f"   ISIN: {'✅' if isin_success else '❌'}, DESC: {'✅' if desc_success else '❌'}, BOTH: {'✅' if both_success else '❌'}")
    
    print(f"\n📊 OVERALL RESULTS:")
    print(f"   ISIN Method Success Rate: {isin_successes}/{len(BLOOMBERG_BONDS)} ({isin_successes/len(BLOOMBERG_BONDS)*100:.1f}%)")
    print(f"   Description Method Success Rate: {desc_successes}/{len(BLOOMBERG_BONDS)} ({desc_successes/len(BLOOMBERG_BONDS)*100:.1f}%)")
    print(f"   Both Method Success Rate: {both_successes}/{len(BLOOMBERG_BONDS)} ({both_successes/len(BLOOMBERG_BONDS)*100:.1f}%)")
    
    print(f"\n🔍 This diagnostic shows exactly what's happening with each bond.")
    print(f"   Look for patterns in the failures and routing decisions above.")

if __name__ == "__main__":
    main()
