#!/usr/bin/env python3
"""
25-Bond Portfolio Timing Test
=============================

This script measures the actual response time for processing 
a 25-bond portfolio to verify our documentation claims.
"""

import requests
import json
import time
from datetime import datetime

# API Configuration - Test both local and production
API_BASE_LOCAL = "http://localhost:8080"
API_BASE_PROD = "https://future-footing-414610.uc.r.appspot.com"
API_KEY = "xtrillion-ga9-key-2024"

# 25-Bond Portfolio Data (from comprehensive test)
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

def test_portfolio_timing():
    """Test portfolio processing timing with 25 bonds"""
    
    print("⏱️  25-Bond Portfolio Timing Test")
    print("=" * 60)
    print(f"🔗 API Base: {API_BASE}")
    print(f"📊 Portfolio Size: {len(BOND_PORTFOLIO)} bonds")
    print(f"🕐 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Prepare the request
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    payload = {
        "data": BOND_PORTFOLIO,
        "context": "portfolio"
    }
    
    print("🚀 Starting portfolio analysis...")
    
    # Record start time with high precision
    start_time = time.perf_counter()
    
    try:
        # Make the API request
        response = requests.post(
            f"{API_BASE}/api/v1/portfolio/analysis",
            json=payload,
            headers=headers,
            timeout=30  # 30 second timeout
        )
        
        # Record end time
        end_time = time.perf_counter()
        
        # Calculate timing
        total_time_ms = (end_time - start_time) * 1000
        per_bond_ms = total_time_ms / len(BOND_PORTFOLIO)
        
        print(f"✅ Request completed!")
        print(f"📊 Status Code: {response.status_code}")
        print()
        
        # Display timing results
        print("⏱️  TIMING RESULTS:")
        print("=" * 40)
        print(f"   Total Time:     {total_time_ms:,.1f} ms")
        print(f"   Total Time:     {total_time_ms/1000:,.2f} seconds")
        print(f"   Per Bond:       {per_bond_ms:,.1f} ms")
        print(f"   Bonds/Second:   {len(BOND_PORTFOLIO)/(total_time_ms/1000):,.1f}")
        print()
        
        # Performance assessment
        if total_time_ms < 1000:
            print("🎯 PERFORMANCE: EXCELLENT - Under 1 second!")
        elif total_time_ms < 2000:
            print("✅ PERFORMANCE: GOOD - Under 2 seconds")
        elif total_time_ms < 5000:
            print("⚠️  PERFORMANCE: FAIR - Under 5 seconds")
        else:
            print("❌ PERFORMANCE: POOR - Over 5 seconds")
        
        print()
        
        # Analyze response if successful
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Check portfolio metrics
                if 'portfolio_metrics' in data:
                    metrics = data['portfolio_metrics']
                    total_bonds = metrics.get('total_bonds', 0)
                    success_rate = metrics.get('success_rate', 0)
                    portfolio_yield = metrics.get('portfolio_yield', 0)
                    portfolio_duration = metrics.get('portfolio_duration', 0)
                    
                    print("📈 PORTFOLIO RESULTS:")
                    print("=" * 40)
                    print(f"   Processed Bonds: {total_bonds}/{len(BOND_PORTFOLIO)}")
                    print(f"   Success Rate:    {success_rate}%")
                    print(f"   Portfolio Yield: {portfolio_yield}%")
                    print(f"   Portfolio Duration: {portfolio_duration} years")
                    print()
                
                # Check individual bond results
                if 'bonds' in data:
                    bonds = data['bonds']
                    successful = sum(1 for bond in bonds if bond.get('success', False))
                    failed = len(bonds) - successful
                    
                    print("🔍 INDIVIDUAL BOND ANALYSIS:")
                    print("=" * 40)
                    print(f"   Successful: {successful}")
                    print(f"   Failed:     {failed}")
                    
                    if failed > 0:
                        print(f"   Failed bonds:")
                        for i, bond in enumerate(bonds):
                            if not bond.get('success', False):
                                name = BOND_PORTFOLIO[i].get('description', f'Bond {i+1}')
                                error = bond.get('error', 'Unknown error')
                                print(f"     - {name[:50]}... | {error}")
                
            except json.JSONDecodeError:
                print("❌ Response is not valid JSON")
                print(f"Response text (first 500 chars): {response.text[:500]}")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
        
        return total_time_ms
        
    except requests.exceptions.Timeout:
        end_time = time.perf_counter()
        timeout_ms = (end_time - start_time) * 1000
        print(f"⏰ REQUEST TIMEOUT after {timeout_ms:,.1f} ms")
        print("❌ Portfolio processing took longer than 30 seconds")
        return None
        
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR")
        print("   Make sure the API server is running:")
        print("   python3 google_analysis10_api.py")
        return None
        
    except Exception as e:
        end_time = time.perf_counter()
        error_time_ms = (end_time - start_time) * 1000
        print(f"❌ UNEXPECTED ERROR after {error_time_ms:,.1f} ms")
        print(f"   Error: {e}")
        return None

def test_warmup():
    """Run a small warmup request to eliminate cold start effects"""
    
    print("🔥 Running warmup request...")
    
    headers = {
        "Content-Type": "application/json", 
        "X-API-Key": API_KEY
    }
    
    # Single bond warmup
    warmup_payload = {
        "description": "T 3 15/08/52",
        "price": 71.66
    }
    
    try:
        start_time = time.perf_counter()
        response = requests.post(
            f"{API_BASE}/api/v1/bond/analysis",
            json=warmup_payload,
            headers=headers,
            timeout=10
        )
        end_time = time.perf_counter()
        
        warmup_time_ms = (end_time - start_time) * 1000
        
        if response.status_code == 200:
            print(f"✅ Warmup successful in {warmup_time_ms:.1f} ms")
        else:
            print(f"⚠️  Warmup status {response.status_code} in {warmup_time_ms:.1f} ms")
            
        return True
        
    except Exception as e:
        print(f"❌ Warmup failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 25-Bond Portfolio Performance Test")
    print("Testing actual response times for documentation validation")
    print("=" * 60)
    print()
    
    # Run warmup
    if test_warmup():
        print()
        
        # Run main timing test
        timing_result = test_portfolio_timing()
        
        if timing_result:
            print()
            print("🎯 CONCLUSION:")
            print("=" * 30)
            
            if timing_result < 1000:
                print("✅ CLAIM VERIFIED: Portfolio processing under 1 second")
                print("📝 Documentation timing claims are ACCURATE")
            else:
                print("❌ CLAIM DISPUTED: Portfolio took longer than 1 second")
                print("📝 Documentation should be updated with actual timing")
                print(f"   Suggested update: ~{timing_result/1000:.1f} seconds for 25-bond portfolio")
    else:
        print()
        print("❌ Cannot proceed without successful warmup")
        print("   Check API server status and try again")