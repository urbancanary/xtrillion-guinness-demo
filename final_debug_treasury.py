#!/usr/bin/env python3
"""Final debug of treasury column mapping"""

import requests
import pandas as pd
from io import StringIO

# Fetch and parse
url = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2025"
response = requests.get(url, timeout=30)
tables = pd.read_html(StringIO(response.text))
df = tables[0]

print("All columns in DataFrame:")
for i, col in enumerate(df.columns):
    print(f"  {i:2}: '{col}'")

# Check August 1st mapping
mask = df[df.columns[0]] == '08/01/2025'
if mask.any():
    row = df[mask].iloc[0]
    
    print("\nAugust 1st, 2025 - Column values:")
    print("Column Name -> Value")
    print("-" * 40)
    
    # Show all non-null values
    for col in df.columns:
        val = row[col]
        if pd.notna(val) and col != 'Date':
            try:
                print(f"{col.strip():15} -> {float(val):6.2f}")
            except:
                print(f"{col.strip():15} -> {val}")
                
print("\nFrom Treasury website you provided:")
print("1 Mo: 4.49, 1.5 Mo: 4.46, 2 Mo: 4.44, 3 Mo: 4.35, 4 Mo: 4.30")
print("6 Mo: 4.16, 1 Yr: 3.87, 2 Yr: 3.69, 3 Yr: 3.67, 5 Yr: 3.77")
print("7 Yr: 3.97, 10 Yr: 4.23, 20 Yr: 4.79, 30 Yr: 4.81")