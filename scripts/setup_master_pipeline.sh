#!/bin/bash

# Master Pipeline Setup Script for Casablanca Insights
# This script sets up the complete data pipeline with Airflow and Supabase

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    error "Please run this script from the project root directory"
    exit 1
fi

log "🚀 Starting Master Pipeline Setup for Casablanca Insights"

# Step 1: Check environment variables
log "📋 Checking environment variables..."

if [ -z "$NEXT_PUBLIC_SUPABASE_URL" ]; then
    error "NEXT_PUBLIC_SUPABASE_URL environment variable is not set"
    exit 1
fi

if [ -z "$SUPABASE_SERVICE_ROLE_KEY" ]; then
    error "SUPABASE_SERVICE_ROLE_KEY environment variable is not set"
    exit 1
fi

log "✅ Environment variables are set"

# Step 2: Install Python dependencies
log "📦 Installing Python dependencies..."

cd apps/backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    log "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

log "✅ Python dependencies installed"

# Step 3: Deploy database tables to Supabase
log "🗄️ Deploying database tables to Supabase..."

cd ../..

# Run the database deployment script
python scripts/deploy_master_pipeline_tables.py

if [ $? -eq 0 ]; then
    log "✅ Database tables deployed successfully"
else
    error "Failed to deploy database tables"
    exit 1
fi

# Step 4: Set up Airflow
log "⚙️ Setting up Airflow..."

cd apps/backend/airflow

# Check if Airflow is already initialized
if [ ! -d "logs" ]; then
    log "Initializing Airflow database..."
    airflow db init
fi

# Create Airflow user if it doesn't exist
log "Creating Airflow admin user..."
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@casablancainsights.com \
    --password admin123

# Step 5: Start Airflow services
log "🚀 Starting Airflow services..."

# Start Airflow webserver in background
log "Starting Airflow webserver..."
airflow webserver --port 8080 --daemon

# Start Airflow scheduler in background
log "Starting Airflow scheduler..."
airflow scheduler --daemon

# Wait a moment for services to start
sleep 5

# Check if services are running
if pgrep -f "airflow webserver" > /dev/null; then
    log "✅ Airflow webserver is running"
else
    error "Airflow webserver failed to start"
    exit 1
fi

if pgrep -f "airflow scheduler" > /dev/null; then
    log "✅ Airflow scheduler is running"
else
    error "Airflow scheduler failed to start"
    exit 1
fi

# Step 6: Deploy the master DAG
log "📋 Deploying master data pipeline DAG..."

# Copy the master DAG to Airflow dags directory
cp dags/master_data_pipeline_dag.py ~/airflow/dags/

# Wait for DAG to be loaded
sleep 10

# Check if DAG is loaded
if airflow dags list | grep -q "master_data_pipeline"; then
    log "✅ Master data pipeline DAG deployed successfully"
else
    error "Failed to deploy master data pipeline DAG"
    exit 1
fi

# Step 7: Test the pipeline
log "🧪 Testing the pipeline..."

# Trigger a test run of the master DAG
airflow dags trigger master_data_pipeline

log "✅ Test run triggered successfully"

# Step 8: Set up monitoring
log "📊 Setting up monitoring..."

# Create monitoring directory
mkdir -p monitoring

# Create health check script
cat > monitoring/health_check.sh << 'EOF'
#!/bin/bash

# Health check for Airflow services
if ! pgrep -f "airflow webserver" > /dev/null; then
    echo "ERROR: Airflow webserver is not running"
    exit 1
fi

if ! pgrep -f "airflow scheduler" > /dev/null; then
    echo "ERROR: Airflow scheduler is not running"
    exit 1
fi

echo "OK: All Airflow services are running"
EOF

chmod +x monitoring/health_check.sh

# Step 9: Create startup script
log "📝 Creating startup script..."

cat > start_master_pipeline.sh << 'EOF'
#!/bin/bash

# Start Master Pipeline Script
cd "$(dirname "$0")/apps/backend/airflow"

# Activate virtual environment
source ../venv/bin/activate

# Start Airflow services
echo "Starting Airflow webserver..."
airflow webserver --port 8080 --daemon

echo "Starting Airflow scheduler..."
airflow scheduler --daemon

echo "Master pipeline started successfully!"
echo "Airflow UI: http://localhost:8080"
echo "Username: admin"
echo "Password: admin123"
EOF

chmod +x start_master_pipeline.sh

# Step 10: Create stop script
log "📝 Creating stop script..."

cat > stop_master_pipeline.sh << 'EOF'
#!/bin/bash

# Stop Master Pipeline Script
echo "Stopping Airflow services..."

# Kill Airflow processes
pkill -f "airflow webserver" || true
pkill -f "airflow scheduler" || true

echo "Master pipeline stopped successfully!"
EOF

chmod +x stop_master_pipeline.sh

# Step 11: Final status check
log "🔍 Performing final status check..."

# Check if everything is working
if ./monitoring/health_check.sh; then
    log "✅ All services are running correctly"
else
    error "Some services are not running correctly"
    exit 1
fi

# Summary
log "🎉 Master Pipeline Setup Completed Successfully!"
echo ""
log "📊 Setup Summary:"
echo "   ✅ Database tables deployed to Supabase"
echo "   ✅ Airflow services started"
echo "   ✅ Master data pipeline DAG deployed"
echo "   ✅ Monitoring scripts created"
echo "   ✅ Startup/stop scripts created"
echo ""
log "🔗 Access Points:"
echo "   • Airflow UI: http://localhost:8080"
echo "   • Username: admin"
echo "   • Password: admin123"
echo "   • Website: https://morningmaghreb.com"
echo ""
log "📋 Next Steps:"
echo "   • The master pipeline will run daily at 6:00 AM UTC"
echo "   • Data will be automatically scraped and stored in Supabase"
echo "   • Your website will have access to real-time market data"
echo "   • Monitor the pipeline through Airflow UI"
echo ""
log "🛠️ Management Commands:"
echo "   • Start pipeline: ./start_master_pipeline.sh"
echo "   • Stop pipeline: ./stop_master_pipeline.sh"
echo "   • Health check: ./monitoring/health_check.sh"
echo ""

# Return to project root
cd ../..

log "Setup completed! Your master data pipeline is ready to go! 🚀" 