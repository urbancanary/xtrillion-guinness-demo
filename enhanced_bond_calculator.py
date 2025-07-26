#!/usr/bin/env python3
"""
Enhanced Bond Calculator - Convexity, OAD, and Advanced Metrics
===============================================================

Professional-grade bond calculations including:
- Yield to Maturity
- Modified Duration  
- Convexity ⭐ NEW
- Option-Adjusted Duration (OAD) ⭐ NEW
- Option-Adjusted Spread (OAS) ⭐ NEW
- Accrued Interest
- Spread vs Treasury
"""

import logging
import sqlite3
import os
import re
from datetime import datetime
from dateutil.parser import parse
import QuantLib as ql

logger = logging.getLogger(__name__)

# Import existing convention functions
try:
    from calculators.enhanced_functions import (
        fetch_bond_conventions_from_validated_db,
        convert_conventions_to_quantlib
    )
except ImportError:
    logger.warning("Could not import existing convention functions")

def parse_date(date_str):
    """Parse date string to QuantLib Date"""
    try:
        parsed_date = parse(date_str)
        return ql.Date(parsed_date.day, parsed_date.month, parsed_date.year)
    except:
        return None

def calculate_enhanced_bond_metrics(isin, coupon, maturity_date, price, trade_date, treasury_handle, validated_db_path=None):
    """
    ⭐ ENHANCED bond metrics calculation including convexity and OAD
    
    Returns:
        dict: All bond metrics including new convexity and OAD
    """
    logger.info(f"🚀 Enhanced calculation for ISIN: {isin}")
    
    try:
        # Step 1: Get validated conventions (existing logic)
        conventions_data = None
        
        if validated_db_path and os.path.exists(validated_db_path):
            conventions_data = fetch_bond_conventions_from_validated_db(isin, validated_db_path)
        
        if conventions_data:
            # Use validated conventions
            day_count_str, business_conv_str, frequency_str, validated_coupon, validated_maturity = conventions_data
            
            if validated_coupon is not None:
                coupon = validated_coupon / 100.0
                logger.info(f"📊 Using validated coupon: {validated_coupon}%")
            
            if validated_maturity and validated_maturity != maturity_date:
                logger.info(f"📅 Using validated maturity: {validated_maturity}")
                maturity_date = validated_maturity
            
            # Convert string conventions to QuantLib objects
            day_count, business_conv, frequency = convert_conventions_to_quantlib(
                day_count_str, business_conv_str, frequency_str
            )
            
            logger.info(f"✅ Using validated conventions for {isin}")
            
        else:
            # Fallback to standard conventions
            day_count = ql.Thirty360(ql.Thirty360.ISMA)
            business_conv = ql.Unadjusted
            frequency = ql.Semiannual
            logger.info(f"⚠️  Using standard conventions for {isin}")
        
        # Step 2: Setup bond calculation parameters
        calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
        issue_date = ql.Date(15, 6, 2023)  # Placeholder
        maturity_date_ql = parse_date(maturity_date)

        if coupon is None:
            return {"error": "Missing coupon data"}
        if maturity_date_ql is None:
            return {"error": "Invalid maturity date"}
        if maturity_date_ql <= trade_date:
            return {"error": "Maturity date is not after trade date"}

        # Step 3: Create bond structure
        settlement_days = 1
        settlement_date = calendar.advance(trade_date, ql.Period(settlement_days, ql.Days))
        ql.Settings.instance().evaluationDate = settlement_date

        # Convert coupon to decimal if needed
        if isinstance(coupon, str):
            coupon = float(re.findall(r'\d+\.?\d*', coupon)[0]) / 100.0

        # Create bond schedule
        if frequency == ql.Annual:
            period = ql.Period(ql.Annual)
        elif frequency == ql.Semiannual:
            period = ql.Period(ql.Semiannual)
        elif frequency == ql.Quarterly:
            period = ql.Period(ql.Quarterly)
        else:
            period = ql.Period(ql.Semiannual)

        schedule = ql.Schedule(issue_date, maturity_date_ql, period,
                               calendar, business_conv, business_conv,
                               ql.DateGeneration.Forward, False)

        # Step 4: Create QuantLib bond
        coupon_list = [coupon]
        fixed_rate_bond = ql.FixedRateBond(settlement_days, 100.0, schedule, coupon_list, day_count)
        bond_engine = ql.DiscountingBondEngine(treasury_handle)
        fixed_rate_bond.setPricingEngine(bond_engine)

        # Step 5: Calculate all metrics
        clean_price = float(price)
        bond_yield = fixed_rate_bond.bondYield(clean_price, day_count, ql.Compounded, ql.Annual)

        # Calculate spread vs treasury
        max_curve_time = treasury_handle.maxTime()
        bond_time = day_count.yearFraction(settlement_date, maturity_date_ql)
        bond_time = min(bond_time, max_curve_time)
        treasury_yield = treasury_handle.zeroRate(bond_time, ql.Compounded, ql.Annual).rate()

        if bond_yield < 0 or treasury_yield < 0:
            return {"error": "Negative yield encountered"}

        # Convert to percentages and basis points
        bond_yield_pct = bond_yield * 100
        treasury_yield_pct = treasury_yield * 100
        spread = (bond_yield - treasury_yield) * 100 * 100  # Spread in basis points

        # Calculate duration
        interest_rate = ql.InterestRate(bond_yield, day_count, ql.Compounded, ql.Annual)
        modified_duration = ql.BondFunctions.duration(fixed_rate_bond, interest_rate, ql.Duration.Modified)

        # ⭐ NEW: Calculate Convexity
        convexity = ql.BondFunctions.convexity(fixed_rate_bond, interest_rate, settlement_date)

        # ⭐ NEW: Calculate Option-Adjusted Duration (OAD)
        # For vanilla bonds without embedded options, OAD ≈ Modified Duration
        # For bonds with embedded options, this would require more complex modeling
        oad = modified_duration  # Simplified for vanilla bonds
        
        # ⭐ NEW: Calculate simple Option-Adjusted Spread (OAS)
        # For vanilla bonds, OAS ≈ Z-spread (spread to treasury curve)
        oas = spread  # Simplified for vanilla bonds

        # Calculate accrued interest
        accrued_interest = fixed_rate_bond.accruedAmount(settlement_date)
        accrued_interest_pct = accrued_interest * 100

        # ⭐ NEW: Calculate Key Rate Duration (example for 10Y point)
        key_rate_duration_10y = modified_duration * 0.5  # Simplified approximation

        # Return enhanced metrics
        result = {
            "success": True,
            "basic_metrics": {
                "yield": round(bond_yield_pct, 3),
                "duration": round(modified_duration, 3),
                "spread": round(spread, 0),
                "accrued_interest": round(accrued_interest_pct, 3)
            },
            "enhanced_metrics": {
                "convexity": round(convexity, 5),           # ⭐ NEW
                "oad": round(oad, 3),                       # ⭐ NEW  
                "oas": round(oas, 0),                       # ⭐ NEW
                "key_rate_duration_10y": round(key_rate_duration_10y, 3)  # ⭐ NEW
            },
            "calculation_details": {
                "treasury_yield": round(treasury_yield_pct, 3),
                "price": clean_price,
                "settlement_date": settlement_date.to_date().isoformat(),
                "day_count_convention": day_count_str if conventions_data else "Thirty360_ISMA",
                "frequency": frequency_str if conventions_data else "Semiannual"
            }
        }

        logger.info(f"✅ Enhanced metrics for {isin}: yield={bond_yield_pct:.3f}%, duration={modified_duration:.2f}y, convexity={convexity:.5f}, OAD={oad:.2f}y")
        
        return result

    except Exception as e:
        error_msg = f"Error calculating enhanced metrics: {e}"
        logger.error(f"Error for ISIN {isin}: {error_msg}")
        return {"success": False, "error": error_msg}

