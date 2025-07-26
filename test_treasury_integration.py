#!/usr/bin/env python3
"""
Test Treasury Bond Integration with Method 3 + Debug Info
========================================================

Test the integrated Method 3 approach with Bloomberg expected values:
- Expected Duration: 16.3578392273866 years
- Expected Accrued per Million: 11,187.845
"""

import sys
sys.path.append('.')

from google_analysis10 import calculate_bond_metrics_with_conventions_using_shared_engine
import QuantLib as ql
import logging

# Set up logging to see debug info
logging.basicConfig(level=logging.INFO)

def test_treasury_integration():
    """Test the integrated Method 3 Treasury calculation"""
    
    print("🧪 TESTING TREASURY INTEGRATION WITH METHOD 3 + DEBUG")
    print("=" * 60)
    
    # Test data
    isin = "US912810TJ79"
    coupon = 3.0
    maturity_date = "2052-08-15"
    price = 71.66
    trade_date = ql.Date(30, 6, 2025)
    
    # Treasury handle (mock yield curve)
    treasury_handle = ql.YieldTermStructureHandle(
        ql.FlatForward(trade_date, 0.045, ql.ActualActual(ql.ActualActual.Bond))
    )
    
    # Treasury conventions
    ticker_conventions = {
        'day_count': 'ActualActual_Bond',
        'business_convention': 'Following',
        'frequency': 'Semiannual',
        'source': 'treasury',
        'treasury_override': True
    }
    
    print(f"📋 Test Bond: {isin}")
    print(f"💰 Price: {price}")
    print(f"📅 Trade Date: {trade_date}")
    print(f"📅 Maturity: {maturity_date}")
    print()
    
    # Expected Bloomberg values
    expected_duration = 16.3578392273866
    expected_accrued_per_million = 11187.845
    
    print(f"🎯 Bloomberg Expected Values:")
    print(f"   Duration: {expected_duration:.10f} years")
    print(f"   Accrued per Million: {expected_accrued_per_million:.3f}")
    print()
    
    # Run calculation
    try:
        result = calculate_bond_metrics_with_conventions_using_shared_engine(
            isin, coupon, maturity_date, price, trade_date, treasury_handle, ticker_conventions
        )
        
        if result and len(result) >= 4 and result[4] is None:  # No error
            yield_val, duration, spread, accrued, error = result
            
            print(f"💰 CALCULATION RESULTS:")
            print(f"   Yield: {yield_val:.5f}%")
            print(f"   Duration: {duration:.10f} years")
            print(f"   Spread: {spread:.0f} bps")
            print(f"   Accrued: {accrued:.4f}%")
            print()
            
            # Calculate differences
            duration_diff = duration - expected_duration
            accrued_as_per_million = (accrued / 100.0) * 1000000
            accrued_per_million_diff = accrued_as_per_million - expected_accrued_per_million
            
            print(f"📊 COMPARISON WITH BLOOMBERG:")
            print(f"   Duration Diff: {duration_diff:+.8f} years")
            print(f"   Accrued per Million: {accrued_as_per_million:.3f}")
            print(f"   Accrued per Million Diff: {accrued_per_million_diff:+.3f}")
            print()
            
            # Evaluation
            duration_close = abs(duration_diff) < 0.01
            accrued_close = abs(accrued_per_million_diff) < 100
            
            print(f"✅ EVALUATION:")
            print(f"   Duration Close: {'✅ YES' if duration_close else '❌ NO'} (within 0.01)")
            print(f"   Accrued Close: {'✅ YES' if accrued_close else '❌ NO'} (within 100)")
            print(f"   Overall: {'🎯 EXCELLENT' if duration_close and accrued_close else '⚠️ NEEDS IMPROVEMENT'}")
            
        else:
            print(f"❌ CALCULATION FAILED: {result[4] if result else 'Unknown error'}")
            
    except Exception as e:
        print(f"❌ INTEGRATION TEST FAILED: {str(e)}")

if __name__ == "__main__":
    test_treasury_integration()
