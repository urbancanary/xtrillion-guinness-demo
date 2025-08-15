#!/usr/bin/env python3
"""
QuantLib Convention Mapper
Maps database convention strings to proper QuantLib objects
"""

import QuantLib as ql

def get_quantlib_day_counter(convention_str):
    """
    Map convention strings from database to QuantLib day counter objects.
    
    Handles both our internal names and database names.
    """
    # Create mapping dictionary
    convention_map = {
        # Our preferred internal names (QuantLib-style)
        'ActualActual.Bond': ql.ActualActual(ql.ActualActual.Bond),
        'ActualActual.ISMA': ql.ActualActual(ql.ActualActual.ISMA),
        'ActualActual.ISDA': ql.ActualActual(ql.ActualActual.ISDA),
        'Thirty360.BondBasis': ql.Thirty360(ql.Thirty360.BondBasis),
        'Thirty360.USA': ql.Thirty360(ql.Thirty360.USA),
        'Thirty360.European': ql.Thirty360(ql.Thirty360.European),
        'Actual360': ql.Actual360(),
        'Actual365Fixed': ql.Actual365Fixed(),
        
        # Legacy/database names (for compatibility)
        'ActualActual_Bond': ql.ActualActual(ql.ActualActual.Bond),
        'Actual/Actual (ISMA)': ql.ActualActual(ql.ActualActual.Bond),  # Use Bond for clarity
        'Actual/Actual (ISDA)': ql.ActualActual(ql.ActualActual.ISDA),
        '30/360': ql.Thirty360(ql.Thirty360.BondBasis),
        'Thirty360': ql.Thirty360(ql.Thirty360.BondBasis),
        'ACT/360': ql.Actual360(),
        'ACT/365': ql.Actual365Fixed(),
        
        # Additional variations
        '30/360 Bond Basis': ql.Thirty360(ql.Thirty360.BondBasis),
        'Actual/360': ql.Actual360(),
        'Actual/365 Fixed': ql.Actual365Fixed(),
    }
    
    # Return the mapped convention or default
    if convention_str in convention_map:
        return convention_map[convention_str]
    else:
        # Default to ActualActual.ISDA if not found
        print(f"Warning: Unknown day count convention '{convention_str}', defaulting to ActualActual.ISDA")
        return ql.ActualActual(ql.ActualActual.ISDA)


def get_quantlib_business_convention(convention_str):
    """
    Map business day convention strings to QuantLib objects.
    """
    convention_map = {
        'Following': ql.Following,
        'ModifiedFollowing': ql.ModifiedFollowing,
        'Preceding': ql.Preceding,
        'ModifiedPreceding': ql.ModifiedPreceding,
        'Unadjusted': ql.Unadjusted,
        
        # Variations
        'Modified Following': ql.ModifiedFollowing,
        'Modified Preceding': ql.ModifiedPreceding,
    }
    
    if convention_str in convention_map:
        return convention_map[convention_str]
    else:
        print(f"Warning: Unknown business convention '{convention_str}', defaulting to Following")
        return ql.Following


def get_quantlib_frequency(frequency_str):
    """
    Map frequency strings to QuantLib frequency objects.
    """
    frequency_map = {
        'Annual': ql.Annual,
        'Semiannual': ql.Semiannual,
        'Quarterly': ql.Quarterly,
        'Monthly': ql.Monthly,
        'Weekly': ql.Weekly,
        'Daily': ql.Daily,
        'Once': ql.Once,
        
        # Variations
        'Semi-annual': ql.Semiannual,
        'Semi-Annual': ql.Semiannual,
        'Annually': ql.Annual,
    }
    
    if frequency_str in frequency_map:
        return frequency_map[frequency_str]
    else:
        print(f"Warning: Unknown frequency '{frequency_str}', defaulting to Semiannual")
        return ql.Semiannual


# Recommended database schema update
RECOMMENDED_CONVENTIONS = {
    'US_TREASURY': {
        'day_count': 'ActualActual.Bond',
        'business_convention': 'Following',
        'frequency': 'Semiannual',
        'end_of_month': True
    },
    'CORPORATE_BOND': {
        'day_count': 'Thirty360.BondBasis',
        'business_convention': 'Following',
        'frequency': 'Semiannual',
        'end_of_month': False
    },
    'MONEY_MARKET': {
        'day_count': 'Actual360',
        'business_convention': 'Following',
        'frequency': 'Once',
        'end_of_month': False
    }
}


if __name__ == "__main__":
    # Test the mapper
    print("Testing QuantLib Convention Mapper")
    print("=" * 60)
    
    test_conventions = [
        'ActualActual.Bond',
        'ActualActual_Bond',
        'Actual/Actual (ISMA)',
        '30/360',
        'Thirty360',
        'Unknown Convention'
    ]
    
    for conv in test_conventions:
        dc = get_quantlib_day_counter(conv)
        print(f"'{conv}' -> {dc}")
    
    print("\n" + "=" * 60)
    print("Recommended convention names for database:")
    for bond_type, conventions in RECOMMENDED_CONVENTIONS.items():
        print(f"\n{bond_type}:")
        for key, value in conventions.items():
            print(f"  {key}: {value}")