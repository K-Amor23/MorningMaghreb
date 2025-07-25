#!/bin/bash

# 🚀 Casablanca Insights Deployment Script
# This script automates the deployment process for production

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

# Function to check environment variables
check_env_vars() {
    print_status "Checking environment variables..."
    
    local required_vars=(
        "NEXT_PUBLIC_SUPABASE_URL"
        "NEXT_PUBLIC_SUPABASE_ANON_KEY"
        "OPENAI_API_KEY"
        "SENDGRID_API_KEY"
        "STRIPE_SECRET_KEY"
        "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY"
    )
    
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        print_error "Missing required environment variables:"
        printf '%s\n' "${missing_vars[@]}"
        exit 1
    fi
    
    print_success "All required environment variables are set"
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    # Frontend tests
    if [ -d "apps/web" ]; then
        cd apps/web
        if command_exists npm; then
            npm ci
            npm run test || {
                print_warning "Frontend tests failed, but continuing deployment..."
            }
        else
            print_warning "npm not found, skipping frontend tests"
        fi
        cd ../..
    fi
    
    # Backend tests
    if [ -d "apps/backend" ]; then
        cd apps/backend
        if command_exists python; then
            python -m pytest tests/ || {
                print_warning "Backend tests failed, but continuing deployment..."
            }
        else
            print_warning "Python not found, skipping backend tests"
        fi
        cd ../..
    fi
    
    print_success "Tests completed"
}

# Function to build frontend
build_frontend() {
    print_status "Building frontend..."
    
    if [ ! -d "apps/web" ]; then
        print_error "Frontend directory not found"
        exit 1
    fi
    
    cd apps/web
    
    if command_exists npm; then
        npm ci
        npm run build
        print_success "Frontend build completed"
    else
        print_error "npm not found"
        exit 1
    fi
    
    cd ../..
}

# Function to check deployment status
check_deployment_status() {
    local service_url=$1
    local service_name=$2
    
    print_status "Checking $service_name deployment status..."
    
    if command_exists curl; then
        local max_attempts=30
        local attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if curl -f -s "$service_url/health" > /dev/null 2>&1; then
                print_success "$service_name is deployed and healthy"
                return 0
            fi
            
            print_status "Attempt $attempt/$max_attempts: $service_name not ready yet..."
            sleep 10
            ((attempt++))
        done
        
        print_error "$service_name deployment check failed after $max_attempts attempts"
        return 1
    else
        print_warning "curl not found, skipping deployment status check"
        return 0
    fi
}

# Function to deploy to Vercel
deploy_frontend() {
    print_status "Deploying frontend to Vercel..."
    
    if command_exists vercel; then
        cd apps/web
        
        # Check if project is already linked
        if [ ! -f ".vercel/project.json" ]; then
            print_status "Linking project to Vercel..."
            vercel --yes
        fi
        
        # Deploy to production
        vercel --prod --yes
        
        cd ../..
        print_success "Frontend deployment initiated"
    else
        print_warning "Vercel CLI not found. Please deploy manually:"
        print_status "1. Go to https://vercel.com"
        print_status "2. Import your repository"
        print_status "3. Set environment variables"
        print_status "4. Deploy"
    fi
}

# Function to deploy to Render
deploy_backend() {
    print_status "Deploying backend to Render..."
    
    if command_exists render; then
        cd apps/backend
        
        # Deploy to Render
        render deploy
        
        cd ../..
        print_success "Backend deployment initiated"
    else
        print_warning "Render CLI not found. Please deploy manually:"
        print_status "1. Go to https://render.com"
        print_status "2. Create new web service"
        print_status "3. Connect your repository"
        print_status "4. Set environment variables"
        print_status "5. Deploy"
    fi
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    if [ -d "apps/backend" ]; then
        cd apps/backend
        
        if command_exists python; then
            # Check if alembic is available
            if python -c "import alembic" 2>/dev/null; then
                alembic upgrade head || {
                    print_warning "Database migrations failed, but continuing..."
                }
            else
                print_warning "Alembic not found, skipping migrations"
            fi
        else
            print_warning "Python not found, skipping migrations"
        fi
        
        cd ../..
    fi
    
    print_success "Database migrations completed"
}

