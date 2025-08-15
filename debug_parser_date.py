#!/usr/bin/env python3
"""
Debug the date parsing for EMPRESA MAESTRO
"""

from centralized_bond_date_parser import parse_bond_date_simple
from bond_description_parser import SmartBondParser

def test_date_parser():
    """Test the centralized date parser directly"""
    print("🔍 Testing centralized date parser")
    print("=" * 60)
    
    # Test various date formats
    test_dates = [
        "07-May-2050",
        "May-07-2050", 
        "05/07/2050",
        "07/05/2050",
        "2050-05-07",
        "2050-07-05"
    ]
    
    for date_str in test_dates:
        result = parse_bond_date_simple(date_str)
        print(f"'{date_str}' → '{result}'")

def test_parse_maturity():
    """Test the parse_maturity_date function"""
    print("\n\n🔍 Testing parse_maturity_date")
    print("=" * 60)
    
    # Initialize parser
    parser = SmartBondParser('./bloomberg_index.db', './validated_quantlib_bonds.db', './bloomberg_index.db')
    
    # Test with the components
    month = "May"  # or "05"
    day = "07"
    year = "2050"
    
    print(f"Components: month='{month}', day='{day}', year='{year}'")
    
    # This should create "May 07 2050" and parse it
    result = parser.parse_maturity_date(month, day, year)
    print(f"Result: {result}")
    
    # Also test numeric format
    month_num = "05"
    print(f"\nNumeric: month='{month_num}', day='{day}', year='{year}'")
    result2 = parser.parse_maturity_date(month_num, day, year)
    print(f"Result: {result2}")

def analyze_pattern():
    """Analyze what pattern is matching"""
    print("\n\n🔍 Analyzing pattern matching")
    print("=" * 60)
    
    import re
    
    # The description that's causing issues
    description = "EMPRESA MAESTRO, 4.7%, 07-May-2050"
    print(f"Description: '{description}'")
    
    # Pattern that might be matching (from parser code)
    # Looking for patterns like "ISSUER, X.X%, DD-Mon-YYYY"
    pattern = r'^([A-Z\s&]+),\s*(\d+\.?\d*)%?,\s*(\d{1,2})-([A-Za-z]{3})-(\d{4})$'
    
    match = re.match(pattern, description)
    if match:
        groups = match.groups()
        print(f"\n✅ Pattern matched!")
        print(f"   Groups: {groups}")
        print(f"   Issuer: '{groups[0]}'")
        print(f"   Coupon: '{groups[1]}'")
        print(f"   Day: '{groups[2]}'")
        print(f"   Month: '{groups[3]}'")
        print(f"   Year: '{groups[4]}'")
        
        # The parser would call parse_maturity_date(month, day, year)
        # But it looks like it might be passing them in the wrong order!
        print(f"\n   Parser should call: parse_maturity_date('{groups[3]}', '{groups[2]}', '{groups[4]}')")
        print(f"   Which is: parse_maturity_date('May', '07', '2050')")

if __name__ == "__main__":
    test_date_parser()
    test_parse_maturity()
    analyze_pattern()