#!/bin/bash

# 🎯 Start Local Bond Analysis Demo
# ================================
# This script starts both:
# 1. Google Analysis 10 API (localhost:8081)
# 2. Streamlit Demo App (localhost:8501)

echo "🚀 Starting Local Bond Analysis Demo"
echo "===================================="
echo ""

# Check if we're in the right directory
if [ ! -f "google_analysis10_api.py" ]; then
    echo "❌ ERROR: google_analysis10_api.py not found"
    echo "📂 Please run this script from the google_analysis10 directory"
    exit 1
fi

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "📦 Installing Streamlit..."
    pip3 install streamlit
fi

# Kill any existing processes on these ports
echo "🧹 Cleaning up existing processes..."
lsof -ti:8080 | xargs kill -9 2>/dev/null || true
lsof -ti:8501 | xargs kill -9 2>/dev/null || true

# Start the API in background
echo "🚀 Starting API server on port 8080..."
python3 google_analysis10_api.py &
API_PID=$!

# Wait for API to start
echo "⏳ Waiting for API to start..."
sleep 3

# Test API health
echo "🔍 Testing API health..."
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ API is running on http://localhost:8080"
else
    echo "⚠️  API may still be starting..."
fi

echo ""
echo "🎨 Starting Streamlit Demo App..."
echo "📱 Demo will open in your browser at: http://localhost:8501"
echo ""
echo "🛑 To stop both services, press Ctrl+C"
echo ""

# Function to cleanup when script exits
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $API_PID 2>/dev/null || true
    lsof -ti:8080 | xargs kill -9 2>/dev/null || true
    lsof -ti:8501 | xargs kill -9 2>/dev/null || true
    echo "✅ Cleanup complete"
    exit 0
}

# Set trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Start Streamlit (this will run in foreground)
streamlit run bond_analysis_demo.py --server.port=8501

# If we get here, streamlit was stopped, so cleanup
cleanup
