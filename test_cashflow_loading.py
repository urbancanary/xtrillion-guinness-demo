#!/usr/bin/env python3
"""
Test if cash flow extension loads successfully
"""

import sys
import traceback

print("Testing cash flow extension loading...")

# Test 1: Check if xtrillion_cash_flow_calculator exists and imports
try:
    from xtrillion_cash_flow_calculator import calculate_bond_cash_flows
    print("✅ xtrillion_cash_flow_calculator imported successfully")
except Exception as e:
    print(f"❌ Failed to import xtrillion_cash_flow_calculator: {e}")
    traceback.print_exc()

# Test 2: Check if api_cash_flow_extension exists and imports
try:
    from api_cash_flow_extension import add_cash_flow_endpoints
    print("✅ api_cash_flow_extension imported successfully")
except Exception as e:
    print(f"❌ Failed to import api_cash_flow_extension: {e}")
    traceback.print_exc()

# Test 3: Try to create a simple Flask app and add endpoints
try:
    from flask import Flask
    app = Flask(__name__)
    
    # Try to add cash flow endpoints
    from api_cash_flow_extension import add_cash_flow_endpoints
    add_cash_flow_endpoints(app)
    
    # Check if endpoints were added
    print("\nRegistered endpoints:")
    for rule in app.url_map.iter_rules():
        if 'cashflow' in str(rule):
            print(f"  {rule.rule} -> {rule.endpoint}")
    
    print("\n✅ Cash flow endpoints added successfully to Flask app")
    
except Exception as e:
    print(f"\n❌ Failed to add cash flow endpoints: {e}")
    traceback.print_exc()

# Test 4: Check QuantLib availability
try:
    import QuantLib as ql
    print(f"\n✅ QuantLib imported successfully (version: {ql.__version__})")
except Exception as e:
    print(f"\n❌ Failed to import QuantLib: {e}")