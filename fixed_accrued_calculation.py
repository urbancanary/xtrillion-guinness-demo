#!/usr/bin/env python3
"""
Fixed Accrued Interest Calculation
=================================

This fixes the issue where bond schedules are generated from settlement date
instead of properly determining the coupon payment schedule from maturity.

The fix ensures that coupon dates are correctly identified by working
backward from maturity date, which is the standard for bond calculations.
"""

import QuantLib as ql
import logging
from datetime import datetime, date, timedelta
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)

def generate_proper_bond_schedule(
    maturity_date: ql.Date,
    settlement_date: ql.Date,
    frequency,
    calendar,
    business_convention,
    day_counter,
    log_prefix: str = ""
) -> ql.Schedule:
    """
    Generate a proper bond schedule by working backward from maturity.
    
    This fixes the issue where schedules were generated from settlement date,
    which caused incorrect coupon dates for bonds like PEMEX.
    """
    logger.info(f"{log_prefix} Generating proper bond schedule from maturity date")
    
    # Step 1: Determine the period based on frequency
    if frequency == ql.Annual:
        period = ql.Period(1, ql.Years)
        months_between_coupons = 12
    elif frequency == ql.Semiannual:
        period = ql.Period(6, ql.Months)
        months_between_coupons = 6
    elif frequency == ql.Quarterly:
        period = ql.Period(3, ql.Months)
        months_between_coupons = 3
    else:
        raise ValueError(f"Unsupported frequency: {frequency}")
    
    logger.info(f"{log_prefix} Frequency: {frequency}, Period: {period}")
    
    # Step 2: Work backward from maturity to find all coupon dates
    coupon_dates = [maturity_date]
    current_date = maturity_date
    
    # Generate dates going backward until we're well before settlement
    # We go back far enough to ensure we capture the issue date
    max_periods = 200  # Safety limit (e.g., 100 years for semi-annual)
    periods_generated = 0
    
    while periods_generated < max_periods:
        # Move back by one period
        previous_date = calendar.advance(current_date, -period, business_convention)
        
        # Check if we've gone far enough back
        if previous_date < calendar.advance(settlement_date, ql.Period(-2, ql.Years)):
            break
            
        coupon_dates.insert(0, previous_date)
        current_date = previous_date
        periods_generated += 1
    
    # Add a reasonable issue date if we need more dates
    if len(coupon_dates) < 2:
        issue_date = calendar.advance(coupon_dates[0], -period, business_convention)
        coupon_dates.insert(0, issue_date)
    
    logger.info(f"{log_prefix} Generated {len(coupon_dates)} coupon dates")
    logger.info(f"{log_prefix} First coupon: {coupon_dates[0]}, Last coupon: {coupon_dates[-1]}")
    
    # Step 3: Find the last coupon date before or on settlement
    last_coupon_before_settlement = None
    next_coupon_after_settlement = None
    
    for i in range(len(coupon_dates) - 1):
        if coupon_dates[i] <= settlement_date < coupon_dates[i + 1]:
            last_coupon_before_settlement = coupon_dates[i]
            next_coupon_after_settlement = coupon_dates[i + 1]
            break
    
    if last_coupon_before_settlement:
        logger.info(f"{log_prefix} Last coupon before settlement: {last_coupon_before_settlement}")
        logger.info(f"{log_prefix} Next coupon after settlement: {next_coupon_after_settlement}")
        
        # Calculate accrued days
        days_accrued = day_counter.dayCount(last_coupon_before_settlement, settlement_date)
        days_in_period = day_counter.dayCount(last_coupon_before_settlement, next_coupon_after_settlement)
        logger.info(f"{log_prefix} Days accrued: {days_accrued} / {days_in_period}")
    
    # Step 4: Create the schedule using the first and last dates
    schedule = ql.Schedule(
        coupon_dates[0],  # Start from first coupon date
        maturity_date,    # End at maturity
        period,
        calendar,
        business_convention,
        business_convention,
        ql.DateGeneration.Backward,
        False
    )
    
    return schedule

