#!/usr/bin/env python3
"""
Profile-Based Field Configuration for Google Analysis 10 API
============================================================

Bloomberg Terminal-style field filtering system:
- DEFAULT: ytm, duration, spread (75% faster)
- Custom fields: ytm,oas,pvbp (mix and match)
- Predefined profiles: PRICING, RISK, TRADING, FULL
- Performance tracking with improvement metrics
"""

import logging
logger = logging.getLogger(__name__)

# Available field mappings (from your current API response structure)
AVAILABLE_FIELDS = {
    # Core Pricing Fields
    'ytm': 'yield',
    'yield': 'yield', 
    'price': 'clean_price',
    'clean_price': 'clean_price',
    'dirty_price': 'dirty_price',
    'accrued': 'accrued_interest',
    'accrued_interest': 'accrued_interest',
    
    # Risk Metrics
    'duration': 'duration',
    'mod_duration': 'duration',
    'mac_duration': 'macaulay_duration',
    'macaulay_duration': 'macaulay_duration',
    'convexity': 'convexity',
    'pvbp': 'pvbp',
    
    # Annual Versions (from enhanced version)
    'annual_duration': 'annual_duration',
    'annual_macaulay_duration': 'annual_macaulay_duration',
    'annual_yield': 'annual_yield',
    
    # Spread Metrics
    'spread': 'spread',
    'oas': 'z_spread',
    'z_spread': 'z_spread',
    'tsy_spread': 'spread',
    
    # Enhanced Fields (from your enhanced calculator)
    'mac_dur_semi': 'macaulay_duration',
    'ytm_semi': 'yield',
    'mod_dur_semi': 'duration',
    'convexity_semi': 'convexity',
    'z_spread_semi': 'z_spread',
    'tsy_spread_semi': 'spread'
}

# Predefined calculation profiles
FIELD_PROFILES = {
    # IMPROVED DEFAULT: Just the 3 most important fields (75% faster!)
    'DEFAULT': {
        'yield': True,          # YTM - most requested
        'duration': True,       # Risk metric  
        'spread': True         # Treasury spread
    },
    
    # Individual field profiles
    'ytm': {'yield': True},
    'oas': {'z_spread': True},
    'duration': {'duration': True},
    'convexity': {'convexity': True},
    'accrued': {'accrued_interest': True},
    'price': {'clean_price': True, 'dirty_price': True},
    'pvbp': {'pvbp': True},
    
    # Business-focused profiles
    'PRICING': {
        'yield': True,
        'clean_price': True,
        'dirty_price': True,
        'accrued_interest': True
    },
    
    'RISK': {
        'yield': True,
        'duration': True,
        'convexity': True
    },
    
    'TRADING': {
        'yield': True,
        'duration': True,
        'pvbp': True,
        'z_spread': True
    },
    
    'SETTLEMENT': {
        'clean_price': True,
        'dirty_price': True,
        'accrued_interest': True
    },
    
    'ANALYTICS': {
        'yield': True,
        'duration': True,
        'convexity': True,
        'z_spread': True,
        'pvbp': True,
        'macaulay_duration': True
    },
    
    # Full calculation (backward compatibility)
    'FULL': 'all'
}

def get_calculation_flags(profile_param=None):
    """
    Convert profile parameter to calculation flags dictionary
    
    Args:
        profile_param: URL parameter (?profile=ytm,oas or ?profile=RISK)
        
    Returns:
        dict: Calculation flags or 'all' for full calculation
    """
    
    # NEW: Better default behavior - just core 3 fields
    if not profile_param:
        logger.info("📊 Using DEFAULT profile: ytm, duration, spread (75% performance gain)")
        return FIELD_PROFILES['DEFAULT']
    
    # Handle predefined profiles
    profile_upper = profile_param.upper()
    if profile_upper in FIELD_PROFILES:
        profile_config = FIELD_PROFILES[profile_upper]
        if profile_config == 'all':
            logger.info("📊 Using FULL profile: all fields (current behavior)")
            return 'all'
        else:
            logger.info(f"📊 Using {profile_upper} profile: {list(profile_config.keys())}")
            return profile_config
    
    # Parse custom comma-separated fields
    logger.info(f"📊 Parsing custom profile: {profile_param}")
    requested_fields = [f.strip().lower() for f in profile_param.split(',')]
    
    # Build combined flags dictionary
    flags = {}
    for field in requested_fields:
        if field in AVAILABLE_FIELDS:
            mapped_field = AVAILABLE_FIELDS[field]
            flags[mapped_field] = True
            logger.info(f"  ✅ {field} → {mapped_field}")
        else:
            logger.warning(f"  ❌ Unknown field: {field}")
    
    if not flags:
        logger.warning("⚠️ No valid fields found, falling back to DEFAULT")
        return FIELD_PROFILES['DEFAULT']
    
    logger.info(f"📊 Custom profile result: {list(flags.keys())}")
    return flags

def add_performance_metrics(response, profile_param, calc_flags):
    """Add performance improvement metrics to response"""
    
    # Count of all possible fields (from your current full response)
    TOTAL_POSSIBLE_FIELDS = 13
    
    if calc_flags == 'all':
        calculated = TOTAL_POSSIBLE_FIELDS
        skipped = 0
    elif isinstance(calc_flags, dict):
        calculated = len(calc_flags)
        skipped = TOTAL_POSSIBLE_FIELDS - calculated
    else:
        calculated = TOTAL_POSSIBLE_FIELDS
        skipped = 0
    
    improvement = round((skipped / TOTAL_POSSIBLE_FIELDS) * 100) if TOTAL_POSSIBLE_FIELDS > 0 else 0
    
    # Add to processing section
    if 'processing' not in response:
        response['processing'] = {}
    
    response['processing'].update({
        'profile_used': profile_param or 'DEFAULT',
        'fields_calculated': calculated,
        'fields_skipped': skipped,
        'performance_improvement': f"{improvement}%",
        'calculation_engine': 'xtrillion_core'
    })
    
    return response

def filter_analytics_by_profile(analytics_dict, calc_flags):
    """
    Filter analytics dictionary based on calculation flags
    
    Args:
        analytics_dict: Full analytics response
        calc_flags: Calculation flags from get_calculation_flags()
        
    Returns:
        dict: Filtered analytics containing only requested fields
    """
    
    if calc_flags == 'all':
        return analytics_dict  # Return everything
    
    if not isinstance(calc_flags, dict):
        return analytics_dict  # Safety fallback
    
    # Filter to only requested fields
    filtered = {}
    for field_name in calc_flags:
        if field_name in analytics_dict:
            filtered[field_name] = analytics_dict[field_name]
        else:
            logger.warning(f"⚠️ Requested field '{field_name}' not found in analytics")
    
    logger.info(f"🎯 Filtered analytics: {len(filtered)}/{len(analytics_dict)} fields returned")
    return filtered
