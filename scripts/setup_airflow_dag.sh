#!/bin/bash
# Setup Airflow DAG and Connections
# This script configures Airflow with the master DAG and required connections

set -e

echo "🛫 Setting up Airflow DAG and Connections"
echo "=========================================="

# Check if .env.local exists for connection details
if [ ! -f ".env.local" ]; then
    echo "❌ .env.local not found. Please create it first with your connection details."
    exit 1
fi

# Load environment variables
source .env.local

echo "📋 Required environment variables:"
echo "  - SUPABASE_URL"
echo "  - SUPABASE_SERVICE_KEY"
echo "  - SLACK_WEBHOOK_URL (optional)"
echo "  - SMTP_HOST (optional)"
echo "  - SMTP_PORT (optional)"
echo "  - SMTP_USER (optional)"
echo "  - SMTP_PASSWORD (optional)"
echo ""

# Check if required variables are set
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_SERVICE_ROLE_KEY" ]; then
    echo "❌ Missing required environment variables."
    echo "Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env.local"
    exit 1
fi

echo "✅ Environment variables loaded successfully!"
echo ""

# Extract database connection details from Supabase URL
# Format: postgresql://postgres:[password]@[host]:5432/postgres
DB_HOST=$(echo "$SUPABASE_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_PASSWORD=$(echo "$SUPABASE_URL" | sed -n 's/.*postgres:\([^@]*\)@.*/\1/p')

if [ -z "$DB_HOST" ] || [ -z "$DB_PASSWORD" ]; then
    echo "⚠️  Could not parse Supabase URL. Please set up connections manually."
    echo ""
    echo "Manual setup instructions:"
    echo "1. Copy airflow/dags/master_dag.py to your Airflow dags/ folder"
    echo "2. Add Supabase connection in Airflow UI:"
    echo "   - Connection Id: supabase_default"
    echo "   - Connection Type: PostgreSQL"
    echo "   - Host: [your-supabase-host]"
    echo "   - Schema: postgres"
    echo "   - Login: postgres"
    echo "   - Password: [your-supabase-password]"
    echo "   - Port: 5432"
    echo ""
    echo "3. Add Variables:"
    echo "   - SUPABASE_URL: $SUPABASE_URL"
    echo "   - SUPABASE_SERVICE_KEY: [your-service-key]"
    if [ ! -z "$SLACK_WEBHOOK_URL" ]; then
        echo "   - SLACK_WEBHOOK_URL: $SLACK_WEBHOOK_URL"
    fi
    exit 0
fi

echo "🔗 Setting up Airflow connections..."

# Create Supabase connection
echo "Adding Supabase connection..."
airflow connections add supabase_default \
    --conn-type postgresql \
    --conn-host "$DB_HOST" \
    --conn-schema postgres \
    --conn-login postgres \
    --conn-password "$DB_PASSWORD" \
    --conn-port 5432

echo "✅ Supabase connection added!"

# Add variables
echo "Adding Airflow variables..."
airflow variables set SUPABASE_URL "$SUPABASE_URL"
airflow variables set SUPABASE_SERVICE_ROLE_KEY "$SUPABASE_SERVICE_ROLE_KEY"

if [ ! -z "$SLACK_WEBHOOK_URL" ]; then
    airflow variables set SLACK_WEBHOOK_URL "$SLACK_WEBHOOK_URL"
    echo "✅ Slack webhook URL added!"
fi

if [ ! -z "$SMTP_HOST" ]; then
    airflow variables set SMTP_HOST "$SMTP_HOST"
    airflow variables set SMTP_PORT "$SMTP_PORT"
    airflow variables set SMTP_USER "$SMTP_USER"
    airflow variables set SMTP_PASSWORD "$SMTP_PASSWORD"
    echo "✅ SMTP settings added!"
fi

echo "✅ All variables added!"
echo ""

echo "📁 Copying DAG to Airflow..."
# This assumes Airflow is installed locally or you have access to the dags folder
DAG_SOURCE="airflow/dags/master_dag.py"
DAG_DEST="$HOME/airflow/dags/master_dag.py"  # Adjust path as needed

if [ -f "$DAG_SOURCE" ]; then
    mkdir -p "$(dirname "$DAG_DEST")"
    cp "$DAG_SOURCE" "$DAG_DEST"
    echo "✅ DAG copied to $DAG_DEST"
else
    echo "⚠️  DAG file not found at $DAG_SOURCE"
    echo "Please copy airflow/dags/master_dag.py to your Airflow dags/ folder manually"
fi

echo ""
echo "🔄 Restarting Airflow services..."
echo "Please run these commands on your Airflow server:"
echo "  systemctl restart airflow-scheduler"
echo "  systemctl restart airflow-webserver"
echo ""
echo "🔍 To verify setup:"
echo "1. Open Airflow UI"
echo "2. Check Connections tab for 'supabase_default'"
echo "3. Check Variables tab for Supabase settings"
echo "4. Look for 'master_dag' in DAGs list"
echo "5. Trigger a manual run to test"
echo ""
echo "✅ Airflow setup complete!" 