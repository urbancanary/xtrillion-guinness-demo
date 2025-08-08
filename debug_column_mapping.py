#!/usr/bin/env python3
"""Debug the actual column mapping"""

import requests
import pandas as pd
from datetime import datetime
from io import StringIO

# Fetch the data
url = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2025"
response = requests.get(url, timeout=30)

if response.status_code == 200:
    tables = pd.read_html(StringIO(response.text))
    df = tables[0]
    
    # Find August 1st row
    date_col = df.columns[0]
    mask = df[date_col] == '08/01/2025'
    
    if mask.any():
        row = df[mask].iloc[0]
        
        print("Column mapping for August 1st, 2025:")
        print("=====================================")
        
        # Expected values from treasury website
        expected = {
            '1M': 4.49, '2M': 4.46, '3M': 4.44, '6M': 4.35,
            '1Y': 4.30, '2Y': 4.16, '3Y': 3.87, '5Y': 3.69,
            '7Y': 3.67, '10Y': 3.77, '20Y': 3.97, '30Y': 4.23
        }
        
        print("\nExpected values from Treasury website:")
        for tenor, value in expected.items():
            print(f"  {tenor:3}: {value}")
            
        print("\nActual columns and values in DataFrame:")
        for i, col in enumerate(df.columns):
            val = row[col]
            if pd.notna(val) and col != 'Date':
                try:
                    num_val = float(val)
                    # Find which expected value this matches
                    matches = []
                    for tenor, exp_val in expected.items():
                        if abs(num_val - exp_val) < 0.01:
                            matches.append(tenor)
                    
                    match_str = f" -> Matches {', '.join(matches)}" if matches else ""
                    print(f"  Col {i:2}: '{col:25}' = {num_val:.2f}{match_str}")
                except:
                    print(f"  Col {i:2}: '{col:25}' = {val}")
                    
        # Now let's see what the issue is
        print("\nChecking specific columns:")
        test_cols = ['1 Mo', '2 Mo', '3 Mo', '6 Mo', '1 Yr', '2 Yr', '3 Yr', '5 Yr', '7 Yr', '10 Yr', '20 Yr', '30 Yr']
        
        for col in test_cols:
            if col in df.columns:
                idx = df.columns.get_loc(col)
                val = row[col]
                print(f"  '{col}' at index {idx} = {val}")