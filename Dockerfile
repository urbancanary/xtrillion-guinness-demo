FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install Google Cloud SDK for database downloads
RUN curl https://sdk.cloud.google.com | bash && \
    /root/google-cloud-sdk/install.sh --quiet && \
    /root/google-cloud-sdk/bin/gcloud components update

# Add gcloud to PATH
ENV PATH="/root/google-cloud-sdk/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files (including databases for embedded deployment)
COPY . .
RUN rm -rf archive/ __pycache__/ *.log test_*.py debug_*.py

# Ensure databases are present for embedded deployment
RUN ls -la bonds_data.db validated_quantlib_bonds.db || echo "Warning: Database files missing"

# Create data directory for potential database downloads
RUN mkdir -p /app/data

# Make database download script executable (if needed)
RUN [ -f "download_databases_from_gcs.sh" ] && chmod +x download_databases_from_gcs.sh || echo "Download script not found"

# Set environment variables for XTrillion-GA10
ENV PORT=8080
ENV PYTHONPATH="/app"
ENV DATA_DIR="/app/data"
ENV SERVICE_NAME="xtrillion-ga10"
ENV ENVIRONMENT="production"
ENV DATABASE_SOURCE="gcs"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Create XTrillion-GA10 startup script
RUN echo '#!/bin/bash' > /app/startup.sh && \
    echo 'set -e' >> /app/startup.sh && \
    echo 'echo "🚀 Starting XTrillion-GA10 Bond Analytics Service..."' >> /app/startup.sh && \
    echo 'echo "📊 Service: xtrillion-ga10"' >> /app/startup.sh && \
    echo 'echo "🌐 Environment: $ENVIRONMENT"' >> /app/startup.sh && \
    echo 'echo "💾 Database Source: $DATABASE_SOURCE"' >> /app/startup.sh && \
    echo 'echo ""' >> /app/startup.sh && \
    echo '# Check database source and handle accordingly' >> /app/startup.sh && \
    echo 'if [ "$DATABASE_SOURCE" = "local_copy" ]; then' >> /app/startup.sh && \
    echo '    echo "⏳ Waiting for local databases to be copied..."' >> /app/startup.sh && \
    echo '    for i in {1..60}; do' >> /app/startup.sh && \
    echo '        if [ -f "bonds_data.db" ] && [ -f "validated_quantlib_bonds.db" ] && [ -f "bloomberg_index.db" ]; then' >> /app/startup.sh && \
    echo '            echo "✅ All databases found after ${i} seconds"' >> /app/startup.sh && \
    echo '            export DATABASE_PATH="/app/bonds_data.db"' >> /app/startup.sh && \
    echo '            export VALIDATED_DB_PATH="/app/validated_quantlib_bonds.db"' >> /app/startup.sh && \
    echo '            export BLOOMBERG_DB_PATH="/app/bloomberg_index.db"' >> /app/startup.sh && \
    echo '            break' >> /app/startup.sh && \
    echo '        fi' >> /app/startup.sh && \
    echo '        echo "   Waiting... ($i/60)"' >> /app/startup.sh && \
    echo '        sleep 1' >> /app/startup.sh && \
    echo '    done' >> /app/startup.sh && \
    echo '    if [ ! -f "bonds_data.db" ]; then' >> /app/startup.sh && \
    echo '        echo "❌ Timeout waiting for databases to be copied"' >> /app/startup.sh && \
    echo '        exit 1' >> /app/startup.sh && \
    echo '    fi' >> /app/startup.sh && \
    echo '# Check if databases exist locally (embedded deployment)' >> /app/startup.sh && \
    echo 'elif [ -f "bonds_data.db" ] && [ -f "validated_quantlib_bonds.db" ]; then' >> /app/startup.sh && \
    echo '    echo "✅ Using embedded databases"' >> /app/startup.sh && \
    echo '    export DATABASE_PATH="/app/bonds_data.db"' >> /app/startup.sh && \
    echo '    export VALIDATED_DB_PATH="/app/validated_quantlib_bonds.db"' >> /app/startup.sh && \
    echo 'elif [ -f "download_databases_from_gcs.sh" ]; then' >> /app/startup.sh && \
    echo '    echo "🔽 Downloading databases from GCS..."' >> /app/startup.sh && \
    echo '    ./download_databases_from_gcs.sh' >> /app/startup.sh && \
    echo '    export DATABASE_PATH="/app/bonds_data.db"' >> /app/startup.sh && \
    echo '    export VALIDATED_DB_PATH="/app/validated_quantlib_bonds.db"' >> /app/startup.sh && \
    echo 'else' >> /app/startup.sh && \
    echo '    echo "❌ No databases found and no download script available"' >> /app/startup.sh && \
    echo '    exit 1' >> /app/startup.sh && \
    echo 'fi' >> /app/startup.sh && \
    echo 'echo ""' >> /app/startup.sh && \
    echo 'echo "🎯 Starting XTrillion-GA10 API server..."' >> /app/startup.sh && \
    echo 'python3 google_analysis10_api.py' >> /app/startup.sh && \
    chmod +x /app/startup.sh

# Start XTrillion-GA10 service
CMD ["/app/startup.sh"]
