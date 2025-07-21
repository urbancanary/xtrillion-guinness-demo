#!/bin/bash
# Google Analysis 10 Deployment Script - Following XTrillion Patterns
# Uses Podman + GCS database download + Secrets (no embedded databases)

set -e

# Configuration based on your existing fund-reports-service patterns
SERVICE_NAME="xtrillion-ga10"
IMAGE_NAME="xtrillion/xtrillion-ga10:latest"
CONTAINER_NAME="xtrillion-ga10"
PORT=8085
SECRET_NAME="gcs-credentials"
GCS_BUCKET="json-receiver-databases"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_header() { echo -e "${BLUE}[XTRILLION-GA10]${NC} $1"; }

show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup         - Setup Podman secrets and build image"
    echo "  deploy        - Deploy container with GCS database download"
    echo "  stop          - Stop and remove container"
    echo "  logs          - Show container logs"
    echo "  status        - Show container status"
    echo "  rebuild       - Rebuild image and redeploy"
    echo "  test          - Test the deployed service"
    echo ""
    echo "This script follows XTrillion patterns:"
    echo "  ✅ Podman containers (not Docker)"
    echo "  ✅ Podman secrets for GCS credentials"
    echo "  ✅ GCS database download at runtime"
    echo "  ✅ No embedded databases in containers"
}

check_requirements() {
    print_header "Checking requirements..."
    
    # Check Podman
    if ! command -v podman &> /dev/null; then
        print_error "Podman is not installed. Please install Podman first."
        exit 1
    fi
    
    # Check for credentials
    if [ ! -f "./credentials.json" ] && [ ! -f "../credentials.json" ]; then
        print_error "credentials.json not found in current or parent directory"
        print_error "Please place your GCS service account credentials file here"
        exit 1
    fi
    
    # Check for Dockerfile
    if [ ! -f "Dockerfile" ]; then
        print_error "Dockerfile not found in current directory"
        exit 1
    fi
    
    print_status "Requirements check passed ✅"
}

