#!/bin/bash

# Morning Maghreb Airflow Local Production Setup
# This script sets up Airflow locally without Docker

set -e

echo "🚀 Starting Morning Maghreb Airflow Local Production..."
echo "======================================================"

# Navigate to Airflow directory (robust to spaces)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
AIRFLOW_DIR="$PROJECT_ROOT/apps/backend/airflow"
cd "$AIRFLOW_DIR"

# Check if Python and pip are available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Set PATH to include user's Python bin directory
export PATH="/Users/karimamor/Library/Python/3.9/bin:$PATH"

# Install Airflow if not already installed
echo "📦 Installing Airflow..."
python3 -m pip install apache-airflow==2.7.1

# Load project .env.local for Supabase values (if present)
ENV_LOCAL="$PROJECT_ROOT/../.env.local"
if [ ! -f "$ENV_LOCAL" ]; then
  # Try project root as fallback
  ENV_LOCAL="$PROJECT_ROOT/.env.local"
fi

if [ -f "$ENV_LOCAL" ]; then
  echo "🔑 Loading Supabase config from: $ENV_LOCAL"
  # shellcheck disable=SC2046
  export $(grep -E '^(NEXT_PUBLIC_SUPABASE_URL|NEXT_PUBLIC_SUPABASE_ANON_KEY|SUPABASE_SERVICE_ROLE_KEY)=' "$ENV_LOCAL" | xargs)
else
  echo "⚠️  .env.local not found. Ensure Supabase env vars are exported in your shell."
fi

# Create environment file for Airflow, sourcing Supabase from env
cat > .env << EOF
# Airflow Environment
AIRFLOW_UID=50000
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=admin

# Logging
AIRFLOW__LOGGING__LOGGING_LEVEL=INFO
AIRFLOW__LOGGING__FAB_LOGGING_LEVEL=WARN

# Environment
ENVIRONMENT=production
AIRFLOW_ENV=production

# Supabase (from env)
NEXT_PUBLIC_SUPABASE_URL=${NEXT_PUBLIC_SUPABASE_URL}
NEXT_PUBLIC_SUPABASE_ANON_KEY=${NEXT_PUBLIC_SUPABASE_ANON_KEY}
SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}

# ETL Configuration
ETL_COMPANIES=["ATW","IAM","BCP","BMCE","CIH","WAA","CMT","SID"]
ETL_BATCH_SIZE=10
ETL_MAX_RETRIES=3
ETL_SCHEDULE_INTERVAL=0 6 * * *
EOF

echo "✅ Environment file created (Supabase pulled from .env.local/env)"

echo "📊 DAG files unchanged; DAGs read Supabase from env at runtime"

# Set Airflow home
export AIRFLOW_HOME=$(pwd)

# Initialize Airflow database
echo "🗄️ Initializing Airflow database..."
airflow db init

# Create admin user
echo "👤 Creating admin user..."
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@morningmaghreb.com \
    --password admin

# Set Airflow variables
echo "⚙️ Setting Airflow variables..."
airflow variables set ETL_COMPANIES '["ATW","IAM","BCP","BMCE","CIH","WAA","CMT","SID"]'
airflow variables set ETL_BATCH_SIZE 10
airflow variables set ETL_MAX_RETRIES 3
airflow variables set ENVIRONMENT production
airflow variables set SUPABASE_URL "$NEXT_PUBLIC_SUPABASE_URL"
airflow variables set SUPABASE_ANON_KEY "$NEXT_PUBLIC_SUPABASE_ANON_KEY"
airflow variables set SUPABASE_SERVICE_KEY "$SUPABASE_SERVICE_ROLE_KEY"

echo "✅ Airflow variables configured"

# Start Airflow webserver in background
echo "🌐 Starting Airflow webserver..."
airflow webserver --port 8080 --daemon

# Start Airflow scheduler in background
echo "⏰ Starting Airflow scheduler..."
airflow scheduler --daemon

echo "⏳ Waiting for Airflow to start..."
sleep 10

# Check if Airflow is running
if curl -s http://localhost:8080 > /dev/null; then
    echo "✅ Airflow is running successfully!"
else
    echo "⚠️ Airflow might still be starting up..."
fi

echo ""
echo "🎉 AIRFLOW LOCAL PRODUCTION DEPLOYMENT COMPLETE"
echo "==============================================="
echo "📍 Airflow UI: http://localhost:8080"
echo "👤 Username: admin"
echo "🔑 Password: admin"
echo "🗄️ Database: https://gzsgehciddnrssuqxtsj.supabase.co"
echo "⏰ Schedule: Daily at 6:00 AM UTC"
echo "📊 DAGs: casablanca_etl_dag, live_quotes_dag, smart_ir_scraping_dag"
echo "==============================================="
echo "🚀 Your automated data collection is now running!"
echo "==============================================="

echo ""
echo "📋 Next Steps:"
echo "1. Open http://localhost:8080 in your browser"
echo "2. Login with admin/admin"
echo "3. Go to DAGs tab to see your pipelines"
echo "4. Enable the DAGs you want to run automatically"
echo "5. Monitor the runs in the Airflow UI"

echo ""
echo "🛠️ Useful Commands:"
echo "- View webserver logs: tail -f ~/airflow/logs/scheduler/latest/*.log"
echo "- View scheduler logs: tail -f ~/airflow/logs/webserver/latest/*.log"
echo "- Stop Airflow: pkill -f airflow"
echo "- Restart Airflow: ./scripts/start_airflow_local.sh"

echo ""
echo "📝 Note: Airflow is running in the background."
echo "To stop it, run: pkill -f airflow" 