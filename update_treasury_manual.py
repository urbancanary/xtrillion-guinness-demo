#!/usr/bin/env python3
"""
Manually update treasury yields with current market data
"""

import sqlite3
from datetime import datetime
from database_config import BONDS_DATA_DB

# Current treasury yields as of August 8, 2025
# Source: https://www.treasury.gov/resource-center/data-chart-center/interest-rates/
CURRENT_YIELDS = {
    'M1M': 4.28,   # 1 Month
    'M2M': 4.31,   # 2 Month
    'M3M': 4.35,   # 3 Month
    'M6M': 4.15,   # 6 Month
    'M1Y': 3.87,   # 1 Year
    'M2Y': 3.65,   # 2 Year
    'M3Y': 3.62,   # 3 Year
    'M5Y': 3.77,   # 5 Year
    'M7Y': 3.93,   # 7 Year
    'M10Y': 4.11,  # 10 Year
    'M20Y': 4.55,  # 20 Year
    'M30Y': 4.45   # 30 Year
}

def update_treasury_yields():
    """Update treasury yields in database"""
    conn = sqlite3.connect(BONDS_DATA_DB)
    cursor = conn.cursor()
    
    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')
    
    # First, let's check what table structure we have
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%treasury%'")
    tables = cursor.fetchall()
    print(f"Found treasury tables: {[t[0] for t in tables]}")
    
    # Let's check if us_treasury_yields table exists, if not create it
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS us_treasury_yields (
            Date DATE PRIMARY KEY,
            M1M REAL,
            M2M REAL,
            M3M REAL,
            M6M REAL,
            M1Y REAL,
            M2Y REAL,
            M3Y REAL,
            M5Y REAL,
            M7Y REAL,
            M10Y REAL,
            M20Y REAL,
            M30Y REAL,
            source TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    
    # Check if today's data already exists
    cursor.execute("SELECT COUNT(*) FROM us_treasury_yields WHERE Date = ?", (today,))
    if cursor.fetchone()[0] > 0:
        print(f"✅ Treasury data for {today} already exists. Updating...")
        # Update existing record
        update_query = f"""
        UPDATE us_treasury_yields 
        SET {', '.join([f'{col} = ?' for col in CURRENT_YIELDS.keys()])},
            source = 'manual_update',
            updated_at = datetime('now')
        WHERE Date = ?
        """
        cursor.execute(update_query, list(CURRENT_YIELDS.values()) + [today])
    else:
        print(f"📊 Inserting new treasury data for {today}")
        # Insert new record
        columns = ['Date'] + list(CURRENT_YIELDS.keys()) + ['source', 'created_at', 'updated_at']
        values = [today] + list(CURRENT_YIELDS.values()) + ['manual_update', datetime.now(), datetime.now()]
        
        insert_query = f"""
        INSERT INTO us_treasury_yields ({', '.join(columns)})
        VALUES ({', '.join(['?' for _ in columns])})
        """
        cursor.execute(insert_query, values)
    
    conn.commit()
    
    # Verify the update
    cursor.execute(f"SELECT Date, M1Y, M5Y, M10Y, M30Y FROM us_treasury_yields WHERE Date = ?", (today,))
    row = cursor.fetchone()
    
    if row:
        print(f"\n✅ Successfully updated treasury yields for {today}:")
        print(f"   1Y: {row[1]}%")
        print(f"   5Y: {row[2]}%")
        print(f"   10Y: {row[3]}%")
        print(f"   30Y: {row[4]}%")
    
    conn.close()

if __name__ == "__main__":
    update_treasury_yields()