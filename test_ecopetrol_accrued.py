#!/usr/bin/env python3
"""
Test ECOPETROL bond accrued interest calculation
"""

import requests
import json

def test_ecopetrol_production():
    """Test ECOPETROL bond against production API"""
    print("🧪 Testing ECOPETROL bond accrued interest")
    print("=" * 60)
    
    url = "https://future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis"
    
    # Test with the exact description from the user
    payload = {
        "description": "ECOPETROL SA, 5.875%, 28-May-2045",
        "price": 100.0,
        "settlement_date": "2025-04-18"
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "xTr1ll10n_2025_pr0d"
    }
    
    print(f"📤 Testing with user's description format...")
    print(f"   Description: {payload['description']}")
    print(f"   Settlement date: {payload['settlement_date']}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()
        
        if result.get('status') == 'success':
            analytics = result.get('analytics', {})
            accrued = analytics.get('accrued_interest', 0)
            accrued_per_million = accrued * 10000
            
            print(f"\n📊 Production API Results:")
            print(f"   Accrued interest: {accrued:.6f}%") 
            print(f"   Accrued per million: ${accrued_per_million:,.2f}")
            
            print(f"\n💡 Expected from validated DB:")
            print(f"   Accrued per million: $22,847.22")
            print(f"   Difference: ${abs(accrued_per_million - 22847.22):,.2f}")
            
            # Calculate implied days
            semi_annual_coupon = 5.875 / 2.0
            implied_days = (accrued / semi_annual_coupon) * 180
            print(f"\n📐 Calculation check:")
            print(f"   Semi-annual coupon: {semi_annual_coupon}%")
            print(f"   Implied days: {implied_days:.1f}")
            
        else:
            print(f"❌ API Error: {result}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_ecopetrol_validated_format():
    """Test with validated DB description format"""
    print("\n\n🧪 Testing with validated DB description format")
    print("=" * 60)
    
    url = "https://future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis"
    
    # Test with the validated DB format
    payload = {
        "description": "ECOPET 5 ⅞ 05/28/45",  # Format from validated DB
        "price": 100.0,
        "settlement_date": "2025-04-18"
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "xTr1ll10n_2025_pr0d"
    }
    
    print(f"📤 Testing with validated DB format...")
    print(f"   Description: {payload['description']}")
    print(f"   Settlement date: {payload['settlement_date']}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        result = response.json()
        
        if result.get('status') == 'success':
            analytics = result.get('analytics', {})
            accrued = analytics.get('accrued_interest', 0)
            accrued_per_million = accrued * 10000
            
            print(f"\n📊 Production API Results:")
            print(f"   Accrued interest: {accrued:.6f}%") 
            print(f"   Accrued per million: ${accrued_per_million:,.2f}")
            
            print(f"\n💡 Expected from validated DB:")
            print(f"   Accrued per million: $22,847.22")
            print(f"   Difference: ${abs(accrued_per_million - 22847.22):,.2f}")
            
        else:
            print(f"❌ API Error: {result}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def calculate_manual_accrued():
    """Calculate accrued manually"""
    print("\n\n📐 Manual calculation check:")
    print("=" * 60)
    
    # ECOPETROL bond details
    coupon = 5.875
    semi_annual_coupon = coupon / 2.0
    
    # Previous coupon: November 28, 2024
    # Next coupon: May 28, 2025
    # Settlement: April 18, 2025
    
    # Using 30/360 day count
    # From Nov 28, 2024 to Apr 18, 2025:
    # Nov 28 to Nov 30: 2 days
    # Dec: 30 days
    # Jan: 30 days
    # Feb: 30 days
    # Mar: 30 days
    # Apr 1 to Apr 18: 18 days
    # Total: 2 + 30 + 30 + 30 + 30 + 18 = 140 days
    
    days_accrued = 140
    days_in_period = 180
    
    accrued_fraction = days_accrued / days_in_period
    accrued_interest = semi_annual_coupon * accrued_fraction
    accrued_per_million = accrued_interest * 10000
    
    print(f"   Coupon: {coupon}%")
    print(f"   Semi-annual coupon: {semi_annual_coupon}%")
    print(f"   Previous coupon: November 28, 2024")
    print(f"   Settlement date: April 18, 2025")
    print(f"   Next coupon: May 28, 2025")
    print(f"   Days accrued (30/360): {days_accrued}")
    print(f"   Days in period: {days_in_period}")
    print(f"   Accrued fraction: {accrued_fraction:.6f}")
    print(f"   Accrued interest: {accrued_interest:.6f}%")
    print(f"   Accrued per million: ${accrued_per_million:,.2f}")

if __name__ == "__main__":
    test_ecopetrol_production()
    test_ecopetrol_validated_format()
    calculate_manual_accrued()