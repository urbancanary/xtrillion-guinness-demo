#!/usr/bin/env python3
"""Verify the correct treasury mapping based on actual treasury website data"""

# From the treasury website data you provided:
treasury_website_data = {
    '07/30/2025': {
        '1 Mo': 4.41, '1.5 Mo': 4.48, '2 Mo': 4.45, '3 Mo': 4.41, '4 Mo': 4.39,
        '6 Mo': 4.31, '1 Yr': 4.12, '2 Yr': 3.94, '3 Yr': 3.89, '5 Yr': 3.96,
        '7 Yr': 4.15, '10 Yr': 4.38, '20 Yr': 4.90, '30 Yr': 4.89
    },
    '07/31/2025': {
        '1 Mo': 4.49, '1.5 Mo': 4.47, '2 Mo': 4.46, '3 Mo': 4.41, '4 Mo': 4.40,
        '6 Mo': 4.31, '1 Yr': 4.10, '2 Yr': 3.94, '3 Yr': 3.89, '5 Yr': 3.96,
        '7 Yr': 4.14, '10 Yr': 4.37, '20 Yr': 4.89, '30 Yr': 4.89
    },
    '08/01/2025': {
        '1 Mo': 4.49, '1.5 Mo': 4.46, '2 Mo': 4.44, '3 Mo': 4.35, '4 Mo': 4.30,
        '6 Mo': 4.16, '1 Yr': 3.87, '2 Yr': 3.69, '3 Yr': 3.67, '5 Yr': 3.77,
        '7 Yr': 3.97, '10 Yr': 4.23, '20 Yr': 4.79, '30 Yr': 4.81
    }
}

# What we got from the DataFrame
dataframe_columns = [
    ('1 Mo', 4.49),
    ('1.5 Mo', 4.46),
    ('2 Mo', 4.44),
    ('3 Mo', 4.35),
    ('4 Mo', 4.30),
    ('6 Mo', 4.16),
    ('1 Yr', 3.87),
    ('2 Yr', 3.69),
    ('3 Yr', 3.67),
    ('5 Yr', 3.77),
    ('7 Yr', 3.97),
    ('10 Yr', 4.23),
    ('20 Yr', 4.79),
    ('30 Yr', 4.81)
]

print("Verifying August 1st, 2025 data:")
print("=================================")
print("\nTreasury Website vs DataFrame:")
print("Column    | Treasury | DataFrame | Match")
print("----------|----------|-----------|------")

expected_aug1 = treasury_website_data['08/01/2025']

for col_name, df_value in dataframe_columns:
    if col_name in expected_aug1:
        treasury_val = expected_aug1[col_name]
        match = "✓" if abs(treasury_val - df_value) < 0.01 else "✗"
        print(f"{col_name:9} | {treasury_val:8.2f} | {df_value:9.2f} | {match}")
    else:
        print(f"{col_name:9} | N/A      | {df_value:9.2f} | ?")

print("\nConclusion: The DataFrame values match the Treasury website perfectly!")
print("\nThe issue is that our database only stores these columns:")
print("M1M, M2M, M3M, M6M, M1Y, M2Y, M3Y, M5Y, M7Y, M10Y, M20Y, M30Y")
print("\nBut Treasury provides these columns:")
print("1 Mo, 1.5 Mo, 2 Mo, 3 Mo, 4 Mo, 6 Mo, 1 Yr, 2 Yr, 3 Yr, 5 Yr, 7 Yr, 10 Yr, 20 Yr, 30 Yr")
print("\nWe need to decide which columns to skip (1.5 Mo and 4 Mo)")