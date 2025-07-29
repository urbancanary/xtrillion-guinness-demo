#!/bin/bash
# 🌸 Google Analysis 10 - LOCAL TESTING CONTAINER SETUP
# =====================================================
# PURPOSE: Run production API locally for safe testing and development
# TECHNOLOGY: Podman container (identical to production environment)
# USE CASE: Testing your portfolio data without affecting production
# 
# ⚠️  THIS IS FOR LOCAL DEVELOPMENT ONLY - NOT PRODUCTION DEPLOYMENT
# 🚀 For production deployment, see: PRODUCTION_DEPLOYMENT_README.md
# 
# Quick Start Instructions: LOCAL_CONTAINER_TESTING_README.md
# Definitive Documentation: DEPLOYMENT_SCRIPTS_DOCUMENTATION.md

set -e

PROJECT_DIR="/Users/andyseaman/Notebooks/json_receiver_project/google_analysis10"
CONTAINER_NAME="ga10-local"
LOCAL_PORT="8080"

echo "🌸 Google Analysis 10 - Local Container Setup"
echo "=============================================="

# Function to check if Podman is installed
check_podman() {
    if ! command -v podman &> /dev/null; then
        echo "❌ Podman not found. Installing with Homebrew..."
        if command -v brew &> /dev/null; then
            brew install podman
            echo "✅ Podman installed"
        else
            echo "❌ Please install Homebrew first: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
    else
        echo "✅ Podman found: $(podman --version)"
    fi
}

# Function to initialize Podman machine if needed
init_podman() {
    echo "🔧 Checking Podman machine..."
    if ! podman machine list | grep -q "Currently running"; then
        echo "🚀 Starting Podman machine..."
        podman machine init --cpus 2 --memory 4096 --disk-size 20 2>/dev/null || echo "Machine already exists"
        podman machine start
    else
        echo "✅ Podman machine is running"
    fi
}

# Function to build the container
build_container() {
    echo "🔨 Building GA10 container..."
    
    cd "$PROJECT_DIR"
    
    # Stop and remove any existing container
    podman stop "$CONTAINER_NAME" 2>/dev/null || true
    podman rm "$CONTAINER_NAME" 2>/dev/null || true
    
    # Build the container
    podman build -t ga10-api:latest .
    
    echo "✅ Container built successfully"
}

# Function to run the container
run_container() {
    echo "🚀 Starting GA10 API container with runtime database integration..."
    
    # Verify local databases exist
    cd "$PROJECT_DIR"
    for db in "bonds_data.db" "validated_quantlib_bonds.db" "bloomberg_index.db"; do
        if [ ! -f "$db" ]; then
            echo "❌ Database not found: $db"
            echo "💡 Ensure all databases are in the project root directory"
            exit 1
        fi
        size=$(ls -lh "$db" | awk '{print $5}')
        echo "   ✅ Found $db ($size)"
    done
    
    # Start container normally (databases will be copied after startup)
    podman run -d \
        --name "$CONTAINER_NAME" \
        -p ${LOCAL_PORT}:8080 \
        -e ENVIRONMENT="local" \
        -e SERVICE_NAME="xtrillion-ga10-local" \
        -e DATABASE_SOURCE="local_copy" \
        -e DATABASE_PATH="/app/bonds_data.db" \
        -e VALIDATED_DB_PATH="/app/validated_quantlib_bonds.db" \
        -e BLOOMBERG_DB_PATH="/app/bloomberg_index.db" \
        -e PORT=8080 \
        ga10-api:latest
    
    # Wait for container to start
    sleep 3
    
    # Copy databases into running container
    echo "📦 Copying local databases into container..."
    podman cp "${PROJECT_DIR}/bonds_data.db" "${CONTAINER_NAME}:/app/"
    podman cp "${PROJECT_DIR}/validated_quantlib_bonds.db" "${CONTAINER_NAME}:/app/"
    podman cp "${PROJECT_DIR}/bloomberg_index.db" "${CONTAINER_NAME}:/app/"
    
    echo "✅ Container started with local database copies"
    echo "🌐 API available at: http://localhost:${LOCAL_PORT}"
    echo "📁 Using latest databases from: $PROJECT_DIR"
}

