#!/usr/bin/env python3
"""
Bond Master Calculation Test - CORRECTED VERSION
===============================================

Tests both ISIN-based and description-based calculations side by side
to verify semi-annual duration consistency and accuracy.

FIXES APPLIED:
1. ✅ Unit conversion fix for yield comparison (decimal vs percentage)
2. ✅ Proper basis point calculation 
3. ✅ Enhanced day count convention validation
4. ✅ More accurate Bloomberg comparison logic
"""

import sys
import json
from datetime import datetime
import logging

# Add path for google_analysis10 module
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

from google_analysis10 import process_bond_portfolio

# Set up logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise for cleaner output

def create_test_portfolio():
    """Create test portfolio with both ISIN and description versions"""
    
    bonds = [
        {
            "name": "🏛️ US Treasury 3% 2052",
            "isin": "US912810TJ79",
            "description": "US TREASURY N/B, 3%, 15-Aug-2052",
            "price": 71.66,
            "bloomberg_yield": 4.89960,  # Bloomberg as percentage
            "bloomberg_duration": 16.35658,
            "bloomberg_convexity": 370.22
        },
        {
            "name": "🌎 Panama 3.87% 2060", 
            "isin": "US698299BL70",
            "description": "PANAMA, 3.87%, 23-Jul-2060",
            "price": 56.60,
            "bloomberg_yield": 7.36000,
            "bloomberg_duration": 13.57604,
            "bloomberg_convexity": 245.89
        },
        {
            "name": "🛢️ Ecopetrol 5.875% 2045",
            "isin": "US279158AJ82", 
            "description": "ECOPETROL SA, 5.875%, 28-May-2045",
            "price": 69.31,
            "bloomberg_yield": 9.28000,
            "bloomberg_duration": 9.80447,
            "bloomberg_convexity": 123.45
        },
        {
            "name": "🏗️ Galaxy Pipeline 3.25% 2040",
            "isin": "XS2249741674",
            "description": "GALAXY PIPELINE, 3.25%, 30-Sep-2040", 
            "price": 77.88,
            "bloomberg_yield": 5.64000,
            "bloomberg_duration": 11.22303,
            "bloomberg_convexity": 156.78
        },
        {
            "name": "🇸🇦 Saudi Aramco 4.25% 2039",
            "isin": "XS1982113463",
            "description": "SAUDI ARAB OIL, 4.25%, 16-Apr-2039",
            "price": 87.14,
            "bloomberg_yield": 5.60000,
            "bloomberg_duration": 9.93052,
            "bloomberg_convexity": 134.56
        }
    ]
    
    return bonds

def run_calculations(bond, method_type, include_isin=True):
    """Run calculation for a bond with or without ISIN"""
    
    portfolio_data = {
        "data": [
            {
                "isin": bond["isin"] if include_isin else "",
                "description": bond["description"],
                "price": bond["price"],
                "weighting": 1.0
            }
        ]
    }
    
    try:
        results = process_bond_portfolio(
            portfolio_data,
            db_path="/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/portfolio_database.db",
            validated_db_path="/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bloomberg_index.db",
            bloomberg_db_path="/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bloomberg_index.db",
            settlement_date="2025-06-30"
        )
        
        if results and len(results) > 0:
            result = results[0]
            return {
                "method": method_type,
                "success": True,
                "yield": result.get('yield', None),
                "duration": result.get('duration', None),
                "convexity": result.get('convexity', None),
                "isin": result.get('isin', 'N/A'),
                "conventions": result.get('conventions', {}),
                "settlement_date": result.get('settlement_date_str', 'N/A')
            }
        else:
            return {
                "method": method_type,
                "success": False,
                "error": "No results returned"
            }
            
    except Exception as e:
        return {
            "method": method_type,
            "success": False,
            "error": str(e)
        }

def format_number(value, decimals=6):
    """Format number with specified decimals or return N/A"""
    if value is None:
        return "N/A"
    if isinstance(value, (int, float)):
        return f"{value:.{decimals}f}"
    return str(value)

def calculate_difference_corrected(actual, expected, metric_type="yield"):
    """
    ✅ CORRECTED: Calculate difference with proper unit handling
    
    Args:
        actual: Our calculated value
        expected: Bloomberg baseline value  
        metric_type: "yield", "duration", or "convexity"
    
    Returns:
        (difference_string, status_emoji)
    """
    if actual is None or expected is None:
        return "N/A", "❌"
    
    if metric_type == "yield":
        # ✅ FIX: Convert our decimal yield to percentage for comparison
        actual_pct = actual * 100  # Convert 0.04900 to 4.900%
        expected_pct = expected    # Bloomberg already in percentage (4.89960%)
        
        diff = abs(actual_pct - expected_pct)
        
        # Yield difference thresholds in basis points (1% = 100bp)
        diff_bps = diff * 100  # Convert to basis points
        
        if diff_bps < 1.0:      # Less than 1 basis point
            status = "✅"
        elif diff_bps < 5.0:    # Less than 5 basis points  
            status = "🟡"
        else:                   # 5+ basis points
            status = "❌"