#!/bin/bash

# 🚀 Casablanca Insights - One-Step Server Startup Script
# This script starts both the frontend and backend servers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        print_warning "Killing process on port $port (PID: $pid)"
        kill -9 $pid 2>/dev/null || true
        sleep 2
    fi
}

# Function to install backend dependencies
install_backend_deps() {
    print_status "Installing backend dependencies..."
    
    # Install essential packages first
    python3 -m pip install fastapi uvicorn python-dotenv --quiet
    
    # Install additional required packages
    python3 -m pip install openai supabase stripe sendgrid --quiet
    
    # Install other dependencies from requirements.txt
    if [ -f "requirements.txt" ]; then
        print_status "Installing remaining dependencies from requirements.txt..."
        python3 -m pip install -r requirements.txt --quiet
    fi
    
    print_success "Backend dependencies installed"
}

# Function to start backend server
start_backend() {
    print_status "Starting backend server..."
    
    # Check if Python3 is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 is not installed or not in PATH"
        return 1
    fi
    
    # Navigate to backend directory
    cd apps/backend
    
    # Install backend dependencies if needed
    if ! python3 -c "import fastapi, openai, supabase" 2>/dev/null; then
        install_backend_deps
    fi
    
    # Kill any existing process on port 8000
    kill_port 8000
    
    # Start backend server
    print_status "Starting FastAPI server on http://localhost:8000"
    python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    # Wait for backend to start
    sleep 8
    
    # Test backend health
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        print_success "Backend server is running on http://localhost:8000"
    else
        print_warning "Backend server may not be fully ready yet - checking for errors..."
        # Check if the process is still running
        if kill -0 $BACKEND_PID 2>/dev/null; then
            print_warning "Backend process is running but health check failed"
        else
            print_error "Backend process failed to start"
            return 1
        fi
    fi
    
    cd ../..
}

# Function to install frontend dependencies
install_frontend_deps() {
    print_status "Installing frontend dependencies..."
    
    # Install dependencies with progress
    npm install --progress=false
    
    print_success "Frontend dependencies installed"
}

# Function to start frontend server
start_frontend() {
    print_status "Starting frontend server..."
    
    # Check if Node.js is available
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed or not in PATH"
        return 1
    fi
    
    # Check if npm is available
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed or not in PATH"
        return 1
    fi
    
    # Navigate to frontend directory
    cd apps/web
    
    # Install frontend dependencies if needed
    if [ ! -d "node_modules" ]; then
        install_frontend_deps
    fi
    
    # Kill any existing process on port 3000
    kill_port 3000
    
    # Start frontend server
    print_status "Starting Next.js server on http://localhost:3000"
    npm run dev &
    FRONTEND_PID=$!
    
    # Wait for frontend to start
    sleep 15
    
    # Test frontend
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        print_success "Frontend server is running on http://localhost:3000"
    else
        print_warning "Frontend server may not be fully ready yet - checking for errors..."
        # Check if the process is still running
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            print_warning "Frontend process is running but health check failed"
        else
            print_error "Frontend process failed to start"
            return 1
        fi
    fi
    
    cd ../..
}

# Function to show status
show_status() {
    echo ""
    print_status "=== Server Status ==="
    
    if check_port 8000; then
        print_success "Backend: http://localhost:8000 ✅"
    else
        print_error "Backend: Not running ❌"
    fi
    
    if check_port 3000; then
        print_success "Frontend: http://localhost:3000 ✅"
    else
        print_error "Frontend: Not running ❌"
    fi
    
    echo ""
    print_status "=== Quick Links ==="
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8000"
    echo "API Health: http://localhost:8000/health"
    echo "API Docs: http://localhost:8000/docs"
    echo ""
}

# Function to cleanup on exit
cleanup() {
    print_status "Shutting down servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    print_success "Servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
echo "🚀 Starting Casablanca Insights Servers..."
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "apps" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Start servers
print_status "Starting backend server..."
if start_backend; then
    print_success "Backend started successfully"
else
    print_error "Failed to start backend server"
    exit 1
fi

print_status "Starting frontend server..."
if start_frontend; then
    print_success "Frontend started successfully"
else
    print_error "Failed to start frontend server"
    exit 1
fi

# Show status
show_status

print_success "🎉 Casablanca Insights is starting up!"
print_status "Press Ctrl+C to stop all servers"
echo ""

# Keep script running
while true; do
    sleep 10
    # Show status every 30 seconds
    if [ $((SECONDS % 30)) -eq 0 ]; then
        show_status
    fi
done 