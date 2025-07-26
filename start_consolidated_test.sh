#!/bin/bash
"""
QUICK START: Consolidated 6-Way Bond Testing
===========================================

Simple script to run the comprehensive 6-way bond testing framework.
"""

echo "🚀 STARTING CONSOLIDATED 6-WAY BOND TESTING"
echo "==========================================="
echo "📁 Project: google_analysis10"
echo "⏰ Started: $(date)"
echo ""

# Change to project directory
cd "/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10"

# Check if python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3."
    exit 1
fi

# Run the consolidated tester
echo "🧪 Running consolidated 6-way tester..."
python3 run_consolidated_6way_test.py

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ TESTING COMPLETE!"
    echo "📊 Check the HTML report in the project directory"
    echo "💾 Results saved to database"
    echo "📁 Old files archived to archive/ directory"
else
    echo ""
    echo "❌ TESTING FAILED!"
    echo "Check the logs above for error details"
fi

echo ""
echo "⏰ Finished: $(date)"