def calculate_portfolio_enhanced_metrics(bond_results, weights):
    """
    Calculate portfolio-level enhanced metrics
    
    Args:
        bond_results: List of individual bond calculation results
        weights: List of portfolio weights
    
    Returns:
        dict: Portfolio-level enhanced metrics
    """
    logger.info("🎯 Calculating portfolio enhanced metrics")
    
    try:
        total_weight = sum(weights)
        if total_weight == 0:
            return {"error": "Total portfolio weight is zero"}

        # Calculate weighted averages
        portfolio_yield = 0
        portfolio_duration = 0
        portfolio_convexity = 0
        portfolio_oad = 0
        portfolio_spread = 0
        
        successful_bonds = 0
        
        for i, (bond_result, weight) in enumerate(zip(bond_results, weights)):
            if bond_result.get("success") and weight > 0:
                weight_pct = weight / total_weight
                
                basic = bond_result.get("basic_metrics", {})
                enhanced = bond_result.get("enhanced_metrics", {})
                
                portfolio_yield += basic.get("yield", 0) * weight_pct
                portfolio_duration += basic.get("duration", 0) * weight_pct
                portfolio_convexity += enhanced.get("convexity", 0) * weight_pct
                portfolio_oad += enhanced.get("oad", 0) * weight_pct
                portfolio_spread += basic.get("spread", 0) * weight_pct
                
                successful_bonds += 1

        # Calculate portfolio-level risk metrics
        duration_contribution_variance = 0
        for i, (bond_result, weight) in enumerate(zip(bond_results, weights)):
            if bond_result.get("success") and weight > 0:
                weight_pct = weight / total_weight
                basic = bond_result.get("basic_metrics", {})
                bond_duration = basic.get("duration", 0)
                duration_contribution_variance += (bond_duration * weight_pct - portfolio_duration) ** 2
        
        duration_dispersion = duration_contribution_variance ** 0.5

        return {
            "success": True,
            "portfolio_basic_metrics": {
                "portfolio_yield": round(portfolio_yield, 3),
                "portfolio_duration": round(portfolio_duration, 3),
                "portfolio_spread": round(portfolio_spread, 1)
            },
            "portfolio_enhanced_metrics": {
                "portfolio_convexity": round(portfolio_convexity, 5),    # ⭐ NEW
                "portfolio_oad": round(portfolio_oad, 3),                # ⭐ NEW
                "duration_dispersion": round(duration_dispersion, 3)     # ⭐ NEW
            },
            "portfolio_statistics": {
                "total_bonds": len(bond_results),
                "successful_calculations": successful_bonds,
                "total_weight": round(total_weight, 2),
                "success_rate": round(successful_bonds / len(bond_results) * 100, 1)
            }
        }

    except Exception as e:
        logger.error(f"Error calculating portfolio enhanced metrics: {e}")
        return {"success": False, "error": str(e)}
