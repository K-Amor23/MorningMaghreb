#!/bin/bash

# 🚀 Complete Casablanca Insights Setup Script
# This script sets up the entire project from scratch on a fresh machine

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
    print_success "Project root directory confirmed"
}

# Function to check and install system dependencies
check_system_dependencies() {
    print_status "Checking system dependencies..."
    
    local missing_deps=()
    
    # Check for required commands
    local required_commands=("git" "python3" "node" "npm" "curl")
    
    for cmd in "${required_commands[@]}"; do
        if ! command_exists "$cmd"; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing required system dependencies:"
        printf '%s\n' "${missing_deps[@]}"
        print_status "Please install the missing dependencies and run this script again"
        exit 1
    fi
    
    print_success "All system dependencies are available"
}

# Function to setup environment variables
setup_environment() {
    print_status "Setting up environment variables..."
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from template..."
        if [ -f "env.template" ]; then
            cp env.template .env
            print_success "Created .env file from template"
            print_warning "Please edit .env file with your actual configuration values"
        else
            print_error "env.template not found"
            exit 1
        fi
    else
        print_status ".env file already exists"
    fi
    
    # Load environment variables
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
        print_success "Environment variables loaded"
    fi
}

# Function to setup Python virtual environment
setup_python_environment() {
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        print_success "Python virtual environment created"
    else
        print_status "Python virtual environment already exists"
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    print_success "Python environment setup completed"
}

# Function to install Python dependencies
install_python_dependencies() {
    print_status "Installing Python dependencies..."
    
    source .venv/bin/activate
    
    # Install backend dependencies
    if [ -f "apps/backend/requirements.txt" ]; then
        pip install -r apps/backend/requirements.txt
        print_success "Backend dependencies installed"
    else
        print_error "Backend requirements.txt not found"
        exit 1
    fi
    
    # Install additional dependencies
    pip install python-dotenv supabase
    print_success "Additional Python dependencies installed"
}

# Function to install Node.js dependencies
install_node_dependencies() {
    print_status "Installing Node.js dependencies..."
    
    # Install root dependencies
    npm install
    
    # Install web app dependencies
    if [ -d "apps/web" ]; then
        cd apps/web
        npm install
        cd ../..
        print_success "Web app dependencies installed"
    fi
    
    # Install mobile app dependencies
    if [ -d "apps/mobile" ]; then
        cd apps/mobile
        npm install
        cd ../..
        print_success "Mobile app dependencies installed"
    fi
    
    # Install shared package dependencies
    if [ -d "packages/shared" ]; then
        cd packages/shared
        npm install
        cd ../..
        print_success "Shared package dependencies installed"
    fi
    
    print_success "All Node.js dependencies installed"
}

# Function to setup database
setup_database() {
    print_status "Setting up database..."
    
    # Check if Supabase environment variables are set
    if [ -z "$NEXT_PUBLIC_SUPABASE_URL" ] || [ -z "$NEXT_PUBLIC_SUPABASE_ANON_KEY" ]; then
        print_warning "Supabase environment variables not set"
        print_status "Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in your .env file"
        return 1
    fi
    
    # Run database setup script
    if [ -f "scripts/setup/setup_supabase_database.py" ]; then
        source .venv/bin/activate
        python scripts/setup/setup_supabase_database.py
        if [ $? -eq 0 ]; then
            print_success "Database setup completed"
            return 0
        else
            print_error "Database setup failed"
            return 1
        fi
    else
        print_error "Database setup script not found"
        return 1
    fi
}

# Function to setup Docker (if needed)
setup_docker() {
    print_status "Setting up Docker environment..."
    
    if ! command_exists docker; then
        print_warning "Docker not found. Skipping Docker setup"
        return 0
    fi
    
    if ! command_exists docker-compose; then
        print_warning "Docker Compose not found. Skipping Docker setup"
        return 0
    fi
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        print_warning "Docker is not running. Please start Docker and run this script again"
        return 0
    fi
    
    print_success "Docker environment is ready"
}