def calculate_bond_metrics_FIXED_ACCRUED(
    isin: Optional[str],
    description: str,
    coupon: float,
    maturity_date: str,
    price: float,
    trade_date: str,
    is_treasury: bool = False,
    is_corporate: bool = True,
    settlement_days: int = 0
) -> Dict[str, Any]:
    """
    Fixed version with proper accrued interest calculation.
    
    This version ensures that bond schedules are generated correctly
    by working backward from maturity date instead of settlement date.
    """
    log_prefix = f"[FIXED_ACCRUED {isin or description}]"
    logger.info(f"{log_prefix} Starting calculation with proper schedule generation")
    
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
        
        # Determine conventions based on bond type
        if is_treasury:
            logger.info(f"{log_prefix} Treasury bond - using ActualActual day count")
            frequency = ql.Semiannual
            day_counter = ql.ActualActual(ql.ActualActual.Bond)
            business_convention = ql.Following
        else:
            logger.info(f"{log_prefix} Corporate bond - using 30/360 day count")
            frequency = ql.Semiannual
            day_counter = ql.Thirty360(ql.Thirty360.BondBasis)
            business_convention = ql.Following
        
        # Create maturity QuantLib date
        maturity_ql = ql.Date(maturity_date.day, maturity_date.month, maturity_date.year)
        
        # Generate proper bond schedule
        schedule = generate_proper_bond_schedule(
            maturity_ql,
            settlement_date,
            frequency,
            calendar,
            business_convention,
            day_counter,
            log_prefix
        )
        
        # Convert coupon to decimal
        coupon_decimal = coupon / 100.0
        logger.info(f"{log_prefix} Coupon: {coupon}% -> {coupon_decimal} (decimal)")
        
        # Create QuantLib bond
        bond = ql.FixedRateBond(
            0,  # settlement days (we handle this manually)
            100.0,  # Face value
            schedule,
            [coupon_decimal],
            day_counter
        )
        
        logger.info(f"{log_prefix} Bond created with proper schedule")
        
        # Calculate accrued interest
        accrued_amount = bond.accruedAmount(settlement_date)
        accrued_percent = accrued_amount  # QuantLib returns percentage directly
        accrued_per_million = accrued_amount * 10000
        
        logger.info(f"{log_prefix} Accrued interest: {accrued_percent:.6f}%")
        logger.info(f"{log_prefix} Accrued per million: ${accrued_per_million:,.2f}")
        
        # Calculate yield
        bond_yield_decimal = bond.bondYield(
            price,
            day_counter,
            ql.Compounded,
            frequency
        )
        
        # Calculate duration
        duration = ql.BondFunctions.duration(
            bond,
            bond_yield_decimal,
            day_counter,
            ql.Compounded,
            frequency,
            ql.Duration.Modified
        )
        
        # Calculate other metrics
        clean_price = price
        dirty_price = clean_price + accrued_percent
        
        # Calculate Macaulay duration
        macaulay_duration = ql.BondFunctions.duration(
            bond,
            bond_yield_decimal,
            day_counter,
            ql.Compounded,
            frequency,
            ql.Duration.Macaulay
        )
        
        # Calculate convexity
        convexity = ql.BondFunctions.convexity(
            bond,
            bond_yield_decimal,
            day_counter,
            ql.Compounded,
            frequency
        )
        
        # Calculate PVBP (Price Value of Basis Point)
        pvbp = ql.BondFunctions.basisPointValue(
            bond,
            bond_yield_decimal,
            day_counter,
            ql.Compounded,
            frequency
        )
        
        logger.info(f"{log_prefix} All calculations completed successfully")
        
        return {
            'status': 'success',
            'isin': isin,
            'description': description,
            'analytics': {
                'ytm': bond_yield_decimal * 100,
                'duration': duration,
                'macaulay_duration': macaulay_duration,
                'convexity': convexity,
                'accrued_interest': accrued_percent,
                'clean_price': clean_price,
                'dirty_price': dirty_price,
                'pvbp': abs(pvbp),
                'settlement_date': str(ql_to_date(settlement_date)),
                'accrued_per_million': accrued_per_million
            },
            'debug_info': {
                'schedule_dates': len(schedule),
                'day_count': str(day_counter),
                'frequency': frequency_to_string(frequency),
                'fix_applied': 'proper_schedule_generation_from_maturity'
            }
        }
        
    except Exception as e:
        logger.error(f"{log_prefix} Calculation failed: {e}", exc_info=True)
        return {
            'status': 'error',
            'error': str(e),
            'isin': isin,
            'description': description
        }

def ql_to_date(ql_date: ql.Date) -> date:
    """Convert QuantLib date to Python date"""
    return date(ql_date.year(), ql_date.month(), ql_date.dayOfMonth())

def frequency_to_string(freq) -> str:
    """Convert QuantLib frequency to string"""
    freq_map = {
        ql.Annual: "Annual",
        ql.Semiannual: "Semiannual",
        ql.Quarterly: "Quarterly",
        ql.Monthly: "Monthly"
    }
    return freq_map.get(freq, f"Unknown({freq})")

def test_pemex_fix():
    """Test the fix for PEMEX bond"""
    print("🧪 Testing PEMEX Bond Fix")
    print("=" * 60)
    
    result = calculate_bond_metrics_FIXED_ACCRUED(
        isin=None,
        description="PETROLEOS MEXICA, 6.95%, 28-Jan-2060",
        coupon=6.95,
        maturity_date="2060-01-28",
        price=100.0,
        trade_date="2025-04-21",
        is_treasury=False,
        is_corporate=True,
        settlement_days=0
    )
    
    if result['status'] == 'success':
        analytics = result['analytics']
        print(f"\n✅ Calculation successful!")
        print(f"   Accrued interest: {analytics['accrued_interest']:.6f}%")
        print(f"   Accrued per million: ${analytics['accrued_per_million']:,.2f}")
        print(f"   YTM: {analytics['ytm']:.5f}%")
        print(f"   Duration: {analytics['duration']:.3f} years")
        print(f"\n💡 Expected values:")
        print(f"   Accrued interest: 1.602361%")
        print(f"   Accrued per million: $16,023.61")
    else:
        print(f"\n❌ Calculation failed: {result.get('error')}")

if __name__ == "__main__":
    test_pemex_fix()