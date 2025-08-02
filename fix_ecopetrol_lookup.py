#!/usr/bin/env python3
"""
Fix for ECOPETROL ISIN lookup
"""

import sqlite3
import logging

logger = logging.getLogger(__name__)

def find_isin_from_parsed_data(parsed_data, validated_db_path):
    """
    Find ISIN from validated database using parsed bond details
    """
    if not parsed_data or not validated_db_path:
        return None
        
    try:
        coupon = parsed_data.get('coupon')
        maturity = parsed_data.get('maturity')
        issuer = parsed_data.get('issuer', '').upper()
        
        if not coupon or not maturity:
            return None
            
        # Connect to validated database
        with sqlite3.connect(validated_db_path) as conn:
            cursor = conn.cursor()
            
            # Try exact match first
            query = """
            SELECT isin, description 
            FROM validated_quantlib_bonds 
            WHERE coupon = ? 
            AND maturity = ?
            """
            
            cursor.execute(query, (coupon, maturity))
            results = cursor.fetchall()
            
            # If we have results, try to match by issuer
            for isin, description in results:
                desc_upper = description.upper()
                # Check if issuer matches
                if 'ECOPETROL' in issuer and 'ECOPET' in desc_upper:
                    logger.info(f"✅ Found ISIN {isin} for ECOPETROL bond via validated DB lookup")
                    return isin
                elif 'PEMEX' in issuer and 'PEMEX' in desc_upper:
                    logger.info(f"✅ Found ISIN {isin} for PEMEX bond via validated DB lookup")
                    return isin
                # Add more issuer mappings as needed
                
            # If no issuer match, return first result if only one
            if len(results) == 1:
                isin = results[0][0]
                logger.info(f"✅ Found unique ISIN {isin} via coupon/maturity match")
                return isin
                
    except Exception as e:
        logger.error(f"Error finding ISIN from parsed data: {e}")
        
    return None

def test_lookup():
    """Test the ISIN lookup"""
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Test ECOPETROL
    parsed_data = {
        'issuer': 'ECOPETROL SA',
        'coupon': 5.875,
        'maturity': '2045-05-28'
    }
    
    validated_db_path = './validated_quantlib_bonds.db'
    
    isin = find_isin_from_parsed_data(parsed_data, validated_db_path)
    print(f"Found ISIN: {isin}")
    
    # Verify the ISIN
    if isin:
        with sqlite3.connect(validated_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT description, fixed_business_convention, bloomberg_accrued 
                FROM validated_quantlib_bonds 
                WHERE isin = ?
            """, (isin,))
            result = cursor.fetchone()
            if result:
                print(f"Description: {result[0]}")
                print(f"Business Convention: {result[1]}")
                print(f"Bloomberg Accrued: ${result[2]:.2f}")

if __name__ == "__main__":
    test_lookup()