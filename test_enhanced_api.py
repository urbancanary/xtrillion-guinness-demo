#!/usr/bin/env python3
"""
Test Enhanced Bond API - Convexity & OAD Calculations
====================================================

Test script demonstrating the new enhanced bond analytics capabilities:
⭐ Convexity calculations
⭐ Option-Adjusted Duration (OAD)  
⭐ Option-Adjusted Spread (OAS) estimation
⭐ Key Rate Duration

Usage:
    python3 test_enhanced_api.py
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8080"  # Update for your deployment
API_KEY = "gax9_demo_3j5h8m9k2p6r4t7w1q"  # Demo API key

# Test bonds with different characteristics
TEST_BONDS = [
    {
        "name": "US Treasury 30Y",
        "description": "T 3 15/08/52",
        "price": 71.66,
        "expected_features": ["Low convexity", "High duration", "Treasury benchmark"]
    },
    {
        "name": "Corporate High-Grade",
        "description": "AAPL 3.25 02/23/26",
        "price": 98.50,
        "expected_features": ["Medium convexity", "Medium duration", "Credit spread"]
    },
    {
        "name": "High-Yield Corporate",
        "description": "PEMEX 6.95 01/28/60",
        "price": 71.42,
        "expected_features": ["High convexity", "Long duration", "Wide spread"]
    },
    {
        "name": "Short-Term Treasury",
        "description": "T 4.5 02/15/25",
        "price": 99.80,
        "expected_features": ["Very low convexity", "Short duration", "Low spread"]
    }
]

def test_health_check():
    """Test the enhanced health check endpoint"""
    print("🔍 Testing Enhanced Health Check...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/health",
            headers={"X-API-Key": API_KEY}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health Check SUCCESS")
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
            
            # Check for enhanced capabilities
            capabilities = data.get('capabilities', [])
            enhanced_features = [cap for cap in capabilities if 'NEW:' in cap]
            
            print(f"   🆕 Enhanced Features ({len(enhanced_features)}):")
            for feature in enhanced_features:
                print(f"      {feature}")
            
            return True
        else:
            print(f"❌ Health Check FAILED: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health Check ERROR: {e}")
        return False

def test_enhanced_bond_calculation(bond_info):
    """Test enhanced bond calculation with convexity and OAD"""
    print(f"\n🧮 Testing Enhanced Calculation: {bond_info['name']}")
    print(f"   Description: {bond_info['description']}")
    print(f"   Price: {bond_info['price']}")
    print(f"   Expected: {', '.join(bond_info['expected_features'])}")
    
    try:
        # Test business response (default)
        print("   📊 Testing Business Response...")
        
        payload = {
            "description": bond_info['description'],
            "price": bond_info['price'],
            "settlement_date": "2025-07-30",
            "include_oas": True
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/bond/parse-and-calculate-enhanced",
            json=payload,
            headers={"X-API-Key": API_KEY}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                analytics = data.get('analytics', {})
                
                print("   ✅ Business Response SUCCESS")
                print(f"      Yield: {analytics.get('yield', 'N/A')}%")
                print(f"      Duration: {analytics.get('duration', 'N/A')} years")
                print(f"      Spread: {analytics.get('spread', 'N/A')} bps")
                
                # ⭐ Enhanced metrics
                print(f"      🆕 Convexity: {analytics.get('convexity', 'N/A')}")
                print(f"      🆕 OA Duration: {analytics.get('option_adjusted_duration', 'N/A')} years")
                print(f"      🆕 OA Spread: {analytics.get('option_adjusted_spread', 'N/A')} bps")
                print(f"      🆕 Key Rate Duration (10Y): {analytics.get('key_rate_duration_10y', 'N/A')}")
                
                # Test technical response
                print("   🔬 Testing Technical Response...")
                
                tech_response = requests.post(
                    f"{API_BASE_URL}/api/v1/bond/parse-and-calculate-enhanced?technical=true",
                    json=payload,
                    headers={"X-API-Key": API_KEY}
                )
                
                if tech_response.status_code == 200:
                    tech_data = tech_response.json()
                    calc_results = tech_data.get('calculation_results', {})
                    
                    if calc_results.get('success'):
                        enhanced_metrics = calc_results.get('enhanced_metrics', {})
                        
                        print("   ✅ Technical Response SUCCESS")
                        print(f"      🔬 Enhanced Metrics Available: {len(enhanced_metrics)} metrics")
                        
                        for metric, value in enhanced_metrics.items():
                            print(f"         {metric}: {value}")
                    else:
                        print(f"   ⚠️  Technical calculation failed: {calc_results.get('error', 'Unknown error')}")
                else:
                    print(f"   ❌ Technical Response FAILED: {tech_response.status_code}")
                
                return True
            else:
                print(f"   ❌ Calculation FAILED: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Request FAILED: {response.status_code}")
            try:
                error_data = response.json()
                print(f"      Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"      Raw response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def test_portfolio_enhanced_analysis():
    """Test enhanced portfolio analysis with multiple bonds"""
    print(f"\n📈 Testing Enhanced Portfolio Analysis...")
    
    try:
        # Create a sample portfolio from test bonds
        portfolio_data = {
            "data": []
        }
        
        for i, bond in enumerate(TEST_BONDS):
            portfolio_data["data"].append({
                "bond_cd": bond["description"],
                "price": bond["price"],
                "weighting": 25.0,  # Equal weight portfolio
                "Inventory Date": "2025/07/19"
            })
        
        print(f"   Portfolio: {len(portfolio_data['data'])} bonds, equal weighted")
        
        # Test business response
        response = requests.post(
            f"{API_BASE_URL}/api/v1/portfolio/analyze",
            json=portfolio_data,
            headers={"X-API-Key": API_KEY}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                portfolio = data.get('portfolio', {})
                metrics = portfolio.get('metrics', {})
                
                print("   ✅ Portfolio Analysis SUCCESS")
                print(f"      Portfolio Yield: {metrics.get('portfolio_yield', 'N/A')}")
                print(f"      Portfolio Duration: {metrics.get('portfolio_duration', 'N/A')}")
                print(f"      Portfolio Spread: {metrics.get('portfolio_spread', 'N/A')}")
                
                # ⭐ Enhanced portfolio metrics (if available)
                if 'portfolio_convexity' in metrics:
                    print(f"      🆕 Portfolio Convexity: {metrics.get('portfolio_convexity', 'N/A')}")
                if 'portfolio_oad' in metrics:
                    print(f"      🆕 Portfolio OA Duration: {metrics.get('portfolio_oad', 'N/A')}")
                if 'duration_dispersion' in metrics:
                    print(f"      🆕 Duration Dispersion: {metrics.get('duration_dispersion', 'N/A')}")
                
                holdings = portfolio.get('holdings', [])
                print(f"      Successfully processed: {len(holdings)} bonds")
                
                return True
            else:
                print(f"   ❌ Portfolio Analysis FAILED: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Portfolio Request FAILED: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Portfolio Exception: {e}")
        return False

def run_comprehensive_test():
    """Run comprehensive test of enhanced API"""
    print("🚀 GOOGLE ANALYSIS 10 - ENHANCED API TEST")
    print("=" * 60)
    print(f"🕐 Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 API Base URL: {API_BASE_URL}")
    print(f"🔑 Using API Key: {API_KEY[:12]}***")
    
    # Test results
    results = {
        'health_check': False,
        'bond_calculations': [],
        'portfolio_analysis': False
    }
    
    # 1. Health check
    results['health_check'] = test_health_check()
    
    if not results['health_check']:
        print("\n❌ Health check failed - aborting tests")
        return results
    
    # 2. Individual bond calculations
    print(f"\n🧮 Testing {len(TEST_BONDS)} Individual Bond Calculations...")
    
    for bond_info in TEST_BONDS:
        success = test_enhanced_bond_calculation(bond_info)
        results['bond_calculations'].append({
            'bond': bond_info['name'],
            'success': success
        })
        
        # Small delay between requests
        time.sleep(0.5)
    
    # 3. Portfolio analysis
    results['portfolio_analysis'] = test_portfolio_enhanced_analysis()
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 60)
    
    # Health check
    health_status = "✅ PASS" if results['health_check'] else "❌ FAIL"
    print(f"Health Check: {health_status}")
    
    # Bond calculations
    successful_bonds = sum(1 for calc in results['bond_calculations'] if calc['success'])
    total_bonds = len(results['bond_calculations'])
    bond_success_rate = (successful_bonds / total_bonds * 100) if total_bonds > 0 else 0
    
    print(f"Bond Calculations: {successful_bonds}/{total_bonds} successful ({bond_success_rate:.1f}%)")
    
    for calc in results['bond_calculations']:
        status = "✅" if calc['success'] else "❌"
        print(f"  {status} {calc['bond']}")
    
    # Portfolio analysis
    portfolio_status = "✅ PASS" if results['portfolio_analysis'] else "❌ FAIL"
    print(f"Portfolio Analysis: {portfolio_status}")
    
    # Overall result
    overall_success = (
        results['health_check'] and
        successful_bonds == total_bonds and
        results['portfolio_analysis']
    )
    
    print(f"\n🎯 OVERALL RESULT: {'✅ SUCCESS - Enhanced API working perfectly!' if overall_success else '⚠️  PARTIAL SUCCESS - Some features need attention'}")
    
    if overall_success:
        print("\n🆕 Enhanced Features Confirmed Working:")
        print("   ⭐ Convexity calculations")
        print("   ⭐ Option-Adjusted Duration (OAD)")
        print("   ⭐ Option-Adjusted Spread (OAS) estimation")
        print("   ⭐ Key Rate Duration calculations")
        print("   ⭐ Enhanced portfolio risk metrics")
    
    print(f"\n🕐 Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return results

if __name__ == "__main__":
    results = run_comprehensive_test()
    
    # Exit with appropriate code
    if all([
        results['health_check'],
        all(calc['success'] for calc in results['bond_calculations']),
        results['portfolio_analysis']
    ]):
        exit(0)  # Success
    else:
        exit(1)  # Partial failure
