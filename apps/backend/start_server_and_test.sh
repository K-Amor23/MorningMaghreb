#!/bin/bash

# Start Server and Test Inventory Sync
# This script starts the FastAPI server and runs comprehensive tests

set -e  # Exit on any error

echo "🚀 Starting Server and Testing Inventory Sync"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the correct directory
if [ ! -f "main.py" ]; then
    print_error "Please run this script from the apps/backend directory"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required dependencies are installed
print_status "Checking dependencies..."
if ! python3 -c "import fastapi, uvicorn, httpx" 2>/dev/null; then
    print_warning "Some dependencies are missing. Installing..."
    pip install -r requirements.txt
fi

# Set environment variables if not already set
print_status "Setting up environment variables..."
export BC_TENANT_ID=${BC_TENANT_ID:-"test-tenant"}
export BC_ENVIRONMENT=${BC_ENVIRONMENT:-"sandbox"}
export BC_COMPANY_ID=${BC_COMPANY_ID:-"test-company"}
export BC_CLIENT_ID=${BC_CLIENT_ID:-"test-client"}
export BC_CLIENT_SECRET=${BC_CLIENT_SECRET:-"test-secret"}
export ZOHO_CLIENT_ID=${ZOHO_CLIENT_ID:-"test-client"}
export ZOHO_CLIENT_SECRET=${ZOHO_CLIENT_SECRET:-"test-secret"}
export ZOHO_REFRESH_TOKEN=${ZOHO_REFRESH_TOKEN:-"test-token"}

# Create a log directory
mkdir -p logs

# Function to cleanup background processes
cleanup() {
    print_status "Cleaning up..."
    if [ ! -z "$SERVER_PID" ]; then
        kill $SERVER_PID 2>/dev/null || true
        wait $SERVER_PID 2>/dev/null || true
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start the server in the background
print_status "Starting FastAPI server..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > logs/server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
print_status "Waiting for server to start..."
sleep 5

# Check if server is running
if ! kill -0 $SERVER_PID 2>/dev/null; then
    print_error "Server failed to start. Check logs/server.log for details."
    cat logs/server.log
    exit 1
fi

# Test server health
print_status "Testing server health..."
if curl -s http://localhost:8000/health > /dev/null; then
    print_status "✅ Server is healthy and responding"
else
    print_error "❌ Server is not responding"
    print_error "Server logs:"
    tail -20 logs/server.log
    cleanup
    exit 1
fi

# Show server info
print_status "Server is running at: http://localhost:8000"
print_status "API documentation: http://localhost:8000/docs"
print_status "Server PID: $SERVER_PID"

# Run the comprehensive test suite
print_status "Running comprehensive inventory sync tests..."
python3 test_inventory_sync.py

# Check test results
if [ $? -eq 0 ]; then
    print_status "✅ All tests completed successfully!"
else
    print_error "❌ Some tests failed. Check the logs for details."
fi

# Show test results
if [ -f "inventory_sync_audit_report.json" ]; then
    print_status "📊 Test Results Summary:"
    python3 -c "
import json
with open('inventory_sync_audit_report.json', 'r') as f:
    report = json.load(f)
    summary = report['audit_summary']
    print(f'  Total Tests: {summary[\"total_tests\"]}')
    print(f'  Passed: {summary[\"passed\"]}')
    print(f'  Failed: {summary[\"failed\"]}')
    print(f'  Warnings: {summary[\"warnings\"]}')
    print(f'  Success Rate: {summary[\"success_rate\"]:.1f}%')
    print(f'  Duration: {summary[\"duration_seconds\"]:.2f}s')
"
fi

# Show available endpoints
print_status "📋 Available Inventory Sync Endpoints:"
echo "  GET  /api/inventory/health                - Health check"
echo "  GET  /api/inventory/test-bc-connection    - Test Business Central"
echo "  GET  /api/inventory/test-zoho-connection  - Test Zoho"
echo "  POST /api/inventory/sync                  - Run inventory sync"
echo "  GET  /api/inventory/history               - Sync history"
echo "  GET  /api/inventory/logs                  - View logs"

# Interactive menu
echo
echo "🎯 What would you like to do next?"
echo "1) Run inventory sync manually"
echo "2) Test Business Central connection"
echo "3) Test Zoho connection"
echo "4) View server logs"
echo "5) Keep server running"
echo "6) Stop server and exit"

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        print_status "Running inventory sync..."
        curl -X POST http://localhost:8000/api/inventory/sync | python3 -m json.tool
        ;;
    2)
        print_status "Testing Business Central connection..."
        curl -s http://localhost:8000/api/inventory/test-bc-connection | python3 -m json.tool
        ;;
    3)
        print_status "Testing Zoho connection..."
        curl -s http://localhost:8000/api/inventory/test-zoho-connection | python3 -m json.tool
        ;;
    4)
        print_status "Server logs (last 50 lines):"
        tail -50 logs/server.log
        ;;
    5)
        print_status "Server will keep running. Press Ctrl+C to stop."
        print_status "Monitor logs with: tail -f logs/server.log"
        wait $SERVER_PID
        ;;
    6)
        print_status "Stopping server..."
        cleanup
        ;;
    *)
        print_warning "Invalid choice. Keeping server running."
        print_status "Press Ctrl+C to stop the server."
        wait $SERVER_PID
        ;;
esac

cleanup