create_gcs_dockerfile() {
    print_header "Creating GCS-enabled Dockerfile..."
    
    # Create a new Dockerfile that downloads databases from GCS (following your patterns)
    cat > Dockerfile.gcs << 'EOF'
FROM python:3.11-slim

# Install system dependencies including gcloud CLI
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install Google Cloud SDK
RUN curl https://sdk.cloud.google.com | bash && \
    /root/google-cloud-sdk/install.sh --quiet
ENV PATH="/root/google-cloud-sdk/bin:${PATH}"

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files (NO databases - they'll be downloaded from GCS)
COPY *.py .
COPY data/.env ./data/
RUN rm -rf archive/ __pycache__/ *.log test_*.py debug_*.py

# Create data directory for GCS downloads
RUN mkdir -p /app/data

# Create startup script that downloads databases from GCS
RUN echo '#!/bin/bash' > /app/download_and_start.sh && \
    echo 'set -e' >> /app/download_and_start.sh && \
    echo 'echo "🚀 Starting XTrillion-GA10 with GCS database download..."' >> /app/download_and_start.sh && \
    echo 'echo "📡 GCS Bucket: $GCS_BUCKET"' >> /app/download_and_start.sh && \
    echo 'echo "🔐 Credentials: $GOOGLE_APPLICATION_CREDENTIALS"' >> /app/download_and_start.sh && \
    echo '' >> /app/download_and_start.sh && \
    echo '# Download databases from GCS' >> /app/download_and_start.sh && \
    echo 'if [ -n "$GCS_BUCKET" ]; then' >> /app/download_and_start.sh && \
    echo '    echo "🔽 Downloading databases from GCS bucket: $GCS_BUCKET"' >> /app/download_and_start.sh && \
    echo '    gsutil cp gs://$GCS_BUCKET/bonds_data.db /app/data/ || echo "⚠️ bonds_data.db not found in GCS"' >> /app/download_and_start.sh && \
    echo '    gsutil cp gs://$GCS_BUCKET/validated_quantlib_bonds.db /app/data/ || echo "⚠️ validated_quantlib_bonds.db not found in GCS"' >> /app/download_and_start.sh && \
    echo '    gsutil cp gs://$GCS_BUCKET/bloomberg_index.db /app/data/ || echo "⚠️ bloomberg_index.db not found in GCS"' >> /app/download_and_start.sh && \
    echo '    echo "✅ Database download complete"' >> /app/download_and_start.sh && \
    echo 'else' >> /app/download_and_start.sh && \
    echo '    echo "⚠️ No GCS_BUCKET specified, using local databases if available"' >> /app/download_and_start.sh && \
    echo 'fi' >> /app/download_and_start.sh && \
    echo '' >> /app/download_and_start.sh && \
    echo '# List downloaded files' >> /app/download_and_start.sh && \
    echo 'echo "📊 Available database files:"' >> /app/download_and_start.sh && \
    echo 'ls -lh /app/data/*.db 2>/dev/null || echo "No database files found"' >> /app/download_and_start.sh && \
    echo '' >> /app/download_and_start.sh && \
    echo '# Start the API server' >> /app/download_and_start.sh && \
    echo 'echo "🎯 Starting XTrillion-GA10 API server..."' >> /app/download_and_start.sh && \
    echo 'python3 google_analysis10_api.py' >> /app/download_and_start.sh && \
    chmod +x /app/download_and_start.sh

# Set environment variables
ENV PORT=8080
ENV PYTHONPATH="/app"
ENV ENVIRONMENT="production"
ENV GCS_BUCKET="json-receiver-databases"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Start with GCS download
CMD ["/app/download_and_start.sh"]
EOF

    print_status "GCS-enabled Dockerfile created ✅"
}

setup_secrets() {
    print_header "Setting up Podman secrets..."
    
    # Find credentials file
    CREDS_FILE=""
    if [ -f "./credentials.json" ]; then
        CREDS_FILE="./credentials.json"
    elif [ -f "../credentials.json" ]; then
        CREDS_FILE="../credentials.json"
    else
        print_error "credentials.json not found"
        exit 1
    fi
    
    print_status "Found credentials: $CREDS_FILE"
    
    # Remove existing secret if it exists
    podman secret rm ${SECRET_NAME} 2>/dev/null || true
    
    # Create new secret
    podman secret create ${SECRET_NAME} ${CREDS_FILE}
    print_status "Podman secret created: ${SECRET_NAME} ✅"
    
    # Verify secret exists
    print_status "Available secrets:"
    podman secret ls | grep -E "(NAME|${SECRET_NAME})"
}

build_image() {
    print_header "Building XTrillion-GA10 image..."
    
    # Create GCS-enabled Dockerfile
    create_gcs_dockerfile
    
    # Build the image
    print_status "Building image: ${IMAGE_NAME}"
    podman build -f Dockerfile.gcs -t ${IMAGE_NAME} .
    
    print_status "Image built successfully ✅"
}

deploy_container() {
    print_header "Deploying XTrillion-GA10 container..."
    
    # Stop and remove existing container if it exists
    if podman ps -a | grep -q ${CONTAINER_NAME}; then
        print_status "Stopping existing container..."
        podman stop ${CONTAINER_NAME} 2>/dev/null || true
        podman rm ${CONTAINER_NAME} 2>/dev/null || true
    fi
    
    # Run container with secret and GCS configuration
    print_status "Starting container with GCS database download..."
    podman run -d \
        --name ${CONTAINER_NAME} \
        --secret ${SECRET_NAME} \
        -p ${PORT}:8080 \
        -e GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/${SECRET_NAME} \
        -e GCS_BUCKET=${GCS_BUCKET} \
        -e ENVIRONMENT=production \
        ${IMAGE_NAME}
    
    if [ $? -eq 0 ]; then
        print_status "Container started successfully ✅"
        
        # Wait for startup
        print_status "Waiting for service to start..."
        sleep 10
        
        # Show status
        print_status "Container status:"
        podman ps | grep ${CONTAINER_NAME}
        
        print_status "Service URL: http://localhost:${PORT}"
        print_status "Health check: http://localhost:${PORT}/health"
        
    else
        print_error "Failed to start container ❌"
        print_error "Check logs with: $0 logs"
        exit 1
    fi
}

stop_container() {
    print_header "Stopping XTrillion-GA10..."
    
    if podman ps | grep -q ${CONTAINER_NAME}; then
        podman stop ${CONTAINER_NAME}
        podman rm ${CONTAINER_NAME}
        print_status "Container stopped and removed ✅"
    else
        print_warning "Container not running"
    fi
}

show_logs() {
    print_header "Container logs:"
    podman logs --tail 50 ${CONTAINER_NAME}
}

show_status() {
    print_header "XTrillion-GA10 Status:"
    
    # Container status
    if podman ps | grep -q ${CONTAINER_NAME}; then
        print_status "Container: Running ✅"
        podman ps | grep ${CONTAINER_NAME}
    else
        print_warning "Container: Not running"
    fi
    
    # Secret status
    if podman secret ls | grep -q ${SECRET_NAME}; then
        print_status "Secret: Available ✅"
    else
        print_warning "Secret: Not found"
    fi
    
    # Image status
    if podman image exists ${IMAGE_NAME}; then
        print_status "Image: Available ✅"
    else
        print_warning "Image: Not found"
    fi
}

test_service() {
    print_header "Testing XTrillion-GA10 service..."
    
    # Test health endpoint
    print_status "Testing health endpoint..."
    if curl -s http://localhost:${PORT}/health > /dev/null; then
        print_status "Health check: PASSED ✅"
        echo ""
        print_status "Full health response:"
        curl -s http://localhost:${PORT}/health | python3 -m json.tool
    else
        print_error "Health check: FAILED ❌"
        print_error "Service may not be running or still starting up"
    fi
}

# Main script logic
case "${1:-help}" in
    setup)
        check_requirements
        setup_secrets
        build_image
        ;;
    deploy)
        check_requirements
        deploy_container
        ;;
    stop)
        stop_container
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    rebuild)
        check_requirements
        stop_container
        build_image
        deploy_container
        ;;
    test)
        test_service
        ;;
    help|*)
        show_usage
        ;;
esac
