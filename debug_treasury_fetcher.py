#!/usr/bin/env python3
"""Debug treasury fetcher to see what data it's getting"""

import requests
import pandas as pd
from datetime import datetime
from io import StringIO

# Test fetching the treasury data
url = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2025"

print("Fetching treasury data...")
response = requests.get(url, timeout=30)
print(f"Status code: {response.status_code}")

if response.status_code == 200:
    # Parse HTML tables
    tables = pd.read_html(StringIO(response.text))
    
    if tables:
        df = tables[0]
        print(f"\nTable shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Show first few rows
        print("\nFirst 5 rows:")
        print(df.head())
        
        # Look for August 1st data
        print("\nLooking for 08/01/2025...")
        date_col = df.columns[0]
        
        # Try different date formats
        for date_format in ['08/01/2025', '8/1/2025', '2025-08-01']:
            mask = df[date_col] == date_format
            if mask.any():
                print(f"\nFound data for {date_format}:")
                print(df[mask])
                
                # Show the actual values
                row = df[mask].iloc[0]
                print("\nColumn mapping:")
                for i, col in enumerate(df.columns):
                    print(f"  Column {i}: '{col}' = {row[col]}")
                break
        else:
            print("Could not find August 1st data")
            print(f"\nAvailable dates (last 5):")
            print(df[date_col].tail())