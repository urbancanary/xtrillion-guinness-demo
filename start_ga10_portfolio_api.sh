#!/bin/bash

# 🚀 Start Google Analysis 10 Portfolio API - Local Development Server
# ===================================================================
# 
# This script starts the enhanced Google Analysis 10 API server for 
# real-time bond portfolio analysis and testing.
#
# Features:
# - 25-bond portfolio analytics
# - Enhanced risk metrics (Duration, Convexity, OAD)  
# - Real market price integration
# - Bloomberg-grade calculations
# - Treasury bond detection
#
# Usage: ./start_ga10_portfolio_api.sh
# URL:   http://localhost:8080
# ===================================================================

echo "🚀 Starting Google Analysis 10 Portfolio API..."
echo "📊 Enhanced Bond Analytics & Risk Metrics Server"
echo "📍 Working directory: $(pwd)"
echo "📅 Timestamp: $(date)"
echo ""

# Check if we're in the right directory
if [ ! -f "google_analysis10_api.py" ]; then
    echo "❌ ERROR: google_analysis10_api.py not found in current directory"
    echo "📂 Please run this script from the google_analysis10 directory"
    exit 1
fi

# Check for required files
echo "🔍 Checking required files..."

if [ -f "bonds_data.db" ]; then
    echo "   ✅ bonds_data.db found"
else
    echo "   ⚠️  bonds_data.db not found in current directory"
fi

if [ -f "validated_quantlib_bonds.db" ]; then
    echo "   ✅ validated_quantlib_bonds.db found"
else
    echo "   ⚠️  validated_quantlib_bonds.db not found in current directory"
fi

# Check Python dependencies
echo "🔍 Checking Python dependencies..."
python3 -c "import flask, requests; print('✅ Flask and requests available')" 2>/dev/null || {
    echo "❌ Missing Python dependencies. Installing..."
    pip3 install flask requests
}

# Check QuantLib
python3 -c "import QuantLib; print('✅ QuantLib available')" 2>/dev/null || {
    echo "⚠️  QuantLib not found. Some calculations may fail."
}

# Set environment variables for local testing
export PORT=8080
export ENV=development
export DATABASE_PATH="./bonds_data.db"
export VALIDATED_DB_PATH="./validated_quantlib_bonds.db"

echo ""
echo "🌐 Google Analysis 10 Portfolio API Server Starting..."
echo "   📡 API Base URL: http://localhost:8080" 
echo "   🔍 Health Check: http://localhost:8080/health"
echo "   📊 Portfolio Analytics: http://localhost:8080/api/v1/portfolio/analyze"
echo "   🏦 Individual Bond: http://localhost:8080/api/v1/bond/parse-and-calculate"
echo ""
echo "🎯 Ready for 25-Bond Portfolio Testing!"
echo "💼 Enhanced Features: Duration, Convexity, OAD, Real Market Prices"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the API
python3 google_analysis10_api.py
