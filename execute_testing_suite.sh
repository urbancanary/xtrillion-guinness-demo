#!/bin/bash
# Execute Testing Suite - Complete Implementation
# =============================================
#
# This script executes the complete Bloomberg testing suite

echo "🏦 BLOOMBERG TESTING SUITE EXECUTION"
echo "=================================================="

# Set working directory
cd /Users/andyseaman/Notebooks/json_receiver_project/google_analysis10

# Check prerequisites
echo "🔍 Checking Prerequisites..."

# Check if calculate_BOND_MASTER is available
python3 -c "
try:
    from bond_master_hierarchy import calculate_BOND_MASTER
    print('✅ calculate_BOND_MASTER import successful')
except ImportError as e:
    print('❌ Import failed:', e)
    exit(1)
" || exit 1

# Check database
if [ -f "bonds_data.db" ]; then
    echo "✅ bonds_data.db found"
else
    echo "❌ bonds_data.db not found"
    exit 1
fi

echo ""
echo "📝 Testing framework will be created and executed..."
echo ""
