#!/usr/bin/env python3
"""
Production vs Local Timing Comparison
====================================

Tests the same 25-bond portfolio against both local and production 
endpoints to compare cloud vs local performance.
"""

import requests
import json
import time
from datetime import datetime

# API Configuration
API_BASE_LOCAL = "http://localhost:8080"
API_BASE_PROD = "https://future-footing-414610.uc.r.appspot.com"
API_KEY = "xtrillion-ga9-key-2024"

# 25-Bond Portfolio Data (same as before)
BOND_PORTFOLIO = [
    {"description": "T 3 15/08/52", "CLOSING PRICE": 71.66, "WEIGHTING": 25.0},
    {"description": "GALAXY PIPELINE, 3.25%, 30-Sep-2040", "CLOSING PRICE": 77.88, "WEIGHTING": 4.0},
    {"description": "ABU DHABI CRUDE, 4.6%, 02-Nov-2047", "CLOSING PRICE": 89.40, "WEIGHTING": 4.0},
    {"description": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039", "CLOSING PRICE": 87.14, "WEIGHTING": 4.0},
    {"description": "EMPRESA METRO, 4.7%, 07-May-2050", "CLOSING PRICE": 80.39, "WEIGHTING": 4.0},
    {"description": "CODELCO INC, 6.15%, 24-Oct-2036", "CLOSING PRICE": 101.63, "WEIGHTING": 4.0},
    {"description": "COMISION FEDERAL, 6.264%, 15-Feb-2052", "CLOSING PRICE": 86.42, "WEIGHTING": 4.0},
    {"description": "COLOMBIA REP OF, 3.875%, 15-Feb-2061", "CLOSING PRICE": 52.71, "WEIGHTING": 4.0},
    {"description": "ECOPETROL SA, 5.875%, 28-May-2045", "CLOSING PRICE": 69.31, "WEIGHTING": 4.0},
    {"description": "EMPRESA NACIONAL, 4.5%, 14-Sep-2047", "CLOSING PRICE": 76.24, "WEIGHTING": 4.0},
    {"description": "GREENSAIF PIPELI, 6.129%, 23-Feb-2038", "CLOSING PRICE": 103.03, "WEIGHTING": 4.0},
    {"description": "STATE OF ISRAEL, 3.8%, 13-May-2060", "CLOSING PRICE": 64.50, "WEIGHTING": 4.0},
    {"description": "SAUDI INT BOND, 4.5%, 26-Oct-2046", "CLOSING PRICE": 82.42, "WEIGHTING": 4.0},
    {"description": "KAZMUNAYGAS NAT, 6.375%, 24-Oct-2048", "CLOSING PRICE": 92.21, "WEIGHTING": 4.0},
    {"description": "UNITED MEXICAN, 5.75%, 12-Oct-2110", "CLOSING PRICE": 78.00, "WEIGHTING": 4.0},
    {"description": "MEXICO CITY ARPT, 5.5%, 31-Jul-2047", "CLOSING PRICE": 82.57, "WEIGHTING": 4.0},
    {"description": "PANAMA, 3.87%, 23-Jul-2060", "CLOSING PRICE": 56.60, "WEIGHTING": 4.0},
    {"description": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060", "CLOSING PRICE": 71.42, "WEIGHTING": 4.0},
    {"description": "PETROLEOS MEXICA, 5.95%, 28-Jan-2031", "CLOSING PRICE": 89.55, "WEIGHTING": 4.0},
    {"description": "GACI FIRST INVST, 5.125%, 14-Feb-2053", "CLOSING PRICE": 85.54, "WEIGHTING": 4.0},
    {"description": "QATAR STATE OF, 4.817%, 14-Mar-2049", "CLOSING PRICE": 89.97, "WEIGHTING": 4.0},
    {"description": "QNB FINANCE LTD, 1.625%, 22-Sep-2025", "CLOSING PRICE": 99.23, "WEIGHTING": 4.0},
    {"description": "QATAR ENERGY, 3.125%, 12-Jul-2041", "CLOSING PRICE": 73.79, "WEIGHTING": 4.0},
    {"description": "SAUDI ELEC GLOBA, 5.06%, 08-Apr-2043", "CLOSING PRICE": 93.29, "WEIGHTING": 4.0},
    {"description": "SITIOS, 5.375%, 04-Apr-2032", "CLOSING PRICE": 97.26, "WEIGHTING": 4.0}
]

def test_endpoint_timing(api_base, endpoint_name):
    """Test portfolio processing timing against specific endpoint"""
    
    print(f"⏱️  Testing {endpoint_name}")
    print(f"🔗 Endpoint: {api_base}")
    print("-" * 60)
    
    # Prepare request
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    payload = {
        "data": BOND_PORTFOLIO,
        "context": "portfolio"
    }
    
    try:
        # Record timing with high precision
        start_time = time.perf_counter()
        
        response = requests.post(
            f"{api_base}/api/v1/portfolio/analysis",
            json=payload,
            headers=headers,
            timeout=60  # Longer timeout for cloud
        )
        
        end_time = time.perf_counter()
        
        # Calculate timing
        total_time_ms = (end_time - start_time) * 1000
        per_bond_ms = total_time_ms / len(BOND_PORTFOLIO)
        bonds_per_sec = len(BOND_PORTFOLIO) / (total_time_ms / 1000)
        
        print(f"✅ Status: {response.status_code}")
        print(f"⏱️  Total Time: {total_time_ms:,.1f} ms ({total_time_ms/1000:.2f} seconds)")
        print(f"📊 Per Bond: {per_bond_ms:.1f} ms")
        print(f"🚀 Rate: {bonds_per_sec:.1f} bonds/second")
        
        # Performance assessment
        if total_time_ms < 1000:
            perf_rating = "🎯 EXCELLENT"
        elif total_time_ms < 2000:
            perf_rating = "✅ GOOD"
        elif total_time_ms < 5000:
            perf_rating = "⚠️  FAIR"
        else:
            perf_rating = "❌ POOR"
            
        print(f"📈 Performance: {perf_rating}")
        
        # Check success rate if response is valid
        if response.status_code == 200:
            try:
                data = response.json()
                if 'portfolio_metrics' in data:
                    metrics = data['portfolio_metrics']
                    success_rate = metrics.get('success_rate', 0)
                    total_bonds = metrics.get('total_bonds', 0)
                    print(f"✅ Success: {total_bonds}/{len(BOND_PORTFOLIO)} bonds ({success_rate}%)")
                else:
                    print("⚠️  No portfolio metrics in response")
            except json.JSONDecodeError:
                print("❌ Invalid JSON response")
        else:
            print(f"❌ Error: {response.status_code}")
            if response.text:
                print(f"   Response: {response.text[:200]}...")
        
        return {
            'endpoint': endpoint_name,
            'success': response.status_code == 200,
            'time_ms': total_time_ms,
            'bonds_per_sec': bonds_per_sec,
            'per_bond_ms': per_bond_ms
        }
        
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT - Request took longer than 60 seconds")
        return {'endpoint': endpoint_name, 'success': False, 'time_ms': None, 'error': 'timeout'}
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ CONNECTION ERROR: {e}")
        return {'endpoint': endpoint_name, 'success': False, 'time_ms': None, 'error': 'connection'}
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {'endpoint': endpoint_name, 'success': False, 'time_ms': None, 'error': str(e)}

def main():
    print("🌐 Production vs Local Performance Comparison")
    print("Testing 25-bond portfolio against both endpoints")
    print("=" * 70)
    print(f"🕐 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    
    # Test Local first
    print("🏠 LOCAL ENDPOINT TEST")
    print("=" * 30)
    local_result = test_endpoint_timing(API_BASE_LOCAL, "Local Development")
    results.append(local_result)
    print()
    
    # Test Production
    print("☁️  PRODUCTION ENDPOINT TEST")
    print("=" * 30)
    prod_result = test_endpoint_timing(API_BASE_PROD, "Google Cloud Production")
    results.append(prod_result)
    print()
    
    # Comparison Summary
    print("📊 COMPARISON SUMMARY")
    print("=" * 50)
    
    for result in results:
        if result['success'] and result['time_ms']:
            print(f"{result['endpoint']:.<25} {result['time_ms']:>8.1f} ms ({result['bonds_per_sec']:>6.1f} bonds/sec)")
        else:
            error = result.get('error', 'failed')
            print(f"{result['endpoint']:.<25} {'FAILED':>8} ({error})")
    
    print()
    
    # Performance difference analysis
    if all(r['success'] and r['time_ms'] for r in results):
        local_time = next(r['time_ms'] for r in results if 'Local' in r['endpoint'])
        prod_time = next(r['time_ms'] for r in results if 'Production' in r['endpoint'])
        
        if prod_time > local_time:
            diff = prod_time - local_time
            multiplier = prod_time / local_time
            print(f"⚡ Network Overhead: +{diff:.1f} ms ({multiplier:.1f}x slower)")
        else:
            diff = local_time - prod_time
            multiplier = local_time / prod_time
            print(f"🚀 Cloud Optimization: -{diff:.1f} ms ({multiplier:.1f}x faster)")
        
        print()
        print("🎯 CONCLUSION:")
        print("-" * 20)
        
        if prod_time < 1000:
            print("✅ Production performance is EXCELLENT for contract negotiations")
            print(f"   Cloud processing: {prod_time:.0f}ms for 25 bonds")
            print(f"   Suitable for real-time trading systems")
        elif prod_time < 2000:
            print("✅ Production performance is GOOD for most use cases")
            print(f"   Cloud processing: {prod_time:.0f}ms for 25 bonds")
        else:
            print("⚠️  Production performance may need optimization")
            print(f"   Cloud processing: {prod_time:.0f}ms for 25 bonds")
    
    print()
    print("📝 Note: All timings include network latency for production endpoint")

if __name__ == "__main__":
    main()