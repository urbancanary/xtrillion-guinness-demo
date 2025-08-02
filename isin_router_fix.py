#!/usr/bin/env python3
"""
ISIN Router Fix - Properly handles ISIN vs Description routing
=============================================================

Fixes the issue where ISINs are incorrectly treated as descriptions
"""

import re
import logging

logger = logging.getLogger(__name__)

def is_isin_format(identifier):
    """Check if identifier looks like an ISIN"""
    if not identifier or not isinstance(identifier, str):
        return False
    
    # Clean the identifier
    clean_id = identifier.strip().upper()
    
    # Standard ISIN format: 2 letters + 9 alphanumeric + 1 check digit
    isin_pattern = r'^[A-Z]{2}[A-Z0-9]{9}[0-9]$'
    
    if re.match(isin_pattern, clean_id):
        return True
    
    # Relaxed ISIN format (sometimes ISINs are not perfectly formatted)
    # Length 10-12, starts with 2 letters, alphanumeric only
    if (len(clean_id) >= 10 and len(clean_id) <= 12 and 
        clean_id[:2].isalpha() and 
        clean_id[2:].isalnum() and
        not any(char in clean_id for char in [' ', '%', '/', '-', ','])):
        return True
    
    return False

def fix_isin_routing(bond_input, explicit_isin=None):
    """
    Fix ISIN vs Description routing
    
    Args:
        bond_input: The main input (could be ISIN or description)
        explicit_isin: Explicitly provided ISIN field
    
    Returns:
        tuple: (parsed_isin, parsed_description)
    """
    
    # Case 1: Explicit ISIN provided separately
    if explicit_isin and explicit_isin.strip():
        logger.info(f"✅ Explicit ISIN provided: {explicit_isin}")
        return explicit_isin.strip(), bond_input
    
    # Case 2: bond_input looks like an ISIN
    if is_isin_format(bond_input):
        logger.info(f"✅ bond_input detected as ISIN format: {bond_input}")
        return bond_input.strip(), None
    
    # Case 3: bond_input is clearly a description
    logger.info(f"✅ bond_input detected as description: {bond_input}")
    return None, bond_input

def validate_inputs(parsed_isin, parsed_description):
    """
    Validate that we have sufficient information to proceed
    
    Returns:
        tuple: (is_valid, error_message)
    """
    
    # Case 1: We have an ISIN - this is sufficient for database lookup
    if parsed_isin:
        return True, None
    
    # Case 2: We have a description - this is sufficient for parsing
    if parsed_description:
        return True, None
    
    # Case 3: We have neither - this is an error
    return False, "Either ISIN or bond description must be provided"

def get_routing_strategy(parsed_isin, parsed_description):
    """
    Determine the routing strategy based on available inputs
    
    Returns:
        str: routing strategy ("isin_primary", "description_only", "isin_with_fallback")
    """
    
    if parsed_isin and parsed_description:
        return "isin_with_fallback"
    elif parsed_isin and not parsed_description:
        return "isin_primary"
    elif not parsed_isin and parsed_description:
        return "description_only"
    else:
        return "invalid"
