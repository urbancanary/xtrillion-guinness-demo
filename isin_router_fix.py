#!/usr/bin/env python3
"""
ISIN Detection and Route Fix
===========================

Fix the Universal Parser integration to properly route ISINs to the 
excellent ISIN hierarchy code in bond_master_hierarchy.py
"""

import re
from typing import Tuple, Optional

def detect_isin(input_str: str) -> bool:
    """
    Detect if input string is an ISIN
    
    ISIN format: 2 letter country code + 9 alphanumeric + 1 check digit
    Examples: US912810TJ79, XS2249741674, GB00B24CGK77
    
    Args:
        input_str: Input string to check
        
    Returns:
        bool: True if input looks like an ISIN
    """
    if not input_str or len(input_str) != 12:
        return False
    
    # ISIN pattern: 2 letters + 9 alphanumeric + 1 digit
    isin_pattern = r'^[A-Z]{2}[A-Z0-9]{9}[0-9]$'
    return bool(re.match(isin_pattern, input_str.upper()))

def fix_isin_routing(bond_input: str, provided_isin: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """
    Fix ISIN routing to ensure proper hierarchy routing
    
    Args:
        bond_input: The main input (could be ISIN or description)
        provided_isin: Explicitly provided ISIN field
        
    Returns:
        Tuple[isin, description]: Properly routed ISIN and description
    """
    
    # If explicit ISIN provided, use it
    if provided_isin:
        return provided_isin, bond_input if not detect_isin(bond_input) else None
    
    # If bond_input is an ISIN, route it properly
    if detect_isin(bond_input):
        return bond_input, None  # ISIN route: isin=input, description=None
    
    # Otherwise, it's a description
    return None, bond_input  # Description route: isin=None, description=input

def test_isin_detection():
    """Test ISIN detection and routing"""
    
    test_cases = [
        # (input, expected_is_isin, expected_isin, expected_desc)
        ("XS2249741674", True, "XS2249741674", None),
        ("US912810TJ79", True, "US912810TJ79", None),
        ("T 4.625 02/15/25", False, None, "T 4.625 02/15/25"),
        ("GALAXY PIPELINE, 3.25%, 30-Sep-2040", False, None, "GALAXY PIPELINE, 3.25%, 30-Sep-2040"),
        ("GB00B24CGK77", True, "GB00B24CGK77", None),
        ("XS12345", False, None, "XS12345"),  # Too short
        ("TOOLONGFORISIN", False, None, "TOOLONGFORISIN"),  # Too long
    ]
    
    print("🧪 Testing ISIN Detection and Routing:")
    print("=" * 60)
    
    for input_str, expected_is_isin, expected_isin, expected_desc in test_cases:
        is_isin = detect_isin(input_str)
        routed_isin, routed_desc = fix_isin_routing(input_str)
        
        status = "✅" if (is_isin == expected_is_isin and 
                          routed_isin == expected_isin and 
                          routed_desc == expected_desc) else "❌"
        
        print(f"{status} Input: '{input_str}'")
        print(f"   Is ISIN: {is_isin} (expected: {expected_is_isin})")
        print(f"   Routed ISIN: {routed_isin} (expected: {expected_isin})")
        print(f"   Routed Desc: {routed_desc} (expected: {expected_desc})")
        print()

if __name__ == "__main__":
    test_isin_detection()
