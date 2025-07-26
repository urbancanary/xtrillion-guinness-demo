#!/usr/bin/env python3
"""
Test Script for Refactored API using calculate_bond_master
=========================================================

Tests the newly refactored API that uses calculate_bond_master directly
instead of process_bonds_with_weightings.

Expected improvements:
- ✅ Cleaner API code (no DataFrame manipulation)
- ✅ Better performance (direct function calls)
- ✅ Clearer error handling
- ✅ Route transparency (ISIN vs parse hierarchy)
"""

import requests
import json
import time

def test_api_refactoring():
    """Test the refactored API endpoints"""
    
    print("🧪 Testing Refactored API - calculate_bond_master Integration")
    print("=" * 65)
    
    base_url = "http://localhost:8080"
    
    # Test cases covering both ISIN and parse hierarchy routes
    test_cases = [
        {
            "name": "Route 1: ISIN Hierarchy (US Treasury)",
            "data": {
                "isin": "US912810TJ79",
                "description": "US TREASURY N/B, 3%, 15-Aug-2052",
                "price": 71.66
            }
        },
        {
            "name": "Route 2: Parse Hierarchy (Treasury shorthand)",
            "data": {
                "description": "T 3 15/08/52",
                "price": 71.66
            }
        },
        {
            "name": "Route 1: ISIN Hierarchy (Corporate Bond)",
            "data": {
                "isin": "XS2249741674",
                "description": "GALAXY PIPELINE, 3.25%, 30-Sep-2040",
                "price": 77.88
            }
        },
        {
            "name": "Route 2: Parse Hierarchy (Complex Description)",
            "data": {
                "description": "PANAMA, 3.87%, 23-Jul-2060",
                "price": 56.60
            }
        }
    ]
    
    success_count = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}/{total_tests}: {test_case['name']}")
        print("-" * 50)
        
        try:
            # Test business response (default)
            print("📊 Testing business response...")
            response = requests.post(
                f"{base_url}/api/v1/bond/parse-and-calculate",
                json=test_case['data'],
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": "gax10_test_9r4t7w2k5m8p1z6x3v"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Business response: SUCCESS")
                
                # Check for key fields
                analytics = result.get('analytics', {})
                processing = result.get('processing', {})
                
                print(f"   📈 Yield: {analytics.get('yield', 'N/A')}")
                print(f"   ⏱️  Duration: {analytics.get('duration', 'N/A')}")
                print(f"   🛤️  Route: {processing.get('route_used', 'N/A')}")
                
                # Test technical response
                print("🔧 Testing technical response...")
                tech_response = requests.post(
                    f"{base_url}/api/v1/bond/parse-and-calculate?technical=true",
                    json=test_case['data'],
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": "gax10_test_9r4t7w2k5m8p1z6x3v"
                    },
                    timeout=30
                )
                
                if tech_response.status_code == 200:
                    tech_result = tech_response.json()
                    print("✅ Technical response: SUCCESS")
                    
                    metadata = tech_result.get('metadata', {})
                    print(f"   🔧 Engine: {metadata.get('calculation_engine', 'N/A')}")
                    print(f"   🛤️  Route: {metadata.get('route_used', 'N/A')}")
                    print(f"   📊 Method: {metadata.get('calculation_method', 'N/A')}")
                    
                    success_count += 1
                else:
                    print(f"❌ Technical response failed: {tech_response.status_code}")
                    print(f"   Error: {tech_response.text}")
            else:
                print(f"❌ Business response failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - API server not running?")
            print("💡 Start with: python google_analysis10_api.py")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print(f"\n📊 Test Results Summary")
    print("=" * 30)
    print(f"✅ Successful tests: {success_count}/{total_tests}")
    print(f"📈 Success rate: {success_count/total_tests*100:.1f}%")
    
    if success_count == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ API refactoring successful")
        print("✅ calculate_bond_master integration working")
        print("✅ Both ISIN and parse hierarchy routes functional")
    else:
        print(f"\n⚠️  {total_tests - success_count} tests failed")
        print("🔧 Check API server and database connections")

def test_version_endpoint():
    """Test the version endpoint to verify new capabilities"""
    
    print("\n🔍 Testing Version Endpoint")
    print("-" * 30)
    
    try:
        response = requests.get(
            "http://localhost:8080/api/v1/version",
            timeout=15
        )
        
        if response.status_code == 200:
            version_info = response.json()
            print("✅ Version endpoint: SUCCESS")
            
            engine = version_info.get('analytics_engine', '')
            if 'calculate_bond_master' in engine:
                print("✅ Analytics engine updated correctly")
                print(f"   🔧 Engine: {engine}")
            else:
                print("⚠️  Analytics engine not updated")
            
            capabilities = version_info.get('capabilities', [])
            bond_master_cap = any('calculate_bond_master' in cap for cap in capabilities)
            if bond_master_cap:
                print("✅ Capabilities include calculate_bond_master")
            else:
                print("⚠️  Capabilities not updated")
                
        else:
            print(f"❌ Version endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Version test failed: {e}")

if __name__ == "__main__":
    test_api_refactoring()
    test_version_endpoint()
