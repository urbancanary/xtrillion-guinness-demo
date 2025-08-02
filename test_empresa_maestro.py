#!/usr/bin/env python3
"""
Test EMPRESA MAESTRO bond accrued interest calculation
"""

import requests
import json

def test_empresa_maestro():
    """Test EMPRESA MAESTRO bond"""
    print("🧪 Testing EMPRESA MAESTRO bond")
    print("=" * 60)
    
    # From validated data
    print("📋 Validated data:")
    print("   ISIN: USP37466AS18")
    print("   Description: BMETR 4.7 05/07/50")
    print("   Coupon: 4.7%")
    print("   Maturity: 2050-05-07")
    print("   Business Convention: Unadjusted")
    print("   Expected accrued: $21,019.44 per million")
    print("   Current result: $13,243.09 per million")
    
    url = "https://future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis"
    
    # Test different input formats
    test_cases = [
        {
            "name": "With ISIN",
            "payload": {
                "isin": "USP37466AS18",
                "price": 100.0,
                "settlement_date": "2025-04-18"
            }
        },
        {
            "name": "With validated description",
            "payload": {
                "description": "BMETR 4.7 05/07/50",
                "price": 100.0,
                "settlement_date": "2025-04-18"
            }
        },
        {
            "name": "With full description",
            "payload": {
                "description": "EMPRESA MAESTRO, 4.7%, 07-May-2050",
                "price": 100.0,
                "settlement_date": "2025-04-18"
            }
        }
    ]
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "xTr1ll10n_2025_pr0d"
    }
    
    for test in test_cases:
        print(f"\n📊 Testing {test['name']}...")
        
        try:
            response = requests.post(url, json=test['payload'], headers=headers, timeout=30)
            result = response.json()
            
            if result.get('status') == 'success':
                analytics = result.get('analytics', {})
                accrued = analytics.get('accrued_interest', 0)
                accrued_per_million = accrued * 10000
                
                print(f"   Accrued interest: {accrued:.6f}%")
                print(f"   Accrued per million: ${accrued_per_million:,.2f}")
                
                # Calculate implied days
                semi_annual_coupon = 4.7 / 2.0
                implied_days = (accrued / semi_annual_coupon) * 180
                print(f"   Implied days: {implied_days:.1f}")
                
                # Check difference
                expected = 21019.44
                diff = abs(accrued_per_million - expected)
                print(f"   Difference from expected: ${diff:,.2f}")
                
            else:
                print(f"   ❌ API Error: {result}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")

def calculate_manual():
    """Manual calculation check"""
    print("\n\n📐 Manual calculation:")
    print("=" * 60)
    
    # EMPRESA MAESTRO details
    coupon = 4.7
    semi_annual_coupon = coupon / 2.0
    
    # Maturity: May 7, 2050
    # Settlement: April 18, 2025
    # Previous coupon: November 7, 2024
    # Next coupon: May 7, 2025
    
    # Using 30/360 day count
    # From Nov 7, 2024 to Apr 18, 2025:
    # Nov 7 to Nov 30: 23 days
    # Dec: 30 days
    # Jan: 30 days
    # Feb: 30 days
    # Mar: 30 days
    # Apr 1 to Apr 18: 18 days
    # Total: 23 + 30 + 30 + 30 + 30 + 18 = 161 days
    
    days_accrued = 161
    days_in_period = 180
    
    accrued_fraction = days_accrued / days_in_period
    accrued_interest = semi_annual_coupon * accrued_fraction
    accrued_per_million = accrued_interest * 10000
    
    print(f"   Coupon: {coupon}%")
    print(f"   Semi-annual coupon: {semi_annual_coupon}%")
    print(f"   Previous coupon: November 7, 2024")
    print(f"   Settlement date: April 18, 2025")
    print(f"   Next coupon: May 7, 2025")
    print(f"   Days accrued (30/360): {days_accrued}")
    print(f"   Days in period: {days_in_period}")
    print(f"   Accrued fraction: {accrued_fraction:.6f}")
    print(f"   Accrued interest: {accrued_interest:.6f}%")
    print(f"   Accrued per million: ${accrued_per_million:,.2f}")
    
    # Compare with current result
    current_result = 13243.09
    print(f"\n   Current API result: ${current_result:,.2f}")
    print(f"   Expected result: $21,019.44")
    
    # Work backwards from current result
    implied_accrued = current_result / 10000
    implied_days_from_current = (implied_accrued / semi_annual_coupon) * 180
    print(f"\n   Working backwards from ${current_result:,.2f}:")
    print(f"   Implied accrued: {implied_accrued:.6f}%")
    print(f"   Implied days: {implied_days_from_current:.1f}")
    
    # This suggests the system might be calculating from a different coupon date

if __name__ == "__main__":
    test_empresa_maestro()
    calculate_manual()