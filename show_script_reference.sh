#!/bin/bash
# 🌸 Google Analysis 10 - Quick Script Reference
# ==============================================
# Shows all deployment/testing scripts and their purposes

echo "🌸 Google Analysis 10 - Script Reference"
echo "========================================"
echo ""

echo "📁 Current Directory: $(pwd)"
echo "🕐 Date: $(date)"
echo ""

echo "🔧 LOCAL DEVELOPMENT SCRIPTS:"
echo "-----------------------------"
if [ -f "local_container_setup.sh" ]; then
    echo "✅ local_container_setup.sh    - Local API container (USE THIS FOR TESTING)"
    echo "   Commands: start, status, test, logs, stop"
else
    echo "❌ local_container_setup.sh    - Missing!"
fi

if [ -f "test_local_portfolio.py" ]; then
    echo "✅ test_local_portfolio.py     - Test your portfolio against local container"
else
    echo "❌ test_local_portfolio.py     - Missing!"
fi

echo ""
echo "🚀 PRODUCTION DEPLOYMENT SCRIPTS:"
echo "---------------------------------"
if [ -f "deploy_appengine_fixed.sh" ]; then
    echo "✅ deploy_appengine_fixed.sh   - Deploy to production (USE WITH CAUTION)"
else
    echo "❌ deploy_appengine_fixed.sh   - Missing!"
fi

if [ -f "deploy_appengine.sh" ]; then
    echo "📦 deploy_appengine.sh         - Legacy version (consider archiving)"
else
    echo "   deploy_appengine.sh         - Not found (OK - legacy version)"
fi

echo ""
echo "📖 DOCUMENTATION FILES:"
echo "-----------------------"
if [ -f "DEPLOYMENT_SCRIPTS_DOCUMENTATION.md" ]; then
    echo "✅ DEPLOYMENT_SCRIPTS_DOCUMENTATION.md - Master script overview"
else
    echo "❌ DEPLOYMENT_SCRIPTS_DOCUMENTATION.md - Missing!"
fi

if [ -f "LOCAL_CONTAINER_README.md" ]; then
    echo "✅ LOCAL_CONTAINER_README.md           - Local container testing guide"
else
    echo "❌ LOCAL_CONTAINER_README.md           - Missing!"
fi

echo ""
echo "🎯 QUICK START COMMANDS:"
echo "------------------------"
echo "For local testing (SAFE):"
echo "  ./local_container_setup.sh start"
echo "  python3 test_local_portfolio.py"
echo ""
echo "For production deployment (CAREFUL):"
echo "  ./deploy_appengine_fixed.sh"
echo ""
echo "For help:"
echo "  cat DEPLOYMENT_SCRIPTS_DOCUMENTATION.md"
echo "  cat LOCAL_CONTAINER_README.md"
echo ""

echo "🔍 Container Status Check:"
echo "-------------------------"
if command -v podman &> /dev/null; then
    echo "✅ Podman installed: $(podman --version)"
    if podman ps | grep -q "ga10-local"; then
        echo "✅ Local container is running"
        echo "🌐 API available at: http://localhost:8080"
    else
        echo "⚪ Local container not running"
        echo "💡 Start with: ./local_container_setup.sh start"
    fi
else
    echo "⚪ Podman not installed (will be installed automatically when needed)"
fi

echo ""
echo "📊 Database Files:"
echo "-----------------"
for db in bonds_data.db validated_quantlib_bonds.db bloomberg_index.db; do
    if [ -f "$db" ]; then
        size=$(ls -lh "$db" | awk '{print $5}')
        echo "✅ $db ($size)"
    else
        echo "❌ $db - Missing!"
    fi
done

echo ""
echo "🎉 All scripts documented and organized!"
echo "   No more confusion about which script to use when."
