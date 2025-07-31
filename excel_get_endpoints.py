#!/usr/bin/env python3
"""
EXCEL ONLINE GET ENDPOINTS
Add these to your existing google_analysis10_api.py for direct Excel Online access
No local servers needed - just add these routes to your cloud deployment
"""

from flask import Flask, request, jsonify
from urllib.parse import unquote
import json

# Add these routes to your existing google_analysis10_api.py

@app.route('/excel/yield', methods=['GET'])
def excel_yield():
    """Excel Online friendly yield endpoint"""
    try:
        bond_desc = request.args.get('bond', '')
        price = float(request.args.get('price', 100.0))
        
        if not bond_desc:
            return "ERROR_NO_BOND", 400
        
        # Use your existing bond analysis function
        result = analyze_single_bond(bond_desc, price)
        
        if result.get('status') == 'success':
            ytm = result.get('analytics', {}).get('ytm', 0)
            return f"{ytm:.6f}"
        else:
            return "ERROR_CALCULATION", 500
            
    except Exception as e:
        return f"ERROR_{str(e).replace(' ', '_')}", 500

@app.route('/excel/duration', methods=['GET'])
def excel_duration():
    """Excel Online friendly duration endpoint"""
    try:
        bond_desc = request.args.get('bond', '')
        price = float(request.args.get('price', 100.0))
        
        if not bond_desc:
            return "ERROR_NO_BOND", 400
        
        result = analyze_single_bond(bond_desc, price)
        
        if result.get('status') == 'success':
            duration = result.get('analytics', {}).get('duration', 0)
            return f"{duration:.6f}"
        else:
            return "ERROR_CALCULATION", 500
            
    except Exception as e:
        return f"ERROR_{str(e).replace(' ', '_')}", 500

@app.route('/excel/spread', methods=['GET'])
def excel_spread():
    """Excel Online friendly spread endpoint"""
    try:
        bond_desc = request.args.get('bond', '')
        price = float(request.args.get('price', 100.0))
        
        if not bond_desc:
            return "ERROR_NO_BOND", 400
        
        result = analyze_single_bond(bond_desc, price)
        
        if result.get('status') == 'success':
            spread = result.get('analytics', {}).get('spread', 0)
            if spread is None:
                return "0.0"
            return f"{spread:.2f}"
        else:
            return "ERROR_CALCULATION", 500
            
    except Exception as e:
        return f"ERROR_{str(e).replace(' ', '_')}", 500

@app.route('/excel/accrued', methods=['GET'])
def excel_accrued():
    """Excel Online friendly accrued interest endpoint"""
    try:
        bond_desc = request.args.get('bond', '')
        price = float(request.args.get('price', 100.0))
        
        if not bond_desc:
            return "ERROR_NO_BOND", 400
        
        result = analyze_single_bond(bond_desc, price)
        
        if result.get('status') == 'success':
            accrued = result.get('analytics', {}).get('accrued_interest', 0)
            return f"{accrued:.6f}"
        else:
            return "ERROR_CALCULATION", 500
            
    except Exception as e:
        return f"ERROR_{str(e).replace(' ', '_')}", 500

@app.route('/excel/test', methods=['GET'])
def excel_test():
    """Test endpoint for Excel Online"""
    return "EXCEL_API_WORKING"

@app.route('/excel/help', methods=['GET'])
def excel_help():
    """Excel Online usage help"""
    help_text = """
EXCEL ONLINE USAGE:

Yield:
=WEBSERVICE("https://future-footing-414610.uc.r.appspot.com/excel/yield?bond=T 3 15/08/52&price=71.66")

Duration:
=WEBSERVICE("https://future-footing-414610.uc.r.appspot.com/excel/duration?bond=T 3 15/08/52&price=71.66")

Spread:
=WEBSERVICE("https://future-footing-414610.uc.r.appspot.com/excel/spread?bond=ECOPETROL SA, 5.875%, 28-May-2045&price=69.31")

Accrued:
=WEBSERVICE("https://future-footing-414610.uc.r.appspot.com/excel/accrued?bond=T 3 15/08/52&price=71.66")

Dynamic (A2=bond, B2=price):
=WEBSERVICE("https://future-footing-414610.uc.r.appspot.com/excel/yield?bond="&A2&"&price="&B2)
"""
    return help_text

# Add CORS headers for Excel Online access
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
