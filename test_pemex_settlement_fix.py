#!/usr/bin/env python3
"""
Test PEMEX bond settlement date fix
"""

import os
import sys
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google_analysis10 import process_bond_portfolio
from datetime import datetime

def test_pemex_settlement_fix():
    """Test PEMEX bond calculation with corrected settlement date handling"""
    print("🧪 Testing PEMEX bond settlement date fix")
    print("=" * 60)
    
    # Create portfolio data with explicit settlement date
    portfolio_data = {
        "data": [
            {
                "description": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060",
                "CLOSING PRICE": 100.0,
                "WEIGHTING": 100.0
            }
        ]
    }
    
    # Database paths
    db_path = './bonds_data.db'
    validated_db_path = './validated_quantlib_bonds.db'
    bloomberg_db_path = './bloomberg_index.db'
    
    # Test with April 18 settlement date (should be used directly)
    print("\n📊 Testing with April 18, 2025 settlement date...")
    
    try:
        # Process the bond with explicit settlement date
        results = process_bond_portfolio(
            portfolio_data,
            db_path,
            validated_db_path,
            bloomberg_db_path,
            settlement_days=0,
            settlement_date="2025-04-18"
        )
        
        if len(results) > 0:
            result = results[0]
            
            print("\n📈 Results:")
            print(f"   Description: {result.get('description', 'N/A')}")
            print(f"   Settlement Date: {result.get('settlement_date', 'N/A')}")
            print(f"   Yield: {result.get('yield', 'N/A')}%")
            print(f"   Duration: {result.get('duration', 'N/A')} years")
            print(f"   Accrued Interest: {result.get('accrued_interest', 'N/A')}%")
            
            # Calculate accrued per million
            accrued = float(result.get('accrued_interest', 0))
            accrued_per_million = accrued * 10000
            print(f"   Accrued per million: ${accrued_per_million:,.2f}")
            
            print("\n💡 Expected values (per user calculation):")
            print("   Days from Jan 28 to Apr 18: 80 days")
            print("   Accrued interest: 1.544444%")
            print("   Accrued per million: $15,444.44")
            
            # Check if fix worked
            expected_accrued_per_million = 15444.44
            tolerance = 50.0  # Allow $50 tolerance for rounding
            
            if abs(accrued_per_million - expected_accrued_per_million) < tolerance:
                print("\n✅ FIX SUCCESSFUL! Settlement date is being used correctly.")
                print(f"   Calculated: ${accrued_per_million:,.2f}")
                print(f"   Expected: ${expected_accrued_per_million:,.2f}")
                print(f"   Difference: ${abs(accrued_per_million - expected_accrued_per_million):,.2f}")
                return True
            else:
                print("\n❌ Fix not working correctly.")
                print(f"   Calculated: ${accrued_per_million:,.2f}")
                print(f"   Expected: ${expected_accrued_per_million:,.2f}")
                print(f"   Difference: ${abs(accrued_per_million - expected_accrued_per_million):,.2f}")
                return False
        else:
            print("❌ No results returned")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint():
    """Test via the API endpoint"""
    print("\n\n🌐 Testing via API endpoint...")
    print("=" * 60)
    
    import requests
    
    url = "http://localhost:8080/api/v1/bond/analysis"
    
    payload = {
        "description": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060",
        "price": 100.0,
        "settlement_date": "2025-04-18"
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "test_api_key"
    }
    
    try:
        print("📤 Sending request to API...")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        result = response.json()
        
        if result.get('status') == 'success':
            analytics = result.get('analytics', {})
            accrued = analytics.get('accrued_interest', 0)
            accrued_per_million = accrued * 10000
            
            print(f"\n📊 API Results:")
            print(f"   Settlement date: {analytics.get('settlement_date', 'N/A')}")
            print(f"   Accrued interest: {accrued:.6f}%") 
            print(f"   Accrued per million: ${accrued_per_million:,.2f}")
            
            # Check if fix worked
            expected_accrued_per_million = 15444.44
            if abs(accrued_per_million - expected_accrued_per_million) < 50.0:
                print("\n✅ API FIX SUCCESSFUL!")
                return True
            else:
                print("\n❌ API fix not working correctly.")
                return False
        else:
            print(f"❌ API Error: {result}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  API not running. Start it with: python3 google_analysis10_api.py")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    # Test direct calculation
    direct_success = test_pemex_settlement_fix()
    
    # Test API if available
    api_success = test_api_endpoint()
    
    if direct_success:
        print("\n\n🎉 PEMEX bond settlement date fix is working correctly!")
    else:
        print("\n\n❌ PEMEX bond fix needs more work.")