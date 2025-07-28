#!/bin/bash

# 🚀 Casablanca Insights - Master Setup Script
# This script provides a single command to set up the entire project from scratch

set -e  # Exit on any error

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if we're in the right directory
check_project_root() {
    if [ ! -f "package.json" ] || [ ! -d "apps" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
}

# Function to display help
show_help() {
    echo "🚀 Casablanca Insights - Master Setup Script"
    echo "============================================="
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h           Show this help message"
    echo "  --quick              Quick setup (skip tests and database)"
    echo "  --full               Full setup with all features (default)"
    echo "  --test-only          Run tests only"
    echo "  --validate-only      Validate existing setup only"
    echo "  --docker             Include Docker setup"
    echo "  --production         Production setup (includes monitoring)"
    echo ""
    echo "Examples:"
    echo "  $0                  # Full setup"
    echo "  $0 --quick          # Quick setup for development"
    echo "  $0 --test-only      # Run tests only"
    echo "  $0 --validate-only  # Validate existing setup"
    echo ""
    echo "This script will:"
    echo "1. Check system dependencies"
    echo "2. Set up environment variables"
    echo "3. Install Python and Node.js dependencies"
    echo "4. Set up database (if credentials provided)"
    echo "5. Run tests and validation"
    echo "6. Start development servers (optional)"
    echo ""
}

# Function to run quick setup
run_quick_setup() {
    print_status "Running quick setup..."
    
    # Check project root
    check_project_root
    
    # Run the complete setup script with quick options
    ./scripts/setup/complete_setup.sh --skip-db --skip-tests
    
    print_success "Quick setup completed!"
}

# Function to run full setup
run_full_setup() {
    print_status "Running full setup..."
    
    # Check project root
    check_project_root
    
    # Run the complete setup script
    ./scripts/setup/complete_setup.sh
    
    print_success "Full setup completed!"
}

# Function to run tests only
run_tests() {
    print_status "Running tests..."
    
    # Check project root
    check_project_root
    
    # Run the test script
    python3 scripts/test/test_complete_setup.py
    
    print_success "Tests completed!"
}

# Function to validate existing setup
validate_setup() {
    print_status "Validating existing setup..."
    
    # Check project root
    check_project_root
    
    # Run validation only
    ./scripts/setup/complete_setup.sh --validate-only
    
    print_success "Validation completed!"
}

# Function to setup Docker
setup_docker() {
    print_status "Setting up Docker environment..."
    
    if ! command_exists docker; then
        print_error "Docker not found. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose not found. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and run this script again."
        exit 1
    fi
    
    # Build and start Docker containers
    cd apps/backend
    docker-compose up -d --build
    
    print_success "Docker setup completed!"
}

# Function to setup production environment
setup_production() {
    print_status "Setting up production environment..."
    
    # Check project root
    check_project_root
    
    # Run production deployment script
    if [ -f "scripts/deployment/deploy.sh" ]; then
        ./scripts/deployment/deploy.sh
    else
        print_error "Production deployment script not found"
        exit 1
    fi
    
    print_success "Production setup completed!"
}

# Function to start development servers
start_development_servers() {
    print_status "Starting development servers..."
    
    print_status "Starting backend server..."
    cd apps/backend
    source ../../.venv/bin/activate
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ../..
    
    print_status "Starting frontend server..."
    cd apps/web
    npm run dev &
    FRONTEND_PID=$!
    cd ../..
    
    print_success "Development servers started!"
    echo ""
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend:  http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop servers"
    
    # Function to cleanup
    cleanup() {
        print_status "Stopping servers..."
        kill $BACKEND_PID 2>/dev/null || true
        kill $FRONTEND_PID 2>/dev/null || true
        print_success "Servers stopped"
        exit 0
    }
    
    # Set up signal handlers
    trap cleanup SIGINT SIGTERM
    
    # Keep script running
    wait
}

# Main function
main() {
    print_status "🚀 Starting Casablanca Insights Setup"
    echo "=========================================="
    echo ""
    
    # Parse command line arguments
    case "${1:-}" in
        --help|-h)
            show_help
            exit 0
            ;;
        --quick)
            run_quick_setup
            ;;
        --full)
            run_full_setup
            ;;
        --test-only)
            run_tests
            ;;
        --validate-only)
            validate_setup
            ;;
        --docker)
            setup_docker
            ;;
        --production)
            setup_production
            ;;
        --start)
            start_development_servers
            ;;
        "")
            run_full_setup
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
    
    print_success "Setup completed successfully! 🎉"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Edit .env file with your configuration"
    echo "2. Set up your Supabase project"
    echo "3. Run './setup.sh --start' to start servers"
    echo "4. Visit http://localhost:3000"
    echo ""
}

# Run main function
main "$@" 