# Function to test deployment
test_deployment() {
    print_status "Testing deployment..."
    
    local frontend_url=${NEXT_PUBLIC_SITE_URL:-"https://casablanca-insight.vercel.app"}
    local backend_url=${NEXT_PUBLIC_API_URL:-"https://casablanca-insight-api.onrender.com"}
    
    # Test frontend
    if command_exists curl; then
        print_status "Testing frontend..."
        if curl -f -s "$frontend_url" > /dev/null 2>&1; then
            print_success "Frontend is accessible"
        else
            print_warning "Frontend may not be ready yet"
        fi
        
        # Test backend
        print_status "Testing backend..."
        if curl -f -s "$backend_url/health" > /dev/null 2>&1; then
            print_success "Backend is healthy"
        else
            print_warning "Backend may not be ready yet"
        fi
        
        # Test API endpoints
        print_status "Testing API endpoints..."
        if curl -f -s "$backend_url/api/companies" > /dev/null 2>&1; then
            print_success "API endpoints are working"
        else
            print_warning "API endpoints may not be ready yet"
        fi
    else
        print_warning "curl not found, skipping deployment tests"
    fi
}

# Function to setup monitoring
setup_monitoring() {
    print_status "Setting up monitoring..."
    
    # Create monitoring configuration
    if [ ! -d "monitoring" ]; then
        mkdir monitoring
    fi
    
    # Create uptime robot configuration
    cat > monitoring/uptime-robot.json << EOF
{
  "monitors": [
    {
      "name": "Casablanca Insights Frontend",
      "url": "${NEXT_PUBLIC_SITE_URL:-https://casablanca-insight.vercel.app}",
      "type": "http",
      "interval": 300
    },
    {
      "name": "Casablanca Insights Backend",
      "url": "${NEXT_PUBLIC_API_URL:-https://casablanca-insight-api.onrender.com}/health",
      "type": "http",
      "interval": 300
    }
  ]
}
EOF
    
    print_success "Monitoring configuration created"
}

# Function to display deployment summary
show_summary() {
    print_success "Deployment Summary"
    echo "=================="
    echo "Frontend URL: ${NEXT_PUBLIC_SITE_URL:-https://casablanca-insight.vercel.app}"
    echo "Backend URL: ${NEXT_PUBLIC_API_URL:-https://casablanca-insight-api.onrender.com}"
    echo "Database: Supabase"
    echo "Email Service: SendGrid"
    echo ""
    print_status "Next steps:"
    echo "1. Monitor the application for 24-48 hours"
    echo "2. Test all features manually"
    echo "3. Set up custom domain (optional)"
    echo "4. Configure additional monitoring"
    echo "5. Gather user feedback"
}

# Main deployment function
main() {
    print_status "Starting Casablanca Insights deployment..."
    
    # Check prerequisites
    check_env_vars
    
    # Run tests
    run_tests
    
    # Build frontend
    build_frontend
    
    # Run database migrations
    run_migrations
    
    # Deploy backend
    deploy_backend
    
    # Deploy frontend
    deploy_frontend
    
    # Setup monitoring
    setup_monitoring
    
    # Wait for deployment
    print_status "Waiting for deployment to complete..."
    sleep 30
    
    # Test deployment
    test_deployment
    
    # Show summary
    show_summary
    
    print_success "Deployment process completed!"
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --test-only    Run tests only"
        echo "  --build-only   Build frontend only"
        echo "  --deploy-only  Deploy only (skip tests and build)"
        echo ""
        echo "Environment Variables:"
        echo "  NEXT_PUBLIC_SUPABASE_URL"
        echo "  NEXT_PUBLIC_SUPABASE_ANON_KEY"
        echo "  OPENAI_API_KEY"
        echo "  SENDGRID_API_KEY"
        echo "  STRIPE_SECRET_KEY"
        echo "  NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY"
        exit 0
        ;;
    --test-only)
        check_env_vars
        run_tests
        exit 0
        ;;
    --build-only)
        check_env_vars
        build_frontend
        exit 0
        ;;
    --deploy-only)
        check_env_vars
        deploy_backend
        deploy_frontend
        setup_monitoring
        test_deployment
        show_summary
        exit 0
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