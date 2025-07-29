#!/usr/bin/env python3
"""
🌸 Google Analysis 10 - LOCAL PORTFOLIO TESTING SCRIPT
=====================================================

PURPOSE: Test your 25-bond portfolio against local container API
TECHNOLOGY: Python script that calls local Podman container API
USE CASE: Validate your portfolio calculations using identical production environment

⚠️  THIS TESTS AGAINST LOCAL CONTAINER ONLY - NOT PRODUCTION API
🚀 For production testing, see: PRODUCTION_DEPLOYMENT_README.md

Prerequisites:
  1. Start local container: ./local_container_setup.sh start
  2. Run this script: python3 test_local_portfolio.py

Quick Start Instructions: LOCAL_CONTAINER_TESTING_README.md
Definitive Documentation: DEPLOYMENT_SCRIPTS_DOCUMENTATION.md
"""

import requests
import json
import sys
from datetime import datetime

# Your complete portfolio data
YOUR_PORTFOLIO = [
    {"BOND_CD": "XS2233188353", "CLOSING PRICE": 99.529, "WEIGHTING": 4.87, "BOND_ENAME": "QNBK 1 5/8 09/22/25"},
    {"BOND_CD": "US279158AJ82", "CLOSING PRICE": 70.804, "WEIGHTING": 2.97, "BOND_ENAME": "ECOPET 5 7/8 05/28/45"},
    {"BOND_CD": "US71654QDE98", "CLOSING PRICE": 91.655, "WEIGHTING": 1.28, "BOND_ENAME": "PEMEX 5.95 01/28/31"},
    {"BOND_CD": "US71654QDF63", "CLOSING PRICE": 74.422, "WEIGHTING": 3.9, "BOND_ENAME": "PEMEX 6.95 01/28/60"},
    {"BOND_CD": "USP0R80BAG79", "CLOSING PRICE": 98.336, "WEIGHTING": 3.09, "BOND_ENAME": "AMXLMM 5 3/8 04/04/32"},
    {"BOND_CD": "USP30179BR86", "CLOSING PRICE": 87.251, "WEIGHTING": 6.1, "BOND_ENAME": "CFELEC 6.264 02/15/52"},
    {"BOND_CD": "USP3143NAH72", "CLOSING PRICE": 102.094, "WEIGHTING": 5.71, "BOND_ENAME": "CDEL 6.15 10/24/36"},
    {"BOND_CD": "USP37110AM89", "CLOSING PRICE": 77.461, "WEIGHTING": 2.71, "BOND_ENAME": "ENAPCL 4 1/2 09/14/47"},
    {"BOND_CD": "USP37466AS18", "CLOSING PRICE": 80.902, "WEIGHTING": 4.52, "BOND_ENAME": "BMETR 4.7 05/07/50"},
    {"BOND_CD": "USP6629MAD40", "CLOSING PRICE": 84.093, "WEIGHTING": 3.82, "BOND_ENAME": "MEXCAT 5 1/2 07/31/47"},
    {"BOND_CD": "XS0911024635", "CLOSING PRICE": 93.47, "WEIGHTING": 3.27, "BOND_ENAME": "SECO 5.06 04/08/43"},
    {"BOND_CD": "XS1709535097", "CLOSING PRICE": 89.881, "WEIGHTING": 3.77, "BOND_ENAME": "ADNOUH 4.6 11/02/47"},
    {"BOND_CD": "XS1807299331", "CLOSING PRICE": 93.481, "WEIGHTING": 6.54, "BOND_ENAME": "KZOKZ 6 3/8 10/24/48"},
    {"BOND_CD": "XS1982113463", "CLOSING PRICE": 87.982, "WEIGHTING": 3.69, "BOND_ENAME": "ARAMCO 4 1/4 04/16/39"},
    {"BOND_CD": "XS2249741674", "CLOSING PRICE": 78.43, "WEIGHTING": 3.84, "BOND_ENAME": "ADGLXY 3 1/4 09/30/40"},
    {"BOND_CD": "XS2359548935", "CLOSING PRICE": 74.468, "WEIGHTING": 3.64, "BOND_ENAME": "QPETRO 3 1/8 07/12/41"},
    {"BOND_CD": "XS2542166231", "CLOSING PRICE": 103.757, "WEIGHTING": 2.9, "BOND_ENAME": "GASBCM 6.129 02/23/38"},
    {"BOND_CD": "XS2585988145", "CLOSING PRICE": 85.78, "WEIGHTING": 2.7, "BOND_ENAME": "PIFKSA 5 1/8 02/14/53"},
    {"BOND_CD": "US195325DX04", "CLOSING PRICE": 55.068, "WEIGHTING": 3.85, "BOND_ENAME": "COLOM 3 7/8 02/15/61"},
    {"BOND_CD": "US698299BL70", "CLOSING PRICE": 57.888, "WEIGHTING": 4.05, "BOND_ENAME": "PANAMA 3.87 07/23/60"},
    {"BOND_CD": "US91086QAZ19", "CLOSING PRICE": 77.789, "WEIGHTING": 1.63, "BOND_ENAME": "MEX 5 3/4 10/12/2110"},
    {"BOND_CD": "US912810TJ79", "CLOSING PRICE": 70.53125, "WEIGHTING": 0.99, "BOND_ENAME": "T 3 08/15/52"},
    {"BOND_CD": "XS1508675508", "CLOSING PRICE": 82.462, "WEIGHTING": 4.03, "BOND_ENAME": "KSA 4 1/2 10/26/46"},
    {"BOND_CD": "XS1959337749", "CLOSING PRICE": 91.462, "WEIGHTING": 4.48, "BOND_ENAME": "QATAR 4.817 03/14/49"},
    {"BOND_CD": "XS2167193015", "CLOSING PRICE": 64.591, "WEIGHTING": 4.06, "BOND_ENAME": "ISRAEL 3.8 05/13/60"}
]

