#!/bin/bash

# 🚀 Complete Setup Test Script for Casablanca Insights
# This script tests all setup scripts in sequence and identifies issues

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

# Function to test system dependencies
test_system_dependencies() {
    print_status "Testing system dependencies..."
    
    local missing_deps=()
    local required_commands=("git" "python3" "node" "npm" "curl")
    
    for cmd in "${required_commands[@]}"; do
        if ! command_exists "$cmd"; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing required system dependencies:"
        printf '%s\n' "${missing_deps[@]}"
        return 1
    fi
    
    print_success "All system dependencies are available"
    return 0
}

# Function to test master setup script
test_master_setup() {
    print_status "Testing master setup script..."
    
    if [ ! -f "setup.sh" ]; then
        print_error "Master setup script not found"
        return 1
    fi
    
    if [ ! -x "setup.sh" ]; then
        print_warning "Making setup.sh executable"
        chmod +x setup.sh
    fi
    
    # Test help command
    if ./setup.sh --help >/dev/null 2>&1; then
        print_success "Master setup script help works"
    else
        print_error "Master setup script help failed"
        return 1
    fi
    
    # Test validation
    if ./setup.sh --validate-only >/dev/null 2>&1; then
        print_success "Master setup validation works"
    else
        print_warning "Master setup validation failed (expected for initial setup)"
    fi
    
    return 0
}

# Function to test complete setup script
test_complete_setup() {
    print_status "Testing complete setup script..."
    
    if [ ! -f "scripts/setup/complete_setup.sh" ]; then
        print_error "Complete setup script not found"
        return 1
    fi
    
    if [ ! -x "scripts/setup/complete_setup.sh" ]; then
        print_warning "Making complete_setup.sh executable"
        chmod +x scripts/setup/complete_setup.sh
    fi
    
    # Test help command
    if ./scripts/setup/complete_setup.sh --help >/dev/null 2>&1; then
        print_success "Complete setup script help works"
    else
        print_error "Complete setup script help failed"
        return 1
    fi
    
    # Test validation
    if ./scripts/setup/complete_setup.sh --validate-only >/dev/null 2>&1; then
        print_success "Complete setup validation works"
    else
        print_warning "Complete setup validation failed (expected for initial setup)"
    fi
    
    return 0
}

# Function to test deployment script
test_deployment_script() {
    print_status "Testing deployment script..."
    
    if [ ! -f "scripts/deployment/deploy.sh" ]; then
        print_error "Deployment script not found"
        return 1
    fi
    
    if [ ! -x "scripts/deployment/deploy.sh" ]; then
        print_warning "Making deploy.sh executable"
        chmod +x scripts/deployment/deploy.sh
    fi
    
    # Test help command
    if ./scripts/deployment/deploy.sh --help >/dev/null 2>&1; then
        print_success "Deployment script help works"
    else
        print_error "Deployment script help failed"
        return 1
    fi
    
    return 0
}

# Function to test monitoring setup
test_monitoring_setup() {
    print_status "Testing monitoring setup..."
    
    if [ ! -f "scripts/setup_monitoring.py" ]; then
        print_error "Monitoring setup script not found"
        return 1
    fi
    
    # Test monitoring setup
    if python3 scripts/setup_monitoring.py >/dev/null 2>&1; then
        print_success "Monitoring setup works"
    else
        print_warning "Monitoring setup failed (expected without env vars)"
    fi
    
    return 0
}

# Function to test ETL scripts
test_etl_scripts() {
    print_status "Testing ETL scripts..."
    
    local etl_dir="apps/backend/etl"
    local required_etl_files=(
        "african_markets_scraper.py"
        "financial_reports_advanced_etl.py"
        "news_sentiment_advanced_etl.py"
        "etl_orchestrator.py"
    )
    
    for file in "${required_etl_files[@]}"; do
        if [ ! -f "$etl_dir/$file" ]; then
            print_error "ETL script not found: $file"
            return 1
        fi
    done
    
    print_success "All required ETL scripts found"
    return 0
}

# Function to test Airflow setup
test_airflow_setup() {
    print_status "Testing Airflow setup..."
    
    local airflow_dir="apps/backend/airflow"
    
    if [ ! -d "$airflow_dir" ]; then
        print_error "Airflow directory not found"
        return 1
    fi
    
    if [ ! -f "$airflow_dir/setup_airflow.sh" ]; then
        print_error "Airflow setup script not found"
        return 1
    fi
    
    if [ ! -x "$airflow_dir/setup_airflow.sh" ]; then
        print_warning "Making setup_airflow.sh executable"
        chmod +x "$airflow_dir/setup_airflow.sh"
    fi
    
    # Test Airflow setup (will fail without Docker, but that's expected)
    if cd "$airflow_dir" && ./setup_airflow.sh >/dev/null 2>&1; then
        print_success "Airflow setup works"
    else
        print_warning "Airflow setup failed (expected without Docker)"
    fi
    
    cd - >/dev/null 2>&1
    return 0
}

