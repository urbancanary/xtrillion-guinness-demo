#!/usr/bin/env python3
"""
Database ISIN Inspection - Check what ISINs are actually in our databases
=========================================================================
"""

import sqlite3
import os
from typing import Dict, List

def inspect_database(db_path: str, table_name: str = None) -> Dict:
    """Inspect a database and show sample ISINs"""
    if not os.path.exists(db_path):
        return {"error": f"Database not found: {db_path}"}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        result = {
            "database": db_path,
            "size_mb": round(os.path.getsize(db_path) / 1024 / 1024, 1),
            "tables": tables,
            "table_data": {}
        }
        
        # Inspect each table for ISIN columns
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Look for ISIN-like columns
            isin_columns = [col for col in columns if 'isin' in col.lower()]
            
            if isin_columns:
                # Get sample data
                cursor.execute(f"SELECT * FROM {table} LIMIT 5")
                sample_rows = cursor.fetchall()
                
                # Get total row count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                total_rows = cursor.fetchone()[0]
                
                result["table_data"][table] = {
                    "columns": columns,
                    "isin_columns": isin_columns,
                    "total_rows": total_rows,
                    "sample_data": sample_rows
                }
        
        conn.close()
        return result
        
    except Exception as e:
        return {"error": f"Database error: {e}"}

def check_specific_isins(db_path: str, isins: List[str]) -> Dict:
    """Check if specific ISINs exist in database"""
    if not os.path.exists(db_path):
        return {"error": f"Database not found: {db_path}"}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        found_isins = {}
        
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Look for ISIN-like columns
            isin_columns = [col for col in columns if 'isin' in col.lower()]
            
            if isin_columns:
                for isin_col in isin_columns:
                    for isin in isins:
                        cursor.execute(f"SELECT * FROM {table} WHERE {isin_col} = ?", (isin,))
                        rows = cursor.fetchall()
                        if rows:
                            if isin not in found_isins:
                                found_isins[isin] = []
                            found_isins[isin].append({
                                "table": table,
                                "column": isin_col,
                                "rows_found": len(rows),
                                "sample_row": rows[0] if rows else None
                            })
        
        conn.close()
        return {
            "database": db_path,
            "isins_checked": len(isins),
            "isins_found": len(found_isins),
            "found_details": found_isins
        }
        
    except Exception as e:
        return {"error": f"Database error: {e}"}

def main():
    """Main inspection function"""
    print("🔍 DATABASE ISIN INSPECTION")
    print("="*60)
    
    # Test ISINs from our failed bonds
    test_isins = [
        "US912810TJ79",  # US Treasury
        "US279158AJ82",  # ECOPETROL 
        "US698299BL70",  # PANAMA
        "XS2249741674",  # GALAXY PIPELINE
        "US195325DX04",  # COLOMBIA
        "US71654QDF63",  # PETROLEOS MEXICA
        "XS1959337749"   # QATAR
    ]
    
    databases = [
        "./bonds_data.db",
        "./validated_quantlib_bonds.db", 
        "./bloomberg_index.db",
        "./bloomberg_index_ticker.db",
        "./portfolio_database.db"
    ]
    
    print(f"Testing {len(test_isins)} ISINs across {len(databases)} databases")
    print(f"Test ISINs: {', '.join(test_isins[:3])}...")
    
    for db_path in databases:
        print(f"\n{'='*60}")
        print(f"🗄️  DATABASE: {db_path}")
        print(f"{'='*60}")
        
        # Basic inspection
        inspection = inspect_database(db_path)
        
        if "error" in inspection:
            print(f"❌ {inspection['error']}")
            continue
            
        print(f"📊 Size: {inspection['size_mb']}MB")
        print(f"📋 Tables: {len(inspection['tables'])}")
        
        if inspection['table_data']:
            print(f"🔑 Tables with ISIN columns:")
            for table, data in inspection['table_data'].items():
                print(f"   • {table}: {data['total_rows']} rows, ISIN cols: {data['isin_columns']}")
        else:
            print(f"⚠️  No tables with ISIN columns found")
            
        # Check for specific ISINs
        print(f"\n🔍 Checking for our test ISINs...")
        isin_check = check_specific_isins(db_path, test_isins)
        
        if "error" in isin_check:
            print(f"❌ {isin_check['error']}")
            continue
            
        print(f"📊 ISINs Found: {isin_check['isins_found']}/{isin_check['isins_checked']}")
        
        if isin_check['found_details']:
            print(f"✅ Found ISINs:")
            for isin, details in isin_check['found_details'].items():
                print(f"   • {isin}: Found in {len(details)} locations")
                for detail in details:
                    print(f"     - Table: {detail['table']}, Column: {detail['column']}, Rows: {detail['rows_found']}")
        else:
            print(f"❌ None of our test ISINs found in this database")
    
    print(f"\n{'='*60}")
    print("🎯 CONCLUSION")
    print(f"{'='*60}")
    print("If none of the major ISINs (US Treasury, ECOPETROL, etc.) are found,")
    print("then the ISIN lookup failures are expected and correct behavior.")
    print("The databases may need to be populated with these ISINs.")

if __name__ == "__main__":
    main()
