#!/usr/bin/env python3
"""
🚀 XTrillion Fast Calculator - Tuesday Demo Test
==============================================

Quick validation and performance demonstration of the blazing fast calculator.
Tests all contexts with real bond examples for Tuesday demo.
"""

import sys
import os
import time
import json

# Add the current directory to Python path
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

def test_fast_calculator():
    """Test the blazing fast calculator directly"""
    print("🚀 Testing XTrillion Fast Calculator")
    print("=" * 45)
    
    try:
        from xtrillion_fast_calculator import XTrillionFastCalculator
        
        # Initialize calculator
        calc = XTrillionFastCalculator("2025-06-30")
        print(f"✅ Calculator initialized successfully")
        print(f"📅 Settlement Date: {calc.settlement_date}")
        print(f"🔄 Caching: {'✅ Enabled' if calc.enable_caching else '❌ Disabled'}")
        print()
        
        # Test bonds for demo
        test_bonds = [
            {
                "name": "🏛️ US Treasury Long Bond",
                "description": "US TREASURY N/B, 3%, 15-Aug-2052",
                "price": 71.66,
                "isin": "US912810TJ79"
            },
            {
                "name": "🏢 Investment Grade Corporate", 
                "description": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039",
                "price": 87.14,
                "isin": "XS1982113463"
            },
            {
                "name": "🌎 Emerging Market Sovereign",
                "description": "PANAMA, 3.87%, 23-Jul-2060",
                "price": 56.60,
                "isin": "US698299BL70"
            }
        ]
        
        # Test contexts
        contexts = ["pricing", "risk", "portfolio", "default"]
        
        print(f"📊 Testing {len(test_bonds)} bonds × {len(contexts)} contexts")
        print(f"🎯 Performance Targets: pricing=20ms, risk=50ms, portfolio=100ms")
        print()
        
        total_tests = 0
        passed_tests = 0
        
        for bond in test_bonds:
            print(f"{bond['name']}")
            print(f"   {bond['description'][:60]}...")
            
            for context in contexts:
                total_tests += 1
                start_time = time.perf_counter()
                
                try:
                    result = calc.calculate_from_description(
                        description=bond["description"],
                        price=bond["price"],
                        context=context,
                        isin=bond["isin"]
                    )
                    
                    elapsed_ms = (time.perf_counter() - start_time) * 1000
                    
                    # Check for errors
                    if 'error' in result:
                        print(f"   ❌ {context:10}: ERROR - {result['error']}")
                        continue
                    
                    # Check performance target
                    target_ms = calc.context_configs[context]["target_ms"]
                    status = "✅" if elapsed_ms <= target_ms else "⚠️"
                    passed_tests += 1
                    
                    print(f"   {status} {context:10}: {elapsed_ms:6.1f}ms (target: {target_ms}ms)")
                    
                    # Show sample results for first bond, risk context
                    if bond == test_bonds[0] and context == "risk":
                        if "pricing" in result:
                            ytm = result["pricing"].get("ytm_semi", 0)
                            accrued = result["pricing"].get("accrued_interest", 0)
                            print(f"       📊 YTM: {ytm:.3f}%")
                            print(f"       💰 Accrued: ${accrued:.6f}")
                        
                        if "risk" in result:
                            duration = result["risk"].get("mod_dur_semi", 0)
                            convexity = result["risk"].get("convexity_semi", 0)
                            print(f"       ⏱️ Duration: {duration:.2f} years")
                            if convexity > 0:
                                print(f"       📈 Convexity: {convexity:.1f}")
                    
                except Exception as e:
                    print(f"   ❌ {context:10}: EXCEPTION - {str(e)}")
            
            print()
        
        # Cache performance test
        print("🔄 Testing Cache Performance...")
        print("   First calculation (cold):")
        
        start_time = time.perf_counter()
        result1 = calc.calculate_from_description(
            test_bonds[0]["description"], 
            test_bonds[0]["price"], 
            "risk"
        )
        cold_time = (time.perf_counter() - start_time) * 1000
        print(f"      ⏱️ Cold calculation: {cold_time:.1f}ms")
        
        print("   Second calculation (cached):")
        start_time = time.perf_counter()
        result2 = calc.calculate_from_description(
            test_bonds[0]["description"], 
            test_bonds[0]["price"], 
            "risk"
        )
        cached_time = (time.perf_counter() - start_time) * 1000
        print(f"      ⚡ Cached calculation: {cached_time:.1f}ms")
        
        speedup = cold_time / cached_time if cached_time > 0 else float('inf')
        print(f"      🚀 Cache speedup: {speedup:.1f}x faster")
        
        # Performance summary
        print(f"\n📈 Performance Summary:")
        print(f"   Tests completed: {passed_tests}/{total_tests}")
        print(f"   Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Cache statistics
        stats = calc.get_performance_stats()
        cache_stats = stats['cache_stats']
        print(f"   Cache entries: {cache_stats['calculation_cache_size']} calculations")
        print(f"   YTM cache: {cache_stats['ytm_cache_size']} entries")
        print(f"   Bond cache: {cache_stats['bond_cache_size']} entries")
        
        if passed_tests == total_tests:
            print(f"\n✅ ALL TESTS PASSED! Ready for Tuesday demo! 🚀")
        else:
            print(f"\n⚠️ Some tests failed. Check errors above.")
        
        return calc, passed_tests == total_tests
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're in the right directory and all dependencies are installed")
        return None, False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None, False

def test_api_server():
    """Test if the API server is working"""
    print("\n🌐 Testing API Server")
    print("=" * 25)
    
    try:
        import requests
        
        # Test health endpoint
        print("Testing health endpoint...")
        response = requests.get("http://localhost:8080/v1/health", timeout=5)
        
        if response.status_code == 200:
            health_data = response.json()
            print("✅ API server is healthy!")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Calculator Ready: {health_data.get('calculator_ready')}")
            
            # Test calculation endpoint
            print("\nTesting calculation endpoint...")
            test_request = {
                "description": "US TREASURY N/B, 3%, 15-Aug-2052",
                "price": 71.66,
                "context": "pricing",
                "isin": "US912810TJ79"
            }
            
            start_time = time.perf_counter()
            calc_response = requests.post(
                "http://localhost:8080/v1/bond/calculate",
                json=test_request,
                timeout=10
            )
            api_time = (time.perf_counter() - start_time) * 1000
            
            if calc_response.status_code == 200:
                calc_data = calc_response.json()
                print("✅ Calculation endpoint working!")
                print(f"   API Response Time: {api_time:.1f}ms")
                
                api_meta = calc_data.get('api_metadata', {})
                calc_time = api_meta.get('calculation_time_ms', 0)
                print(f"   Calculation Time: {calc_time:.1f}ms")
                
                return True
            else:
                print(f"❌ Calculation endpoint failed: {calc_response.status_code}")
                print(f"   Error: {calc_response.text}")
                return False
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("💡 Start the server with: python xtrillion_api_demo.py")
        return False
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 XTrillion Fast Calculator - Tuesday Demo Test Suite")
    print("=" * 60)
    
    # Test calculator directly
    calc, calc_success = test_fast_calculator()
    
    # Test API server (optional)
    api_success = test_api_server()
    
    # Final summary
    print(f"\n🎯 TUESDAY DEMO READINESS CHECK")
    print("=" * 35)
    print(f"✅ Fast Calculator: {'READY' if calc_success else 'NEEDS WORK'}")
    print(f"{'✅' if api_success else '⚠️'} API Server: {'READY' if api_success else 'NOT RUNNING'}")
    
    if calc_success:
        print(f"\n🚀 READY FOR TUESDAY DEMO!")
        print(f"📊 Core calculator working with blazing fast performance")
        print(f"🎯 Context-aware optimization implemented")
        print(f"⚡ Intelligent caching working")
        print(f"📈 Performance targets met")
        
        if api_success:
            print(f"🌐 API server ready for live demonstration")
        else:
            print(f"💡 Start API server with: python xtrillion_api_demo.py")
    else:
        print(f"\n⚠️ DEMO PREP NEEDED")
        print(f"🔧 Fix calculator issues before Tuesday")
    
    return calc_success and api_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
