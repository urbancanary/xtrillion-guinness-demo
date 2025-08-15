#!/usr/bin/env python3
"""
Ticker lookup functionality for bond conventions
"""

import sqlite3
import logging

logger = logging.getLogger(__name__)

def get_ticker_from_description(description):
    """
    Extract ticker from bond description
    Examples:
    - "ECOPET 5 ⅞ 05/28/45" → "ECOPET"
    - "PEMEX 6.95 01/28/60" → "PEMEX"
    - "T 4.1 02/15/28" → "T"
    """
    if not description:
        return None
        
    # Split by spaces and get first part
    parts = description.strip().split()
    if parts:
        ticker = parts[0].upper()
        # Remove any special characters
        ticker = ticker.replace(',', '').replace('.', '')
        return ticker
    return None

def get_conventions_from_ticker(ticker, db_path):
    """
    Get conventions from ticker_convention_preferences table
    """
    if not ticker or not db_path:
        return None
        
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            query = """
            SELECT 
                day_count,
                business_convention,
                frequency
            FROM ticker_convention_preferences
            WHERE ticker = ?
            """
            cursor.execute(query, (ticker,))
            result = cursor.fetchone()
            
            if result:
                conventions = {
                    'day_count': result[0],
                    'business_convention': result[1],
                    'frequency': result[2]
                }
                logger.info(f"📋 Found ticker conventions for {ticker}: {conventions}")
                return conventions
                
    except Exception as e:
        logger.error(f"Error getting ticker conventions: {e}")
        
    return None

def get_validated_conventions_by_ticker(ticker, validated_db_path):
    """
    Get conventions from validated_quantlib_bonds by matching ticker in description
    This is more reliable than ticker_convention_preferences
    """
    if not ticker or not validated_db_path:
        return None
        
    try:
        with sqlite3.connect(validated_db_path) as conn:
            cursor = conn.cursor()
            
            # Get the most common convention for this ticker
            query = """
            SELECT 
                day_count,
                business_convention,
                frequency,
                COUNT(*) as count
            FROM validated_quantlib_bonds
            WHERE description LIKE ? || '%'
            GROUP BY day_count, business_convention, frequency
            ORDER BY count DESC
            LIMIT 1
            """
            cursor.execute(query, (ticker,))
            result = cursor.fetchone()
            
            if result:
                conventions = {
                    'day_count': result[0],
                    'business_convention': result[1],
                    'frequency': result[2],
                    'source': 'validated_ticker_lookup',
                    'bond_count': result[3]
                }
                logger.info(f"✅ Found validated conventions for ticker {ticker} (used by {result[3]} bonds): {conventions}")
                return conventions
                
    except Exception as e:
        logger.error(f"Error getting validated ticker conventions: {e}")
        
    return None

def test_ticker_lookup():
    """Test ticker lookup functionality"""
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Test ticker extraction
    test_descriptions = [
        "ECOPET 5 ⅞ 05/28/45",
        "PEMEX 6.95 01/28/60",
        "T 4.1 02/15/28",
        "ECOPETROL SA, 5.875%, 28-May-2045"
    ]
    
    print("🔍 Testing ticker extraction:")
    for desc in test_descriptions:
        ticker = get_ticker_from_description(desc)
        print(f"   '{desc}' → '{ticker}'")
    
    # Test convention lookup
    print("\n🔍 Testing convention lookup:")
    
    bloomberg_db = './bloomberg_index.db'
    validated_db = './validated_quantlib_bonds.db'
    
    # Check ECOPET conventions
    ticker = "ECOPET"
    
    # From ticker_convention_preferences
    ticker_conv = get_conventions_from_ticker(ticker, bloomberg_db)
    print(f"\n📁 Ticker conventions for {ticker}:")
    print(f"   {ticker_conv}")
    
    # From validated DB
    validated_conv = get_validated_conventions_by_ticker(ticker, validated_db)
    print(f"\n📁 Validated conventions for {ticker}:")
    print(f"   {validated_conv}")

if __name__ == "__main__":
    test_ticker_lookup()