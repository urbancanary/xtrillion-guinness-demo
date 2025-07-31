#!/bin/bash

# Efficient Agent Runner - Minimizes Token Usage
# ==============================================

echo "🚀 Efficient Agent Runner - Token Optimized"
echo "=========================================="

# Function to run quick checks
quick_check() {
    echo "⚡ Running quick health checks (minimal tokens)..."
    
    # 1. Check for obvious issues only
    echo "📍 Checking recent test files for cleanup..."
    find . -name "*test*_202*.json" -mtime -7 -type f | head -10
    
    # 2. Quick duplication check on critical files only
    echo "📍 Checking main API files for duplication..."
    ls -la google_analysis10_api*.py 2>/dev/null | wc -l
    
    # 3. Count backup files
    echo "📍 Counting backup files..."
    find . -name "*backup*" -o -name "*_old*" -o -name "*_v[0-9]*" | wc -l
}

# Function for targeted scans
targeted_scan() {
    local target_dir=${1:-"."}
    local pattern=${2:-"*.py"}
    
    echo "🎯 Running targeted scan on $target_dir with pattern $pattern"
    
    # Duplication scan - targeted
    if [ -f "code_duplication_agent.py" ]; then
        python3 code_duplication_agent.py --scan --dir "$target_dir" --pattern "$pattern" --top 5
    fi
    
    # Orphaned code - quick mode
    if [ -f "orphaned_code_agent.py" ]; then
        python3 orphaned_code_agent.py --scan --days 30 --skip-imports
    fi
}

# Function for incremental scan (only changed files)
incremental_scan() {
    echo "📈 Running incremental scan (changed files only)..."
    
    # Get files changed in last 7 days
    changed_files=$(find . -name "*.py" -mtime -7 -type f | grep -v __pycache__ | head -20)
    
    if [ -n "$changed_files" ]; then
        echo "Found $(echo "$changed_files" | wc -l) recently changed files"
        # Would pass these to agents if they supported file lists
    else
        echo "No recently changed files found"
    fi
}

# Main menu
case "${1:-menu}" in
    "quick")
        quick_check
        ;;
    "targeted")
        targeted_scan "${2:-.}" "${3:-*.py}"
        ;;
    "incremental")
        incremental_scan
        ;;
    "full")
        echo "⚠️  Full scan uses significant tokens. Continue? (y/n)"
        read -r response
        if [[ "$response" == "y" ]]; then
            python3 agent_scheduler.py --run-all --skip-api
        fi
        ;;
    *)
        echo "Token-Efficient Agent Options:"
        echo "=============================="
        echo ""
        echo "1. quick       - Minimal token usage, basic health check"
        echo "2. targeted    - Scan specific directory/pattern"
        echo "3. incremental - Scan only recently changed files"  
        echo "4. full        - Complete scan (high token usage)"
        echo ""
        echo "Usage examples:"
        echo "  ./efficient_agent_runner.sh quick"
        echo "  ./efficient_agent_runner.sh targeted ./src '*.py'"
        echo "  ./efficient_agent_runner.sh incremental"
        echo ""
        echo "💡 Tip: Use 'quick' daily, 'targeted' weekly, 'full' monthly"
        ;;
esac

echo ""
echo "✅ Token-efficient scan complete!"