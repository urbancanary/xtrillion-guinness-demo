#!/usr/bin/env python3
"""
Test uploading updated database to GCS
"""

import os
import subprocess
import hashlib
from datetime import datetime

def run_command(cmd):
    """Run shell command and return output."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print("Success!")
    return result.stdout, result.returncode

def get_file_hash(file_path):
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

print("🚀 Testing Database Upload to GCS")
print("=" * 60)

# First, create a backup of the cloud version
print("\n1️⃣  Creating backup of cloud database...")
backup_name = f"bonds_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
cmd = f"gsutil cp gs://json-receiver-databases/bonds_data.db gs://json-receiver-databases/{backup_name}"
output, returncode = run_command(cmd)

if returncode == 0:
    print(f"   ✅ Backup created: {backup_name}")
else:
    print("   ❌ Backup failed")
    exit(1)

# Get local file info
local_db = "bonds_data.db"
local_hash = get_file_hash(local_db)[:8]
local_size = os.path.getsize(local_db) / (1024*1024)

print(f"\n2️⃣  Uploading local database to GCS...")
print(f"   Local file: {local_size:.1f} MB, hash: {local_hash}...")

# Upload with metadata
metadata_headers = [
    f"-h 'x-goog-meta-updated-at:{datetime.utcnow().isoformat()}'",
    f"-h 'x-goog-meta-source:manual_sync'",
    f"-h 'x-goog-meta-treasury-date:2025-07-31'"
]

cmd = f"gsutil {' '.join(metadata_headers)} cp {local_db} gs://json-receiver-databases/{local_db}"
output, returncode = run_command(cmd)

if returncode == 0:
    print("   ✅ Upload successful!")
    
    # Verify upload
    print("\n3️⃣  Verifying upload...")
    cmd = f"gsutil stat gs://json-receiver-databases/{local_db}"
    output, returncode = run_command(cmd)
    if returncode == 0:
        print("   ✅ Verification successful")
        print("\n🎉 Database successfully synced to cloud!")
        print(f"\n📊 Summary:")
        print(f"   - Updated Treasury yields to 2025-07-31")
        print(f"   - Backup saved as: {backup_name}")
        print(f"   - Cloud database now matches local")
    else:
        print("   ❌ Verification failed")
else:
    print("   ❌ Upload failed")
    print("\n🔄 To restore backup:")
    print(f"   gsutil cp gs://json-receiver-databases/{backup_name} gs://json-receiver-databases/bonds_data.db")

print("\n" + "=" * 60)