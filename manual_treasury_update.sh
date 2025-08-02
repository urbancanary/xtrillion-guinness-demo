#!/bin/bash
#
# Manual Treasury Yield Update Script
# Run this before deployment to update yields
#

echo "🏦 Updating Treasury Yields"
echo "========================="

# Navigate to project directory
cd "$(dirname "$0")"

# Run the update script
python3 us_treasury_yield_fetcher.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Treasury yields updated successfully!"
    
    # Vacuum the database to ensure consistency
    echo ""
    echo "🔄 Vacuuming database for consistency..."
    sqlite3 bonds_data.db "PRAGMA wal_checkpoint(FULL); VACUUM;"
    
    echo ""
    echo "Next steps:"
    echo "1. Review changes: git diff bonds_data.db"
    echo "2. Commit: git add bonds_data.db && git commit -m '🏦 Update Treasury yields'"
    echo "3. Deploy: ./deploy_appengine.sh"
else
    echo "❌ Failed to update Treasury yields"
    exit 1
fi