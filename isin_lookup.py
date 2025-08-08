#!/usr/bin/env python3
"""
ISIN Lookup Module
Provides database lookup functionality for ISINs across multiple bond databases
"""

import sqlite3
import logging
import os
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

def lookup_isin_in_database(isin: str, 
                          db_path: str, 
                          validated_db_path: Optional[str] = None,
                          bloomberg_db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Look up bond details by ISIN across multiple databases.
    
    Args:
        isin: The ISIN code to look up
        db_path: Primary database path (bonds_data.db)
        validated_db_path: Validated conventions database path
        bloomberg_db_path: Bloomberg reference database path
        
    Returns:
        Dict with bond details if found, None otherwise
    """
    if not isin:
        return None
        
    logger.info(f"🔍 Looking up ISIN: {isin}")
    
    # Try each database in order
    databases = [
        (db_path, "bonds", "Primary"),
        (validated_db_path, "validated_bonds", "Validated"),
        (bloomberg_db_path, "bloomberg_bonds", "Bloomberg")
    ]
    
    for db_file, table_hint, db_name in databases:
        if not db_file or not os.path.exists(db_file):
            logger.debug(f"Skipping {db_name} database - not available")
            continue
            
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # First, try to find tables that might contain ISINs
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for (table_name,) in tables:
                # Get column names for this table
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                column_names = [col[1].lower() for col in columns]
                
                # Look for ISIN column
                isin_column = None
                for col_name in ['isin', 'isin_code', 'bond_cd', 'bond_code', 'identifier']:
                    if col_name in column_names:
                        isin_column = col_name
                        break
                
                if not isin_column:
                    continue
                
                # Query for the ISIN
                query = f"SELECT * FROM {table_name} WHERE {isin_column} = ?"
                cursor.execute(query, (isin,))
                result = cursor.fetchone()
                
                if result:
                    # Found the ISIN - construct result dict
                    logger.info(f"✅ Found ISIN in {db_name} database, table: {table_name}")
                    
                    # Map column names to values
                    bond_data = {}
                    for i, (col_info) in enumerate(columns):
                        col_name = col_info[1]
                        bond_data[col_name.lower()] = result[i]
                    
                    # Extract key fields with various possible column names
                    description = (bond_data.get('description') or 
                                 bond_data.get('bond_description') or 
                                 bond_data.get('name') or 
                                 bond_data.get('bond_name'))
                    
                    coupon = (bond_data.get('coupon') or 
                             bond_data.get('coupon_rate') or 
                             bond_data.get('cpn') or 
                             bond_data.get('rate'))
                    
                    maturity = (bond_data.get('maturity') or 
                               bond_data.get('maturity_date') or 
                               bond_data.get('mat_date'))
                    
                    # Build return structure
                    result_dict = {
                        'isin': isin,
                        'description': description,
                        'coupon': float(coupon) if coupon else None,
                        'maturity': maturity,
                        'issuer': bond_data.get('issuer'),
                        'currency': bond_data.get('currency', 'USD'),
                        'face_value': bond_data.get('face_value', 1000000),
                        'day_count': bond_data.get('day_count'),
                        'frequency': bond_data.get('frequency'),
                        'business_convention': (bond_data.get('business_convention') or 
                                              bond_data.get('business_day_convention')),
                        'end_of_month': bond_data.get('end_of_month', True),
                        'database': db_name,
                        'table': table_name,
                        'raw_data': bond_data
                    }
                    
                    conn.close()
                    return result_dict
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error searching {db_name} database: {e}")
            if 'conn' in locals():
                conn.close()
    
    logger.warning(f"❌ ISIN {isin} not found in any database")
    return None


def get_isin_error_response(isin: str, description: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a helpful error response when ISIN is not found.
    
    Args:
        isin: The ISIN that was not found
        description: Optional description that was provided
        
    Returns:
        Error response dictionary
    """
    error_response = {
        'status': 'error',
        'code': 404,
        'message': 'Bond not found',
        'details': {
            'isin_provided': isin,
            'description_provided': description,
            'error': f'ISIN {isin} not found in bond database'
        },
        'suggestions': [
            'Verify the ISIN is correct',
            'Try providing a bond description instead',
            'Common formats: "T 3 15/08/52", "AAPL 4.5 02/23/36"',
            'The ISIN may not be in our current database coverage'
        ]
    }
    
    if not description:
        error_response['details']['error'] += ' and no description provided'
        error_response['suggestions'].insert(1, 'Provide both ISIN and description for better results')
    
    return error_response


# Test function
if __name__ == "__main__":
    # Test ISIN lookup
    test_isin = "US912810TJ79"
    
    # You'll need to adjust these paths for your environment
    db_path = "bonds_data.db"
    validated_db = "validated_quantlib_bonds.db"
    bloomberg_db = "bloomberg_index.db"
    
    result = lookup_isin_in_database(test_isin, db_path, validated_db, bloomberg_db)
    
    if result:
        print(f"✅ Found ISIN {test_isin}:")
        print(f"   Description: {result.get('description')}")
        print(f"   Coupon: {result.get('coupon')}")
        print(f"   Maturity: {result.get('maturity')}")
        print(f"   Database: {result.get('database')}")
    else:
        print(f"❌ ISIN {test_isin} not found")
        error = get_isin_error_response(test_isin)
        print(f"Error response: {error}")