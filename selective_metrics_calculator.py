#!/usr/bin/env python3
"""
Selective Metrics Calculator for XTrillion Bond API
Optimized calculation engine that only computes requested metrics
"""

import logging
from typing import Dict, Any, List, Optional, Set
from bond_master_hierarchy_enhanced import calculate_bond_master

logger = logging.getLogger(__name__)

# Default metrics for different endpoints
DEFAULT_QUICK_METRICS = ["ytm", "duration", "spread"]
DEFAULT_FULL_METRICS = None  # None means return all available metrics

# All available metrics
AVAILABLE_METRICS = {
    # Core metrics (native convention)
    "ytm",                      # Yield to maturity (native)
    "duration",                 # Modified duration (native)
    "spread",                   # G-spread
    "macaulay_duration",        # Macaulay duration
    
    # Convention-specific yields
    "ytm_semi",                 # Semi-annual yield
    "ytm_annual",               # Annual yield
    
    # Convention-specific durations
    "duration_semi",            # Semi-annual duration
    "duration_annual",          # Annual duration
    "macaulay_duration_semi",   # Macaulay duration (semi)
    "macaulay_duration_annual", # Macaulay duration (annual)
    
    # Pricing metrics
    "clean_price",              # Clean price
    "dirty_price",              # Dirty price
    "accrued_interest",         # Accrued interest
    "accrued_per_million",      # Accrued per million
    
    # Risk metrics
    "convexity",                # Convexity
    "pvbp",                     # Price value of basis point
    "z_spread",                 # Z-spread (when treasury curve available)
    
    # Additional info
    "settlement_date",          # Settlement date used
}

# Metric dependencies (what needs to be calculated first)
METRIC_DEPENDENCIES = {
    "duration": ["ytm"],
    "duration_semi": ["ytm_semi"],
    "duration_annual": ["ytm_annual"],
    "macaulay_duration": ["ytm"],
    "macaulay_duration_semi": ["ytm_semi"],
    "macaulay_duration_annual": ["ytm_annual"],
    "convexity": ["ytm"],
    "pvbp": ["ytm"],
    "spread": ["ytm"],
    "z_spread": ["ytm"],
    "dirty_price": ["clean_price", "accrued_interest"],
}

def get_required_calculations(requested_metrics: List[str]) -> Set[str]:
    """
    Determine all metrics that need to be calculated based on dependencies
    """
    required = set(requested_metrics)
    
    # Add dependencies recursively
    added = True
    while added:
        added = False
        for metric in list(required):
            if metric in METRIC_DEPENDENCIES:
                for dep in METRIC_DEPENDENCIES[metric]:
                    if dep not in required:
                        required.add(dep)
                        added = True
    
    return required

