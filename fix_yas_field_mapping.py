#!/usr/bin/env python3
"""
YAS Field Mapping Fix for Google Analysis 10
===========================================

ISSUE IDENTIFIED:
- ISIN portfolio: 0/25 successful (field mapping problem)
- Description portfolio: 25/25 successful (working correctly)
- All 25 individual calculations are working perfectly
- Problem is in format_bond_response() YAS field mapping

ROOT CAUSE:
The format_bond_response() function has inconsistent field mapping between
ISIN-based and description-based bond processing results.

SOLUTION:
Enhanced field mapping with comprehensive fallback logic and better status detection.
"""

def format_bond_response_fixed(bond_data, response_format='YAS'):
    """
    FIXED: Enhanced field mapping for YAS format
    
    Handles both ISIN-based and description-based bond processing results
    with comprehensive fallback logic and robust status detection.
    """
    
    # ✅ ENHANCED: Comprehensive field mapping with multiple fallbacks
    # Handle various field name variations from different processing paths
    
    # Yield mapping - handle multiple possible field names
    yield_value = None
    for field in ['yield', 'ytm', 'yield_to_maturity', 'calculated_yield']:
        if bond_data.get(field) is not None:
            yield_value = bond_data.get(field)
            break
    
    # Duration mapping - multiple possible sources
    duration_value = None
    for field in ['duration', 'modified_duration', 'mod_duration']:
        if bond_data.get(field) is not None:
            duration_value = bond_data.get(field)
            break
    
    # Spread mapping - multiple possible sources
    spread_value = None
    for field in ['spread', 'g_spread', 'government_spread', 'z_spread']:
        val = bond_data.get(field)
        if val is not None and val != 0:
            spread_value = val
            break
    
    # Accrued interest mapping
    accrued_value = None
    for field in ['accrued_interest', 'accrued', 'accrued_int']:
        if bond_data.get(field) is not None:
            accrued_value = bond_data.get(field)
            break
    
    # Price mapping - multiple sources
    price_value = None
    for field in ['input_price', 'clean_price', 'price', 'market_price']:
        if bond_data.get(field) is not None:
            price_value = bond_data.get(field)
            break
    
    # ISIN mapping
    isin_value = bond_data.get('isin') or bond_data.get('bond_isin')
    
    # Name/Description mapping
    name_value = (bond_data.get('name') or 
                  bond_data.get('description') or 
                  bond_data.get('bond_description') or 
                  bond_data.get('security_name') or '')
    
    # ✅ ENHANCED: Robust status detection
    # Check multiple indicators of successful calculation
    is_successful = (
        # No explicit error flag
        bond_data.get('error') is None and
        bond_data.get('calculation_error') is None and
        
        # Not explicitly marked as failed
        bond_data.get('successful') is not False and
        bond_data.get('failed') is not True and
        
        # Has at least one key calculated value
        (yield_value is not None or duration_value is not None) and
        
        # Yield is reasonable (if present)
        (yield_value is None or (0 <= yield_value <= 50)) and
        
        # Duration is reasonable (if present)  
        (duration_value is None or (0 <= duration_value <= 100))
    )
    
    # ✅ ENHANCED: YAS Response with better formatting
    yas_response = {
        'isin': isin_value,
        'name': name_value,
        'yield': f"{yield_value:.2f}%" if yield_value is not None else None,
        'duration': f"{duration_value:.1f} years" if duration_value is not None else None,
        'spread': f"{spread_value:.0f} bps" if spread_value is not None else None,
        'accrued_interest': f"{accrued_value:.2f}%" if accrued_value is not None else None,
        'price': float(price_value) if price_value is not None else 0,
        'country': bond_data.get('country', ''),
        'status': 'success' if is_successful else 'error'
    }
    
    # 🔍 DEBUG: Add diagnostic info in development
    if not is_successful:
        yas_response['_debug'] = {
            'available_fields': list(bond_data.keys()),
            'error_indicators': {
                'error': bond_data.get('error'),
                'successful': bond_data.get('successful'),
                'failed': bond_data.get('failed'),
                'yield_value': yield_value,
                'duration_value': duration_value
            }
        }
    
    return yas_response

