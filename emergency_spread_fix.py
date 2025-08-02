#!/usr/bin/env python3
"""
Emergency Fix for Production Spread Calculation
==============================================

The issue: GCS downloads databases to current directory (.)
but code expects them in /app/

Quick fix: Create symlinks or update paths
"""

import os
import shutil

print("🚑 Emergency Spread Fix")
print("=" * 40)

# Check where databases actually are
databases = ['bonds_data.db', 'validated_quantlib_bonds.db', 'bloomberg_index.db']

for db in databases:
    if os.path.exists(f'./{db}'):
        print(f"✅ Found {db} in current directory")
        # Create symlink in /app if needed
        if not os.path.exists(f'/app/{db}') and os.path.exists('/app'):
            try:
                os.symlink(f'{os.getcwd()}/{db}', f'/app/{db}')
                print(f"   Created symlink: /app/{db} -> ./{db}")
            except Exception as e:
                print(f"   ❌ Could not create symlink: {e}")
    elif os.path.exists(f'/app/{db}'):
        print(f"✅ Found {db} in /app directory")
    else:
        print(f"❌ {db} not found")

print("\n🔧 Suggested Fix:")
print("Update google_analysis10.py to use current directory:")
print("""
# In fetch_treasury_yields function:
alt_paths = ['./bonds_data.db', 'bonds_data.db', '/app/bonds_data.db']
""")