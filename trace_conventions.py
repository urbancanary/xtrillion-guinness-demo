#!/usr/bin/env python3
"""
Trace where fixed_business_convention comes from
"""

import logging
logging.basicConfig(level=logging.DEBUG)

# Monkey patch to trace convention usage
original_calculate = None

def trace_conventions(*args, **kwargs):
    print("\n🔍 TRACING CONVENTIONS IN CALCULATION ENGINE")
    print("Args:", args[:3] if args else "None")  # Don't print all args
    print("Kwargs keys:", list(kwargs.keys()) if kwargs else "None")
    
    if 'default_conventions' in kwargs:
        print("Default conventions passed:")
        for k, v in kwargs['default_conventions'].items():
            print(f"  {k}: {v}")
    
    return original_calculate(*args, **kwargs)

# Import and patch
from google_analysis10 import calculate_bond_metrics_with_conventions_using_shared_engine
original_calculate = calculate_bond_metrics_with_conventions_using_shared_engine
import google_analysis10
google_analysis10.calculate_bond_metrics_with_conventions_using_shared_engine = trace_conventions

# Now run test
from bond_master_hierarchy_enhanced import calculate_bond_master

DB_PATH = "bonds_data.db"
VALIDATED_DB = "validated_quantlib_bonds.db"
BLOOMBERG_DB = "bloomberg_index.db"

print("=" * 80)
print("TESTING DESCRIPTION ROUTE:")
print("=" * 80)

desc_result = calculate_bond_master(
    description="T 3 15/08/52",
    price=71.66,
    settlement_date="2025-08-01",
    db_path=DB_PATH,
    validated_db_path=VALIDATED_DB,
    bloomberg_db_path=BLOOMBERG_DB
)