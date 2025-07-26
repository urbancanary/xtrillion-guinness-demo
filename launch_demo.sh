#!/bin/bash
"""
🚀 XTrillion Demo Launcher - Tuesday Ready
========================================

Quick launcher script for Tuesday demo.
Tests everything and starts the API server.
"""

echo "🚀 XTrillion Tuesday Demo Launcher"
echo "================================="
echo "📅 Demo Date: Tuesday"
echo "🎯 Target: Blazing fast bond calculations"
echo ""

# Set working directory
cd /Users/andyseaman/Notebooks/json_receiver_project/google_analysis10

echo "📂 Working directory: $(pwd)"
echo ""

# Check Python and dependencies
echo "🐍 Checking Python environment..."
python3 --version
echo ""

# Test the fast calculator
echo "🧪 Testing Fast Calculator..."
echo "================================"
python3 test_demo_readiness.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Calculator tests passed!"
    echo ""
    
    # Ask if user wants to start API server
    echo "🌐 Ready to start API server for demo?"
    echo "   This will start the API on http://localhost:8080"
    echo ""
    read -p "Start API server? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "🚀 Starting XTrillion API Demo Server..."
        echo "======================================="
        echo "📡 API will be available at: http://localhost:8080"
        echo "📊 Available endpoints:"
        echo "   POST /v1/bond/calculate   - Individual calculations"
        echo "   POST /v1/bond/portfolio   - Portfolio calculations" 
        echo "   GET  /v1/bond/demo        - Demo examples"
        echo "   GET  /v1/health           - Health check"
        echo ""
        echo "🛑 Press Ctrl+C to stop the server"
        echo ""
        
        # Start the API server
        python3 xtrillion_api_demo.py
    else
        echo ""
        echo "💡 To start API later, run:"
        echo "   python3 xtrillion_api_demo.py"
        echo ""
        echo "🧪 To test again, run:"
        echo "   python3 test_demo_readiness.py"
    fi
else
    echo ""
    echo "❌ Calculator tests failed!"
    echo "🔧 Please fix issues before demo"
    echo ""
    echo "💡 Check the error messages above"
    echo "💡 Make sure QuantLib is installed: pip install QuantLib"
    exit 1
fi

echo ""
echo "🎯 Tuesday Demo Ready!"
echo "===================="
