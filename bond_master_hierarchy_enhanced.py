#!/usr/bin/env python3
"""
Bond Master Calculator - Enhanced with Phase 1 Outputs
======================================================

ENHANCEMENT: Original calculate_bond_master + 6 new Phase 1 outputs:
✅ mac_dur_semi - Macaulay Duration  
✅ clean_price - Clean Price
✅ dirty_price - Dirty Price
✅ ytm_annual - Annual Yield
✅ mod_dur_annual - Annual Modified Duration  
✅ mac_dur_annual - Annual Macaulay Duration

This is the master function you described that handles:

Route 1: ISIN Hierarchy (when ISIN provided)
Route 2: Parse Hierarchy (when no ISIN)
Both routes converge to the same calculation engine.
"""

import sys
import os
import pandas as pd
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta

# Add project paths
project_root = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10'
sys.path.append(project_root)

from google_analysis10 import process_bond_portfolio

def get_prior_month_end():
    """
    Get the last day of the previous month for institutional settlement
    
    Returns:
        str: Date in YYYY-MM-DD format (prior month end)
    """
    today = datetime.now()
    # Get first day of current month
    first_day_current_month = today.replace(day=1)
    # Get last day of previous month
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    return last_day_previous_month.strftime("%Y-%m-%d")

logger = logging.getLogger(__name__)

