#!/usr/bin/env python3
"""
Rename fixed_day_count column to day_count in validated_quantlib_bonds.db
"""

import sqlite3
import sys

def rename_column():
    """Rename fixed_day_count to day_count."""
    
    print("Renaming column fixed_day_count to day_count in validated_quantlib_bonds.db")
    print("=" * 80)
    
    try:
        conn = sqlite3.connect("validated_quantlib_bonds.db")
        cursor = conn.cursor()
        
        # Check current table structure
        cursor.execute("PRAGMA table_info(validated_quantlib_bonds)")
        columns = cursor.fetchall()
        
        print("\nCurrent columns:")
        column_names = []
        for col in columns:
            column_names.append(col[1])
            print(f"  {col[1]:<30} {col[2]:<15}")
        
        if 'day_count' in column_names:
            print("\nColumn 'day_count' already exists!")
            return
            
        if 'fixed_day_count' not in column_names:
            print("\nColumn 'fixed_day_count' not found!")
            return
        
        # SQLite doesn't support direct column rename in older versions
        # We'll use the ALTER TABLE RENAME COLUMN syntax (SQLite 3.25.0+)
        print("\nRenaming column...")
        
        try:
            # Try the modern way first
            cursor.execute("ALTER TABLE validated_quantlib_bonds RENAME COLUMN fixed_day_count TO day_count")
            conn.commit()
            print("Column renamed successfully using ALTER TABLE RENAME COLUMN")
            
        except sqlite3.OperationalError as e:
            # If that fails, we need to recreate the table
            print(f"Direct rename failed ({e}), using table recreation method...")
            
            # Get the current table schema
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='validated_quantlib_bonds'")
            create_sql = cursor.fetchone()[0]
            
            # Create new table with renamed column
            new_create_sql = create_sql.replace('fixed_day_count', 'day_count')
            new_create_sql = new_create_sql.replace('validated_quantlib_bonds', 'validated_quantlib_bonds_new')
            
            print("\nCreating new table with renamed column...")
            cursor.execute(new_create_sql)
            
            # Copy data with column mapping
            all_columns = [col[1] for col in columns]
            new_columns = [col.replace('fixed_day_count', 'day_count') for col in all_columns]
            
            insert_sql = f"""
                INSERT INTO validated_quantlib_bonds_new ({','.join(new_columns)})
                SELECT {','.join(all_columns)} FROM validated_quantlib_bonds
            """
            cursor.execute(insert_sql)
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE validated_quantlib_bonds")
            cursor.execute("ALTER TABLE validated_quantlib_bonds_new RENAME TO validated_quantlib_bonds")
            
            conn.commit()
            print("Column renamed successfully using table recreation")
        
        # Verify the change
        print("\n" + "=" * 80)
        print("Updated columns:")
        cursor.execute("PRAGMA table_info(validated_quantlib_bonds)")
        for col in cursor.fetchall():
            print(f"  {col[1]:<30} {col[2]:<15}")
        
        # Check some data
        cursor.execute("SELECT isin, description, day_count FROM validated_quantlib_bonds LIMIT 5")
        print("\nSample data:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[2]}")
        
        conn.close()
        print("\nColumn rename completed successfully!")
        
    except Exception as e:
        print(f"\nError: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        sys.exit(1)

if __name__ == "__main__":
    # Confirm before running
    print("This script will rename fixed_day_count to day_count")
    response = input("\nProceed with rename? (yes/no): ")
    
    if response.lower() == 'yes':
        rename_column()
    else:
        print("Rename cancelled.")