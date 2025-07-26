#!/usr/bin/env python3
"""
Treasury Issue Date Calculator
=============================

Calculate proper issue dates for Treasury bonds to align with Feb 15/Aug 15 schedule
"""

import QuantLib as ql

def calculate_treasury_issue_date(settlement_date, maturity_date):
    """
    Calculate proper issue date for Treasury bond based on maturity date
    
    Treasury bonds typically pay on Feb 15 and Aug 15.
    Issue date should align with this schedule.
    
    Args:
        settlement_date: ql.Date - settlement date
        maturity_date: ql.Date - maturity date
        
    Returns:
        ql.Date - proper issue date for Treasury schedule
    """
    
    # Treasury bonds typically mature on Feb 15 or Aug 15
    maturity_month = maturity_date.month()
    maturity_day = maturity_date.dayOfMonth()
    
    # Determine the coupon payment months based on maturity
    if maturity_month == 8 and maturity_day == 15:
        # Matures Aug 15, so pays Feb 15 and Aug 15
        coupon_months = [2, 8]  # Feb, Aug
    elif maturity_month == 2 and maturity_day == 15:
        # Matures Feb 15, so pays Feb 15 and Aug 15
        coupon_months = [2, 8]  # Feb, Aug
    else:
        # For other maturity dates, use standard Feb/Aug schedule
        coupon_months = [2, 8]  # Feb, Aug
    
    # Find the issue date that would create this maturity pattern
    # Work backwards from settlement to find the previous coupon date
    
    settlement_year = settlement_date.year()
    settlement_month = settlement_date.month()
    
    # Find the most recent coupon date before settlement
    if settlement_month <= 2:
        # Before Feb 15, so use Aug 15 of previous year
        issue_year = settlement_year - 1
        issue_month = 8
    elif settlement_month <= 8:
        # Between Feb 15 and Aug 15, so use Feb 15 of current year
        issue_year = settlement_year
        issue_month = 2
    else:
        # After Aug 15, so use Aug 15 of current year
        issue_year = settlement_year
        issue_month = 8
    
    issue_date = ql.Date(15, issue_month, issue_year)
    
    # Ensure issue date is before settlement date
    while issue_date >= settlement_date:
        if issue_month == 8:
            issue_month = 2
        else:
            issue_month = 8
            issue_year -= 1
        issue_date = ql.Date(15, issue_month, issue_year)
    
    return issue_date

def is_treasury_bond_description(description, isin=None):
    """
    Detect if this is a Treasury bond from description or ISIN
    
    Args:
        description: str - bond description
        isin: str - bond ISIN (optional)
        
    Returns:
        bool - True if Treasury bond
    """
    if not description:
        return False
        
    description_upper = description.upper()
    
    # Check for Treasury indicators in description
    treasury_indicators = [
        'US TREASURY',
        'TREASURY',
        'UST ',
        'T 3',  # Common Treasury format
        'US91',  # Treasury ISIN pattern
    ]
    
    for indicator in treasury_indicators:
        if indicator in description_upper:
            return True
    
    # Check ISIN pattern
    if isin and isin.upper().startswith('US91'):
        return True
        
    return False

# Test the function
if __name__ == "__main__":
    print("🏛️ Testing Treasury Issue Date Calculator")
    print("=" * 50)
    
    # Test with our specific case
    settlement = ql.Date(30, 6, 2025)  # June 30, 2025
    maturity = ql.Date(15, 8, 2052)    # August 15, 2052
    
    issue_date = calculate_treasury_issue_date(settlement, maturity)
    
    print(f"Settlement Date: {settlement}")
    print(f"Maturity Date: {maturity}")
    print(f"Calculated Issue Date: {issue_date}")
    print()
    
    # Test Treasury detection
    test_descriptions = [
        "US TREASURY N/B, 3%, 15-Aug-2052",
        "T 3 15/08/52",
        "GALAXY PIPELINE, 3.25%, 30-Sep-2040",
        "UST 2.5 05/31/24"
    ]
    
    for desc in test_descriptions:
        is_treasury = is_treasury_bond_description(desc)
        print(f"'{desc}' -> Treasury: {is_treasury}")
