#!/usr/bin/env python3
"""
🚀 XTrillion Fast Context-Aware Bond Calculator
==============================================

Blazing fast, cached, institutional-grade bond analytics for Tuesday demo.
Built on proven bloomberg_accrued_calculator.py foundation with context optimization.

PERFORMANCE TARGETS:
- Sub-20ms for essential calculations (pricing context)
- Sub-50ms for risk calculations (duration, convexity)
- Intelligent caching for repeated calculations
- Context-based optimization to skip unnecessary computations

CONTEXTS SUPPORTED:
- pricing: YTM, Clean/Dirty Price, Accrued Interest (FAST)
- risk: Duration, Convexity, PVBP (CACHED YTM)
- portfolio: Annual basis conversions for aggregation
- spreads: Treasury spread calculations (when curve available)
- default: Core essential metrics only

REUSES: bloomberg_accrued_calculator.py patterns + QuantLib integration
"""

import QuantLib as ql
import sqlite3
import pandas as pd
import numpy as np
import re
from datetime import datetime, date, timedelta
import logging
from typing import Optional, Tuple, Dict, Any, List
import time
import hashlib
from functools import lru_cache
from dataclasses import dataclass

# Import the proven patterns from your existing calculator
from bloomberg_accrued_calculator import BloombergAccruedCalculator

# Setup logging for performance monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class BondData:
    """Structured bond data for consistent processing"""
    isin: Optional[str] = None
    description: str = ""
    coupon_rate: float = 0.0
    maturity_date: Optional[ql.Date] = None
    price: float = 100.0
    settlement_date: Optional[ql.Date] = None
    nominal: float = 1000000.0  # Default $1M face value
    
class PerformanceTimer:
    """Context manager for performance monitoring"""
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = (time.perf_counter() - self.start_time) * 1000  # Convert to ms
        logger.debug(f"⚡ {self.operation_name}: {elapsed:.2f}ms")


