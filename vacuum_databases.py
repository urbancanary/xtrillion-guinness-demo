#!/usr/bin/env python3
"""
Vacuum SQLite Databases
======================

Ensures SQLite databases are properly vacuumed before copying/uploading.
This prevents issues with Write-Ahead Log (WAL) files not being included.
"""

import sqlite3
import os
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def vacuum_database(db_path: str) -> tuple[int, int]:
    """
    Vacuum a SQLite database and return size before/after.
    
    Returns:
        Tuple of (size_before, size_after) in bytes
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found: {db_path}")
    
    size_before = os.path.getsize(db_path)
    
    try:
        with sqlite3.connect(db_path) as conn:
            # First checkpoint the WAL file to ensure all changes are in main database
            cursor = conn.cursor()
            cursor.execute("PRAGMA wal_checkpoint(FULL)")
            checkpoint_result = cursor.fetchone()
            
            # Then vacuum to rebuild and optimize
            cursor.execute("VACUUM")
            
            # Get some stats
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            
        size_after = os.path.getsize(db_path)
        
        return size_before, size_after
        
    except sqlite3.Error as e:
        logger.error(f"SQLite error for {db_path}: {e}")
        return size_before, size_before


def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def main():
    """Vacuum all project databases."""
    databases = [
        'bonds_data.db',
        'validated_quantlib_bonds.db',
        'bloomberg_index.db'
    ]
    
    print("🔧 Vacuuming SQLite Databases")
    print("=" * 40)
    
    total_before = 0
    total_after = 0
    
    for db_name in databases:
        if os.path.exists(db_name):
            print(f"\n📁 {db_name}:")
            try:
                size_before, size_after = vacuum_database(db_name)
                total_before += size_before
                total_after += size_after
                
                reduction = ((size_before - size_after) / size_before * 100) if size_before > 0 else 0
                
                print(f"   Before: {format_size(size_before)}")
                print(f"   After:  {format_size(size_after)}")
                if reduction > 0:
                    print(f"   Saved:  {format_size(size_before - size_after)} ({reduction:.1f}% reduction)")
                else:
                    print(f"   Status: Already optimized")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        else:
            print(f"\n📁 {db_name}: Not found")
    
    if total_before > 0:
        total_reduction = ((total_before - total_after) / total_before * 100)
        print("\n" + "=" * 40)
        print(f"📊 Total:")
        print(f"   Before: {format_size(total_before)}")
        print(f"   After:  {format_size(total_after)}")
        if total_reduction > 0:
            print(f"   Saved:  {format_size(total_before - total_after)} ({total_reduction:.1f}% reduction)")
    
    print("\n✅ Vacuum complete!")
    
    # Check for WAL files
    wal_files = list(Path('.').glob('*.db-wal'))
    if wal_files:
        print("\n⚠️  WAL files found (should be empty after vacuum):")
        for wal in wal_files:
            size = os.path.getsize(wal)
            if size > 0:
                print(f"   {wal}: {format_size(size)} - Consider investigating")
            else:
                print(f"   {wal}: Empty (OK)")


if __name__ == "__main__":
    main()