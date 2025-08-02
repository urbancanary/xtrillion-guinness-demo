#!/usr/bin/env python3
"""
Simple test of database sync using gsutil commands
"""

import os
import subprocess
import hashlib
import sqlite3
from datetime import datetime

def run_command(cmd):
    """Run shell command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result.stdout, result.returncode

def get_file_hash(file_path):
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_latest_treasury_date(db_path):
    """Get the latest date in tsys_enhanced table."""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(Date) FROM tsys_enhanced")
            return cursor.fetchone()[0]
    except Exception as e:
        return f"Error: {e}"

print("🔄 Testing Database Sync")
print("=" * 60)

# Check local database
local_db = "bonds_data.db"
if os.path.exists(local_db):
    local_hash = get_file_hash(local_db)[:8]
    local_size = os.path.getsize(local_db) / (1024*1024)  # MB
    local_treasury_date = get_latest_treasury_date(local_db)
    print(f"\n🔵 Local {local_db}:")
    print(f"   Size: {local_size:.1f} MB")
    print(f"   Hash: {local_hash}...")
    print(f"   Latest Treasury date: {local_treasury_date}")
else:
    print(f"\n❌ Local {local_db} not found")

# Download cloud database to temp file
print(f"\n☁️  Downloading from GCS...")
temp_db = "bonds_data_cloud.db"
cmd = f"gsutil cp gs://json-receiver-databases/{local_db} {temp_db}"
output, returncode = run_command(cmd)

if returncode == 0:
    cloud_hash = get_file_hash(temp_db)[:8]
    cloud_size = os.path.getsize(temp_db) / (1024*1024)  # MB
    cloud_treasury_date = get_latest_treasury_date(temp_db)
    print(f"\n🔴 Cloud {local_db}:")
    print(f"   Size: {cloud_size:.1f} MB")
    print(f"   Hash: {cloud_hash}...")
    print(f"   Latest Treasury date: {cloud_treasury_date}")
    
    # Compare
    print(f"\n🔍 Comparison:")
    if local_hash == cloud_hash:
        print("   ✅ Databases are identical")
    else:
        print("   ⚠️  Databases differ")
        print(f"   Local Treasury date: {local_treasury_date}")
        print(f"   Cloud Treasury date: {cloud_treasury_date}")
    
    # Clean up
    os.remove(temp_db)
else:
    print(f"\n❌ Failed to download from GCS")

print("\n" + "=" * 60)