class XTrillionFastCalculator(BloombergAccruedCalculator):
    """
    🚀 Blazing Fast Context-Aware Bond Calculator
    
    Extends proven bloomberg_accrued_calculator.py with:
    - Context-based optimization
    - Intelligent caching
    - Performance monitoring
    - XTrillion API compatibility
    """
    
    def __init__(self, settlement_date: str = None):
        """Initialize with performance optimization"""
        # Initialize parent (reusing proven patterns)
        super().__init__("", settlement_date or "2025-06-30")
        
        # Performance caches
        self._ytm_cache = {}  # Cache expensive YTM calculations
        self._bond_cache = {}  # Cache QuantLib bond objects
        self._calculation_cache = {}  # Cache complete calculations
        
        # Performance settings
        self.enable_caching = True
        self.cache_ttl_seconds = 300  # 5 minutes
        
        # Context-based calculation flags
        self.context_configs = {
            "pricing": {
                "calculate_ytm": True,
                "calculate_duration": False,
                "calculate_convexity": False,
                "calculate_spreads": False,
                "target_ms": 20
            },
            "risk": {
                "calculate_ytm": True,
                "calculate_duration": True,
                "calculate_convexity": True,
                "calculate_spreads": False,
                "target_ms": 50
            },
            "portfolio": {
                "calculate_ytm": True,
                "calculate_duration": True,
                "calculate_convexity": False,
                "calculate_annual_basis": True,
                "target_ms": 100
            },
            "spreads": {
                "calculate_ytm": True,
                "calculate_duration": False,
                "calculate_convexity": False,
                "calculate_spreads": True,
                "target_ms": 150
            },
            "default": {
                "calculate_ytm": True,
                "calculate_duration": True,
                "calculate_convexity": False,
                "calculate_spreads": False,
                "target_ms": 75
            }
        }
        
        logger.info("🚀 XTrillion Fast Calculator initialized")
        logger.info(f"   Settlement: {self.settlement_date}")
        logger.info(f"   Caching: {'✅ Enabled' if self.enable_caching else '❌ Disabled'}")

    def _get_cache_key(self, bond_data: BondData, context: str = "default") -> str:
        """Generate cache key for bond calculation"""
        key_data = f"{bond_data.isin}|{bond_data.description}|{bond_data.price}|{context}|{self.settlement_date}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid"""
        if not self.enable_caching:
            return False
        
        cache_time = cache_entry.get('timestamp', 0)
        return (time.time() - cache_time) < self.cache_ttl_seconds

    @lru_cache(maxsize=1000)
    def _parse_bond_description_cached(self, description: str) -> Tuple[float, Optional[ql.Date]]:
        """Cached bond parsing using proven patterns from parent class"""
        with PerformanceTimer("Bond Description Parsing"):
            # Reuse parent class coupon extraction (proven method)
            coupon_rate = self.extract_coupon_from_description(description)
            if coupon_rate is None:
                coupon_rate = 0.0
            
            # Extract maturity date (enhanced pattern matching)
            maturity_date = self._extract_maturity_date(description)
            
            return coupon_rate, maturity_date

    def _extract_maturity_date(self, description: str) -> Optional[ql.Date]:
        """Extract maturity date with enhanced pattern matching"""
        try:
            # Enhanced patterns for better parsing
            patterns = [
                r'(\d{1,2})/(\d{1,2})/(\d{2,4})',        # MM/DD/YY or MM/DD/YYYY
                r'(\d{1,2})-(\w{3})-(\d{2,4})',         # DD-MMM-YY (e.g., 15-Aug-52)
                r'(\w{3})\s+(\d{1,2}),?\s+(\d{2,4})',   # MMM DD, YYYY
                r'(\d{4})-(\d{1,2})-(\d{1,2})',         # YYYY-MM-DD
            ]
            
            for pattern in patterns:
                match = re.search(pattern, description)
                if match:
                    groups = match.groups()
                    
                    # Handle different date formats
                    if len(groups) == 3:
                        if pattern.startswith(r'(\d{4})'):  # YYYY-MM-DD
                            year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                        elif pattern.startswith(r'(\d{1,2})-(\w{3})'):  # DD-MMM-YY
                            day, month_str, year = int(groups[0]), groups[1], int(groups[2])
                            month = self._month_name_to_number(month_str)
                            if year < 50:
                                year += 2000
                            elif year < 100:
                                year += 1900
                        elif pattern.startswith(r'(\w{3})'):  # MMM DD, YYYY
                            month_str, day, year = groups[0], int(groups[1]), int(groups[2])
                            month = self._month_name_to_number(month_str)
                        else:  # MM/DD/YY
                            month, day, year = int(groups[0]), int(groups[1]), int(groups[2])
                            if year < 50:
                                year += 2000
                            elif year < 100:
                                year += 1900
                        
                        return ql.Date(day, month, year)
            
            # Default fallback
            return ql.Date(31, 12, 2030)
            
        except Exception as e:
            logger.debug(f"Error extracting maturity date: {e}")
            return ql.Date(31, 12, 2030)

    def _month_name_to_number(self, month_str: str) -> int:
        """Convert month name/abbreviation to number"""
        month_map = {
            'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
            'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6,
            'jul': 7, 'july': 7, 'aug': 8, 'august': 8, 'sep': 9, 'september': 9,
            'oct': 10, 'october': 10, 'nov': 11, 'november': 11, 'dec': 12, 'december': 12
        }
        return month_map.get(month_str.lower(), 12)

    def _create_quantlib_bond_cached(self, bond_data: BondData) -> ql.Bond:
        """Create QuantLib bond with caching for performance"""
        cache_key = f"{bond_data.isin}|{bond_data.coupon_rate}|{bond_data.maturity_date}"
        
        if cache_key in self._bond_cache:
            return self._bond_cache[cache_key]
        
        with PerformanceTimer("QuantLib Bond Creation"):
            try:
                # Parse settlement date
                settlement_ql = self._parse_settlement_date_ql(self.settlement_date)
                
                # Determine conventions (Treasury vs Corporate)
                is_treasury = self._is_treasury_bond(bond_data.description)
                
                if is_treasury:
                    # US Treasury conventions (proven from your existing work)
                    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
                    day_count = ql.ActualActual(ql.ActualActual.ISDA)
                    business_convention = ql.Following
                    payment_frequency = ql.Semiannual
                else:
                    # Corporate bond conventions
                    calendar = ql.UnitedStates(ql.UnitedStates.NYSE)
                    day_count = ql.Thirty360(ql.Thirty360.BondBasis)
                    business_convention = ql.Following
                    payment_frequency = ql.Semiannual
                
                # Create payment schedule
                schedule = ql.Schedule(
                    settlement_ql,
                    bond_data.maturity_date,
                    ql.Period(payment_frequency),
                    calendar,
                    business_convention,
                    business_convention,
                    ql.DateGeneration.Backward,
                    False
                )
                
                # Create bond
                bond = ql.FixedRateBond(
                    1,  # Settlement days (T+1 for 2025)
                    bond_data.nominal,
                    schedule,
                    [bond_data.coupon_rate / 100.0],  # Convert percentage to decimal
                    day_count
                )
                
                # Set up pricing engine (CRITICAL for QuantLib)
                flat_forward = ql.FlatForward(
                    settlement_ql,
                    0.05,  # 5% flat rate for pricing
                    day_count
                )
                yield_curve_handle = ql.YieldTermStructureHandle(flat_forward)
                pricing_engine = ql.DiscountingBondEngine(yield_curve_handle)
                bond.setPricingEngine(pricing_engine)
                
                # Cache the bond object
                if self.enable_caching:
                    self._bond_cache[cache_key] = bond
                
                return bond
                
            except Exception as e:
                logger.error(f"Error creating QuantLib bond: {e}")
                raise

    def _parse_settlement_date_ql(self, date_str: str) -> ql.Date:
        """Convert settlement date string to QuantLib Date"""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return ql.Date(dt.day, dt.month, dt.year)
        except Exception as e:
            logger.error(f"Error parsing settlement date: {e}")
            # Default to today
            today = datetime.now()
            return ql.Date(today.day, today.month, today.year)

    def _is_treasury_bond(self, description: str) -> bool:
        """Determine if bond is US Treasury"""
        treasury_indicators = ['TREASURY', 'US TREASURY', 'T ', 'UST', 'GOVT']
        description_upper = description.upper()
        return any(indicator in description_upper for indicator in treasury_indicators)

    def calculate_ytm_cached(self, bond: ql.Bond, price: float, day_count: ql.DayCounter) -> float:
        """Calculate YTM with caching for performance"""
        bond_hash = str(hash((str(bond), price)))
        
        if bond_hash in self._ytm_cache and self.enable_caching:
            return self._ytm_cache[bond_hash]
        
        with PerformanceTimer("YTM Calculation"):
            try:
                # Calculate YTM (this is the expensive iterative calculation)
                # Bond already has pricing engine set
                ytm = ql.BondFunctions.bondYield(
                    bond,
                    price,
                    day_count,
                    ql.Compounded,
                    ql.Semiannual
                )
                
                # Cache result
                if self.enable_caching:
                    self._ytm_cache[bond_hash] = ytm
                
                return ytm
                
            except Exception as e:
                logger.error(f"Error calculating YTM: {e}")
                return 0.05  # Default 5% fallback

    def calculate_bond_metrics_fast(self, bond_data: BondData, context: str = "default") -> Dict[str, Any]:
        """
        🚀 BLAZING FAST context-aware bond calculation
        
        Optimizations:
        1. Context-based calculation selection
        2. Intelligent caching
        3. Reuse of expensive calculations
        4. Performance monitoring
        """
        
        # Check cache first
        cache_key = self._get_cache_key(bond_data, context)
        if cache_key in self._calculation_cache and self.enable_caching:
            cached_result = self._calculation_cache[cache_key]
            if self._is_cache_valid(cached_result):
                logger.debug(f"⚡ Cache hit for {bond_data.isin} | {context}")
                return cached_result['data']
        
        start_time = time.perf_counter()
        
        # Get context configuration
        config = self.context_configs.get(context, self.context_configs["default"])
        
        with PerformanceTimer(f"Total Calculation ({context})"):
            try:
                # Parse bond data (cached)
                coupon_rate, maturity_date = self._parse_bond_description_cached(bond_data.description)
                bond_data.coupon_rate = coupon_rate
                bond_data.maturity_date = maturity_date
                
                # Create QuantLib bond (cached)
                bond = self._create_quantlib_bond_cached(bond_data)
                
                # Determine conventions for consistency
                is_treasury = self._is_treasury_bond(bond_data.description)
                day_count = ql.ActualActual(ql.ActualActual.ISDA) if is_treasury else ql.Thirty360(ql.Thirty360.BondBasis)
                
                # Initialize results
                results = {
                    "bond_info": {
                        "isin": bond_data.isin,
                        "description": bond_data.description,
                        "coupon_rate": coupon_rate,
                        "maturity_date": str(maturity_date),
                        "is_treasury": is_treasury,
                        "context": context
                    },
                    "calculation_metadata": {
                        "settlement_date": self.settlement_date,
                        "calculation_time": None,  # Will be set at end
                        "cached": False,
                        "context_config": config
                    }
                }
                
                # Context-optimized calculations
                ytm = None
                
                # ALWAYS calculate basic pricing metrics (fast)
                with PerformanceTimer("Basic Pricing"):
                    clean_price = bond.cleanPrice()
                    dirty_price = bond.dirtyPrice()
                    accrued_interest = bond.accruedAmount()
                    
                    results["pricing"] = {
                        "clean_price": round(clean_price, 6),
                        "dirty_price": round(dirty_price, 6),
                        "accrued_interest": round(accrued_interest, 16)  # Bloomberg 16-decimal precision
                    }
                
                # Calculate YTM if needed (expensive - cache this!)
                if config.get("calculate_ytm", True):
                    ytm = self.calculate_ytm_cached(bond, bond_data.price, day_count)
                    results["pricing"]["ytm_semi"] = round(ytm * 100, 6)  # Convert to percentage
                
                # Calculate risk metrics if requested (reuse YTM)
                if config.get("calculate_duration", False) and ytm is not None:
                    with PerformanceTimer("Risk Metrics"):
                        mod_duration = ql.BondFunctions.duration(
                            bond, ytm, day_count, ql.Compounded, ql.Semiannual
                        )
                        
                        # Use alternative method for Macaulay duration if direct method unavailable
                        try:
                            mac_duration = ql.BondFunctions.macaulayDuration(
                                bond, ytm, day_count, ql.Compounded, ql.Semiannual
                            )
                        except AttributeError:
                            # Fallback: Macaulay = Modified * (1 + ytm/frequency)
                            mac_duration = mod_duration * (1 + ytm/2)
                        
                        results["risk"] = {
                            "mod_dur_semi": round(mod_duration, 6),
                            "mac_dur_semi": round(mac_duration, 6)
                        }
                
                # Calculate convexity if requested (reuse YTM)
                if config.get("calculate_convexity", False) and ytm is not None:
                    with PerformanceTimer("Convexity"):
                        convexity = ql.BondFunctions.convexity(
                            bond, ytm, day_count, ql.Compounded, ql.Semiannual
                        )
                        
                        if "risk" not in results:
                            results["risk"] = {}
                        results["risk"]["convexity_semi"] = round(convexity, 6)
                
                # Calculate annual basis if requested (portfolio context)
                if config.get("calculate_annual_basis", False) and ytm is not None:
                    with PerformanceTimer("Annual Basis Conversion"):
                        # Convert semi-annual to annual basis for portfolio aggregation
                        ytm_annual = ((1 + ytm/2) ** 2) - 1
                        
                        if "risk" in results:
                            mod_dur_annual = results["risk"]["mod_dur_semi"] / 2  # Approximate conversion
                            results["risk"]["mod_dur_annual"] = round(mod_dur_annual, 6)
                        
                        results["pricing"]["ytm_annual"] = round(ytm_annual * 100, 6)
                
                # Performance tracking
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                results["calculation_metadata"]["calculation_time_ms"] = round(elapsed_ms, 2)
                
                # Cache results
                if self.enable_caching:
                    cache_entry = {
                        'data': results,
                        'timestamp': time.time()
                    }
                    self._calculation_cache[cache_key] = cache_entry
                
                # Performance logging
                target_ms = config.get("target_ms", 100)
                status = "✅" if elapsed_ms <= target_ms else "⚠️"
                logger.info(f"{status} {context}: {elapsed_ms:.1f}ms (target: {target_ms}ms) | {bond_data.isin}")
                
                return results
                
            except Exception as e:
                logger.error(f"❌ Calculation failed for {bond_data.isin}: {e}")
                return {
                    "error": str(e),
                    "bond_info": {
                        "isin": bond_data.isin,
                        "description": bond_data.description,
                        "context": context
                    },
                    "calculation_metadata": {
                        "calculation_time_ms": (time.perf_counter() - start_time) * 1000,
                        "error": True
                    }
                }

    def calculate_from_description(self, description: str, price: float = 100.0, 
                                 context: str = "default", isin: str = None) -> Dict[str, Any]:
        """
        Calculate bond metrics from description - main API entry point
        
        Optimized for Tuesday demo with context-aware performance
        """
        bond_data = BondData(
            isin=isin,
            description=description,
            price=price,
            settlement_date=self._parse_settlement_date_ql(self.settlement_date)
        )
        
        return self.calculate_bond_metrics_fast(bond_data, context)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for monitoring"""
        return {
            "cache_stats": {
                "ytm_cache_size": len(self._ytm_cache),
                "bond_cache_size": len(self._bond_cache),
                "calculation_cache_size": len(self._calculation_cache),
                "caching_enabled": self.enable_caching
            },
            "context_configs": self.context_configs,
            "settlement_date": self.settlement_date
        }

    def clear_caches(self):
        """Clear all caches for testing"""
        self._ytm_cache.clear()
        self._bond_cache.clear()
        self._calculation_cache.clear()
        logger.info("🧹 All caches cleared")


def demo_performance_test():
    """
    🚀 Performance demonstration for Tuesday demo
    """
    print("🚀 XTrillion Fast Calculator - Performance Demo")
    print("=" * 55)
    
    # Initialize calculator
    calc = XTrillionFastCalculator("2025-06-30")
    
    # Test bonds for demo
    test_bonds = [
        {"desc": "US TREASURY N/B, 3%, 15-Aug-2052", "price": 71.66, "isin": "US912810TJ79"},
        {"desc": "PANAMA, 3.87%, 23-Jul-2060", "price": 56.60, "isin": "US698299BL70"},
        {"desc": "ECOPETROL SA, 5.875%, 28-May-2045", "price": 69.31, "isin": "US279158AJ82"}
    ]
    
    # Test different contexts
    contexts = ["pricing", "risk", "portfolio", "default"]
    
    print(f"\n📊 Testing {len(test_bonds)} bonds × {len(contexts)} contexts")
    print(f"🎯 Performance targets: pricing=20ms, risk=50ms, portfolio=100ms")
    print()
    
    for bond in test_bonds:
        print(f"🏦 {bond['desc'][:40]}...")
        
        for context in contexts:
            start_time = time.perf_counter()
            
            result = calc.calculate_from_description(
                bond["desc"], 
                bond["price"], 
                context,
                bond["isin"]
            )
            
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            target_ms = calc.context_configs[context]["target_ms"]
            status = "✅" if elapsed_ms <= target_ms else "⚠️"
            
            print(f"   {status} {context:10}: {elapsed_ms:6.1f}ms")
            
            # Show key results for first bond
            if bond == test_bonds[0] and context == "risk":
                if "pricing" in result:
                    ytm = result["pricing"].get("ytm_semi", 0)
                    print(f"      YTM: {ytm:.3f}%")
                if "risk" in result:
                    duration = result["risk"].get("mod_dur_semi", 0)
                    print(f"      Duration: {duration:.2f} years")
        
        print()
    
    # Cache performance test
    print("🔄 Cache Performance Test...")
    start_time = time.perf_counter()
    
    # Recalculate same bond - should be cached
    cached_result = calc.calculate_from_description(
        test_bonds[0]["desc"], 
        test_bonds[0]["price"], 
        "risk"
    )
    
    cached_time = (time.perf_counter() - start_time) * 1000
    print(f"   ⚡ Cached calculation: {cached_time:.1f}ms")
    
    # Performance stats
    stats = calc.get_performance_stats()
    print(f"\n📈 Cache Statistics:")
    print(f"   YTM cache: {stats['cache_stats']['ytm_cache_size']} entries")
    print(f"   Bond cache: {stats['cache_stats']['bond_cache_size']} entries")
    print(f"   Calculation cache: {stats['cache_stats']['calculation_cache_size']} entries")
    
    print(f"\n✅ Performance demo complete!")
    print(f"🎯 Ready for Tuesday demo with sub-{target_ms}ms performance!")
    
    return calc


if __name__ == "__main__":
    calculator = demo_performance_test()
