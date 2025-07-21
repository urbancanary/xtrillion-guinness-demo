#!/bin/bash
# Google Analysis 10 Environment Manager & Deployment Script
# XTrillion-GA10 Bond Analytics Service Deployment
# Based on project structure analysis

set -e  # Exit on any error

# Configuration
PROJECT_ID="future-footing-414610"
SERVICE_NAME="xtrillion-ga10"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
PORT="8080"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[XTRILLION-GA10]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND] [ENVIRONMENT]"
    echo ""
    echo "Commands:"
    echo "  setup                 - Setup local development environment"
    echo "  local                 - Run local development server"
    echo "  build                 - Build Docker image"
    echo "  test                  - Test Docker image locally"
    echo "  deploy [env]          - Deploy to specified environment"
    echo ""
    echo "Environments:"
    echo "  dev                   - Development environment"
    echo "  staging               - Staging environment"
    echo "  prod                  - Production environment"
    echo ""
    echo "Examples:"
    echo "  $0 setup"
    echo "  $0 local"
    echo "  $0 deploy prod"
}

# Function to check prerequisites
check_prerequisites() {
    print_header "Checking prerequisites..."
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed. Please install Google Cloud SDK."
        exit 1
    fi
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker."
        exit 1
    fi
    
    # Check if required files exist
    if [ ! -f "Dockerfile" ]; then
        print_error "Dockerfile not found in current directory"
        exit 1
    fi
    
    if [ ! -f "google_analysis10_api.py" ]; then
        print_error "google_analysis10_api.py not found"
        exit 1
    fi
    
    print_status "Prerequisites check passed ✅"
}

# Function to setup local environment
setup_local() {
    print_header "Setting up local development environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install requirements
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    print_status "Local environment setup complete ✅"
}

# Function to run local development server
run_local() {
    print_header "Starting local development server..."
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Set environment variables
    export ENVIRONMENT="development"
    export PORT="8080"
    export DATABASE_SOURCE="embedded"
    
    print_status "Starting XTrillion-GA10 API on http://localhost:8080"
    python3 google_analysis10_api.py
}

# Function to build Docker image
build_docker() {
    print_header "Building Docker image..."
    
    # Build the Docker image
    print_status "Building ${IMAGE_NAME}:latest..."
    docker build -t ${IMAGE_NAME}:latest .
    
    print_status "Docker image built successfully ✅"
}

# Function to test Docker image locally
test_docker() {
    print_header "Testing Docker image locally..."
    
    # Stop any existing container
    docker stop ${SERVICE_NAME}-test 2>/dev/null || true
    docker rm ${SERVICE_NAME}-test 2>/dev/null || true
    
    # Run the container locally
    print_status "Starting test container on http://localhost:8081..."
    docker run -d --name ${SERVICE_NAME}-test -p 8081:8080 ${IMAGE_NAME}:latest
    
    # Wait for container to start
    sleep 5
    
    # Test health endpoint
    if curl -s http://localhost:8081/health > /dev/null; then
        print_status "Docker container test passed ✅"
        print_status "You can test the API at: http://localhost:8081"
        print_status "To stop test container: docker stop ${SERVICE_NAME}-test"
    else
        print_error "Docker container test failed ❌"
        docker logs ${SERVICE_NAME}-test
        exit 1
    fi
}

# Function to deploy to different environments
deploy_environment() {
    local environment=$1
    
    case $environment in
        dev)
            PROJECT_ID="future-footing-414610"
            SERVICE_NAME="xtrillion-ga10-dev"
            ;;
        staging)
            PROJECT_ID="future-footing-414610"
            SERVICE_NAME="xtrillion-ga10-staging"
            ;;
        prod)
            PROJECT_ID="future-footing-414610"
            SERVICE_NAME="xtrillion-ga10"
            ;;
        *)
            print_error "Unknown environment: $environment"
            print_error "Valid environments: dev, staging, prod"
            exit 1
            ;;
    esac
    
    IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
    
    print_header "Deploying to $environment environment..."
    print_status "Project: $PROJECT_ID"
    print_status "Service: $SERVICE_NAME"
    print_status "Image: $IMAGE_NAME"
    
    # Check prerequisites
    check_prerequisites
    
    # Authenticate with gcloud (if not already done)
    print_status "Checking Google Cloud authentication..."
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_warning "No active Google Cloud authentication found. Please authenticate:"
        gcloud auth login
    fi
    
    # Set the project
    print_status "Setting Google Cloud project: ${PROJECT_ID}"
    gcloud config set project ${PROJECT_ID}
    
    # Enable required APIs
    print_status "Enabling required Google Cloud APIs..."
    gcloud services enable run.googleapis.com
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable containerregistry.googleapis.com
    
    # Build and push to Google Container Registry
    print_status "Building and pushing to Google Container Registry..."
    print_status "🔨 Using CLOUD-ONLY Dockerfile (no embedded databases)"
    print_status "📦 Will download FRESH databases from GCS at runtime"
    gcloud builds submit --config=cloudbuild.yaml --substitutions=_IMAGE_NAME=${IMAGE_NAME} --timeout=20m .
    
    # Deploy to Cloud Run
    print_status "Deploying to Cloud Run..."
    gcloud run deploy ${SERVICE_NAME} \
        --image ${IMAGE_NAME}:latest \
        --platform managed \
        --region ${REGION} \
        --allow-unauthenticated \
        --port ${PORT} \
        --memory 2Gi \
        --cpu 1 \
        --max-instances 10 \
        --set-env-vars="ENVIRONMENT=${environment},DATABASE_SOURCE=gcs" \
        --timeout=300
    
    # Get the service URL
    SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format='value(status.url)')
    
    print_status "Deployment complete! ✅"
    print_status "Service URL: ${SERVICE_URL}"
    print_status "Health check: ${SERVICE_URL}/health"
    
    # Test the deployed service
    print_status "Testing deployed service..."
    if curl -s "${SERVICE_URL}/health" > /dev/null; then
        print_status "Deployment health check passed ✅"
    else
        print_warning "Deployment health check failed ⚠️"
        print_warning "Service may still be starting up. Check Cloud Run logs."
    fi
}

# Function to check database files
check_databases() {
    print_header "Checking database files..."
    
    # Check in root directory first, then data directory
    for db_file in "bonds_data.db" "validated_quantlib_bonds.db"; do
        if [ -f "$db_file" ]; then
            size=$(stat -f%z "$db_file" 2>/dev/null || stat -c%s "$db_file" 2>/dev/null)
            print_status "$db_file found in root (${size} bytes)"
        elif [ -f "data/$db_file" ]; then
            size=$(stat -f%z "data/$db_file" 2>/dev/null || stat -c%s "data/$db_file" 2>/dev/null)
            print_status "$db_file found in data/ (${size} bytes)"
        else
            print_warning "$db_file not found in root or data/ directory"
        fi
    done
}

# Main script logic
main() {
    if [ $# -eq 0 ]; then
        show_usage
        exit 1
    fi
    
    local command=$1
    local environment=${2:-"prod"}
    
    case $command in
        setup)
            check_prerequisites
            setup_local
            ;;
        local)
            check_databases
            run_local
            ;;
        build)
            check_prerequisites
            check_databases
            build_docker
            ;;
        test)
            check_prerequisites
            build_docker
            test_docker
            ;;
        deploy)
            check_databases
            deploy_environment $environment
            ;;
        *)
            print_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