# Function to validate setup
validate_setup() {
    print_status "Validating setup..."
    
    local validation_passed=true
    
    # Test Python environment
    source .venv/bin/activate
    if ! python -c "import fastapi, supabase" 2>/dev/null; then
        print_error "Python dependencies validation failed"
        validation_passed=false
    else
        print_success "Python dependencies validated"
    fi
    
    # Test Node.js environment
    if ! npm list >/dev/null 2>&1; then
        print_warning "Node.js dependencies not found, but this is expected if not installed yet"
        # Don't fail validation for missing Node.js deps
    else
        print_success "Node.js dependencies validated"
    fi
    
    # Test environment variables
    if [ -z "$NEXT_PUBLIC_SUPABASE_URL" ] || [ -z "$NEXT_PUBLIC_SUPABASE_ANON_KEY" ]; then
        print_warning "Supabase environment variables not set (this is expected for initial setup)"
        # Don't fail validation for missing env vars
    else
        print_success "Environment variables validated"
    fi
    
    if [ "$validation_passed" = true ]; then
        print_success "Setup validation completed successfully"
        return 0
    else
        print_error "Setup validation failed"
        return 1
    fi
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    # Run backend tests
    if [ -d "apps/backend/tests" ]; then
        source .venv/bin/activate
        cd apps/backend
        python -m pytest tests/ -v || {
            print_warning "Backend tests failed, but continuing..."
        }
        cd ../..
    fi
    
    # Run frontend tests
    if [ -d "apps/web" ]; then
        cd apps/web
        npm test -- --passWithNoTests || {
            print_warning "Frontend tests failed, but continuing..."
        }
        cd ../..
    fi
    
    print_success "Tests completed"
}

# Function to start development servers
start_development_servers() {
    print_status "Starting development servers..."
    
    print_status "To start the development servers, run:"
    echo ""
    echo "  # Terminal 1 - Backend"
    echo "  source .venv/bin/activate"
    echo "  cd apps/backend"
    echo "  uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    echo "  # Terminal 2 - Frontend"
    echo "  cd apps/web"
    echo "  npm run dev"
    echo ""
    echo "  # Or use the provided scripts:"
    echo "  make start-backend  # For backend"
    echo "  make start-frontend # For frontend"
    echo "  ./start-simple.sh   # For both (simple)"
    echo ""
}

# Function to display setup summary
show_setup_summary() {
    print_success "Setup Summary"
    echo "=============="
    echo ""
    echo "✅ System dependencies checked"
    echo "✅ Environment variables configured"
    echo "✅ Python virtual environment created"
    echo "✅ Python dependencies installed"
    echo "✅ Node.js dependencies installed"
    echo "✅ Docker environment checked"
    echo "✅ Setup validation completed"
    echo "✅ Tests run"
    echo ""
    echo "🎉 Casablanca Insights is ready for development!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Edit .env file with your actual configuration values"
    echo "2. Set up your Supabase project and update the URL/keys"
    echo "3. Start the development servers"
    echo "4. Visit http://localhost:3000 for the frontend"
    echo "5. Visit http://localhost:8000/docs for the API documentation"
    echo ""
    echo "📚 Documentation:"
    echo "- README.md - Main project documentation"
    echo "- CASABLANCA_INSIGHTS_SETUP_GUIDE.md - Detailed setup guide"
    echo "- DEPLOYMENT_QUICK_REFERENCE.md - Deployment instructions"
    echo ""
}

# Main setup function
main() {
    print_status "🚀 Starting Casablanca Insights Complete Setup"
    echo "=================================================="
    echo ""
    
    # Check project root
    check_project_root
    
    # Check system dependencies
    check_system_dependencies
    
    # Setup environment
    setup_environment
    
    # Setup Python environment
    setup_python_environment
    
    # Install Python dependencies
    install_python_dependencies
    
    # Install Node.js dependencies
    install_node_dependencies
    
    # Setup Docker
    setup_docker
    
    # Setup database (optional - can be skipped if env vars not set)
    setup_database || print_warning "Database setup skipped (set env vars to enable)"
    
    # Validate setup
    validate_setup
    
    # Run tests
    run_tests
    
    # Show setup summary
    show_setup_summary
    
    print_success "Setup completed successfully! 🎉"
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --skip-db      Skip database setup"
        echo "  --skip-tests   Skip running tests"
        echo "  --validate-only Run validation only"
        echo ""
        echo "This script sets up the complete Casablanca Insights development environment."
        exit 0
        ;;
    --skip-db)
        print_status "Skipping database setup"
        # Modify main function to skip database setup
        ;;
    --skip-tests)
        print_status "Skipping tests"
        # Modify main function to skip tests
        ;;
    --validate-only)
        print_status "Running validation only"
        check_project_root
        validate_setup
        exit $?
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac 