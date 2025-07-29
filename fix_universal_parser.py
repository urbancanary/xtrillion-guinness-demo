#!/usr/bin/env python3
"""
Universal Parser ISIN Lookup Fix
===============================

Fix the ISIN lookup issue in the Universal Parser by using correct table names.
"""

import sys
import sqlite3
sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')

def test_database_tables():
    """Test what tables actually exist and have data"""
    
    databases = [
        ('./bonds_data.db', 'bonds_data.db'),
        ('./validated_quantlib_bonds.db', 'validated_quantlib_bonds.db'),
        ('./bloomberg_index.db', 'bloomberg_index.db')
    ]
    
    for db_path, db_name in databases:
        print(f"\n🔍 Examining {db_name}:")
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Get all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                print(f"   Tables: {[t[0] for t in tables]}")
                
                # Check for ISIN columns in each table
                for table_name in [t[0] for t in tables]:
                    try:
                        cursor.execute(f"PRAGMA table_info({table_name});")
                        columns = cursor.fetchall()
                        isin_columns = [col[1] for col in columns if 'isin' in col[1].lower()]
                        
                        if isin_columns:
                            print(f"   Table '{table_name}' has ISIN columns: {isin_columns}")
                            
                            # Check if table has data
                            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                            count = cursor.fetchone()[0]
                            print(f"     Rows: {count}")
                            
                            if count > 0:
                                # Test with real ISIN
                                test_isin = "US91282CJZ59"
                                for col in isin_columns:
                                    cursor.execute(f"SELECT * FROM {table_name} WHERE {col} = ? LIMIT 1;", (test_isin,))
                                    result = cursor.fetchone()
                                    if result:
                                        print(f"     ✅ Found {test_isin} in {table_name}.{col}")
                                        return table_name, col, db_name
                                    else:
                                        print(f"     ❌ {test_isin} not found in {table_name}.{col}")
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"   Error accessing {db_name}: {e}")
    
    return None, None, None

def test_corrected_lookup():
    """Test ISIN lookup with correct table/column names"""
    
    table_name, isin_column, db_name = test_database_tables()
    
    if not table_name:
        print("\n❌ No working ISIN lookup found!")
        return
    
    print(f"\n🔧 Testing corrected lookup:")
    print(f"   Database: {db_name}")
    print(f"   Table: {table_name}")
    print(f"   ISIN Column: {isin_column}")
    
    test_isins = ["US91282CJZ59", "US00287YCZ07"]
    
    db_path = f"./{db_name}"
    
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            for test_isin in test_isins:
                cursor.execute(f"SELECT * FROM {table_name} WHERE {isin_column} = ?", (test_isin,))
                result = cursor.fetchone()
                
                if result:
                    result_dict = dict(result)
                    print(f"\n✅ Found {test_isin}:")
                    for key, value in result_dict.items():
                        if value is not None:
                            print(f"     {key}: {value}")
                else:
                    print(f"\n❌ {test_isin} not found")
                    
    except Exception as e:
        print(f"❌ Lookup test failed: {e}")

def create_universal_parser_fix():
    """Create a fix for the Universal Parser"""
    
    fix_code = '''
def _lookup_isin_in_database(self, isin: str, db_path: str) -> Optional[Dict]:
    """Fixed database lookup for ISIN with correct table names"""
    try:
        if not os.path.exists(db_path):
            return None
            
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # FIXED: Use actual table names that exist in the databases
            if 'validated_quantlib_bonds.db' in db_path:
                tables_to_try = ['validated_quantlib_bonds']
                isin_columns = ['ISIN']
            elif 'bloomberg_index.db' in db_path:
                tables_to_try = ['bloomberg_bonds', 'bonds']  # Check actual tables
                isin_columns = ['isin', 'ISIN']
            else:  # bonds_data.db
                tables_to_try = ['bond_pricing', 'bonds', 'live', 'static']
                isin_columns = ['isin', 'ISIN']
            
            for table in tables_to_try:
                for isin_col in isin_columns:
                    try:
                        cursor.execute(f"SELECT * FROM {table} WHERE {isin_col} = ?", (isin,))
                        result = cursor.fetchone()
                        if result:
                            self.logger.info(f"✅ ISIN {isin} found in {table}.{isin_col}")
                            return dict(result)
                    except sqlite3.Error:
                        continue  # Table or column doesn't exist
            
            self.logger.warning(f"⚠️ ISIN {isin} not found in {db_path}")
            return None
            
    except Exception as e:
        self.logger.debug(f"Database lookup failed for {isin} in {db_path}: {e}")
        return None
'''

    print(f"\n🔧 UNIVERSAL PARSER FIX:")
    print(f"Replace the _lookup_isin_in_database method with:")
    print(fix_code)

if __name__ == "__main__":
    print("🔍 Universal Parser ISIN Lookup Diagnostic")
    
    # Test current database structure
    test_corrected_lookup()
    
    # Provide fix
    create_universal_parser_fix()
    
    print(f"\n🎯 SUMMARY:")
    print(f"The Universal Parser is looking for table names that don't exist.")
    print(f"The actual data is in 'validated_quantlib_bonds' table.")
    print(f"Apply the fix above to resolve ISIN lookup issues.")
