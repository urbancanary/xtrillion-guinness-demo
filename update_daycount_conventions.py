#!/usr/bin/env python3
"""
Update day count conventions in validated_quantlib_bonds.db to match QuantLib naming
"""

import sqlite3
import sys

def update_conventions():
    """Update day count conventions to QuantLib format."""
    
    # Define the mapping
    convention_mapping = {
        'Actual/Actual (ISMA)': 'ActualActual.Bond',
        'Thirty360': 'Thirty360.BondBasis',
        'ACT/360': 'Actual360',
        'ACT/365': 'Actual365Fixed',
        '30/360': 'Thirty360.BondBasis',
        'Actual/360': 'Actual360',
        'Actual/365 Fixed': 'Actual365Fixed',
        'Actual/Actual (ISDA)': 'ActualActual.ISDA',
        '30/360 Bond Basis': 'Thirty360.BondBasis',
    }
    
    print("Updating day count conventions in validated_quantlib_bonds.db")
    print("=" * 80)
    
    try:
        # Connect to database
        conn = sqlite3.connect("validated_quantlib_bonds.db")
        cursor = conn.cursor()
        
        # First, check current conventions
        cursor.execute("SELECT DISTINCT fixed_day_count, COUNT(*) FROM validated_quantlib_bonds GROUP BY fixed_day_count")
        current_conventions = cursor.fetchall()
        
        print("\nCurrent conventions:")
        for conv, count in current_conventions:
            print(f"  {conv:<30} - {count:>6} bonds")
        
        # Create backup first
        print("\nCreating backup of current data...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS validated_quantlib_bonds_backup AS 
            SELECT * FROM validated_quantlib_bonds
        """)
        conn.commit()
        print("Backup created in validated_quantlib_bonds_backup table")
        
        # Perform updates
        print("\nPerforming updates...")
        total_updated = 0
        
        for old_conv, new_conv in convention_mapping.items():
            cursor.execute(
                "UPDATE validated_quantlib_bonds SET fixed_day_count = ? WHERE fixed_day_count = ?",
                (new_conv, old_conv)
            )
            rows_affected = cursor.rowcount
            if rows_affected > 0:
                print(f"  Updated '{old_conv}' -> '{new_conv}': {rows_affected} rows")
                total_updated += rows_affected
        
        # Commit changes
        conn.commit()
        
        # Verify updates
        print("\n" + "=" * 80)
        print("Updated conventions:")
        cursor.execute("SELECT DISTINCT fixed_day_count, COUNT(*) FROM validated_quantlib_bonds GROUP BY fixed_day_count")
        updated_conventions = cursor.fetchall()
        
        for conv, count in updated_conventions:
            print(f"  {conv:<30} - {count:>6} bonds")
        
        print(f"\nTotal bonds updated: {total_updated}")
        print("Update completed successfully!")
        
        # Close connection
        conn.close()
        
    except Exception as e:
        print(f"\nError updating conventions: {e}")
        print("Rolling back changes...")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        sys.exit(1)

if __name__ == "__main__":
    # Confirm before running
    print("This script will update day count conventions in validated_quantlib_bonds.db")
    print("A backup table will be created first.")
    response = input("\nProceed with update? (yes/no): ")
    
    if response.lower() == 'yes':
        update_conventions()
    else:
        print("Update cancelled.")