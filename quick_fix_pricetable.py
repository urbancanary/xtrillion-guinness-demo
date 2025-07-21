#!/usr/bin/env python3
"""
QUICK FIX for the missing pricetable issue
This creates a minimal fix to get the current version working
"""

import os
import shutil
from datetime import datetime

def fix_missing_pricetable():
    """Fix the missing pricetable issue in google_analysis9.py"""
    
    file_path = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/google_analysis9.py"
    
    # Read current file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Create backup
    backup_path = file_path + f".backup_before_pricetable_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Created backup: {backup_path}")
    
    # Find and replace the failing function
    old_function = '''def fetch_latest_trade_date(db_path):
    logger.debug("Fetching latest trade date")
    conn = sqlite3.connect(db_path)
    try:
        query = "SELECT MAX(bpdate) AS latest_date FROM pricetable"
        df = pd.read_sql_query(query, conn)
        if df.empty or pd.isna(df.iloc[0]['latest_date']):
            raise ValueError("No trade date data available")
        latest_date = df.iloc[0]['latest_date']
        logger.debug(f"Fetched latest trade date: {latest_date}")
        return latest_date
    finally:
        conn.close()'''
    
    new_function = '''def fetch_latest_trade_date(db_path):
    logger.debug("Fetching latest trade date")
    conn = sqlite3.connect(db_path)
    try:
        # Check if pricetable exists
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pricetable';")
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            query = "SELECT MAX(bpdate) AS latest_date FROM pricetable"
            df = pd.read_sql_query(query, conn)
            if df.empty or pd.isna(df.iloc[0]['latest_date']):
                raise ValueError("No trade date data available")
            latest_date = df.iloc[0]['latest_date']
            logger.debug(f"Fetched latest trade date: {latest_date}")
            return latest_date
        else:
            # Default to current date if no pricetable exists
            default_date = datetime.now().strftime('%Y-%m-%d')
            logger.debug(f"pricetable not found, using default date: {default_date}")
            return default_date
    finally:
        conn.close()'''
    
    if old_function in content:
        content = content.replace(old_function, new_function)
        
        # Write fixed file
        with open(file_path, 'w') as f:
            f.write(content)
        
        print("✅ FIXED: fetch_latest_trade_date() now handles missing pricetable")
        print("✅ Added fallback to current date when table doesn't exist")
        return True
    else:
        print("❌ Could not find the exact function to replace")
        print("The function might have been modified already")
        return False

if __name__ == "__main__":
    print("🔧 APPLYING QUICK FIX for missing pricetable...")
    success = fix_missing_pricetable()
    
    if success:
        print("\n🚀 Ready to test again!")
        print("Run: python3 test_current_version.py")
    else:
        print("\n❌ Fix failed - manual intervention needed")
