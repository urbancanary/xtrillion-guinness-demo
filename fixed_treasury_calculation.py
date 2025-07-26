#!/usr/bin/env python3
"""
Fixed Treasury Duration Calculation
==================================

This fixes the 16.60 vs 16.35 duration issue by ensuring correct yield units
and consistent frequency usage in QuantLib calculations.
"""

import QuantLib as ql
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)

def calculate_bond_metrics_FIXED(isin, coupon, maturity_date, price, trade_date, 
                                is_treasury=False, settlement_days=0):
    """
    FIXED version of bond calculation with correct yield units and frequency
    
    The issue was in yield unit handling - QuantLib bondYield returns decimal
    but duration calculation needs to use the same decimal format.
    """
    log_prefix = f"[FIXED_CALC ISIN: {isin}, T+{settlement_days}]"
    logger.info(f"{log_prefix} Starting FIXED calculation.")
    
    try:
        # Parse dates
        if isinstance(maturity_date, str):
            maturity_date = datetime.strptime(maturity_date, '%Y-%m-%d').date()
        if isinstance(trade_date, str):
            trade_date = datetime.strptime(trade_date, '%Y-%m-%d').date()
            
        # Set up QuantLib
        calculation_date = ql.Date(trade_date.day, trade_date.month, trade_date.year)
        ql.Settings.instance().evaluationDate = calculation_date
        
        # Set up calendar and settlement
        calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
        settlement_date = calendar.advance(calculation_date, ql.Period(settlement_days, ql.Days))
        
        # CRITICAL FIX: Use consistent conventions for Treasury bonds
        if is_treasury:
            logger.info(f"{log_prefix} TREASURY DETECTED - Using Bloomberg-validated conventions")
            frequency = ql.Semiannual  # ✅ FIXED: Explicitly use semiannual
            day_counter = ql.ActualActual(ql.ActualActual.ISDA)  # ✅ FIXED: Correct Treasury day count
            logger.info(f"{log_prefix} Treasury frequency: {frequency} (2=Semiannual)")
            logger.info(f"{log_prefix} Treasury day count: {day_counter}")
        else:
            frequency = ql.Semiannual  # Default for most bonds
            day_counter = ql.Thirty360(ql.Thirty360.BondBasis)
            
        # Create bond schedule
        maturity_ql = ql.Date(maturity_date.day, maturity_date.month, maturity_date.year)
        schedule = ql.Schedule(
            settlement_date, maturity_ql,
            ql.Period(frequency),
            calendar,
            ql.Following, ql.Following,
            ql.DateGeneration.Backward,
            False
        )
        
        # CRITICAL FIX: Convert coupon to decimal format for QuantLib
        coupon_decimal = coupon / 100.0
        logger.info(f"{log_prefix} Coupon: {coupon}% -> {coupon_decimal} (decimal)")
        
        # Create QuantLib bond
        bond = ql.FixedRateBond(
            settlement_days,
            100.0,  # Face value
            schedule,
            [coupon_decimal],
            day_counter
        )
        
        logger.info(f"{log_prefix} Bond created successfully")
        
        # CRITICAL FIX: Calculate yield with explicit frequency matching
        logger.info(f"{log_prefix} Calculating yield for price {price} with frequency {frequency}")
        
        bond_yield_decimal = bond.bondYield(
            price,
            day_counter,
            ql.Compounded,
            frequency  # ✅ FIXED: Use same frequency consistently
        )
        
        logger.info(f"{log_prefix} Yield calculated: {bond_yield_decimal:.6f} (decimal) = {bond_yield_decimal*100:.5f}%")
        
        # CRITICAL FIX: Use the SAME yield format and frequency for duration
        logger.info(f"{log_prefix} Calculating duration with SAME yield format and frequency")
        
        duration = ql.BondFunctions.duration(
            bond,
            bond_yield_decimal,  # ✅ FIXED: Use decimal format yield directly
            day_counter,
            ql.Compounded,
            frequency,  # ✅ FIXED: Same frequency as yield calculation
            ql.Duration.Modified
        )
        
        logger.info(f"{log_prefix} Duration calculated: {duration:.6f}")
        
        # Calculate convexity for completeness
        convexity = ql.BondFunctions.convexity(
            bond,
            bond_yield_decimal,
            day_counter,
            ql.Compounded,
            frequency
        )
        
        logger.info(f"{log_prefix} FIXED calculation successful!")
        
        return {
            'isin': isin,
            'yield_decimal': bond_yield_decimal,
            'yield_percent': bond_yield_decimal * 100,
            'duration': duration,
            'convexity': convexity,
            'frequency_used': frequency,
            'day_count_used': str(day_counter),
            'successful': True,
            'fix_applied': 'yield_unit_consistency_and_frequency_matching'
        }
        
    except Exception as e:
        logger.error(f"{log_prefix} FIXED calculation failed: {e}", exc_info=True)
        return {
            'isin': isin,
            'successful': False,
            'error': str(e)
        }

def test_fixed_calculation():
    """Test the fixed calculation against the Treasury bond"""
    
    print("🔧 TESTING FIXED TREASURY CALCULATION")
    print("=" * 60)
    
    # The problematic Treasury bond
    test_data = {
        'isin': 'US912810TJ79',
        'coupon': 3.0,  # 3% coupon
        'maturity_date': '2052-08-15',
        'price': 71.66,
        'trade_date': '2025-06-30',
        'expected_yield': 4.89960,
        'expected_duration': 16.35658
    }
    
    print(f"📊 Testing Treasury: {test_data['isin']}")
    print(f"💰 Price: {test_data['price']}")
    print(f"🎯 Expected Yield: {test_data['expected_yield']:.5f}%")
    print(f"🎯 Expected Duration: {test_data['expected_duration']:.5f}")
    print()
    
    # Test the FIXED calculation
    result = calculate_bond_metrics_FIXED(
        isin=test_data['isin'],
        coupon=test_data['coupon'],
        maturity_date=test_data['maturity_date'],
        price=test_data['price'],
        trade_date=test_data['trade_date'],
        is_treasury=True,
        settlement_days=0
    )
    
    if result['successful']:
        yield_diff = abs(result['yield_percent'] - test_data['expected_yield'])
        duration_diff = abs(result['duration'] - test_data['expected_duration'])
        
        print("✅ FIXED CALCULATION RESULTS:")
        print(f"   📈 Yield: {result['yield_percent']:.5f}% (expected: {test_data['expected_yield']:.5f}%)")
        print(f"   📊 Yield Difference: {yield_diff:.5f}%")
        print(f"   ⏱️  Duration: {result['duration']:.5f} (expected: {test_data['expected_duration']:.5f})")
        print(f"   📊 Duration Difference: {duration_diff:.5f}")
        print(f"   🔧 Frequency Used: {result['frequency_used']}")
        print(f"   📅 Day Count: {result['day_count_used']}")
        print(f"   🛠️  Fix Applied: {result['fix_applied']}")
        print()
        
        # Check if the fix worked
        if duration_diff < 0.1:  # Within 0.1 years
            print("🎉 SUCCESS! Duration calculation FIXED!")
            print("✅ The yield unit consistency fix resolved the issue")
        else:
            print("⚠️ Duration still has significant difference")
            print("🔍 May need additional investigation")
            
        if yield_diff < 0.01:  # Within 1bp
            print("✅ Yield calculation accurate")
        else:
            print("⚠️ Yield may need fine-tuning")
            
    else:
        print(f"❌ FIXED calculation failed: {result['error']}")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    test_fixed_calculation()
