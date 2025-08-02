#!/usr/bin/env python3
"""
Test Production Spread Issue
===========================

Diagnose why spread calculations return null in production.
"""

import requests
import json
import sqlite3
import os
from datetime import datetime

# Check local database for Treasury yields
def check_treasury_yields():
    """Check if Treasury yields are available locally."""
    db_path = 'bonds_data.db'
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check if tsys_enhanced table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tsys_enhanced';")
            if not cursor.fetchone():
                print("❌ tsys_enhanced table not found")
                return
            
            # Get latest Treasury yields
            cursor.execute("""
                SELECT Date, M2Y, M5Y, M10Y, M30Y 
                FROM tsys_enhanced 
                ORDER BY Date DESC 
                LIMIT 5
            """)
            
            rows = cursor.fetchall()
            if rows:
                print("✅ Treasury yields available:")
                print("Date        | 2Y    | 5Y    | 10Y   | 30Y")
                print("-" * 45)
                for row in rows:
                    print(f"{row[0]} | {row[1]:.3f} | {row[2]:.3f} | {row[3]:.3f} | {row[4]:.3f}")
            else:
                print("❌ No Treasury yield data found")
                
    except Exception as e:
        print(f"❌ Database error: {e}")

# Test production API
def test_production_api():
    """Test spread calculation in production."""
    api_url = "https://future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis"
    api_key = "gax10_test_9r4t7w2k5m8p1z6x3v"
    
    # Test with a corporate bond that should have spread
    test_bond = {
        "description": "IBM 3.45 02/19/26",
        "price": 95.0,
        "settlement_date": "2025-07-31"
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    
    print("\n🌐 Testing Production API:")
    print(f"URL: {api_url}")
    print(f"Bond: {test_bond['description']}")
    print(f"Settlement: {test_bond['settlement_date']}")
    
    try:
        response = requests.post(api_url, headers=headers, json=test_bond)
        response.raise_for_status()
        
        data = response.json()
        analytics = data.get('analytics', {})
        
        print("\n📊 Results:")
        print(f"YTM: {analytics.get('ytm', 'N/A')}%")
        print(f"Duration: {analytics.get('duration', 'N/A')} years")
        print(f"Spread: {analytics.get('spread', 'N/A')}")
        print(f"Z-Spread: {analytics.get('z_spread', 'N/A')}")
        
        # Debug: print raw response
        print("\n🔍 Raw analytics object:")
        print(json.dumps(analytics, indent=2))
        
    except Exception as e:
        print(f"\n❌ API Error: {e}")

def check_code_implementation():
    """Check if spread calculation code exists."""
    print("\n🔧 Checking Code Implementation:")
    
    # Check if WorkingTreasuryDetector import exists
    if os.path.exists('google_analysis10.py'):
        with open('google_analysis10.py', 'r') as f:
            content = f.read()
            if 'WorkingTreasuryDetector' in content:
                print("✅ WorkingTreasuryDetector import found")
                if 'g_spread =' in content or 'z_spread =' in content:
                    print("✅ Spread calculation code found")
                else:
                    print("❌ Spread calculation code not found")
            else:
                print("❌ WorkingTreasuryDetector not imported")
    
    # Check if treasury_bond_fix.py exists
    if os.path.exists('treasury_bond_fix.py'):
        print("✅ treasury_bond_fix.py exists")
        with open('treasury_bond_fix.py', 'r') as f:
            content = f.read()
            if 'get_treasury_yield' in content:
                print("✅ get_treasury_yield method found")
            else:
                print("❌ get_treasury_yield method NOT found")
    else:
        print("❌ treasury_bond_fix.py not found")

if __name__ == "__main__":
    print("🔍 Diagnosing Production Spread Issue")
    print("=" * 50)
    
    # Check local setup
    check_treasury_yields()
    check_code_implementation()
    
    # Test production
    test_production_api()