def add_phase1_outputs(bond_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    🚀 PHASE 1 ENHANCEMENT: Add 6 new outputs to existing bond calculation
    
    Args:
        bond_result: Original result from calculate_bond_master
        
    Returns:
        Enhanced result with 6 additional outputs:
        - mac_dur_semi: Macaulay Duration
        - clean_price: Clean Price  
        - dirty_price: Dirty Price
        - ytm_annual: Annual Yield
        - mod_dur_annual: Annual Modified Duration
        - mac_dur_annual: Annual Macaulay Duration
    """
    
    if not bond_result.get('success'):
        return bond_result
    
    # Extract existing values
    ytm = bond_result.get('yield')  # Yield (semi-annual basis)
    mod_dur = bond_result.get('duration')  # Modified duration
    price = bond_result.get('price', 100.0)  # Bond price
    accrued = bond_result.get('accrued_interest', 0.0)  # Accrued interest
    
    enhanced = bond_result.copy()
    
    try:
        # 🟢 1. Macaulay Duration (30 seconds to implement)
        if ytm and mod_dur:
            frequency = 2  # Semi-annual for most bonds
            ytm_decimal = ytm / 100.0  # Convert percentage to decimal
            mac_dur_semi = mod_dur * (1 + ytm_decimal/frequency)
            enhanced['mac_dur_semi'] = round(mac_dur_semi, 6)
            logger.debug(f"✅ Macaulay Duration: {mac_dur_semi:.6f} years")
        
        # 🟢 2. Clean Price (10 seconds to implement)
        enhanced['clean_price'] = round(price, 6)
        logger.debug(f"✅ Clean Price: {price:.6f}")
        
        # 🟢 4. Annual Yield (2 minutes to implement) - FIXED
        if ytm:
            # Handle ytm whether it's in decimal (0.048997) or percentage (4.8997) format
            if ytm < 1:  # Likely in decimal format already
                ytm_decimal = ytm
            else:  # In percentage format
                ytm_decimal = ytm / 100.0
                
            semi_rate = ytm_decimal / 2  # Semi-annual rate (decimal)
            annual_rate = ((1 + semi_rate) ** 2 - 1) * 100  # Annual percentage
            enhanced['ytm_annual'] = round(annual_rate, 6)
            logger.debug(f"✅ Annual Yield: {annual_rate:.6f}%")
        
        # 🟢 3. Dirty Price (10 seconds to implement) - FIXED
        accrued = bond_result.get('accrued_interest')
        if accrued is not None:
            dirty_price = price + accrued
            enhanced['dirty_price'] = round(dirty_price, 6)
            logger.debug(f"✅ Dirty Price: {dirty_price:.6f}")
        else:
            # If no accrued interest available, assume dirty = clean for now
            enhanced['dirty_price'] = round(price, 6)
            logger.debug(f"✅ Dirty Price: {price:.6f} (no accrued data)")

        
        # 🟢 5. Annual Modified Duration (CORRECTED - proper conversion)
        if mod_dur and ytm:
            # Handle ytm whether it's in decimal (0.048997) or percentage (4.8997) format
            if ytm < 1:  # Likely in decimal format already
                ytm_decimal = ytm
            else:  # In percentage format
                ytm_decimal = ytm / 100.0
            
            # Proper conversion: Duration_annual = Duration_semi / (1 + yield_semi/2)
            mod_dur_annual = mod_dur / (1 + ytm_decimal/2)
            enhanced['mod_dur_annual'] = round(mod_dur_annual, 6)
            logger.debug(f"✅ Annual Modified Duration: {mod_dur_annual:.6f} years")
        
        # 🟢 6. Annual Macaulay Duration (CORRECTED - proper conversion)
        if enhanced.get('mac_dur_semi') and ytm:
            # Handle ytm whether it's in decimal (0.048997) or percentage (4.8997) format
            if ytm < 1:  # Likely in decimal format already
                ytm_decimal = ytm
            else:  # In percentage format
                ytm_decimal = ytm / 100.0
                
            # Proper conversion: MacDuration_annual = MacDuration_semi / (1 + yield_semi/2)
            mac_dur_annual = enhanced['mac_dur_semi'] / (1 + ytm_decimal/2)
            enhanced['mac_dur_annual'] = round(mac_dur_annual, 6)
            logger.debug(f"✅ Annual Macaulay Duration: {mac_dur_annual:.6f} years")
        
        # Add API field name mappings for XTrillion compatibility
        enhanced['ytm_semi'] = enhanced.get('yield')  # Map existing field
        enhanced['mod_dur_semi'] = enhanced.get('duration')  # Map existing field
        enhanced['tsy_spread_semi'] = enhanced.get('spread')  # Map existing field
        
        # Add metadata
        enhanced['phase1_outputs_added'] = True
        enhanced['new_outputs'] = [
            'mac_dur_semi', 'clean_price', 'dirty_price', 
            'ytm_annual', 'mod_dur_annual', 'mac_dur_annual'
        ]
        
        logger.info(f"🚀 Phase 1 enhancement complete: {len(enhanced['new_outputs'])} new outputs added")
        return enhanced
        
    except Exception as e:
        # Fail gracefully - return original result if enhancement fails
        logger.error(f"❌ Phase 1 enhancement failed: {e}")
        bond_result['phase1_error'] = str(e)
        return bond_result


def calculate_bond_master(
    isin: Optional[str] = None,
    description: str = "T 3 15/08/52", 
    price: float = 100.0,
    settlement_date: Optional[str] = None,
    db_path: str = './bonds_data.db',
    validated_db_path: str = './validated_quantlib_bonds.db',
    bloomberg_db_path: str = './bloomberg_index.db'
) -> Dict[str, Any]:
    """
    🎯 ENHANCED MASTER BOND CALCULATION FUNCTION
    
    ORIGINAL FUNCTIONALITY + 6 NEW PHASE 1 OUTPUTS
    
    Implements complete ISIN and parse hierarchy as you described:
    
    1. If ISIN present → ISIN hierarchy route
    2. If no ISIN → Parse hierarchy route  
    3. Both routes converge to same calculation engine
    4. ✨ NEW: Phase 1 outputs automatically added
    
    Args:
        isin: Optional ISIN code (triggers ISIN hierarchy)
        description: Bond description like "T 3 15/08/52" 
        price: Bond price (default 100.0)
        settlement_date: Optional settlement date
        db_path: Main database path
        validated_db_path: Validated conventions database
        bloomberg_db_path: Bloomberg data database
        
    Returns:
        Dict with yield, duration, spread, accrued_interest + 6 NEW OUTPUTS:
        - mac_dur_semi: Macaulay Duration
        - clean_price: Clean Price
        - dirty_price: Dirty Price  
        - ytm_annual: Annual Yield
        - mod_dur_annual: Annual Modified Duration
        - mac_dur_annual: Annual Macaulay Duration
    """
    
    logger.info(f"🎯 Enhanced Master calculation: ISIN={isin}, Description='{description}', Price={price}")
    
    # ✅ FIXED: Handle settlement date logic - default to prior month end
    if settlement_date is None:
        settlement_date = get_prior_month_end()
        logger.info(f"📅 Using default settlement date (prior month end): {settlement_date}")
    else:
        logger.info(f"📅 Using provided settlement date: {settlement_date}")
    
    # Construct portfolio data for the current API
    bond_data = {
        'price': price,  # ✅ FIXED: Use correct field name
        'description': description
    }
    
    # Route 1: ISIN Hierarchy (when ISIN provided)
    if isin:
        logger.info(f"📍 Route 1: ISIN Hierarchy - {isin}")
        bond_data['isin'] = isin  # ✅ FIXED: Use correct field name
        route_used = "isin_hierarchy"
    
    # Route 2: Parse Hierarchy (when no ISIN)  
    else:
        logger.info(f"📖 Route 2: Parse Hierarchy - '{description}'")
        route_used = "parse_hierarchy"
    
    # Add weighting (required by current API)
    bond_data['WEIGHTING'] = 1.0
    
    # Construct portfolio_data format expected by current API
    portfolio_data = {
        'data': [bond_data]
    }
    
    # Convergence Point: Both routes use same calculation engine
    logger.info(f"🔗 Converging to shared calculation engine")
    
    try:
        results_list = process_bond_portfolio(
            portfolio_data=portfolio_data,
            db_path=db_path,
            validated_db_path=validated_db_path, 
            bloomberg_db_path=bloomberg_db_path,
            settlement_days=0,
            settlement_date=settlement_date
        )
        
        if not results_list:
            return {
                'success': False,
                'error': 'Empty results from calculation engine',
                'route_used': route_used,
                'isin_provided': isin is not None
            }
        
        result = results_list[0]
        
        if result.get('error'):
            return {
                'success': False,
                'error': result.get('error'),
                'route_used': route_used,
                'isin_provided': isin is not None
            }
        
        # Extract and format results (ORIGINAL CODE)
        success_result = {
            'success': True,
            'isin': result.get('isin') or isin,
            'description': description,
            'price': price,
            'yield': result.get('yield'),
            'duration': result.get('duration'), 
            'spread': result.get('spread'),
            'accrued_interest': result.get('accrued_interest'),
            'conventions': result.get('conventions'),
            'route_used': route_used,
            'isin_provided': isin is not None,
            'calculation_method': 'xtrillion_core',
            'settlement_date': result.get('settlement_date_str') or settlement_date
        }
        
        # 🚀 PHASE 1 ENHANCEMENT: Add 6 new outputs
        success_result = add_phase1_outputs(success_result)
        
        logger.info(f"✅ Enhanced Master calculation successful via {route_used}: Yield={result.get('yield'):.4f}%")
        logger.info(f"🚀 Phase 1 outputs added: {success_result.get('new_outputs', [])}")
        return success_result
        
    except Exception as e:
        logger.error(f"🚨 Master calculation failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'route_used': route_used,
            'isin_provided': isin is not None
        }


def process_bonds_with_weightings(df: pd.DataFrame, db_path: str, record_number: int = 1) -> pd.DataFrame:
    """
    🔄 COMPATIBILITY WRAPPER for old comprehensive tester
    
    Bridges the old DataFrame interface to the new portfolio API.
    This allows the comprehensive_6way_tester.py to work without changes.
    """
    
    logger.info(f"🔄 Compatibility wrapper called with {len(df)} bonds")
    
    results = []
    
    for idx, row in df.iterrows():
        # Extract bond data from DataFrame row
        isin = row.get('isin')
        description = row.get('Name') or row.get('BOND_ENAME') or row.get('description')
        price = row.get('price', 100.0)
        
        # Call the enhanced master function
        result = calculate_bond_master(
            isin=isin,
            description=description,
            price=price,
            db_path=db_path
        )
        
        # Convert back to DataFrame format expected by tester
        df_result = {
            'isin': result.get('isin'),
            'description': result.get('description'),
            'yield': result.get('yield'),
            'duration': result.get('duration'),
            'spread': result.get('spread'),
            'error': None if result.get('success') else result.get('error'),
            'route_used': result.get('route_used'),
            'success': result.get('success'),
            # Phase 1 outputs
            'mac_dur_semi': result.get('mac_dur_semi'),
            'clean_price': result.get('clean_price'),
            'dirty_price': result.get('dirty_price'),
            'ytm_annual': result.get('ytm_annual'),
            'mod_dur_annual': result.get('mod_dur_annual'),
            'mac_dur_annual': result.get('mac_dur_annual')
        }
        
        results.append(df_result)
    
    return pd.DataFrame(results)


# Test function to verify both routes work with Phase 1 enhancements
def test_enhanced_master_function():
    """Test both ISIN and parse hierarchy routes with Phase 1 outputs"""
    
    print("🧪 Testing Enhanced Master Function - Phase 1 Outputs")
    print("=" * 60)
    
    # Test Route 1: ISIN Hierarchy  
    print("\n📍 Route 1: ISIN Hierarchy")
    result1 = calculate_bond_master(
        isin="US912810TJ79",
        description="US TREASURY N/B, 3%, 15-Aug-2052",
        price=71.66
    )
    print(f"Route: {result1.get('route_used')}")
    print(f"Success: {result1.get('success')}")
    
    if result1.get('success'):
        print(f"📊 ORIGINAL OUTPUTS:")
        print(f"   Yield: {result1.get('yield'):.4f}%")
        print(f"   Duration: {result1.get('duration'):.4f} years")
        print(f"   Spread: {result1.get('spread'):.1f} bps")
        
        print(f"🚀 NEW PHASE 1 OUTPUTS:")
        print(f"   Macaulay Duration: {result1.get('mac_dur_semi'):.6f} years")
        print(f"   Clean Price: {result1.get('clean_price'):.6f}")
        print(f"   Dirty Price: {result1.get('dirty_price'):.6f}")
        print(f"   Annual Yield: {result1.get('ytm_annual'):.6f}%")
        print(f"   Annual Duration: {result1.get('mod_dur_annual'):.6f} years")
        print(f"   Annual Mac Duration: {result1.get('mac_dur_annual'):.6f} years")
    
    # Test Route 2: Parse Hierarchy
    print("\n📖 Route 2: Parse Hierarchy")  
    result2 = calculate_bond_master(
        isin=None,  # No ISIN provided
        description="T 3 15/08/52",
        price=71.66
    )
    print(f"Route: {result2.get('route_used')}")
    print(f"Success: {result2.get('success')}")
    
    if result2.get('success'):
        print(f"📊 ORIGINAL OUTPUTS:")
        print(f"   Yield: {result2.get('yield'):.4f}%")
        print(f"   Duration: {result2.get('duration'):.4f} years")
        print(f"   Spread: {result2.get('spread'):.1f} bps")
        
        print(f"🚀 NEW PHASE 1 OUTPUTS:")
        print(f"   Macaulay Duration: {result2.get('mac_dur_semi'):.6f} years")
        print(f"   Clean Price: {result2.get('clean_price'):.6f}")
        print(f"   Dirty Price: {result2.get('dirty_price'):.6f}")
        print(f"   Annual Yield: {result2.get('ytm_annual'):.6f}%")
        print(f"   Annual Duration: {result2.get('mod_dur_annual'):.6f} years")
    
    # Compare results
    print(f"\n🔍 Route Comparison:")
    if result1.get('yield') and result2.get('yield'):
        diff = abs(result1.get('yield') - result2.get('yield'))
        print(f"Yield difference: {diff:.4f}% ({diff*100:.2f} bps)")
        if diff < 0.01:  # Less than 1bp difference
            print("✅ Routes converge correctly!")
        else:
            print("⚠️ Routes have different results")
    
    # Test Phase 1 validation
    print(f"\n🚀 Phase 1 Validation:")
    if result1.get('phase1_outputs_added'):
        print("✅ Phase 1 outputs successfully added")
        new_outputs = result1.get('new_outputs', [])
        print(f"✅ New outputs: {', '.join(new_outputs)}")
        
        # Validate mathematical relationships
        mac_dur = result1.get('mac_dur_semi')
        mod_dur = result1.get('duration')
        if mac_dur and mod_dur and mac_dur > mod_dur:
            print("✅ Macaulay > Modified Duration (mathematically correct)")
        
        dirty_price = result1.get('dirty_price')
        clean_price = result1.get('clean_price')
        if dirty_price and clean_price and dirty_price > clean_price:
            print("✅ Dirty > Clean Price (positive accrued interest)")
    
    return result1, result2


if __name__ == "__main__":
    print("🎯 Enhanced Bond Master Calculator")
    print("🚀 Original functionality + 6 new Phase 1 outputs")
    print("🔗 Implements complete ISIN and parse hierarchy")
    print()
    
    # Test both routes with enhancements
    test_enhanced_master_function()
