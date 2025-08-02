#!/usr/bin/env python3
"""
Database ISIN Inspector - Check what ISINs are actually in the databases
========================================================================
This will help us understand why ISIN lookups are failing
"""

import sqlite3
import os
import pandas as pd
from typing import Dict, List, Optional

# Database paths (same as API uses)
DATABASE_PATHS = {
    'primary': './bonds_data.db',
    'validated': './validated_quantlib_bonds.db', 
    'bloomberg': './bloomberg_index.db'
}

# Sample ISINs we're trying to find
TEST_ISINS = [
    "US912810TJ79",  # US TREASURY N/B, 3%, 15-Aug-2052
    "XS2249741674",  # GALAXY PIPELINE, 3.25%, 30-Sep-2040
    "US279158AJ82",  # ECOPETROL SA, 5.875%, 28-May-2045
    "US195325DX04",  # COLOMBIA REP OF, 3.875%, 15-Feb-2061
    "US698299BL70",  # PANAMA, 3.87%, 23-Jul-2060
]

def inspect_database_structure(db_path: str, db_name: str):
    """Inspect database structure and ISIN availability"""
    
    if not os.path.exists(db_path):
        print(f"❌ {db_name}: Database not found at {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get database size
        size_mb = os.path.getsize(db_path) / (1024 * 1024)
        print(f"\n📊 {db_name}: {db_path} ({size_mb:.1f}MB)")
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print(f"   ⚠️  No tables found")
            return
            
        print(f"   📋 Tables: {[table[0] for table in tables]}")
        
        # For each table, check if it has ISIN column and count records
        for table_name in [table[0] for table in tables]:
            try:
                # Get column info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                # Get record count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                record_count = cursor.fetchone()[0]
                
                print(f"   📁 {table_name}: {record_count:,} records")
                print(f"      Columns: {column_names[:10]}{'...' if len(column_names) > 10 else ''}")
                
                # Check for ISIN column
                isin_columns = [col for col in column_names if 'isin' in col.lower()]
                if isin_columns:
                    print(f"      🔍 ISIN columns found: {isin_columns}")
                    
                    # Sample some ISINs from this table
                    for isin_col in isin_columns[:2]:  # Check first 2 ISIN columns
                        cursor.execute(f"SELECT DISTINCT {isin_col} FROM {table_name} WHERE {isin_col} IS NOT NULL LIMIT 5")
                        sample_isins = cursor.fetchall()
                        if sample_isins:
                            print(f"      📋 Sample {isin_col}: {[isin[0] for isin in sample_isins]}")
                else:
                    print(f"      ❌ No ISIN columns found")
                    
            except Exception as e:
                print(f"   ❌ Error inspecting table {table_name}: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ {db_name}: Error accessing database: {e}")

def test_isin_lookups():
    """Test if our sample ISINs can be found in any database"""
    
    print(f"\n🔍 TESTING ISIN LOOKUPS FOR SAMPLE BONDS")
    print("=" * 60)
    
    for isin in TEST_ISINS:
        print(f"\n🎯 Looking for ISIN: {isin}")
        found_in = []
        
        for db_name, db_path in DATABASE_PATHS.items():
            if not os.path.exists(db_path):
                continue
                
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Get all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                for table_name in [table[0] for table in tables]:
                    try:
                        # Get column names
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = cursor.fetchall()
                        column_names = [col[1] for col in columns]
                        
                        # Check each potential ISIN column
                        for col_name in column_names:
                            if 'isin' in col_name.lower():
                                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} = ?", (isin,))
                                count = cursor.fetchone()[0]
                                
                                if count > 0:
                                    # Get some sample data from this match
                                    cursor.execute(f"SELECT * FROM {table_name} WHERE {col_name} = ? LIMIT 1", (isin,))
                                    sample_row = cursor.fetchone()
                                    found_in.append(f"{db_name}.{table_name}.{col_name}")
                                    print(f"   ✅ Found in {db_name}.{table_name}.{col_name} ({count} matches)")
                                    
                                    # Show relevant columns from the match
                                    if sample_row and len(column_names) > 1:
                                        sample_dict = dict(zip(column_names, sample_row))
                                        relevant_keys = [k for k in sample_dict.keys() if any(x in k.lower() for x in ['name', 'description', 'coupon', 'maturity', 'yield', 'duration'])][:5]
                                        if relevant_keys:
                                            print(f"      📋 Sample data: {', '.join([f'{k}={sample_dict[k]}' for k in relevant_keys])}")
                                    
                    except Exception as e:
                        continue  # Skip problematic tables
                        
                conn.close()
                
            except Exception as e:
                print(f"   ❌ Error checking {db_name}: {e}")
        
        if not found_in:
            print(f"   ❌ NOT FOUND in any database")
        else:
            print(f"   ✅ Found in: {', '.join(found_in)}")

def main():
    """Main inspection function"""
    
    print("🔍 DATABASE ISIN INSPECTOR")
    print("="*80)
    print("Checking what ISINs are actually available in our databases")
    print("This will help diagnose why ISIN lookups are failing")
    print("="*80)
    
    # Change to the correct directory
    os.chdir('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')
    
    # Inspect each database
    for db_name, db_path in DATABASE_PATHS.items():
        inspect_database_structure(db_path, db_name)
    
    # Test specific ISIN lookups
    test_isin_lookups()
    
    print(f"\n🎯 SUMMARY")
    print("="*60)
    print("This inspection shows:")
    print("- Which databases exist and their sizes")
    print("- What tables and ISIN columns are available") 
    print("- Whether our test ISINs can be found")
    print("- Sample data from any matches")
    print("\nIf no ISINs are found, we need to:")
    print("1. Check if we're looking in the right tables/columns")
    print("2. Verify the ISIN format (maybe they're stored differently)")
    print("3. Consider importing Bloomberg ISINs into the database")

if __name__ == "__main__":
    main()