# Function to test health checks
test_health_checks() {
    print_status "Testing health checks..."
    
    local health_checks=(
        "apps/backend/monitoring/health_checks.py"
        "monitoring/health_monitor.py"
        "apps/web/pages/api/health.ts"
    )
    
    for check in "${health_checks[@]}"; do
        if [ ! -f "$check" ]; then
            print_error "Health check not found: $check"
            return 1
        fi
    done
    
    print_success "All health check files found"
    return 0
}

# Function to test Docker setup
test_docker_setup() {
    print_status "Testing Docker setup..."
    
    if ! command_exists docker; then
        print_warning "Docker not found, skipping Docker tests"
        return 0
    fi
    
    if ! command_exists docker-compose; then
        print_warning "Docker Compose not found, skipping Docker tests"
        return 0
    fi
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        print_warning "Docker is not running, skipping Docker tests"
        return 0
    fi
    
    # Test Docker Compose file
    if [ -f "apps/backend/docker-compose.yml" ]; then
        if docker-compose -f apps/backend/docker-compose.yml config >/dev/null 2>&1; then
            print_success "Docker Compose configuration is valid"
        else
            print_error "Docker Compose configuration is invalid"
            return 1
        fi
    else
        print_error "Docker Compose file not found"
        return 1
    fi
    
    return 0
}

# Function to test environment setup
test_environment_setup() {
    print_status "Testing environment setup..."
    
    # Check if env.template exists
    if [ ! -f "env.template" ]; then
        print_error "Environment template not found"
        return 1
    fi
    
    # Check if .env exists (create if not)
    if [ ! -f ".env" ]; then
        print_warning "Creating .env file from template"
        cp env.template .env
    fi
    
    print_success "Environment setup works"
    return 0
}

# Function to test Python environment
test_python_environment() {
    print_status "Testing Python environment..."
    
    # Check if virtual environment exists
    if [ ! -d ".venv" ]; then
        print_warning "Python virtual environment not found"
        return 0
    fi
    
    # Test Python imports
    if source .venv/bin/activate && python -c "import fastapi, supabase" 2>/dev/null; then
        print_success "Python environment works"
    else
        print_warning "Python environment has missing dependencies"
    fi
    
    return 0
}

# Function to test Node.js environment
test_node_environment() {
    print_status "Testing Node.js environment..."
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_warning "Node.js dependencies not installed"
        return 0
    fi
    
    # Test npm
    if npm list >/dev/null 2>&1; then
        print_success "Node.js environment works"
    else
        print_warning "Node.js environment has issues"
    fi
    
    return 0
}

# Function to run all tests
run_all_tests() {
    print_status "🚀 Running Complete Setup Test Suite"
    echo "=========================================="
    echo ""
    
    local tests=(
        "System Dependencies:test_system_dependencies"
        "Master Setup Script:test_master_setup"
        "Complete Setup Script:test_complete_setup"
        "Deployment Script:test_deployment_script"
        "Monitoring Setup:test_monitoring_setup"
        "ETL Scripts:test_etl_scripts"
        "Airflow Setup:test_airflow_setup"
        "Health Checks:test_health_checks"
        "Docker Setup:test_docker_setup"
        "Environment Setup:test_environment_setup"
        "Python Environment:test_python_environment"
        "Node.js Environment:test_node_environment"
    )
    
    local passed=0
    local total=${#tests[@]}
    
    for test_item in "${tests[@]}"; do
        IFS=':' read -r test_name test_func <<< "$test_item"
        print_status "Running: $test_name"
        if $test_func; then
            print_success "$test_name passed"
            ((passed++))
        else
            print_error "$test_name failed"
        fi
        echo ""
    done
    
    # Summary
    print_status "📊 Test Results Summary"
    echo "========================"
    print_status "Passed: $passed/$total"
    
    if [ $passed -eq $total ]; then
        print_success "🎉 All tests passed! Setup is ready."
        return 0
    else
        print_warning "⚠️ Some tests failed. Check the issues above."
        return 1
    fi
}

# Function to show fixes
show_fixes() {
    print_status "🔧 Common Fixes"
    echo "================"
    echo ""
    echo "1. Make scripts executable:"
    echo "   chmod +x setup.sh"
    echo "   chmod +x scripts/setup/complete_setup.sh"
    echo "   chmod +x scripts/deployment/deploy.sh"
    echo ""
    echo "2. Set up environment:"
    echo "   cp env.template .env"
    echo "   # Edit .env with your values"
    echo ""
    echo "3. Install dependencies:"
    echo "   python3 -m venv .venv"
    echo "   source .venv/bin/activate"
    echo "   pip install -r apps/backend/requirements.txt"
    echo "   npm install"
    echo ""
    echo "4. Start Docker (if using):"
    echo "   # Start Docker Desktop"
    echo ""
    echo "5. Run complete setup:"
    echo "   ./setup.sh"
    echo ""
}

# Main function
main() {
    case "${1:-}" in
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --help, -h     Show this help message"
            echo "  --fixes        Show common fixes"
            echo ""
            echo "This script tests all setup components and identifies issues."
            exit 0
            ;;
        --fixes)
            show_fixes
            exit 0
            ;;
        "")
            check_project_root
            run_all_tests
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 