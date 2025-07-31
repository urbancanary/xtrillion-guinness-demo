#!/usr/bin/env python3
"""
URGENT FIX: App Engine Database Initialization 
==============================================

The App Engine is crashing because DATABASE_SOURCE=gcs but the API
isn't downloading databases from GCS. This script creates a simple fix.
"""

def create_gcs_database_fix():
    """Create the fix for GCS database initialization"""
    
    print("🚨 APP ENGINE DATABASE INITIALIZATION FIX")
    print("=" * 50)
    print()
    
    print("📍 PROBLEM: App Engine says DATABASE_SOURCE=gcs but databases not downloaded")
    print("🔍 LOCATION: google_analysis10_api.py around line 1535")
    print()
    
    # Create a simple Python script to add proper GCS initialization
    gcs_fix_code = '''
# URGENT FIX: Add this code after line 1535 in google_analysis10_api.py
# Replace the "else:" branch with proper GCS handling

    elif database_source == 'gcs':
        logger.info("📥 Using GCS database source - downloading databases...")
        try:
            from gcs_database_manager import GCSDatabaseManager
            gcs_manager = GCSDatabaseManager()
            
            # Download required databases from GCS
            if gcs_manager.fetch_all_databases():
                logger.info("✅ All databases downloaded from GCS successfully")
            else:
                logger.error("❌ Failed to download databases from GCS")
                sys.exit(1)
                
        except Exception as gcs_error:
            logger.error(f"❌ GCS database manager error: {gcs_error}")
            logger.error("💡 Check GCS bucket permissions and database availability")
            sys.exit(1)
    else:
        # Keep existing local database logic
'''
    
    print("✅ FIX CODE TO ADD:")
    print("-" * 40)
    print(gcs_fix_code)
    
    print("🚀 QUICK DEPLOYMENT FIX:")
    print("1. Edit google_analysis10_api.py around line 1535")
    print("2. Add GCS database download logic above")
    print("3. Redeploy: ./deploy_appengine.sh")
    print()
    
    print("🎯 ALTERNATIVE - Switch to embedded databases:")
    print("1. Change app.yaml: DATABASE_SOURCE: embedded")
    print("2. Copy databases to Docker image")
    print("3. Redeploy with embedded databases")

if __name__ == "__main__":
    create_gcs_database_fix()
