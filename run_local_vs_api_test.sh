#!/bin/bash

# Quick Test Runner for Local vs API Comparison
# ============================================

echo "🧪 GOOGLE ANALYSIS 10: Local vs API Testing"
echo "============================================"

# Check if we're in the right directory
if [ ! -f "google_analysis10.py" ]; then
    echo "❌ Error: Not in google_analysis10 directory"
    echo "Please run: cd /Users/andyseaman/Notebooks/json_receiver_project/google_analysis10"
    exit 1
fi

# Check if API is running
echo "🔍 Checking if local API is running..."
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Local API is running on port 8080"
else
    echo "❌ Local API is not running!"
    echo "Please start it first:"
    echo "   Option 1: ./restart_api.sh"
    echo "   Option 2: python3 google_analysis10_api.py"
    echo "   Option 3: ./start_ga10_portfolio_api.sh"
    exit 1
fi

# Check database files
echo "🔍 Checking database files..."
if [ -f "bonds_data.db" ] || [ -f "data/bonds_data.db" ]; then
    echo "✅ Main database found"
else
    echo "⚠️  Main database not found - some tests may fail"
fi

if [ -f "validated_quantlib_bonds.db" ] || [ -f "data/validated_quantlib_bonds.db" ]; then
    echo "✅ Validated database found"
else
    echo "⚠️  Validated database not found - using fallback conventions"
fi

echo ""
echo "🚀 Starting comprehensive test..."
echo "⏱️  This may take 30-60 seconds..."
echo ""

# Run the test
python3 test_local_vs_api_comprehensive.py

# Capture exit code
TEST_RESULT=$?

echo ""
if [ $TEST_RESULT -eq 0 ]; then
    echo "🎉 TESTING COMPLETED SUCCESSFULLY"
    echo "✅ Ready for cloud deployment"
else
    echo "⚠️  TESTING COMPLETED WITH ISSUES"
    echo "❌ Fix discrepancies before cloud deployment"
fi

echo ""
echo "📋 Next Steps:"
echo "   1. Review test results above"
echo "   2. Check detailed JSON output file"
if [ $TEST_RESULT -eq 0 ]; then
    echo "   3. Deploy to cloud: ./deploy_ga10.sh"
else
    echo "   3. Fix local issues before deploying"
fi

exit $TEST_RESULT
