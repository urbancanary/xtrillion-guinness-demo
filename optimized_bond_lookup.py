#!/usr/bin/env python3
"""
🎯 Google Analysis 10 - Optimized Bond Lookup Hierarchy
Implements the performance-optimized lookup strategy based on database analysis
"""

import sqlite3
import time
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
import logging

class OptimizedBondLookup:
    """
    Optimized bond lookup following priority hierarchy:
    1. validated_quantlib_bonds.db (fastest, highest quality)
    2. Description provided (skip database lookups)
    3. ISIN → Description lookup (fast, controlled)
    4. Error with user guidance
    """
    
    def __init__(self, base_path: str = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10"):
        self.base_path = Path(base_path)
        self.logger = logging.getLogger(__name__)
        
        # Database hierarchy (order matters for performance)
        self.databases = {
            'validated': self.base_path / 'validated_quantlib_bonds.db',
            'primary': self.base_path / 'bonds_data.db',
            'secondary': self.base_path / 'bloomberg_index.db'
        }
        
        # Cache for performance
        self._connection_cache = {}
        self._description_cache = {}
    
    def get_connection(self, db_name: str) -> sqlite3.Connection:
        """Get cached database connection"""
        if db_name not in self._connection_cache:
            db_path = self.databases[db_name]
            if db_path.exists():
                self._connection_cache[db_name] = sqlite3.connect(str(db_path))
                self._connection_cache[db_name].row_factory = sqlite3.Row
        return self._connection_cache.get(db_name)
    
    def lookup_bond_hierarchy(self, isin: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Main lookup function following optimized hierarchy
        """
        start_time = time.time()
        
        # Input validation
        if not isin and not description:
            return self._insufficient_input_error()
        
        # PRIORITY 1: Check validated_quantlib_bonds.db first (FASTEST + BEST QUALITY)
        if isin:
            validated_result = self._check_validated_quantlib_bonds(isin)
            if validated_result:
                elapsed_ms = int((time.time() - start_time) * 1000)
                return {
                    **validated_result,
                    'route_used': 'validated_quantlib_bonds',
                    'lookup_time_ms': elapsed_ms,
                    'hierarchy_level': 1,
                    'status': 'success'
                }
        
        # PRIORITY 2: Description provided - skip database lookups (EFFICIENT)
        if description:
            parsed_result = self._parse_description_directly(description)
            elapsed_ms = int((time.time() - start_time) * 1000)
            return {
                **parsed_result,
                'route_used': 'description_parsing',
                'lookup_time_ms': elapsed_ms,
                'hierarchy_level': 2,
                'status': 'success'
            }
        
        # PRIORITY 3: ISIN → Description lookup (CONTROLLED SPEED)
        if isin:
            found_description = self._fast_description_lookup(isin)
            if found_description:
                parsed_result = self._parse_description_directly(found_description['description'])
                elapsed_ms = int((time.time() - start_time) * 1000)
                return {
                    **parsed_result,
                    'route_used': f"isin_to_description_{found_description['source']}",
                    'lookup_time_ms': elapsed_ms,
                    'hierarchy_level': 3,
                    'status': 'success',
                    'original_isin': isin
                }
        
        # PRIORITY 4: Error with user guidance
        elapsed_ms = int((time.time() - start_time) * 1000)
        return {
            **self._insufficient_input_error(),
            'lookup_time_ms': elapsed_ms,
            'hierarchy_level': 4,
            'attempted_isin': isin
        }
    
    def _check_validated_quantlib_bonds(self, isin: str) -> Optional[Dict[str, Any]]:
        """
        Check validated_quantlib_bonds.db - highest priority
        Returns complete bond data with validated conventions
        """
        try:
            conn = self.get_connection('validated')
            if not conn:
                return None
            
            cursor = conn.cursor()
            
            # Look for ISIN in validated bonds table (using correct column names)
            cursor.execute("""
                SELECT isin, description, coupon, maturity, 
                       fixed_day_count, fixed_business_convention, fixed_frequency,
                       bloomberg_accrued, quantlib_accrued, difference,
                       pass_status, validation_date
                FROM validated_quantlib_bonds 
                WHERE isin = ? AND pass_status = 'PASS' LIMIT 1
            """, (isin,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'isin': row['isin'],
                    'description': row['description'],
                    'coupon': row['coupon'],
                    'maturity': row['maturity'],
                    'conventions': {
                        'day_count': row['fixed_day_count'],
                        'fixed_frequency': row['fixed_frequency'],
                        'business_day_convention': row['fixed_business_convention'],
                        'end_of_month': True  # Default for most bonds
                    },
                    'bloomberg_accrued': row['bloomberg_accrued'],
                    'quantlib_accrued': row['quantlib_accrued'],
                    'difference': row['difference'],
                    'validation_date': row['validation_date'],
                    'data_quality': 'validated'
                }
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error checking validated_quantlib_bonds for {isin}: {e}")
            return None
    
    def _parse_description_directly(self, description: str) -> Dict[str, Any]:
        """
        Parse bond description directly - used when description is provided
        This would integrate with your existing description parsing logic
        """
        # Placeholder for your existing description parsing logic
        # This should integrate with bloomberg_accrued_calculator.py or similar
        
        return {
            'description': description,
            'conventions': {
                'day_count': 'parsed_from_description',
                'fixed_frequency': 'parsed_from_description',
                'business_day_convention': 'parsed_from_description'
            },
            'data_quality': 'parsed'
        }
    
    def _fast_description_lookup(self, isin: str) -> Optional[Dict[str, str]]:
        """
        Fast lookup of description from ISIN in primary databases
        Returns description and source database
        """
        # Check cache first
        if isin in self._description_cache:
            return self._description_cache[isin]
        
        # Try primary database first (bonds_data.db)
        description = self._lookup_description_in_db('primary', isin)
        if description:
            result = {'description': description, 'source': 'bonds_data'}
            self._description_cache[isin] = result
            return result
        
        # Try secondary database (bloomberg_index.db)
        description = self._lookup_description_in_db('secondary', isin)
        if description:
            result = {'description': description, 'source': 'bloomberg_index'}
            self._description_cache[isin] = result
            return result
        
        return None
    
    def _lookup_description_in_db(self, db_name: str, isin: str) -> Optional[str]:
        """
        Lookup description in specific database
        Fast, targeted query
        """
        try:
            conn = self.get_connection(db_name)
            if not conn:
                return None
            
            cursor = conn.cursor()
            
            if db_name == 'primary':  # bonds_data.db
                # Try most likely tables first for speed (using correct column names)
                tables_to_check = [
                    ('description', 'ISIN', 'Description'),  # Correct column names
                    ('static', 'isin', 'descr'),
                    ('live', 'isin', 'descr'),
                    ('raw', 'isin', 'descr')
                ]
                
                for table, isin_col, desc_col in tables_to_check:
                    try:
                        cursor.execute(f"""
                            SELECT {desc_col} FROM {table} 
                            WHERE {isin_col} = ? AND {desc_col} IS NOT NULL 
                            LIMIT 1
                        """, (isin,))
                        
                        row = cursor.fetchone()
                        if row and row[0]:
                            return row[0]
                    except:
                        continue  # Table might not exist or have different schema
            
            elif db_name == 'secondary':  # bloomberg_index.db
                # Check all_bonds table (using correct column name)
                try:
                    cursor.execute("""
                        SELECT description FROM all_bonds 
                        WHERE isin = ? AND description IS NOT NULL 
                        LIMIT 1
                    """, (isin,))
                    
                    row = cursor.fetchone()
                    if row and row[0]:
                        return row[0]
                except:
                    pass
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error looking up description in {db_name} for {isin}: {e}")
            return None
    
    def _insufficient_input_error(self) -> Dict[str, Any]:
        """
        Return helpful error when insufficient input provided
        """
        return {
            'status': 'error',
            'error': 'Insufficient bond identification',
            'message': 'Please provide bond description for calculation',
            'examples': [
                'T 3 15/08/52',
                'ECOPETROL SA, 5.875%, 28-May-2045',
                'PANAMA, 3.87%, 23-Jul-2060',
                'US TREASURY N/B, 3%, 15-Aug-2052'
            ],
            'note': 'Bond descriptions work better than ISINs for calculation speed'
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            'cache_size': len(self._description_cache),
            'connections_active': len(self._connection_cache),
            'databases_available': {
                name: path.exists() for name, path in self.databases.items()
            }
        }
    
    def clear_cache(self):
        """Clear performance cache"""
        self._description_cache.clear()
        for conn in self._connection_cache.values():
            conn.close()
        self._connection_cache.clear()

# Example usage and testing
def test_optimized_lookup():
    """Test the optimized lookup hierarchy"""
    lookup = OptimizedBondLookup()
    
    test_cases = [
        # Test case 1: ISIN in validated DB (should be fastest)
        {'isin': 'US912810TJ79', 'description': None},
        
        # Test case 2: Description provided (should skip DB lookups)
        {'isin': None, 'description': 'T 3 15/08/52'},
        
        # Test case 3: ISIN not in validated, needs description lookup
        {'isin': 'XS2249741674', 'description': None},
        
        # Test case 4: Insufficient input (should give helpful error)
        {'isin': None, 'description': None},
        
        # Test case 5: Both ISIN and description (should prioritize validated)
        {'isin': 'US912810TJ79', 'description': 'T 3 15/08/52'}
    ]
    
    print("🧪 Testing Optimized Bond Lookup Hierarchy")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📊 Test Case {i}: ISIN={test_case['isin']}, Description={test_case['description']}")
        
        result = lookup.lookup_bond_hierarchy(
            isin=test_case['isin'],
            description=test_case['description']
        )
        
        print(f"   Status: {result['status']}")
        print(f"   Route: {result.get('route_used', 'N/A')}")
        print(f"   Hierarchy Level: {result.get('hierarchy_level', 'N/A')}")
        print(f"   Lookup Time: {result.get('lookup_time_ms', 0)}ms")
        
        if result['status'] == 'error':
            print(f"   Error: {result.get('message', 'N/A')}")

if __name__ == "__main__":
    test_optimized_lookup()
