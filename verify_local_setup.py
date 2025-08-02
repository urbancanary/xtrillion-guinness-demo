#!/usr/bin/env python3
"""
Verify Local Setup
==================

Quick verification that all components are working before deployment.
"""

import requests
import json
import sys
import os
import sqlite3
from datetime import datetime


def test_api_health():
    """Test API health endpoint."""
    print("1️⃣ Testing API Health Check...")
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API is healthy - Version: {data.get('version', 'N/A')}")
            print(f"   ✅ Environment: {data.get('environment', 'N/A')}")
            return True
        else:
            print(f"   ❌ API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Failed to connect to API: {e}")
        return False


def test_databases():
    """Test database connections."""
    print("\n2️⃣ Testing Database Connections...")
    databases = {
        "bonds_data.db": "Primary bond database",
        "bloomberg_index.db": "Bloomberg reference data",
        "validated_quantlib_bonds.db": "Validated conventions"
    }
    
    all_good = True
    for db_file, description in databases.items():
        if os.path.exists(db_file):
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                conn.close()
                print(f"   ✅ {db_file}: Connected ({table_count} tables) - {description}")
            except Exception as e:
                print(f"   ❌ {db_file}: Error - {e}")
                all_good = False
        else:
            print(f"   ❌ {db_file}: Not found")
            all_good = False
    
    return all_good


def test_bond_calculation():
    """Test individual bond calculation."""
    print("\n3️⃣ Testing Bond Calculation...")
    
    payload = {
        "description": "T 3 15/08/52",
        "price": 71.66,
        "settlement_date": "2025-04-18"
    }
    
    try:
        response = requests.post(
            "http://localhost:8080/api/v1/bond/analysis",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            analytics = data.get("analytics", {})
            print(f"   ✅ Bond calculation successful")
            print(f"      YTM: {analytics.get('ytm', 'N/A'):.4f}%")
            print(f"      Duration: {analytics.get('duration', 'N/A'):.2f} years")
            print(f"      Clean Price: ${analytics.get('clean_price', 'N/A')}")
            return True
        else:
            print(f"   ❌ API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Failed to calculate bond: {e}")
        return False


def test_portfolio_calculation():
    """Test portfolio calculation."""
    print("\n4️⃣ Testing Portfolio Calculation...")
    
    payload = {
        "data": [
            {
                "description": "T 3 15/08/52",
                "CLOSING PRICE": 71.66,
                "WEIGHTING": 50.0
            },
            {
                "description": "T 4.125 15/10/27",
                "CLOSING PRICE": 99.92,
                "WEIGHTING": 50.0
            }
        ]
    }
    
    try:
        response = requests.post(
            "http://localhost:8080/api/v1/portfolio/analysis",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            metrics = data.get("portfolio_metrics", {})
            print(f"   ✅ Portfolio calculation successful")
            print(f"      Portfolio Yield: {metrics.get('portfolio_yield', 'N/A')}")
            print(f"      Portfolio Duration: {metrics.get('portfolio_duration', 'N/A')}")
            print(f"      Success Rate: {metrics.get('success_rate', 'N/A')}")
            return True
        else:
            print(f"   ❌ API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Failed to calculate portfolio: {e}")
        return False


def main():
    """Run all verification tests."""
    print("🔍 XTrillion Bond Analytics - Local Setup Verification")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = [
        ("API Health", test_api_health),
        ("Database Connections", test_databases),
        ("Bond Calculation", test_bond_calculation),
        ("Portfolio Calculation", test_portfolio_calculation)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - System is ready for deployment!")
    else:
        print("❌ SOME TESTS FAILED - Please fix issues before deployment")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())