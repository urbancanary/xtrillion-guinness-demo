#!/usr/bin/env python3
"""
URGENT FIX: Portfolio Calculation Bug in App Engine
==================================================

The App Engine deployment is failing because portfolio calculations
try to sum None values with numbers, causing:
"unsupported operand type(s) for +=: 'NoneType' and 'int'"

This script shows the fix needed in google_analysis10_api.py around line 1180.
"""

def fix_portfolio_calculation_bug():
    """
    Shows the BEFORE and AFTER code to fix the portfolio calculation bug.
    
    LOCATION: google_analysis10_api.py, around line 1180
    ERROR: "unsupported operand type(s) for +=: 'NoneType' and 'int'"
    """
    
    print("🚨 PORTFOLIO CALCULATION BUG FIX")
    print("=" * 50)
    print()
    
    print("📍 LOCATION: google_analysis10_api.py, line ~1180")
    print("🔍 PROBLEM: None values in portfolio calculations")
    print()
    
    print("❌ CURRENT BROKEN CODE:")
    print("-" * 30)
    broken_code = '''
    # Calculate portfolio-level metrics
    successful_bonds = [b for b in results_list if 'error' not in b and b.get('ytm') is not None and b.get('weighting') is not None]
    total_bonds = len(results_list)
    success_count = len(successful_bonds)

    portfolio_metrics = {}
    if success_count > 0:
        total_weight = sum(b['weighting'] for b in successful_bonds)  # ← Can be None!
        if total_weight > 0:
            portfolio_metrics = {
                'portfolio_yield': float(sum(b['ytm'] * b['weighting'] for b in successful_bonds) / total_weight),        # ← None * number = ERROR
                'portfolio_duration': float(sum(b['duration'] * b['weighting'] for b in successful_bonds) / total_weight), # ← None * number = ERROR  
                'portfolio_spread': float(sum((b.get('g_spread', 0) or 0) * b['weighting'] for b in successful_bonds) / total_weight),
                'total_bonds': total_bonds,
                'successful_bonds': success_count,
                'failed_bonds': total_bonds - success_count,
                'success_rate': round(success_count / total_bonds * 100, 1),
                'total_weight': float(total_weight)
            }
    '''
    print(broken_code)
    
    print("✅ FIXED CODE:")
    print("-" * 30)
    fixed_code = '''
    # Calculate portfolio-level metrics - FIXED: Handle None values
    successful_bonds = [
        b for b in results_list 
        if 'error' not in b 
        and b.get('ytm') is not None 
        and b.get('duration') is not None
        and b.get('weighting') is not None
        and isinstance(b.get('ytm'), (int, float))
        and isinstance(b.get('duration'), (int, float)) 
        and isinstance(b.get('weighting'), (int, float))
    ]
    total_bonds = len(results_list)
    success_count = len(successful_bonds)

    portfolio_metrics = {}
    if success_count > 0:
        # SAFE: Only sum non-None numeric values
        total_weight = sum(float(b['weighting']) for b in successful_bonds if b['weighting'] is not None)
        if total_weight > 0:
            portfolio_metrics = {
                'portfolio_yield': float(sum(float(b['ytm']) * float(b['weighting']) for b in successful_bonds) / total_weight),
                'portfolio_duration': float(sum(float(b['duration']) * float(b['weighting']) for b in successful_bonds) / total_weight),
                'portfolio_spread': float(sum(float(b.get('g_spread', 0) or 0) * float(b['weighting']) for b in successful_bonds) / total_weight),
                'total_bonds': total_bonds,
                'successful_bonds': success_count,
                'failed_bonds': total_bonds - success_count,
                'success_rate': round(success_count / total_bonds * 100, 1),
                'total_weight': float(total_weight)
            }
    '''
    print(fixed_code)
    
    print("🎯 KEY CHANGES:")
    print("1. ✅ Filter out bonds with None or non-numeric values")
    print("2. ✅ Explicit type checking with isinstance()")
    print("3. ✅ Explicit float() conversion for safety")
    print("4. ✅ Safe total_weight calculation")
    print()
    
    print("📝 TO APPLY FIX:")
    print("1. Edit google_analysis10_api.py around line 1180")
    print("2. Replace the portfolio calculation section")
    print("3. Redeploy to App Engine")
    print()
    
    print("🚀 DEPLOYMENT COMMAND:")
    print("./deploy_appengine.sh")

if __name__ == "__main__":
    fix_portfolio_calculation_bug()
