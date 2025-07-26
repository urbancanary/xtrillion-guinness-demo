#!/usr/bin/env python3
"""
🔧 Duration Fix Validation Test
===============================

Tests the brilliant yield/duration fix that converts:
- Decimal yield (0.048997) → Duration 16.60028 (wrong)
- Percentage yield (4.89972%) → Duration 0.16347 × 100 = 16.347 (✅ Bloomberg match!)

Expected Result: Duration ≈ 16.35658 (Bloomberg baseline)
"""

import sys
import os
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

from google_analysis10 import calculate_bond_metrics_with_conventions_using_shared_engine
import QuantLib as ql
from datetime import datetime
import logging

# Set up logging to see the fix in action
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_duration_fix():
    """Test the brilliant duration fix with US Treasury bond"""
    print("🔧 Testing Duration Fix - Your Brilliant Discovery!")
    print("=" * 60)
    
    # Test data: US Treasury bond from your analysis
    test_data = {
        'isin': 'US912810TJ79',
        'coupon': 3.0,  # 3% coupon
        'maturity_date': datetime(2052, 8, 15),
        'price': 71.66,
        'trade_date': datetime(2025, 6, 30).date(),
        'is_treasury': True
    }
    
    print(f"📊 Test Bond: {test_data['isin']}")
    print(f"💰 Coupon: {test_data['coupon']}%")
    print(f"📅 Maturity: {test_data['maturity_date'].strftime('%Y-%m-%d')}")
    print(f"💵 Price: {test_data['price']}")
    print(f"📆 Trade Date: {test_data['trade_date']}")
    print()
    
    # Mock treasury handle (required parameter)
    treasury_handle = ql.YieldTermStructureHandle(
        ql.FlatForward(
            ql.Date(30, 6, 2025), 
            0.03, 
            ql.Actual365Fixed()
        )
    )
    
    # Default conventions
    default_conventions = {
        'fixed_frequency': 'Semiannual',
        'day_count': '30/360',
        'business_day_convention': 'Following',
        'end_of_month': False
    }
    
    print("🚀 Running calculation with YOUR BRILLIANT FIX...")
    print("-" * 40)
    
    # Run the fixed calculation
    result = calculate_bond_metrics_with_conventions_using_shared_engine(
        isin=test_data['isin'],
        coupon=test_data['coupon'],
        maturity_date=test_data['maturity_date'],
        price=test_data['price'],
        trade_date=test_data['trade_date'],
        treasury_handle=treasury_handle,
        default_conventions=default_conventions,
        is_treasury=test_data['is_treasury'],
        settlement_days=1
    )
    
    print()
    print("📊 RESULTS:")
    print("=" * 30)
    
    if result.get('successful'):
        yield_pct = result['yield'] * 100
        duration = result['duration']
        convexity = result['convexity']
        
        print(f"✅ Yield: {yield_pct:.5f}%")
        print(f"✅ Duration: {duration:.5f} years")
        print(f"✅ Convexity: {convexity:.2f}")
        
        # Compare with Bloomberg baseline
        bloomberg_duration = 16.35658
        duration_error = abs(duration - bloomberg_duration)
        error_bps = duration_error * 100  # Convert to basis points
        
        print()
        print("🎯 VALIDATION vs Bloomberg:")
        print("-" * 35)
        print(f"Bloomberg Expected: {bloomberg_duration:.5f}")
        print(f"Your Fixed Result:  {duration:.5f}")
        print(f"Absolute Error:     {duration_error:.5f} years")
        print(f"Error (basis pts):  {error_bps:.2f} bps")
        
        # Determine success
        if error_bps < 10:  # Less than 10 basis points error
            print("🎉 SUCCESS! Duration fix is BRILLIANT!")
            print("✅ Error < 10 bps = Bloomberg-quality accuracy")
        elif error_bps < 50:
            print("✅ GOOD! Significant improvement achieved")
        else:
            print("⚠️ Needs more refinement")
            
        print()
        print("🔧 FIX DETAILS:")
        print("- Converted yield to percentage format for duration calculation")
        print("- Multiplied raw duration result by 100 for Bloomberg scaling")
        print("- Used consistent semiannual frequency throughout")
        
    else:
        print("❌ Calculation failed:")
        print(f"Error: {result.get('error')}")
    
    return result

if __name__ == "__main__":
    test_duration_fix()