# Local container API settings
LOCAL_API_BASE = "http://localhost:8080"
API_KEY = "gax10_demo_3j5h8m9k2p6r4t7w1q"

def check_api_health():
    """Check if local API is running"""
    try:
        response = requests.get(f"{LOCAL_API_BASE}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Local API is healthy")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Service: {health_data.get('service')}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to local API: {e}")
        print("💡 Run: ./local_container_setup.sh start")
        return False

def test_individual_bond(bond_cd, price, description):
    """Test individual bond analysis"""
    print(f"🔍 Testing: {bond_cd} ({description[:30]}...)")
    
    payload = {
        "description": description,
        "price": price
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    try:
        response = requests.post(
            f"{LOCAL_API_BASE}/api/v1/bond/parse-and-calculate",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                bond_data = result.get("bond", {})
                analytics = bond_data.get("analytics", {})
                
                print(f"   ✅ Yield: {analytics.get('yield'):.3f}%, "
                      f"Duration: {analytics.get('duration'):.2f}, "
                      f"Spread: {analytics.get('spread'):.0f} bps")
                return analytics
            else:
                print(f"   ❌ Error: {result.get('error')}")
                return None
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return None

def test_portfolio_analysis(portfolio_data, batch_size=25):
    """Test complete portfolio analysis"""
    print(f"\n📊 Testing Portfolio Analysis ({len(portfolio_data)} bonds)")
    print("=" * 60)
    
    # Convert to API format
    api_data = {
        "data": [
            {
                "BOND_CD": bond["BOND_CD"],
                "CLOSING PRICE": bond["CLOSING PRICE"],
                "WEIGHTING": bond["WEIGHTING"],
                "Inventory Date": "25/07/2025"
            }
            for bond in portfolio_data
        ]
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    try:
        response = requests.post(
            f"{LOCAL_API_BASE}/api/v1/portfolio/analyze",
            headers=headers,
            json=api_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                print("✅ Portfolio analysis successful!")
                
                # Portfolio metrics
                metrics = result.get("portfolio_metrics", {})
                print(f"\n📈 PORTFOLIO METRICS:")
                print(f"   Portfolio Yield: {metrics.get('portfolio_yield', 'N/A'):.3f}%")
                print(f"   Portfolio Duration: {metrics.get('portfolio_duration', 'N/A'):.3f}")
                print(f"   Portfolio Spread: {metrics.get('portfolio_spread', 'N/A'):.0f} bps")
                print(f"   Success Rate: {metrics.get('success_rate', 'N/A'):.1f}%")
                print(f"   Total Weight: {metrics.get('total_weight', 'N/A'):.1f}%")
                
                # Individual bond results
                bond_data = result.get("bond_data", [])
                successful_bonds = [b for b in bond_data if b.get('yield') is not None]
                
                print(f"\n🔍 TOP 10 BONDS BY YIELD:")
                top_bonds = sorted(successful_bonds, key=lambda x: x.get('yield', 0), reverse=True)[:10]
                for i, bond in enumerate(top_bonds, 1):
                    print(f"   {i:2d}. {bond.get('identifier', 'N/A')[:15]:15s} | "
                          f"Yield: {bond.get('yield', 0):6.2f}% | "
                          f"Duration: {bond.get('duration', 0):5.2f} | "
                          f"Weight: {bond.get('weighting', 0):5.2f}%")
                
                return result
            else:
                print(f"❌ Portfolio Error: {result.get('error')}")
                return None
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Portfolio request failed: {e}")
        return None

def main():
    """Main testing function"""
    print("🌸 LOCAL CONTAINER API TESTING")
    print("=" * 50)
    print(f"🕐 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 API Base: {LOCAL_API_BASE}")
    
    # Check API health
    if not check_api_health():
        sys.exit(1)
    
    choice = input("\nChoose test type:\n1. Individual bonds (first 3)\n2. Complete portfolio (25 bonds)\n3. Both\nEnter choice (1-3): ").strip()
    
    if choice in ["1", "3"]:
        print(f"\n1️⃣ INDIVIDUAL BOND TESTS")
        print("-" * 40)
        for i, bond in enumerate(YOUR_PORTFOLIO[:3]):
            test_individual_bond(bond["BOND_CD"], bond["CLOSING PRICE"], bond["BOND_ENAME"])
            if i < 2:  # Add pause between tests
                print()
    
    if choice in ["2", "3"]:
        print(f"\n2️⃣ COMPLETE PORTFOLIO TEST")
        test_portfolio_analysis(YOUR_PORTFOLIO)
    
    print(f"\n✅ Testing complete!")
    print("💡 To view logs: ./local_container_setup.sh logs")
    print("💡 To stop container: ./local_container_setup.sh stop")

if __name__ == "__main__":
    main()