# Function to check container status
check_status() {
    echo "📊 Container Status:"
    echo "==================="
    
    if podman ps | grep -q "$CONTAINER_NAME"; then
        echo "✅ Container is running"
        
        # Wait for API to be ready
        echo "⏳ Waiting for API to be ready..."
        for i in {1..30}; do
            if curl -s "http://localhost:${LOCAL_PORT}/health" >/dev/null 2>&1; then
                echo "✅ API is ready!"
                break
            fi
            echo "   Attempt $i/30..."
            sleep 2
        done
        
        # Show health check
        echo "🏥 Health Check:"
        curl -s "http://localhost:${LOCAL_PORT}/health" | jq '.' || echo "Health check failed"
        
    else
        echo "❌ Container is not running"
        echo "📋 Recent logs:"
        podman logs "$CONTAINER_NAME" --tail 20 || echo "No logs available"
    fi
}

# Function to test the API
test_api() {
    echo "🧪 Testing API Endpoints:"
    echo "========================="
    
    local base_url="http://localhost:${LOCAL_PORT}"
    
    # Test individual bond
    echo "🔍 Testing individual bond analysis..."
    curl -s -X POST "${base_url}/api/v1/bond/parse-and-calculate" \
        -H "Content-Type: application/json" \
        -H "X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q" \
        -d '{
            "description": "QNBK 1 5/8 09/22/25",
            "price": 99.529
        }' | jq '.bond.analytics // .error' || echo "Individual bond test failed"
    
    echo ""
    
    # Test portfolio analysis  
    echo "📊 Testing portfolio analysis..."
    curl -s -X POST "${base_url}/api/v1/portfolio/analyze" \
        -H "Content-Type: application/json" \
        -H "X-API-Key: gax10_demo_3j5h8m9k2p6r4t7w1q" \
        -d '{
            "data": [
                {"BOND_CD": "XS2233188353", "CLOSING PRICE": 99.529, "WEIGHTING": 4.87},
                {"BOND_CD": "US279158AJ82", "CLOSING PRICE": 70.804, "WEIGHTING": 2.97}
            ]
        }' | jq '.portfolio_metrics // .error' || echo "Portfolio test failed"
}

# Function to show container logs
show_logs() {
    echo "📋 Container Logs:"
    echo "=================="
    podman logs "$CONTAINER_NAME" --tail 50
}

# Function to stop container
stop_container() {
    echo "🛑 Stopping GA10 container..."
    podman stop "$CONTAINER_NAME" 2>/dev/null || echo "Container not running"
    podman rm "$CONTAINER_NAME" 2>/dev/null || echo "Container not found"
    echo "✅ Container stopped and removed"
}

# Function to clean up everything
cleanup() {
    echo "🧹 Cleaning up..."
    stop_container
    podman rmi ga10-api:latest 2>/dev/null || echo "Image not found"
    echo "✅ Cleanup complete"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  build     - Build the container"
    echo "  run       - Run the container"
    echo "  start     - Build and run (default)"
    echo "  status    - Check container status"
    echo "  test      - Test API endpoints"
    echo "  logs      - Show container logs"
    echo "  stop      - Stop the container"
    echo "  cleanup   - Stop and remove everything"
    echo "  restart   - Stop, rebuild, and start"
    echo ""
    echo "📖 Quick Start: LOCAL_CONTAINER_TESTING_README.md"
    echo "📋 Full Documentation: DEPLOYMENT_SCRIPTS_DOCUMENTATION.md"
}

# Main execution
case "${1:-start}" in
    "build")
        check_podman
        init_podman
        build_container
        ;;
    "run")
        run_container
        sleep 3
        check_status
        ;;
    "start")
        check_podman
        init_podman
        build_container
        run_container
        sleep 3
        check_status
        echo ""
        echo "🎉 Ready to test! Try these commands:"
        echo "   $0 test      # Test API endpoints"
        echo "   python3 test_local_portfolio.py  # Test your portfolio"
        echo "   $0 logs      # View container logs"
        echo "   $0 stop      # Stop container"
        echo ""
        echo "📖 See: LOCAL_CONTAINER_TESTING_README.md for instructions"
        ;;
    "status")
        check_status
        ;;
    "test")
        test_api
        ;;
    "logs")
        show_logs
        ;;
    "stop")
        stop_container
        ;;
    "cleanup")
        cleanup
        ;;
    "restart")
        stop_container
        build_container
        run_container
        sleep 3
        check_status
        ;;
    *)
        show_usage
        ;;
esac
