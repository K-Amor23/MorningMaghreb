#!/bin/bash
# Daily Data Refresh Script for Casablanca Insights
# This script runs the Morocco financial data pipeline and CSE company updates

# Set the project directory
PROJECT_DIR="/Users/kamor/Casablanca-Insights-1"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/data_refresh_$(date +%Y%m%d_%H%M%S).log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Change to project directory
cd "$PROJECT_DIR" || exit 1

log "🚀 Starting daily data refresh"

# Load environment variables
if [ -f .env ]; then
    set -a
    source .env
    set +a
    log "✅ Environment variables loaded"
else
    log "❌ .env file not found"
    exit 1
fi

# Run Morocco financial data pipeline
log "📊 Running Morocco financial data pipeline..."
python apps/backend/etl/morocco_financial_data_pipeline.py >> "$LOG_FILE" 2>&1
if [ $? -eq 0 ]; then
    log "✅ Morocco financial data pipeline completed successfully"
else
    log "❌ Morocco financial data pipeline failed"
fi

# Run CSE company data refresh
log "🏢 Running CSE company data refresh..."
python apps/backend/etl/import_companies_with_service_role.py >> "$LOG_FILE" 2>&1
if [ $? -eq 0 ]; then
    log "✅ CSE company data refresh completed successfully"
else
    log "❌ CSE company data refresh failed"
fi

# Run Supabase data refresh if available
if [ -f "apps/backend/etl/supabase_data_refresh.py" ]; then
    log "🗄️ Running Supabase data refresh..."
    python apps/backend/etl/supabase_data_refresh.py >> "$LOG_FILE" 2>&1
    if [ $? -eq 0 ]; then
        log "✅ Supabase data refresh completed successfully"
    else
        log "❌ Supabase data refresh failed"
    fi
fi

# Clean up old log files (keep last 30 days)
find "$LOG_DIR" -name "data_refresh_*.log" -mtime +30 -delete

log "🎉 Daily data refresh completed"

# Optional: Send summary email or notification
# You can add email notification here if needed

exit 0 