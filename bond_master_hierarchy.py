#!/usr/bin/env python3
"""
Bond Master Calculator - The Master Function with ISIN Hierarchy
================================================================

This is the master function you described that handles:

Route 1: ISIN Hierarchy (when ISIN provided)
- Look up ISIN in database tables
- Fall back to ticker lookup  
- Apply Treasury overrides if detected
- Check ISIN character patterns for clues
- Use defaults as final fallback

Route 2: Parse Hierarchy (when no ISIN)
- Parse description for bond details
- Extract coupon, maturity, issuer
- Apply convention detection

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
    🎯 MASTER BOND CALCULATION FUNCTION
    
    Implements complete ISIN and parse hierarchy as you described:
    
    1. If ISIN present → ISIN hierarchy route
    2. If no ISIN → Parse hierarchy route  
    3. Both routes converge to same calculation engine
    
    Args:
        isin: Optional ISIN code (triggers ISIN hierarchy)
        description: Bond description like "T 3 15/08/52" 
        price: Bond price (default 100.0)
        settlement_date: Optional settlement date
        db_path: Main database path
        validated_db_path: Validated conventions database
        bloomberg_db_path: Bloomberg data database
        
    Returns:
        Dict with yield, duration, spread, and metadata
    """
    
    logger.info(f"🎯 Master calculation: ISIN={isin}, Description='{description}', Price={price}")
    
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
        
        # Extract and format results
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
        
        logger.info(f"✅ Master calculation successful via {route_used}: Yield={result.get('yield'):.4f}%")
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
        
        # Call the master function
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
            'success': result.get('success')
        }
        
        results.append(df_result)
    
    return pd.DataFrame(results)


# Test function to verify both routes work
def test_master_function():
    """Test both ISIN and parse hierarchy routes"""
    
    print("🧪 Testing Master Function - Both Routes")
    print("=" * 50)
    
    # Test Route 1: ISIN Hierarchy  
    print("\n📍 Route 1: ISIN Hierarchy")
    result1 = calculate_bond_master(
        isin="US912810TJ79",
        description="US TREASURY N/B, 3%, 15-Aug-2052",
        price=71.66
    )
    print(f"Route: {result1.get('route_used')}")
    print(f"Success: {result1.get('success')}")
    print(f"Yield: {result1.get('yield'):.4f}%" if result1.get('yield') else "Yield: FAILED")
    
    # Test Route 2: Parse Hierarchy
    print("\n📖 Route 2: Parse Hierarchy")  
    result2 = calculate_bond_master(
        isin=None,  # No ISIN provided
        description="T 3 15/08/52",
        price=71.66
    )
    print(f"Route: {result2.get('route_used')}")
    print(f"Success: {result2.get('success')}")
    print(f"Yield: {result2.get('yield'):.4f}%" if result2.get('yield') else "Yield: FAILED")
    
    # Compare results
    print(f"\n🔍 Route Comparison:")
    if result1.get('yield') and result2.get('yield'):
        diff = abs(result1.get('yield') - result2.get('yield'))
        print(f"Yield difference: {diff:.4f}% ({diff*100:.2f} bps)")
        if diff < 0.01:  # Less than 1bp difference
            print("✅ Routes converge correctly!")
        else:
            print("⚠️ Routes have different results")
    
    return result1, result2


if __name__ == "__main__":
    print("🎯 Bond Master Calculator")
    print("🔗 Implements complete ISIN and parse hierarchy")
    print()
    
    # Test both routes
    test_master_function()
