#!/usr/bin/env python3
"""
Google Analysis10 API Integration Test
====================================

Quick test to verify Universal Parser integration is working correctly
"""

import requests
import json
import sys

def test_api_integration():
    """Test the enhanced API with Universal Parser integration"""
    
    base_url = "http://localhost:8080"
    
    print("🧪 Testing Google Analysis10 API Integration")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed")
            print(f"   Universal Parser Available: {health_data.get('universal_parser', {}).get('available', 'Unknown')}")
            print(f"   Parser Status: {health_data.get('universal_parser', {}).get('status', 'Unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ API server not running - start with: python google_analysis10_api.py")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Single bond calculation (ISIN)
    print("\n2. Testing Single Bond Calculation (ISIN)...")
    test_data = {
        "bond_input": "US912810TJ79",  # US Treasury ISIN
        "price": 71.66
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/bond/parse-and-calculate",
            json=test_data,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": "gax10_demo_3j5h8m9k2p6r4t7w1q"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ ISIN calculation successful")
            if 'analytics' in result:
                analytics = result['analytics']
                print(f"   Yield: {analytics.get('yield', 'N/A')}")
                print(f"   Duration: {analytics.get('duration', 'N/A')}")
            if 'processing' in result:
                processing = result['processing']
                print(f"   Universal Parser Available: {processing.get('universal_parser_available', 'Unknown')}")
                print(f"   Parsing Method: {processing.get('parsing_method', 'Unknown')}")
        else:
            print(f"❌ ISIN calculation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ ISIN calculation error: {e}")
    
    # Test 3: Single bond calculation (Description)
    print("\n3. Testing Single Bond Calculation (Description)...")
    test_data = {
        "description": "T 2 1/2 07/31/27",  # Treasury description
        "price": 99.5
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/bond/parse-and-calculate",
            json=test_data,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": "gax10_demo_3j5h8m9k2p6r4t7w1q"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Description calculation successful")
            if 'analytics' in result:
                analytics = result['analytics']
                print(f"   Yield: {analytics.get('yield', 'N/A')}")
                print(f"   Duration: {analytics.get('duration', 'N/A')}")
        else:
            print(f"❌ Description calculation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Description calculation error: {e}")
    
    # Test 4: Portfolio analysis
    print("\n4. Testing Portfolio Analysis...")
    portfolio_data = {
        "data": [
            {
                "BOND_CD": "US912810TJ79",
                "CLOSING PRICE": 71.66,
                "WEIGHTING": 50.0
            },
            {
                "description": "T 2 1/2 07/31/27",
                "CLOSING PRICE": 99.5,
                "WEIGHTING": 50.0
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/portfolio/analyze",
            json=portfolio_data,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": "gax10_demo_3j5h8m9k2p6r4t7w1q"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Portfolio analysis successful")
            if 'portfolio' in result:
                portfolio = result['portfolio']
                if 'summary' in portfolio:
                    summary = portfolio['summary']
                    print(f"   Total Bonds: {summary.get('total_bonds', 'N/A')}")
                    print(f"   Success Rate: {summary.get('successful_analysis', 'N/A')}")
                if 'metadata' in portfolio:
                    metadata = portfolio['metadata']
                    print(f"   Universal Parser Available: {metadata.get('universal_parser_available', 'Unknown')}")
        else:
            print(f"❌ Portfolio analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Portfolio analysis error: {e}")
    
    # Test 5: Version info
    print("\n5. Testing Version Info...")
    try:
        response = requests.get(f"{base_url}/api/v1/version", timeout=10)
        if response.status_code == 200:
            version_data = response.json()
            print(f"✅ Version info retrieved")
            print(f"   Service: {version_data.get('service', 'Unknown')}")
            print(f"   Version: {version_data.get('version', 'Unknown')}")
            print(f"   API Version: {version_data.get('api_version', 'Unknown')}")
            print(f"   Analytics Engine: {version_data.get('analytics_engine', 'Unknown')}")
        else:
            print(f"❌ Version info failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Version info error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Integration test complete!")
    print("\n💡 To start the API server:")
    print("   cd /Users/andyseaman/Notebooks/json_receiver_project/google_analysis10")
    print("   python google_analysis10_api.py")
    print("\n📚 Interactive API guide available at: http://localhost:8080/")
    
    return True

if __name__ == "__main__":
    test_api_integration()
