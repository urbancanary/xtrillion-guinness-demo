#!/usr/bin/env python3
"""
Recreate the ticker_convention_preferences table in bloomberg_index.db
Based on analyzing all tickers in validated_quantlib_bonds table and finding
the most frequent convention combinations for each ticker.
"""
import sqlite3
import os
import pandas as pd
from collections import Counter

DB_PATH = 'bloomberg_index.db'

def analyze_validated_bonds_for_conventions():
    """Analyze validated_quantlib_bonds table to find most common conventions per ticker"""
    
    conn = sqlite3.connect(DB_PATH)
    
    # Check if validated_quantlib_bonds table exists
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='validated_quantlib_bonds'")
    if not cursor.fetchone():
        print("❌ validated_quantlib_bonds table not found in bloomberg_index.db")
        print("Available tables:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")
        conn.close()
        return None
    
    # Read the validated bonds data
    print("📊 Reading validated_quantlib_bonds table...")
    query = """
    SELECT ticker, day_count_convention, business_convention, payment_frequency
    FROM validated_quantlib_bonds 
    WHERE ticker IS NOT NULL 
    AND day_count_convention IS NOT NULL 
    AND business_convention IS NOT NULL 
    AND payment_frequency IS NOT NULL
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print(f"✅ Found {len(df)} validated bonds with complete convention data")
    print(f"🎯 Unique tickers: {df['ticker'].nunique()}")
    
    return df

def find_most_frequent_conventions_per_ticker(df):
    """Find the most frequent convention combination for each ticker"""
    
    ticker_conventions = {}
    
    # Group by ticker
    for ticker, group in df.groupby('ticker'):
        # Create convention combinations
        group['convention_combo'] = (
            group['day_count_convention'] + '|' + 
            group['business_convention'] + '|' + 
            group['payment_frequency']
        )
        
        # Count frequency of each combination
        combo_counts = group['convention_combo'].value_counts()
        
        if len(combo_counts) > 0:
            # Get the most frequent combination
            most_frequent_combo = combo_counts.index[0]
            frequency_count = combo_counts.iloc[0]
            total_bonds = len(group)
            
            # Split back into components
            day_count, business_conv, payment_freq = most_frequent_combo.split('|')
            
            # Calculate confidence based on how dominant the most frequent combo is
            confidence_ratio = frequency_count / total_bonds
            if confidence_ratio >= 0.8:
                confidence = 'high'
            elif confidence_ratio >= 0.6:
                confidence = 'medium'
            else:
                confidence = 'low'
            
            ticker_conventions[ticker] = {
                'day_count_convention': day_count,
                'business_convention': business_conv,
                'payment_frequency': payment_freq,
                'frequency_count': frequency_count,
                'total_bonds': total_bonds,
                'confidence': confidence,
                'confidence_ratio': confidence_ratio
            }
            
            print(f"📈 {ticker}: {most_frequent_combo} ({frequency_count}/{total_bonds} bonds, {confidence_ratio:.1%} confidence)")
    
    return ticker_conventions

def create_ticker_convention_preferences_table(ticker_conventions):
    """Create and populate the ticker_convention_preferences table"""
    
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop table if it exists
    cursor.execute("DROP TABLE IF EXISTS ticker_convention_preferences")
    
    # Create the table
    create_table_sql = """
    CREATE TABLE ticker_convention_preferences (
        ticker TEXT PRIMARY KEY,
        day_count_convention TEXT NOT NULL,
        business_convention TEXT NOT NULL,
        payment_frequency TEXT NOT NULL,
        frequency_count INTEGER DEFAULT 1,
        validated_bonds_count INTEGER DEFAULT 0,
        prediction_confidence TEXT DEFAULT 'medium',
        confidence_ratio REAL DEFAULT 0.0,
        notes TEXT,
        created_date TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    cursor.execute(create_table_sql)
    print("✅ Created ticker_convention_preferences table")
    
    # Prepare data for insertion
    insert_data = []
    for ticker, conventions in ticker_conventions.items():
        
        # Convert payment frequency to get frequency count
        freq_mapping = {
            'Annual': 1,
            'Semiannual': 2, 
            'Quarterly': 4,
            'Monthly': 12,
            'Weekly': 52,
            'Daily': 365
        }
        
        freq_count = freq_mapping.get(conventions['payment_frequency'], 1)
        
        notes = f"Based on {conventions['frequency_count']}/{conventions['total_bonds']} validated bonds"
        
        insert_data.append((
            ticker,
            conventions['day_count_convention'],
            conventions['business_convention'],
            conventions['payment_frequency'],
            freq_count,
            conventions['total_bonds'],
            conventions['confidence'],
            conventions['confidence_ratio'],
            notes
        ))
    
    # Insert the ticker conventions
    insert_sql = """
    INSERT INTO ticker_convention_preferences 
    (ticker, day_count_convention, business_convention, payment_frequency, 
     frequency_count, validated_bonds_count, prediction_confidence, 
     confidence_ratio, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    cursor.executemany(insert_sql, insert_data)
    
    print(f"✅ Inserted {len(insert_data)} ticker conventions")
    
    # Add some essential fallback tickers if they don't exist
    add_fallback_tickers(cursor, ticker_conventions)
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"✅ ticker_convention_preferences table created in {DB_PATH}")
    
    # Verify the creation
    verify_table()

def add_fallback_tickers(cursor, existing_tickers):
    """Add essential fallback tickers if they don't exist in the data"""
    
    fallback_tickers = [
        # Generic corporate fallback
        ('CORP', 'Thirty360_BondBasis', 'Following', 'Annual', 1, 0, 'medium', 0.0, 
         'Generic corporate bond fallback when no specific ticker found'),
        
        # US Treasury fallback  
        ('T', 'ActualActual_Bond', 'Following', 'Semiannual', 2, 0, 'high', 1.0,
         'US Treasury bonds fallback'),
        
        # International/EM fallback
        ('INTL', 'Thirty360_BondBasis', 'Following', 'Annual', 1, 0, 'medium', 0.0,
         'International bonds fallback'),
    ]
    
    for ticker_data in fallback_tickers:
        ticker = ticker_data[0]
        if ticker not in existing_tickers:
            cursor.execute("""
                INSERT OR IGNORE INTO ticker_convention_preferences 
                (ticker, day_count_convention, business_convention, payment_frequency, 
                 frequency_count, validated_bonds_count, prediction_confidence, 
                 confidence_ratio, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ticker_data)
            print(f"➕ Added fallback ticker: {ticker}")

def verify_table():
    """Verify the table was created correctly"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check table structure
    cursor.execute("PRAGMA table_info(ticker_convention_preferences)")
    columns = cursor.fetchall()
    print("\n📋 Table structure:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Check row count
    cursor.execute("SELECT COUNT(*) FROM ticker_convention_preferences")
    count = cursor.fetchone()[0]
    print(f"\n📊 Total rows: {count}")
    
    # Show sample data
    cursor.execute("""
        SELECT ticker, day_count_convention, payment_frequency, 
               validated_bonds_count, prediction_confidence 
        FROM ticker_convention_preferences 
        ORDER BY validated_bonds_count DESC 
        LIMIT 10
    """)
    
    sample_data = cursor.fetchall()
    print("\n🎯 Top 10 tickers by validated bonds count:")
    for row in sample_data:
        print(f"  - {row[0]}: {row[1]} + {row[2]} ({row[3]} bonds, {row[4]} confidence)")
    
    conn.close()

def main():
    """Main function to recreate ticker_convention_preferences table"""
    print("🚀 Creating ticker_convention_preferences table from validated bond data...")
    
    # Step 1: Analyze validated bonds
    validated_df = analyze_validated_bonds_for_conventions()
    if validated_df is None:
        return
    
    # Step 2: Find most frequent conventions per ticker
    print("\n🔍 Analyzing most frequent conventions per ticker...")
    ticker_conventions = find_most_frequent_conventions_per_ticker(validated_df)
    
    if not ticker_conventions:
        print("❌ No ticker conventions found!")
        return
    
    # Step 3: Create the table
    print(f"\n📊 Creating table with {len(ticker_conventions)} tickers...")
    create_ticker_convention_preferences_table(ticker_conventions)
    
    print("\n🎉 SUCCESS! ticker_convention_preferences table created successfully!")

if __name__ == "__main__":
    main()
