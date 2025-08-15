#!/usr/bin/env python3
"""
Treasury Cloud Sync - Upload Treasury database to Google Cloud Storage
Integrates with existing json_receiver_project_v2 infrastructure
"""

import os
import sys
import datetime
from pathlib import Path
from google.cloud import storage

def upload_bonds_database_to_gcs(bucket_name='json-receiver-databases'):
    """
    Upload the bonds_data.db file to Google Cloud Storage
    Uses the same bucket as json_receiver_project_v2
    """
    
    # Database file path
    db_file = 'bonds_data.db'
    
    if not os.path.exists(db_file):
        print(f"❌ Database file not found: {db_file}")
        return False
    
    try:
        # Initialize storage client
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        
        # Create blob for the database
        blob = bucket.blob(db_file)
        
        # Check file size
        file_size = os.path.getsize(db_file)
        print(f"📁 Uploading {db_file} ({file_size / 1024 / 1024:.2f} MB)")
        
        # Upload with proper content type
        blob.upload_from_filename(
            db_file,
            content_type='application/x-sqlite3'
        )
        
        # Create timestamped backup
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backups/bonds_data_{timestamp}.db"
        backup_blob = bucket.blob(backup_name)
        backup_blob.upload_from_filename(
            db_file,
            content_type='application/x-sqlite3'
        )
        
        print(f"✅ Successfully uploaded {db_file} to gs://{bucket_name}/")
        print(f"✅ Created backup: gs://{bucket_name}/{backup_name}")
        
        # Verify upload
        updated_blob = bucket.get_blob(db_file)
        if updated_blob:
            upload_time = updated_blob.time_created
            print(f"📅 Upload completed at: {upload_time}")
            print(f"🔗 Cloud URL: gs://{bucket_name}/{db_file}")
            return True
        else:
            print("❌ Upload verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        return False

def main():
    """Main function for command line usage"""
    print("🏦 Treasury Cloud Sync - Upload Database to GCS")
    print("=" * 50)
    
    success = upload_bonds_database_to_gcs()
    
    if success:
        print("\n🎉 Treasury database successfully synced to cloud!")
        print("   The updated yield curve data is now available for:")
        print("   • Production API deployments")
        print("   • Development environments") 
        print("   • Google Sheets functions")
        sys.exit(0)
    else:
        print("\n💥 Failed to sync database to cloud")
        sys.exit(1)

if __name__ == "__main__":
    main()