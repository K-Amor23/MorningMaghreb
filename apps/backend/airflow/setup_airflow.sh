#!/bin/bash

echo "🚀 Setting up Airflow for Casablanca Insights ETL Pipeline..."
echo "🎯 Casablanca Insights Airflow Setup"
echo "====================================="
echo ""

# Check dependencies
echo "[INFO] Checking dependencies..."
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker is not installed or not running"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "[ERROR] Docker Compose is not installed"
    exit 1
fi

echo "[SUCCESS] Dependencies check passed"

# Create directories
echo "[INFO] Creating Airflow directories..."
mkdir -p dags logs plugins config

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cat > .env << EOF
AIRFLOW_UID=50000
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=admin
EOF
    echo "[SUCCESS] Created .env file"
else
    echo "[WARNING] .env file already exists"
fi

echo "[SUCCESS] Directories created"

# Set permissions (skip on non-Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "[INFO] Setting Airflow permissions..."
    sudo chown -R 50000:0 dags logs plugins config
    echo "[SUCCESS] Permissions set"
else
    echo "[WARNING] Skipping permission setting for non-Linux system"
fi

# Start services
echo "[INFO] Starting Airflow services..."
docker-compose up -d postgres redis

# Wait for postgres to be ready
echo "[INFO] Waiting for PostgreSQL to be ready..."
sleep 10

# Initialize Airflow database manually
echo "[INFO] Initializing Airflow database..."
docker-compose run --rm airflow-webserver airflow db init

# Create admin user
echo "[INFO] Creating admin user..."
docker-compose run --rm airflow-webserver airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@casablanca-insights.com \
    --password admin

# Start remaining services
echo "[INFO] Starting remaining services..."
docker-compose up -d

echo ""
echo "🎉 Airflow setup completed successfully!"
echo ""
echo "📊 Access Points:"
echo "   • Airflow Web UI: http://localhost:8080"
echo "   • Username: admin"
echo "   • Password: admin"
echo "   • Flower (Celery Monitor): http://localhost:5555"
echo "   • Casablanca API: http://localhost:8000"
echo ""
echo "📁 DAG Location: ./dags/"
echo "📋 Logs Location: ./logs/"
echo ""
echo "🔧 Next Steps:"
echo "   1. Access the Airflow UI at http://localhost:8080"
echo "   2. The casablanca_etl_dag should be visible in the DAGs list"
echo "   3. Enable the DAG and trigger it manually for testing"
echo "   4. Monitor execution in the Airflow UI"
echo ""
echo "📚 For more information, see AIRFLOW_DEPLOYMENT_GUIDE.md" 