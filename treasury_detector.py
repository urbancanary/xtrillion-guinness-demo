#!/usr/bin/env python3
"""
Treasury Bond Detection & Database Enhancement - Dual Database Edition
====================================================================

Automatically detect US Treasury bonds from bond names and enhance processing
with the dual database system. Works with both ../data/bonds_data.db and ../data/bloomberg_index.db.
"""

import re
import sqlite3
from datetime import datetime
from typing import Dict, Optional, Tuple
import logging

class DualDatabaseTreasuryDetector:
    """Detect and process US Treasury bonds with dual database support"""
    
    def __init__(self, primary_db_path: str, secondary_db_path: str = None):
        self.primary_db_path = primary_db_path
        self.secondary_db_path = secondary_db_path
        self.logger = logging.getLogger(__name__)
        
        # Treasury detection patterns
        self.treasury_patterns = [
            # Pattern: "T 4 1/4 11/15/34"
            (r'^T\s+([\d\s\/]+)\s+(\d{1,2})\/(\d{1,2})\/(\d{2,4})$', 'treasury'),
            
            # Pattern: "UST 2.5 05/31/24" 
            (r'^UST?\s+([\d\.]+)\s+(\d{1,2})\/(\d{1,2})\/(\d{2,4})$', 'treasury'),
            
            # Pattern: "US TREASURY 3.125 08/15/25"
            (r'^US\s*TREASURY\s+([\d\.]+)\s+(\d{1,2})\/(\d{1,2})\/(\d{2,4})$', 'treasury'),
            
            # Pattern: "TREASURY 1.75 12/31/28"
            (r'^TREASURY\s+([\d\.]+)\s+(\d{1,2})\/(\d{1,2})\/(\d{2,4})$', 'treasury'),
        ]
    
    def detect_treasury(self, bond_name: str) -> Optional[Dict]:
        """Detect if bond name matches Treasury patterns and extract data"""
        if not bond_name:
            return None
        
        bond_name = bond_name.strip().upper()
        
        for pattern, bond_type in self.treasury_patterns:
            match = re.match(pattern, bond_name)
            if match:
                groups = match.groups()
                
                try:
                    coupon_str, day, month, year = groups  # FIXED: Correct order day, month
                    
                    # Parse coupon (handle fractions)
                    if ' ' in coupon_str and '/' in coupon_str:
                        parts = coupon_str.split(' ')
                        whole = float(parts[0])
                        num, den = parts[1].split('/')
                        coupon = whole + (float(num) / float(den))
                    else:
                        coupon = float(coupon_str)
                    
                    # Parse date
                    if len(year) == 2:
                        year = f"20{year}"
                    
                    maturity = f"{year}-{month.zfill(2)}-{day.zfill(2)}"  # Now correct: 2052-08-15
                    
                    return {
                        'coupon': coupon,
                        'maturity': maturity,
                        'bond_type': bond_type,
                        'country': 'United States',
                        'region': 'North America',
                        'currency': 'USD',
                        'issuer': 'US Treasury'
                    }
                
                except (ValueError, IndexError) as e:
                    self.logger.warning(f"Failed to parse treasury bond {bond_name}: {e}")
                    continue
        
        return None
    
    def check_bond_exists_in_databases(self, isin: str) -> Tuple[bool, str]:
        """Check if bond exists in either database"""
        # Check primary database (../data/bonds_data.db/static)
        try:
            conn = sqlite3.connect(self.primary_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM static WHERE isin = ?", (isin,))
            if cursor.fetchone()[0] > 0:
                conn.close()
                return True, "primary"
            conn.close()
        except Exception as e:
            self.logger.debug(f"Error checking primary database: {e}")
        
        # Check secondary database (../data/bloomberg_index.db/all_bonds)
        if self.secondary_db_path:
            try:
                conn = sqlite3.connect(self.secondary_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM all_bonds WHERE isin = ?", (isin,))
                if cursor.fetchone()[0] > 0:
                    conn.close()
                    return True, "secondary"
                conn.close()
            except Exception as e:
                self.logger.debug(f"Error checking secondary database: {e}")
        
        return False, None
    
    def enhance_portfolio_with_treasuries(self, portfolio_data: list) -> Dict:
        """Process a list of bonds and detect treasuries (no database modification)"""
        results = {
            'treasuries_detected': 0,
            'treasuries_added': 0,
            'failed_additions': [],
            'detected_bonds': []
        }
        
        for bond in portfolio_data:
            isin = bond.get('BOND_CD') or bond.get('isin')
            name = bond.get('BOND_ENAME') or bond.get('name') or bond.get('bond_name')
            
            if not isin or not name:
                continue
            
            # Check if it's a treasury
            treasury_info = self.detect_treasury(name)
            if treasury_info:
                results['treasuries_detected'] += 1
                results['detected_bonds'].append({
                    'isin': isin,
                    'name': name,
                    'treasury_info': treasury_info
                })
                
                # Check if exists in databases
                exists, db_source = self.check_bond_exists_in_databases(isin)
                if exists:
                    self.logger.info(f"✅ Treasury {isin} found in {db_source} database")
                else:
                    self.logger.info(f"🔍 Treasury {isin} not found in databases, will use CSV parsing")
        
        return results


def enhance_bond_processing_with_treasuries(portfolio_data, primary_db_path, secondary_db_path=None):
    """
    Enhanced function for dual database treasury detection
    
    This function is called from google_analysis9_api.py and works with the dual database system.
    It detects treasuries but doesn't modify databases - the dual database manager handles data lookup.
    """
    
    # Get secondary database path if not provided
    if not secondary_db_path:
        import os
        secondary_db_path = os.environ.get('SECONDARY_DATABASE_PATH')
    
    detector = DualDatabaseTreasuryDetector(primary_db_path, secondary_db_path)
    
    # Extract bond data for processing
    if isinstance(portfolio_data, dict) and 'data' in portfolio_data:
        bonds_list = portfolio_data['data']
    else:
        bonds_list = portfolio_data
    
    # Enhance with treasury detection (but don't modify databases)
    enhancement_results = detector.enhance_portfolio_with_treasuries(bonds_list)
    
    return enhancement_results


# Backward compatibility function
def enhance_bond_processing_with_treasuries_legacy(portfolio_data, db_path):
    """Legacy function signature for backward compatibility"""
    return enhance_bond_processing_with_treasuries(portfolio_data, db_path)
