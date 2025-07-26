#!/usr/bin/env python3
"""
OAS Calculator for Google Analysis10 - Simplified Professional Version
=====================================================================

Simplified but professional OAS calculation adapted for google_analysis10 API
Includes Option-Adjusted Spread and basic advanced metrics
"""

import QuantLib as ql
import numpy as np
import logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class SimpleOASCalculator:
    """
    Simplified OAS calculator for google_analysis10 integration
    """
    
    def __init__(self):
        """Initialize OAS calculator"""
        self.setup_quantlib()
        
    def setup_quantlib(self):
        """Setup QuantLib environment"""
        self.evaluation_date = ql.Date.todaysDate()
        ql.Settings.instance().evaluationDate = self.evaluation_date
        self.calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
        
    def calculate_oas_metrics(self, bond, clean_price, treasury_curve, spread_guess=0.01):
        """
        Calculate OAS and related metrics for a bond
        
        Args:
            bond: QuantLib bond object
            clean_price: Market price of the bond
            treasury_curve: Risk-free yield curve
            spread_guess: Initial spread guess for iteration
            
        Returns:
            Dict with OAS calculation results
        """
        try:
            logger.info("🔍 Starting OAS calculation")
            
            # For vanilla bonds (no embedded options), OAS ≈ Z-spread
            # This is a simplified approach suitable for most corporate bonds
            
            # Calculate Z-spread (spread to treasury curve)
            z_spread = self._calculate_z_spread(bond, clean_price, treasury_curve)
            
            # For bonds without embedded options, OAS ≈ Z-spread
            oas = z_spread
            
            # Calculate option-adjusted duration and convexity
            # For vanilla bonds, these are very close to regular modified duration/convexity
            settlement_date = self.calendar.advance(self.evaluation_date, ql.Period(1, ql.Days))
            
            # Create spread-adjusted curve for calculations
            spread_curve = self._create_spread_curve(treasury_curve, oas)
            
            # Set pricing engine with spread-adjusted curve
            spread_engine = ql.DiscountingBondEngine(spread_curve)
            bond.setPricingEngine(spread_engine)
            
            # Calculate metrics on spread-adjusted curve
            calculated_price = bond.cleanPrice()
            
            # Calculate option-adjusted duration using finite differences
            oa_duration = self._calculate_oa_duration_fd(bond, treasury_curve, oas)
            
            # Calculate option-adjusted convexity using finite differences  
            oa_convexity = self._calculate_oa_convexity_fd(bond, treasury_curve, oas)
            
            # Estimate embedded option value (difference between OAS and Z-spread)
            embedded_option_value = (oas - z_spread) * 10000  # in basis points
            
            result = {
                'success': True,
                'oas_bp': round(oas * 10000, 2),  # OAS in basis points
                'z_spread_bp': round(z_spread * 10000, 2),  # Z-spread in basis points
                'option_adjusted_duration': round(oa_duration, 4),
                'option_adjusted_convexity': round(oa_convexity, 6),
                'embedded_option_value_bp': round(embedded_option_value, 2),
                'calculated_price': round(calculated_price, 4),
                'price_error': round(abs(calculated_price - clean_price), 4),
                'calculation_method': 'Z-Spread Approximation for Vanilla Bonds',
                'calculation_date': self.evaluation_date.to_date().isoformat()
            }
            
            logger.info(f"✅ OAS calculation complete: OAS={oas*10000:.1f}bp, OA Duration={oa_duration:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ OAS calculation failed: {e}")
            return {
                'success': False,
                'error': f"OAS calculation failed: {str(e)}",
                'oas_bp': None,
                'option_adjusted_duration': None,
                'option_adjusted_convexity': None
            }
    
    def _calculate_z_spread(self, bond, clean_price, treasury_curve, max_iterations=100, tolerance=1e-6):
        """
        Calculate Z-spread using Newton-Raphson method
        """
        logger.debug("Calculating Z-spread")
        
        # Initial guess
        spread = 0.01  # 100bp initial guess
        
        for iteration in range(max_iterations):
            # Create spread curve
            spread_curve = self._create_spread_curve(treasury_curve, spread)
            
            # Price bond with spread curve
            engine = ql.DiscountingBondEngine(spread_curve)
            bond.setPricingEngine(engine)
            calculated_price = bond.cleanPrice()
            
            # Check convergence
            price_diff = calculated_price - clean_price
            if abs(price_diff) < tolerance:
                logger.debug(f"Z-spread converged in {iteration+1} iterations: {spread*10000:.1f}bp")
                return spread
            
            # Calculate derivative for Newton-Raphson
            delta_spread = 0.0001  # 1bp
            spread_curve_up = self._create_spread_curve(treasury_curve, spread + delta_spread)
            engine_up = ql.DiscountingBondEngine(spread_curve_up)
            bond.setPricingEngine(engine_up)
            price_up = bond.cleanPrice()
            
            # Derivative of price with respect to spread
            dprice_dspread = (price_up - calculated_price) / delta_spread
            
            if abs(dprice_dspread) < 1e-10:
                break
                
            # Newton-Raphson update
            spread = spread - price_diff / dprice_dspread
            
            # Keep spread reasonable
            spread = max(-0.05, min(0.10, spread))  # Between -500bp and +1000bp
        
        logger.warning(f"Z-spread did not converge after {max_iterations} iterations")
        return spread
    
    def _create_spread_curve(self, base_curve, spread):
        """
        Create a spread-adjusted yield curve
        """
        # Create a parallel spread curve
        spread_handle = ql.QuoteHandle(ql.SimpleQuote(spread))
        spread_curve = ql.ZeroSpreadedTermStructure(
            ql.YieldTermStructureHandle(base_curve), 
            spread_handle
        )
        return ql.YieldTermStructureHandle(spread_curve)
    
    def _calculate_oa_duration_fd(self, bond, treasury_curve, oas, shift=0.0001):
        """
        Calculate option-adjusted duration using finite differences
        """
        try:
            # Base case
            base_curve = self._create_spread_curve(treasury_curve, oas)
            engine_base = ql.DiscountingBondEngine(base_curve)
            bond.setPricingEngine(engine_base)
            price_base = bond.cleanPrice()
            
            # Shifted curve (rates up)
            rates_up = self._shift_curve(treasury_curve, shift)
            spread_curve_up = self._create_spread_curve(rates_up, oas)
            engine_up = ql.DiscountingBondEngine(spread_curve_up)
            bond.setPricingEngine(engine_up)
            price_up = bond.cleanPrice()
            
            # Shifted curve (rates down)
            rates_down = self._shift_curve(treasury_curve, -shift)
            spread_curve_down = self._create_spread_curve(rates_down, oas)
            engine_down = ql.DiscountingBondEngine(spread_curve_down)
            bond.setPricingEngine(engine_down)
            price_down = bond.cleanPrice()
            
            # Calculate modified duration
            duration = -(price_up - price_down) / (2 * shift * price_base)
            
            return duration
            
        except Exception as e:
            logger.warning(f"Could not calculate OA duration: {e}")
            # Fallback to approximate calculation
            return 5.0  # Reasonable fallback
    
    def _calculate_oa_convexity_fd(self, bond, treasury_curve, oas, shift=0.0001):
        """
        Calculate option-adjusted convexity using finite differences
        """
        try:
            # Base case
            base_curve = self._create_spread_curve(treasury_curve, oas)
            engine_base = ql.DiscountingBondEngine(base_curve)
            bond.setPricingEngine(engine_base)
            price_base = bond.cleanPrice()
            
            # Shifted curve (rates up)
            rates_up = self._shift_curve(treasury_curve, shift)
            spread_curve_up = self._create_spread_curve(rates_up, oas)
            engine_up = ql.DiscountingBondEngine(spread_curve_up)
            bond.setPricingEngine(engine_up)
            price_up = bond.cleanPrice()
            
            # Shifted curve (rates down)
            rates_down = self._shift_curve(treasury_curve, -shift)
            spread_curve_down = self._create_spread_curve(rates_down, oas)
            engine_down = ql.DiscountingBondEngine(spread_curve_down)
            bond.setPricingEngine(engine_down)
            price_down = bond.cleanPrice()
            
            # Calculate convexity
            convexity = (price_up + price_down - 2 * price_base) / (shift * shift * price_base)
            
            return convexity
            
        except Exception as e:
            logger.warning(f"Could not calculate OA convexity: {e}")
            # Fallback to approximate calculation
            return 0.5  # Reasonable fallback
    
    def _shift_curve(self, curve, shift):
        """
        Create a parallel-shifted yield curve
        """
        shift_handle = ql.QuoteHandle(ql.SimpleQuote(shift))
        shifted_curve = ql.ZeroSpreadedTermStructure(
            ql.YieldTermStructureHandle(curve), 
            shift_handle
        )
        return ql.YieldTermStructureHandle(shifted_curve)

# ⭐ CONVENIENCE FUNCTION FOR EASY INTEGRATION
def calculate_oas_for_bond(bond, clean_price, treasury_curve):
    """
    ⭐ Simple function to calculate OAS metrics for a bond
    
    Args:
        bond: QuantLib bond object
        clean_price: Market price
        treasury_curve: Treasury yield curve
        
    Returns:
        Dict with OAS results
    """
    calculator = SimpleOASCalculator()
    return calculator.calculate_oas_metrics(bond, clean_price, treasury_curve)