def calculate_selective_metrics(
    isin: Optional[str] = None,
    description: Optional[str] = None,
    price: float = 100.0,
    settlement_date: Optional[str] = None,
    requested_metrics: Optional[List[str]] = None,
    overrides: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calculate only the requested metrics for optimal performance
    
    Args:
        isin: Optional ISIN code
        description: Bond description
        price: Bond price
        settlement_date: Settlement date
        requested_metrics: List of metrics to calculate (None = all)
        overrides: Optional parameter overrides
        
    Returns:
        Dict with only the requested metrics
    """
    
    # If no metrics specified, calculate all (backward compatibility)
    if requested_metrics is None:
        logger.info("No specific metrics requested - calculating all metrics")
        return calculate_bond_master(
            isin=isin,
            description=description,
            price=price,
            settlement_date=settlement_date,
            overrides=overrides
        )
    
    # Validate requested metrics
    invalid_metrics = [m for m in requested_metrics if m not in AVAILABLE_METRICS]
    if invalid_metrics:
        logger.warning(f"Invalid metrics requested: {invalid_metrics}")
        # Remove invalid metrics and continue
        requested_metrics = [m for m in requested_metrics if m in AVAILABLE_METRICS]
    
    # Determine what needs to be calculated
    required_calculations = get_required_calculations(requested_metrics)
    logger.info(f"Requested metrics: {requested_metrics}")
    logger.info(f"Required calculations (with dependencies): {required_calculations}")
    
    # For now, we'll calculate all and filter
    # TODO: Implement actual selective calculation in the underlying engine
    full_result = calculate_bond_master(
        isin=isin,
        description=description,
        price=price,
        settlement_date=settlement_date,
        overrides=overrides
    )
    
    # Handle error cases
    if full_result.get('status') == 'error' or full_result.get('error'):
        return full_result
    
    # Handle success field from calculate_bond_master
    if not full_result.get('success', True):
        return {
            'status': 'error',
            'error': full_result.get('error', 'Calculation failed')
        }
    
    # Extract only requested metrics from analytics
    filtered_analytics = {}
    # Check if analytics are at the top level or nested
    if 'analytics' in full_result:
        analytics = full_result.get('analytics', {})
    else:
        # For calculate_bond_master, metrics are at the top level
        analytics = full_result
    
    # Map internal field names to requested metrics
    field_mapping = {
        'ytm': 'ytm',
        'ytm_semi': 'ytm',  # For UST, native is semi-annual
        'ytm_annual': 'ytm_annual',
        'duration': 'duration',
        'duration_semi': 'duration',  # For UST, native is semi-annual
        'duration_annual': 'duration_annual',
        'macaulay_duration': 'macaulay_duration',
        'macaulay_duration_semi': 'mac_dur_semi',
        'macaulay_duration_annual': 'mac_dur_annual',
        'spread': 'spread',
        'z_spread': 'z_spread',
        'clean_price': 'clean_price',
        'dirty_price': 'dirty_price',
        'accrued_interest': 'accrued_interest',
        'accrued_per_million': 'accrued_per_million',
        'convexity': 'convexity',
        'pvbp': 'pvbp',
        'settlement_date': 'settlement_date'
    }
    
    # Build filtered response with only requested metrics
    for metric in requested_metrics:
        source_field = field_mapping.get(metric, metric)
        if source_field in analytics:
            filtered_analytics[metric] = analytics[source_field]
        elif metric == 'ytm_semi' and 'ytm' in analytics:
            # For bonds with semi-annual convention, ytm IS ytm_semi
            filtered_analytics['ytm_semi'] = analytics['ytm']
        elif metric == 'duration_semi' and 'duration' in analytics:
            # For bonds with semi-annual convention, duration IS duration_semi
            filtered_analytics['duration_semi'] = analytics['duration']
        else:
            # Metric not available in response
            logger.debug(f"Metric {metric} not found in calculation results")
    
    # Build minimal response
    response = {
        'status': 'success',
        'analytics': filtered_analytics
    }
    
    # Add bond info if it's in the full result (for context)
    if 'bond' in full_result and len(requested_metrics) > 3:
        response['bond'] = full_result['bond']
    
    return response

def calculate_quick_metrics(
    isin: Optional[str] = None,
    description: Optional[str] = None,
    price: float = 100.0,
    settlement_date: Optional[str] = None,
    requested_metrics: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Quick calculation endpoint - defaults to minimal metrics
    
    Args:
        isin: Optional ISIN code
        description: Bond description  
        price: Bond price
        settlement_date: Settlement date
        requested_metrics: Optional list of metrics (defaults to ytm, duration, spread)
        
    Returns:
        Minimal response with only essential metrics
    """
    
    # Use default quick metrics if none specified
    if requested_metrics is None:
        requested_metrics = DEFAULT_QUICK_METRICS
    
    return calculate_selective_metrics(
        isin=isin,
        description=description,
        price=price,
        settlement_date=settlement_date,
        requested_metrics=requested_metrics
    )

def add_convention_variants(analytics: Dict[str, Any], bond_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add _semi and _annual variants based on the bond's native convention
    
    Args:
        analytics: Current analytics dict
        bond_info: Bond information including conventions
        
    Returns:
        Enhanced analytics with convention variants
    """
    
    # Determine native convention
    frequency = bond_info.get('conventions', {}).get('fixed_frequency', 'Semiannual')
    is_semi_native = frequency == 'Semiannual'
    
    # Add convention variants if base metrics exist
    enhanced = analytics.copy()
    
    # YTM variants
    if 'ytm' in analytics:
        if is_semi_native:
            enhanced['ytm_semi'] = analytics['ytm']
            # ytm_annual should already exist from calculation
        else:
            enhanced['ytm_annual'] = analytics['ytm']
            # Would need to calculate ytm_semi if not present
    
    # Duration variants
    if 'duration' in analytics:
        if is_semi_native:
            enhanced['duration_semi'] = analytics['duration']
            # duration_annual should already exist
        else:
            enhanced['duration_annual'] = analytics['duration']
            # Would need to calculate duration_semi if not present
    
    # Macaulay duration variants (invariant but included for consistency)
    if 'macaulay_duration' in analytics:
        enhanced['macaulay_duration_semi'] = analytics['macaulay_duration']
        enhanced['macaulay_duration_annual'] = analytics['macaulay_duration']
    
    return enhanced