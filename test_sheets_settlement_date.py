#!/usr/bin/env python3
"""
Test script to simulate Google Sheets XT_SMART function behavior
with settlement date detection from column C
"""

import requests
import json

def test_google_sheets_simulation():
    """Simulate the XT_SMART function processing B2:C51 range"""
    
    # Test data mimicking Google Sheets range B2:C51
    test_data = [
        ["T 3 15/08/52", "30/06/2025"],  # Bond description, Settlement date
        ["71.66", ""],                    # Price, Empty (should use previous settlement)
    ]
    
    # Development API URL and key
    base_url = "https://development-dot-future-footing-414610.uc.r.appspot.com"
    api_key = "gax10_dev_4n8s6k2x7p9v5m8p1z"
    
    print("🧪 Testing Google Sheets XT_SMART simulation")
    print("=" * 50)
    
    # Extract bond description and price
    bond_description = test_data[0][0]  # "T 3 15/08/52"
    price = float(test_data[1][0])      # 71.66
    settlement_date = test_data[0][1]   # "30/06/2025"
    
    print(f"📊 Bond: {bond_description}")
    print(f"💰 Price: {price}")
    print(f"📅 Settlement Date: {settlement_date}")
    print()
    
    # Test 1: Without settlement date (should get 16.26 duration)
    print("🔍 Test 1: Without settlement date")
    payload = {
        "description": bond_description,
        "price": price
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/bond/analysis",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key
            },
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            duration = data.get("analytics", {}).get("duration", "N/A")
            print(f"✅ Duration without settlement date: {duration}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print()
    
    # Test 2: With settlement date (should get 16.35 duration)
    print("🔍 Test 2: With settlement date")
    
    # Convert DD/MM/YYYY to YYYY-MM-DD format
    date_parts = settlement_date.split("/")
    iso_date = f"2025-{date_parts[1]}-{date_parts[0]}"  # Convert 30/06/2025 to 2025-06-30
    
    payload = {
        "description": bond_description,
        "price": price,
        "settlement_date": iso_date
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/bond/analysis",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": api_key
            },
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            duration = data.get("analytics", {}).get("duration", "N/A")
            print(f"✅ Duration with settlement date: {duration}")
            print(f"✅ Settlement date used: {data.get('analytics', {}).get('settlement_date', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print()
    print("🎯 Expected Results:")
    print("   - Without settlement date: ~16.26")
    print("   - With settlement date (30/06/2025): ~16.35")
    print()
    print("📝 Next Step: Test Google Sheets XT_SMART function with:")
    print("   =XT_SMART(A2:A10, B2:C10, , , \"testing\")")
    print("   Where A2 = 'T 3 15/08/52', B2 = 71.66, C2 = '30/06/2025'")

if __name__ == "__main__":
    test_google_sheets_simulation()