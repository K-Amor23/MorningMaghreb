#!/bin/bash

# 🚀 Simple Casablanca Insights Startup Script
# This script starts both frontend and backend servers

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting Casablanca Insights...${NC}"

# Load environment variables
if [ -f ".env" ]; then
    echo -e "${BLUE}📋 Loading environment variables...${NC}"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
fi

# Function to kill processes on ports
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}🔄 Killing process on port $port${NC}"
        kill -9 $pid 2>/dev/null || true
        sleep 2
    fi
}

# Kill existing processes
kill_port 8000
kill_port 3000

# Start backend
echo -e "${BLUE}🐍 Starting backend server...${NC}"
cd apps/backend
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ../..

# Wait for backend
sleep 5

# Start frontend
echo -e "${BLUE}⚛️  Starting frontend server...${NC}"
cd apps/web
npm run dev &
FRONTEND_PID=$!
cd ../..

# Wait for frontend
sleep 10

# Show status
echo -e "${GREEN}✅ Servers started!${NC}"
echo ""
echo -e "${BLUE}📊 Server Status:${NC}"
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"

# Function to cleanup
cleanup() {
    echo -e "${YELLOW}🛑 Stopping servers...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Servers stopped${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Keep script running
wait 