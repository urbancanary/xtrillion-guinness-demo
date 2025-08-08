#!/usr/bin/env python3
"""Verify final treasury data in database"""

import sqlite3

# Treasury website data
treasury_data = {
    '07/31/2025': [4.49, 4.47, 4.46, 4.41, 4.40, 4.31, 4.10, 3.94, 3.89, 3.96, 4.14, 4.37, 4.89, 4.89],
    '08/01/2025': [4.49, 4.46, 4.44, 4.35, 4.30, 4.16, 3.87, 3.69, 3.67, 3.77, 3.97, 4.23, 4.79, 4.81]
}

# Column mapping (treasury website -> database)
# Website has: 1Mo, 1.5Mo, 2Mo, 3Mo, 4Mo, 6Mo, 1Yr, 2Yr, 3Yr, 5Yr, 7Yr, 10Yr, 20Yr, 30Yr
# Database has: M1M, M2M, M3M, M6M, M1Y, M2Y, M3Y, M5Y, M7Y, M10Y, M20Y, M30Y
# So we skip 1.5Mo (index 1) and 4Mo (index 4)

column_mapping = [
    (0, 'M1M', '1 Mo'),
    (2, 'M2M', '2 Mo'),   # Skip 1.5 Mo
    (3, 'M3M', '3 Mo'),
    (5, 'M6M', '6 Mo'),   # Skip 4 Mo
    (6, 'M1Y', '1 Yr'),
    (7, 'M2Y', '2 Yr'),
    (8, 'M3Y', '3 Yr'),
    (9, 'M5Y', '5 Yr'),
    (10, 'M7Y', '7 Yr'),
    (11, 'M10Y', '10 Yr'),
    (12, 'M20Y', '20 Yr'),
    (13, 'M30Y', '30 Yr')
]

# Check database
conn = sqlite3.connect('bonds_data.db')
cursor = conn.cursor()

for date_display, treasury_values in treasury_data.items():
    # Convert date format
    date_db = date_display.replace('/', '-').split('-')
    date_db = f"2025-{date_db[0]}-{date_db[1]}"
    
    print(f"\nChecking {date_display} (DB: {date_db}):")
    print("=" * 60)
    
    cursor.execute("SELECT * FROM tsys_enhanced WHERE date = ?", (date_db,))
    row = cursor.fetchone()
    
    if row:
        print("Tenor | Treasury | Database | Match")
        print("------|----------|----------|------")
        
        all_match = True
        for treasury_idx, db_col, display_name in column_mapping:
            treasury_val = treasury_values[treasury_idx]
            
            # Get database column index (1=M1M, 2=M2M, etc.)
            col_idx = [i for i, (idx, col, _) in enumerate(column_mapping) if col == db_col][0] + 1
            db_val = row[col_idx]
            
            match = "✓" if abs(treasury_val - db_val) < 0.01 else "✗"
            all_match = all_match and (match == "✓")
            
            print(f"{display_name:5} | {treasury_val:8.2f} | {db_val:8.2f} | {match}")
            
        if all_match:
            print("\n✓ All values match perfectly!")
        else:
            print("\n✗ Some values don't match")
    else:
        print(f"No data found for {date_db}")

conn.close()