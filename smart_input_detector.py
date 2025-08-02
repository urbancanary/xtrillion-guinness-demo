#!/usr/bin/env python3
"""
Smart Input Detector - Automatically detect parameter types
==========================================================

Allows flexible parameter ordering by detecting input types:
- Price: Numeric value
- Settlement date: Date string
- ISIN: 12-char alphanumeric code
- Description: Bond description string
"""

import re
from datetime import datetime
from typing import Union, Dict, List, Optional, Tuple

def detect_input_type(value: Union[str, int, float]) -> Tuple[str, any]:
    """
    Detect the type of a single input value
    
    Returns:
        (input_type, processed_value)
    """
    # Handle None
    if value is None:
        return ('unknown', None)
    
    # Handle numeric types (price)
    if isinstance(value, (int, float)):
        # Prices are typically between 0 and 200
        if 0 <= value <= 500:
            return ('price', float(value))
        else:
            # Large numbers might be ISINs sent as numbers
            return ('description', str(value))
    
    # Handle string types
    if isinstance(value, str):
        value_stripped = value.strip()
        
        # Check if it's a date
        if is_date_string(value_stripped):
            return ('settlement_date', value_stripped)
        
        # Check if it's an ISIN
        if is_isin_format(value_stripped):
            return ('isin', value_stripped)
        
        # Check if it looks like a price (numeric string)
        try:
            price_val = float(value_stripped)
            if 0 <= price_val <= 500:
                return ('price', price_val)
        except ValueError:
            pass
        
        # Default to description
        return ('description', value_stripped)
    
    # Unknown type
    return ('unknown', value)

def is_date_string(value: str) -> bool:
    """Check if string looks like a date"""
    # Common date patterns
    date_patterns = [
        r'^\d{4}-\d{1,2}-\d{1,2}$',  # 2025-07-31
        r'^\d{1,2}/\d{1,2}/\d{4}$',  # 07/31/2025 or 7/31/2025
        r'^\d{4}/\d{1,2}/\d{1,2}$',  # 2025/07/31
        r'^\d{1,2}-\w{3}-\d{4}$',    # 31-Jul-2025
        r'^\d{1,2}-\w{3}-\d{2}$',    # 31-Jul-25
    ]
    
    for pattern in date_patterns:
        if re.match(pattern, value):
            return True
    
    # Try parsing as date
    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%Y/%m/%d', '%d-%b-%Y', '%d-%b-%y']:
        try:
            datetime.strptime(value, fmt)
            return True
        except ValueError:
            continue
    
    return False

def is_isin_format(value: str) -> bool:
    """Check if string looks like an ISIN"""
    # Standard ISIN: 2 letters + 9 alphanumeric + 1 check digit = 12 chars
    if len(value) == 12 and value[:2].isalpha() and value[2:].isalnum():
        # No spaces, slashes, or percent signs
        if not any(char in value for char in [' ', '/', '%', '-']):
            return True
    return False

def detect_bond_inputs(inputs: List[Union[str, int, float]]) -> Dict[str, any]:
    """
    Detect types from a list of inputs in any order
    
    Args:
        inputs: List of values in any order
        
    Returns:
        Dictionary with detected values:
        {
            'price': float,
            'settlement_date': str,
            'isin': str,
            'description': str
        }
    """
    result = {
        'price': None,
        'settlement_date': None,
        'isin': None,
        'description': None
    }
    
    # Process each input
    for value in inputs:
        input_type, processed_value = detect_input_type(value)
        
        if input_type != 'unknown':
            # Handle multiple descriptions/ISINs
            if input_type in ['description', 'isin'] and result[input_type] is not None:
                # If we already have a description and get an ISIN, store as ISIN
                if input_type == 'description' and result['isin'] is None and is_isin_format(processed_value):
                    result['isin'] = processed_value
                # Otherwise keep the first one
            else:
                result[input_type] = processed_value
    
    return result

def parse_flexible_request(data: Union[List, Dict]) -> Dict[str, any]:
    """
    Parse flexible request format - either array or object
    
    Args:
        data: Either a list of values or a dictionary
        
    Returns:
        Standardized dictionary with bond parameters
    """
    # Handle array format
    if isinstance(data, list):
        return detect_bond_inputs(data)
    
    # Handle dictionary format
    if isinstance(data, dict):
        # Check if it has standard fields
        if any(key in data for key in ['description', 'bond_input', 'isin', 'price', 'settlement_date']):
            # Already in standard format
            return {
                'description': data.get('description') or data.get('bond_input'),
                'isin': data.get('isin'),
                'price': data.get('price'),
                'settlement_date': data.get('settlement_date')
            }
        else:
            # Try to detect from values
            values = list(data.values())
            return detect_bond_inputs(values)
    
    # Invalid format
    return {}

# Example usage
if __name__ == "__main__":
    # Test cases
    test_cases = [
        ["T 3 15/08/52", 71.66, "2025-07-31"],  # Standard order
        [71.66, "2025-07-31", "T 3 15/08/52"],  # Price first
        ["2025-07-31", "T 3 15/08/52", 71.66],  # Date first
        ["US912810TJ79", 99.5, "2025-07-31"],   # ISIN instead of description
        [100, "US912810TJ79"],                   # Just price and ISIN
        ["T 4.1 02/15/28", "US912810TJ79", 99.5, "2025-07-31"],  # Both description and ISIN
    ]
    
    print("Smart Input Detection Tests")
    print("=" * 50)
    
    for inputs in test_cases:
        result = detect_bond_inputs(inputs)
        print(f"\nInputs: {inputs}")
        print(f"Detected: {result}")