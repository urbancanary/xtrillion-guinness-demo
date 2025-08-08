#!/usr/bin/env python3
"""
Rename all fixed_ columns in validated_quantlib_bonds.db
- fixed_business_convention -> business_convention
- fixed_frequency -> frequency
"""

import sqlite3
import sys

def rename_all_fixed_columns():
    """Rename all fixed_ prefixed columns."""
    
    columns_to_rename = [
        ('fixed_business_convention', 'business_convention'),
        ('fixed_frequency', 'frequency')
    ]
    
    print("Renaming all fixed_ columns in validated_quantlib_bonds.db")
    print("=" * 80)
    
    try:
        conn = sqlite3.connect("validated_quantlib_bonds.db")
        cursor = conn.cursor()
        
        # Check current table structure
        cursor.execute("PRAGMA table_info(validated_quantlib_bonds)")
        columns = cursor.fetchall()
        
        print("\nCurrent columns:")
        current_column_names = []
        for col in columns:
            current_column_names.append(col[1])
            if 'fixed_' in col[1]:
                print(f"  ⚠️  {col[1]:<30} {col[2]:<15}")
            else:
                print(f"     {col[1]:<30} {col[2]:<15}")
        
        # Process each rename
        for old_name, new_name in columns_to_rename:
            if old_name not in current_column_names:
                print(f"\n⚠️  Column '{old_name}' not found, skipping...")
                continue
                
            if new_name in current_column_names:
                print(f"\n⚠️  Column '{new_name}' already exists, skipping...")
                continue
            
            print(f"\nRenaming '{old_name}' -> '{new_name}'...")
            
            try:
                # Try the modern way first
                cursor.execute(f"ALTER TABLE validated_quantlib_bonds RENAME COLUMN {old_name} TO {new_name}")
                conn.commit()
                print(f"✅ Successfully renamed '{old_name}' -> '{new_name}'")
                
            except sqlite3.OperationalError as e:
                print(f"❌ Direct rename failed: {e}")
                # Would need to implement table recreation here if needed
                raise
        
        # Verify the changes
        print("\n" + "=" * 80)
        print("Updated columns:")
        cursor.execute("PRAGMA table_info(validated_quantlib_bonds)")
        for col in cursor.fetchall():
            if 'fixed_' in col[1]:
                print(f"  ⚠️  {col[1]:<30} {col[2]:<15} (still has fixed_ prefix!)")
            else:
                print(f"  ✅  {col[1]:<30} {col[2]:<15}")
        
        # Check some data
        cursor.execute("SELECT isin, description, business_convention, frequency FROM validated_quantlib_bonds LIMIT 3")
        print("\nSample data:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[2]}, {row[3]}")
        
        conn.close()
        print("\nAll column renames completed successfully!")
        
    except Exception as e:
        print(f"\nError: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        sys.exit(1)

if __name__ == "__main__":
    # Confirm before running
    print("This script will rename:")
    print("  - fixed_business_convention -> business_convention")
    print("  - fixed_frequency -> frequency")
    response = input("\nProceed with rename? (yes/no): ")
    
    if response.lower() == 'yes':
        rename_all_fixed_columns()
    else:
        print("Rename cancelled.")