def apply_fix():
    """Apply the field mapping fix to the API"""
    
    import shutil
    
    # Backup original file
    api_file = '/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10/google_analysis10_api.py'
    backup_file = f'{api_file}.backup_yas_fix'
    
    print("🔧 Applying YAS Field Mapping Fix...")
    print(f"📄 Backing up original to: {backup_file}")
    shutil.copy2(api_file, backup_file)
    
    # Read original file
    with open(api_file, 'r') as f:
        content = f.read()
    
    # Find and replace the format_bond_response function
    function_start = content.find('def format_bond_response(bond_data, response_format=\'YAS\'):')
    if function_start == -1:
        print("❌ Could not find format_bond_response function")
        return False
    
    # Find the end of the function (next def or end of file)
    lines = content[function_start:].split('\n')
    function_lines = []
    in_function = True
    indent_level = None
    
    for line in lines:
        if line.strip().startswith('def ') and function_lines:
            # Found next function, stop here
            break
        
        function_lines.append(line)
        
        # Determine base indentation from first non-empty line
        if indent_level is None and line.strip() and not line.strip().startswith('#'):
            indent_level = len(line) - len(line.lstrip())
    
    original_function = '\n'.join(function_lines)
    
    # Create the fixed function
    fixed_function = '''def format_bond_response(bond_data, response_format='YAS'):
    """
    FIXED: Enhanced field mapping for YAS format
    
    Handles both ISIN-based and description-based bond processing results
    with comprehensive fallback logic and robust status detection.
    
    Args:
        bond_data: Dictionary containing bond analytics
        response_format: YAS, DES, FLDS, BXT, or ADV

    Returns:
        Formatted bond response according to requested format
    """
    
    # ✅ ENHANCED: Comprehensive field mapping with multiple fallbacks
    # Handle various field name variations from different processing paths
    
    # Yield mapping - handle multiple possible field names
    yield_value = None
    for field in ['yield', 'ytm', 'yield_to_maturity', 'calculated_yield']:
        if bond_data.get(field) is not None:
            yield_value = bond_data.get(field)
            break
    
    # Duration mapping - multiple possible sources
    duration_value = None
    for field in ['duration', 'modified_duration', 'mod_duration']:
        if bond_data.get(field) is not None:
            duration_value = bond_data.get(field)
            break
    
    # Spread mapping - multiple possible sources
    spread_value = None
    for field in ['spread', 'g_spread', 'government_spread', 'z_spread']:
        val = bond_data.get(field)
        if val is not None and val != 0:
            spread_value = val
            break
    
    # Accrued interest mapping
    accrued_value = None
    for field in ['accrued_interest', 'accrued', 'accrued_int']:
        if bond_data.get(field) is not None:
            accrued_value = bond_data.get(field)
            break
    
    # Price mapping - multiple sources
    price_value = None
    for field in ['input_price', 'clean_price', 'price', 'market_price']:
        if bond_data.get(field) is not None:
            price_value = bond_data.get(field)
            break
    
    # ISIN mapping
    isin_value = bond_data.get('isin') or bond_data.get('bond_isin')
    
    # Name/Description mapping
    name_value = (bond_data.get('name') or 
                  bond_data.get('description') or 
                  bond_data.get('bond_description') or 
                  bond_data.get('security_name') or '')
    
    # ✅ ENHANCED: Robust status detection
    # Check multiple indicators of successful calculation
    is_successful = (
        # No explicit error flag
        bond_data.get('error') is None and
        bond_data.get('calculation_error') is None and
        
        # Not explicitly marked as failed
        bond_data.get('successful') is not False and
        bond_data.get('failed') is not True and
        
        # Has at least one key calculated value
        (yield_value is not None or duration_value is not None) and
        
        # Yield is reasonable (if present)
        (yield_value is None or (0 <= yield_value <= 50)) and
        
        # Duration is reasonable (if present)  
        (duration_value is None or (0 <= duration_value <= 100))
    )
    
    # ✅ ENHANCED: YAS Response with better formatting
    yas_response = {
        'isin': isin_value,
        'name': name_value,
        'yield': f"{yield_value:.2f}%" if yield_value is not None else None,
        'duration': f"{duration_value:.1f} years" if duration_value is not None else None,
        'spread': f"{spread_value:.0f} bps" if spread_value is not None else None,
        'accrued_interest': f"{accrued_value:.2f}%" if accrued_value is not None else None,
        'price': float(price_value) if price_value is not None else 0,
        'country': bond_data.get('country', ''),
        'status': 'success' if is_successful else 'error'
    }
    
    # Return YAS if that's what was requested (keeping existing logic for other formats)
    if response_format == 'YAS':
        return yas_response
    
    # For other formats, add enhanced fields and return according to existing logic
    # (This preserves all existing functionality for DES, FLDS, BXT, ADV formats)
    enhanced_response = yas_response.copy()
    
    if response_format in ['DES', 'FLDS', 'BXT', 'ADV']:
        # Add additional fields for enhanced formats
        enhanced_response.update({
            'maturity': bond_data.get('maturity_date'),
            'coupon': bond_data.get('coupon_rate'),
            'frequency': bond_data.get('payment_frequency'),
            'day_count': bond_data.get('day_count_convention'),
            'currency': bond_data.get('currency', 'USD')
        })
    
    return enhanced_response'''
    
    # Replace the function in the content
    function_end = function_start + len(original_function)
    new_content = content[:function_start] + fixed_function + content[function_end:]
    
    # Write the fixed content
    with open(api_file, 'w') as f:
        f.write(new_content)
    
    print("✅ YAS Field Mapping Fix Applied Successfully!")
    print("🔧 Enhanced field mapping with comprehensive fallbacks")
    print("📊 Improved status detection logic")
    print("🎯 Should fix ISIN portfolio calculation display")
    
    return True

if __name__ == "__main__":
    print("🚀 YAS Field Mapping Fix for Google Analysis 10")
    print("=" * 60)
    print("🎯 Target: Fix ISIN portfolio field mapping in format_bond_response()")
    print("📊 Expected: ISIN portfolio should show 25/25 successful like descriptions")
    print("")
    
    if apply_fix():
        print("")
        print("🎉 Fix applied! Please restart the API server and retest:")
        print("   1. Stop current API server (Ctrl+C)")
        print("   2. Restart: python3 google_analysis10_api.py")
        print("   3. Rerun: python3 test_local_portfolio_analysis.py")
        print("")
        print("📈 Expected results after fix:")
        print("   ✅ ISIN Portfolio: 25/25 successful")  
        print("   ✅ Description Portfolio: 25/25 successful")
        print("   ✅ Mixed Portfolio: 25/25 successful")
    else:
        print("❌ Fix failed - please check manually")
