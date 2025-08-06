#!/bin/bash

# Master Pipeline Deployment Script
# This script sets up the complete data pipeline for Casablanca Insights

echo "🚀 Deploying Master Pipeline for Casablanca Insights"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Step 1: Deploy database tables to Supabase
echo ""
echo "📊 Step 1: Deploying database tables to Supabase..."
python scripts/deploy_master_pipeline_tables.py

if [ $? -eq 0 ]; then
    echo "✅ Database tables deployed successfully"
else
    echo "❌ Failed to deploy database tables"
    exit 1
fi

# Step 2: Set up Airflow (if not already running)
echo ""
echo "⚙️ Step 2: Setting up Airflow..."

cd apps/backend/airflow

# Check if Airflow is already running
if pgrep -f "airflow webserver" > /dev/null && pgrep -f "airflow scheduler" > /dev/null; then
    echo "✅ Airflow is already running"
else
    echo "Starting Airflow services..."
    
    # Initialize Airflow if needed
    if [ ! -d "logs" ]; then
        echo "Initializing Airflow database..."
        airflow db init
    fi
    
    # Start Airflow services
    airflow webserver --port 8080 --daemon
    airflow scheduler --daemon
    
    echo "✅ Airflow services started"
fi

# Step 3: Deploy the master DAG
echo ""
echo "📋 Step 3: Deploying master data pipeline DAG..."

# Copy the master DAG to Airflow dags directory
cp dags/master_data_pipeline_dag.py ~/airflow/dags/

# Wait for DAG to be loaded
sleep 5

# Check if DAG is loaded
if airflow dags list | grep -q "master_data_pipeline"; then
    echo "✅ Master data pipeline DAG deployed successfully"
else
    echo "❌ Failed to deploy master data pipeline DAG"
    exit 1
fi

# Step 4: Test the pipeline
echo ""
echo "🧪 Step 4: Testing the pipeline..."

# Trigger a test run of the master DAG
airflow dags trigger master_data_pipeline

echo "✅ Test run triggered successfully"

# Return to project root
cd ../..

# Summary
echo ""
echo "🎉 Master Pipeline Deployment Completed Successfully!"
echo "=================================================="
echo ""
echo "📊 What was deployed:"
echo "   ✅ Database tables in Supabase"
echo "   ✅ Airflow services"
echo "   ✅ Master data pipeline DAG"
echo "   ✅ Sample data for testing"
echo ""
echo "🔗 Access Points:"
echo "   • Airflow UI: http://localhost:8080"
echo "   • Username: admin"
echo "   • Password: admin123"
echo "   • Website: https://morningmaghreb.com"
echo ""
echo "📋 Pipeline Schedule:"
echo "   • Runs daily at 6:00 AM UTC"
echo "   • Scrapes market data from multiple sources"
echo "   • Stores data in Supabase"
echo "   • Sends notifications on success/failure"
echo ""
echo "🛠️ Management Commands:"
echo "   • Start Airflow: cd apps/backend/airflow && airflow webserver --port 8080"
echo "   • Stop Airflow: pkill -f airflow"
echo "   • View DAGs: http://localhost:8080"
echo ""
echo "Your master data pipeline is now ready! 🚀" 