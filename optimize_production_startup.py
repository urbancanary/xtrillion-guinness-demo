# Production Startup Optimization Script
# Eliminates 155MB GCS database download for embedded databases

# This script modifies google_analysis10_api.py to skip GCS downloads
# when DATABASE_SOURCE=embedded (set in production Dockerfile)

import os
import sys

def optimize_for_production():
    """Modify API file to skip GCS downloads when databases are embedded"""
    
    api_file = "google_analysis10_api.py"
    
    # Read current file
    with open(api_file, 'r') as f:
        content = f.read()
    
    # Check if already optimized
    if "# PRODUCTION_OPTIMIZED" in content:
        print("✅ API already optimized for production")
        return True
    
    # Create optimized version
    optimized_content = content.replace(
        '# 🔧 CRITICAL: Fetch databases from GCS before starting API\n    logger.info("🔍 Ensuring bond databases are available from GCS...")\n    if ensure_databases_available():\n        logger.info("✅ All required databases successfully fetched from GCS")\n    else:',
        '''# 🔧 PRODUCTION_OPTIMIZED: Skip GCS download when databases embedded
    database_source = os.environ.get('DATABASE_SOURCE', 'gcs')
    
    if database_source == 'embedded':
        logger.info("✅ Using embedded databases (no GCS download needed)")
        # Verify embedded databases exist
        if os.path.exists(DATABASE_PATH) and os.path.exists(VALIDATED_DB_PATH):
            logger.info(f"✅ Embedded databases verified: {os.path.getsize(DATABASE_PATH)/(1024*1024):.1f}MB primary")
        else:
            logger.error("❌ Embedded databases missing - check Dockerfile.production")
            sys.exit(1)
    else:
        logger.info("🔍 Ensuring bond databases are available from GCS...")
        if ensure_databases_available():
            logger.info("✅ All required databases successfully fetched from GCS")
        else:'''
    )
    
    # Write optimized file
    with open(f"{api_file}.production", 'w') as f:
        f.write(optimized_content)
    
    print("✅ Created production-optimized API file: google_analysis10_api.py.production")
    print("🚀 This eliminates 155MB GCS download on cold starts")
    return True

if __name__ == "__main__":
    optimize_for_production()