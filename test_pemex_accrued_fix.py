#!/usr/bin/env python3
"""
Test PEMEX bond accrued interest calculation
Verifies the fix for PETROLEOS MEXICA, 6.95%, 28-Jan-2060
"""

import QuantLib as ql
from datetime import datetime, date
import requests
import json

def test_pemex_locally():
    """Test PEMEX bond accrued calculation locally using QuantLib"""
    print("🧪 Testing PEMEX bond accrued interest calculation locally")
    
    # Bond parameters
    coupon = 6.95
    maturity_str = "2060-01-28"
    settlement_str = "2025-04-21"
    
    # Parse dates
    maturity_date = datetime.strptime(maturity_str, "%Y-%m-%d")
    settlement_date = datetime.strptime(settlement_str, "%Y-%m-%d")
    
    # QuantLib dates
    ql_maturity = ql.Date(maturity_date.day, maturity_date.month, maturity_date.year)
    ql_settlement = ql.Date(settlement_date.day, settlement_date.month, settlement_date.year)
    
    # Set evaluation date
    ql.Settings.instance().evaluationDate = ql_settlement
    
    # Create schedule - PEMEX is corporate bond, use 30/360
    calendar = ql.UnitedStates(ql.UnitedStates.Settlement)
    business_convention = ql.Following
    frequency = ql.Semiannual
    day_counter = ql.Thirty360(ql.Thirty360.BondBasis)
    
    # Create schedule backward from maturity
    # Use a much earlier date to ensure we capture all coupon dates
    issue_date = ql.Date(28, 1, 2010)  # Assume issued in 2010
    schedule = ql.Schedule(
        issue_date, ql_maturity,
        ql.Period(frequency),
        calendar,
        business_convention, business_convention,
        ql.DateGeneration.Backward,
        False
    )
    
    print(f"\n📅 Schedule dates (first 5 and last 5):")
    dates = [schedule[i] for i in range(len(schedule))]
    for i, d in enumerate(dates[:5]):
        print(f"   {i}: {d}")
    if len(dates) > 10:
        print("   ...")
        for i, d in enumerate(dates[-5:], len(dates)-5):
            print(f"   {i}: {d}")
    
    # Find the last coupon date before settlement
    last_coupon_date = None
    for i in range(len(schedule)-1, -1, -1):
        if schedule[i] <= ql_settlement:
            last_coupon_date = schedule[i]
            break
    
    if last_coupon_date:
        print(f"\n💡 Last coupon date before settlement: {last_coupon_date}")
        
        # Calculate days using 30/360
        days_30_360 = day_counter.dayCount(last_coupon_date, ql_settlement)
        print(f"📊 Days from last coupon (30/360): {days_30_360}")
        
        # Calculate accrued interest
        semi_annual_coupon = coupon / 2.0
        accrued_fraction = days_30_360 / 180.0  # 180 days in half year for 30/360
        accrued_interest = semi_annual_coupon * accrued_fraction
        accrued_per_million = accrued_interest * 10000
        
        print(f"\n💰 Accrued Interest Calculation:")
        print(f"   Semi-annual coupon: {semi_annual_coupon}%")
        print(f"   Days accrued: {days_30_360}")
        print(f"   Accrued fraction: {accrued_fraction:.6f}")
        print(f"   Accrued interest: {accrued_interest:.6f}%")
        print(f"   Accrued per million: ${accrued_per_million:,.2f}")
    
    # Also create bond and use QuantLib's accrued calculation
    bond = ql.FixedRateBond(
        0,  # settlement days
        100.0,  # face value
        schedule,
        [coupon / 100.0],  # coupon as decimal
        day_counter
    )
    
    ql_accrued = bond.accruedAmount(ql_settlement)
    ql_accrued_pct = ql_accrued / 100.0 * 100.0  # Convert to percentage
    ql_accrued_per_million = ql_accrued * 10000
    
    print(f"\n🔧 QuantLib Bond Calculation:")
    print(f"   Accrued amount: {ql_accrued:.6f}")
    print(f"   Accrued interest: {ql_accrued_pct:.6f}%")
    print(f"   Accrued per million: ${ql_accrued_per_million:,.2f}")
    
    return ql_accrued_per_million

def test_pemex_production():
    """Test PEMEX bond against production API"""
    print("\n\n🌐 Testing PEMEX bond against production API")
    
    url = "https://future-footing-414610.uc.r.appspot.com/api/v1/bond/analysis"
    
    payload = {
        "description": "PETROLEOS MEXICA, 6.95%, 28-Jan-2060",
        "price": 100.0,
        "settlement_date": "2025-04-21"
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "test_api_key"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        result = response.json()
        
        if result.get('status') == 'success':
            analytics = result.get('analytics', {})
            accrued = analytics.get('accrued_interest', 0)
            accrued_per_million = accrued * 10000
            
            print(f"\n📊 Production API Results:")
            print(f"   Accrued interest: {accrued:.6f}%") 
            print(f"   Accrued per million: ${accrued_per_million:,.2f}")
            
            # Also show the bond parsing info
            bond_info = result.get('bond', {})
            print(f"\n🔍 Bond Parsing Info:")
            print(f"   Description: {bond_info.get('description')}")
            print(f"   Route used: {bond_info.get('route_used')}")
            print(f"   Conventions: {json.dumps(bond_info.get('conventions', {}), indent=6)}")
            
            return accrued_per_million
        else:
            print(f"❌ API Error: {result}")
            return None
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def main():
    """Main test function"""
    print("=" * 60)
    print("PEMEX Bond Accrued Interest Test")
    print("Bond: PETROLEOS MEXICA, 6.95%, 28-Jan-2060")
    print("Settlement: April 21, 2025")
    print("=" * 60)
    
    # Test locally
    local_accrued = test_pemex_locally()
    
    # Test production
    prod_accrued = test_pemex_production()
    
    # Compare results
    print("\n" + "=" * 60)
    print("📊 COMPARISON:")
    print(f"   Local calculation: ${local_accrued:,.2f} per million")
    if prod_accrued:
        print(f"   Production API:    ${prod_accrued:,.2f} per million")
        diff = abs(local_accrued - prod_accrued)
        print(f"   Difference:        ${diff:,.2f}")
        
        if diff > 1.0:  # More than $1 difference
            print("   ❌ SIGNIFICANT DIFFERENCE DETECTED!")
        else:
            print("   ✅ Results match within tolerance")
    
    print("\n💡 Expected Result:")
    print("   Days from Jan 28 to Apr 21: 83 days (30/360)")
    print("   Accrued fraction: 83/180 = 0.461111")
    print("   Semi-annual coupon: 3.475%")
    print("   Accrued interest: 1.60236%")
    print("   Accrued per million: $16,023.61")

if __name__ == "__main__":
    main()