#!/usr/bin/env python3
"""
Fix Treasury Ticker Conventions Table
===================================

Creates the missing ticker_convention_preferences table with proper Treasury conventions
to fix the SmartBondParser ticker lookup failure.
"""

import sqlite3
import os

def create_ticker_convention_preferences_table():
    """Create the missing ticker_convention_preferences table with proper conventions"""
    
    db_path = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bloomberg_index.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Drop table if it exists
        cursor.execute("DROP TABLE IF EXISTS ticker_convention_preferences")
        
        # Create table with proper schema
        cursor.execute("""
            CREATE TABLE ticker_convention_preferences (
                ticker TEXT PRIMARY KEY,
                day_count_convention TEXT NOT NULL,
                business_convention TEXT NOT NULL,
                payment_frequency TEXT NOT NULL,
                frequency_count INTEGER DEFAULT 1,
                bond_type TEXT,
                notes TEXT
            )
        """)
        
        # Insert Treasury conventions (the critical fix!)
        treasury_conventions = [
            ('T', 'ActualActual_Bond', 'Following', 'Semiannual', 100, 'TREASURY', 'US Treasury bonds - Bloomberg standard'),
            ('UST', 'ActualActual_Bond', 'Following', 'Semiannual', 100, 'TREASURY', 'US Treasury bonds - alternative ticker'),
            ('TREASURY', 'ActualActual_Bond', 'Following', 'Semiannual', 100, 'TREASURY', 'US Treasury bonds - full name'),
        ]
        
        # Insert corporate conventions  
        corporate_conventions = [
            ('CORP', 'Thirty360_BondBasis', 'Following', 'Semiannual', 50, 'CORPORATE', 'Generic corporate bonds'),
            ('AAPL', 'Thirty360_BondBasis', 'Following', 'Semiannual', 10, 'CORPORATE', 'Apple Inc'),
            ('MSFT', 'Thirty360_BondBasis', 'Following', 'Semiannual', 10, 'CORPORATE', 'Microsoft'),
            ('GOOGL', 'Thirty360_BondBasis', 'Following', 'Semiannual', 10, 'CORPORATE', 'Google/Alphabet'),
            ('AMZN', 'Thirty360_BondBasis', 'Following', 'Semiannual', 10, 'CORPORATE', 'Amazon'),
        ]
        
        # Insert government/sovereign conventions
        government_conventions = [
            ('GOVERNMENT', 'ActualActual_ISDA', 'Following', 'Annual', 25, 'GOVERNMENT', 'Generic government bonds'),
            ('GERMANY', 'ActualActual_ISDA', 'Following', 'Annual', 15, 'GOVERNMENT', 'German government bonds'),
            ('CANADA', 'ActualActual_ISDA', 'Following', 'Semiannual', 15, 'GOVERNMENT', 'Canadian government bonds'),
            ('UK', 'ActualActual_ISDA', 'Following', 'Semiannual', 15, 'GOVERNMENT', 'UK gilts'),
        ]
        
        # International/Euromarket conventions  
        international_conventions = [
            ('INTERNATIONAL', 'Thirty360_BondBasis', 'Following', 'Semiannual', 30, 'INTERNATIONAL', 'International/Euromarket bonds'),
            ('XS', 'Thirty360_BondBasis', 'Following', 'Semiannual', 20, 'INTERNATIONAL', 'Euromarket ISIN prefix'),
        ]
        
        # Combine all conventions
        all_conventions = (treasury_conventions + corporate_conventions + 
                          government_conventions + international_conventions)
        
        # Insert all data
        cursor.executemany("""
            INSERT INTO ticker_convention_preferences 
            (ticker, day_count_convention, business_convention, payment_frequency, 
             frequency_count, bond_type, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, all_conventions)
        
        conn.commit()
        conn.close()
        
        print("✅ SUCCESS: Created ticker_convention_preferences table")
        print(f"📊 Inserted {len(all_conventions)} ticker conventions")
        print("🏛️ Treasury conventions fixed: T, UST, TREASURY -> ActualActual_Bond + Semiannual")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR creating table: {e}")
        return False

def verify_treasury_conventions():
    """Verify that Treasury conventions were inserted correctly"""
    
    db_path = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bloomberg_index.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check Treasury ticker specifically
        cursor.execute("""
            SELECT ticker, day_count_convention, business_convention, payment_frequency, bond_type
            FROM ticker_convention_preferences 
            WHERE ticker = 'T'
        """)
        
        result = cursor.fetchone()
        
        if result:
            ticker, day_count, business_conv, frequency, bond_type = result
            print(f"🎯 Treasury ticker 'T' conventions:")
            print(f"   Day Count: {day_count}")
            print(f"   Business Convention: {business_conv}")
            print(f"   Frequency: {frequency}")
            print(f"   Bond Type: {bond_type}")
            
            # Verify it's correct for Treasury
            if (day_count == 'ActualActual_Bond' and 
                business_conv == 'Following' and 
                frequency == 'Semiannual' and
                bond_type == 'TREASURY'):
                print("✅ Treasury conventions are CORRECT!")
                return True
            else:
                print("❌ Treasury conventions are WRONG!")
                return False
        else:
            print("❌ Treasury ticker 'T' not found!")
            return False
            
        conn.close()
        
    except Exception as e:
        print(f"❌ ERROR verifying conventions: {e}")
        return False

def test_smartbondparser_with_treasury():
    """Test the SmartBondParser with Treasury bond after fixing conventions"""
    
    print("\n🧪 TESTING SmartBondParser with Treasury bond")
    print("=" * 50)
    
    try:
        # Import the parser
        import sys
        sys.path.append('/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10')
        
        from bond_description_parser import SmartBondParser
        
        # Create parser with correct paths
        db_path = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bonds_data.db"
        validated_db_path = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/validated_quantlib_bonds.db"
        bloomberg_db_path = "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/bloomberg_index.db"
        
        parser = SmartBondParser(db_path, validated_db_path, bloomberg_db_path)
        
        # Test Treasury bond parsing
        treasury_desc = "US TREASURY N/B, 3%, 15-Aug-2052"
        
        print(f"📋 Testing: {treasury_desc}")
        
        # Parse the description
        parsed = parser.parse_bond_description(treasury_desc)
        if parsed:
            print(f"✅ Parsed successfully:")
            print(f"   Issuer: {parsed['issuer']}")
            print(f"   Coupon: {parsed['coupon']}%")
            print(f"   Maturity: {parsed['maturity']}")
            print(f"   Type: {parsed['bond_type']}")
            
            # Extract ticker
            ticker = parser.extract_ticker_from_parsed_bond(parsed)
            print(f"   Ticker: {ticker}")
            
            # Look up conventions
            conventions = parser.lookup_ticker_conventions(ticker)
            if conventions:
                print(f"✅ Ticker conventions found:")
                print(f"   Day Count: {conventions['day_count']}")
                print(f"   Business Convention: {conventions['business_convention']}")
                print(f"   Frequency: {conventions['frequency']}")
                print(f"   Source: {conventions['source']}")
                return True
            else:
                print(f"❌ No ticker conventions found for {ticker}")
                return False
        else:
            print(f"❌ Failed to parse Treasury description")
            return False
            
    except Exception as e:
        print(f"❌ Error testing parser: {e}")
        return False

if __name__ == "__main__":
    print("🔧 FIXING TREASURY TICKER CONVENTIONS")
    print("=" * 60)
    
    # Step 1: Create the missing table
    success = create_ticker_convention_preferences_table()
    
    if success:
        # Step 2: Verify Treasury conventions
        verify_success = verify_treasury_conventions()
        
        if verify_success:
            # Step 3: Test the parser
            test_success = test_smartbondparser_with_treasury()
            
            if test_success:
                print("\n🎉 COMPLETE SUCCESS!")
                print("✅ Table created")
                print("✅ Treasury conventions verified")
                print("✅ SmartBondParser working")
                print("\n🏛️ Treasury bond calculations should now be consistent!")
            else:
                print("\n⚠️ Table created but parser test failed")
        else:
            print("\n⚠️ Table created but verification failed")
    else:
        print("\n❌ Failed to create table")
