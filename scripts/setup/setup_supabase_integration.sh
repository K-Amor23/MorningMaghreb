#!/bin/bash

# 🚀 Supabase Database Integration Setup Script
# This script automates the setup of Supabase integration for Casablanca Insights

set -e  # Exit on any error

echo "🗄️  Setting up Supabase Database Integration for Casablanca Insights"
echo "=================================================================="

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

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -d "apps" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Checking prerequisites..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv .venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate

# Install required packages
print_status "Installing required packages..."
pip install supabase python-dotenv

# Check if environment variables are set
print_status "Checking environment variables..."

if [ -z "$NEXT_PUBLIC_SUPABASE_URL" ] || [ -z "$NEXT_PUBLIC_SUPABASE_ANON_KEY" ]; then
    print_warning "Supabase environment variables not found"
    print_status "Please set the following environment variables:"
    echo "  export NEXT_PUBLIC_SUPABASE_URL='your_supabase_url'"
    echo "  export NEXT_PUBLIC_SUPABASE_ANON_KEY='your_supabase_anon_key'"
    echo ""
    print_status "Or add them to your .env file"
    echo ""
    
    # Check if .env file exists
    if [ -f ".env" ]; then
        print_status "Found .env file. Checking for Supabase variables..."
        if grep -q "NEXT_PUBLIC_SUPABASE_URL" .env && grep -q "NEXT_PUBLIC_SUPABASE_ANON_KEY" .env; then
            print_success "Supabase variables found in .env file"
            # Load .env file
            export $(grep -v '^#' .env | xargs)
        else
            print_warning "Supabase variables not found in .env file"
        fi
    else
        print_warning "No .env file found"
    fi
else
    print_success "Supabase environment variables are set"
fi

# Create data directory
print_status "Creating data directories..."
mkdir -p data/refresh
print_success "Data directories created"

# Test Supabase connection
print_status "Testing Supabase connection..."
python3 -c "
from supabase import create_client
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')

if not url or not key:
    print('❌ Supabase credentials not found')
    print('Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY')
    sys.exit(1)

try:
    supabase = create_client(url, key)
    # Try a simple query to test connection
    response = supabase.table('profiles').select('count').limit(1).execute()
    print('✅ Supabase connection successful')
except Exception as e:
    print(f'❌ Supabase connection failed: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    print_success "Supabase connection test passed"
else
    print_error "Supabase connection test failed"
    exit 1
fi

# Display next steps
echo ""
echo "🎉 Setup completed successfully!"
echo "=================================================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. 📊 Add the database schema to your Supabase project:"
echo "   - Go to your Supabase Dashboard"
echo "   - Navigate to SQL Editor"
echo "   - Copy and paste the contents of: apps/backend/database/supabase_financial_schema.sql"
echo ""
echo "2. 🏢 Initialize company data:"
echo "   source venv/bin/activate"
echo "   python apps/backend/etl/initialize_supabase_cse.py"
echo ""
echo "3. 🔄 Set up daily data refresh (optional):"
echo "   # Add to crontab (crontab -e):"
echo "   0 6 * * * cd $(pwd) && source venv/bin/activate && python apps/backend/etl/supabase_data_refresh.py"
echo ""
echo "4. 📖 Read the complete guide:"
echo "   cat SUPABASE_DATABASE_INTEGRATION_GUIDE.md"
echo ""
echo "5. 🧪 Test the setup:"
echo "   source venv/bin/activate"
echo "   python -c \"from supabase import create_client; import os; supabase = create_client(os.getenv('NEXT_PUBLIC_SUPABASE_URL'), os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')); print('✅ Ready to use!')\""
echo ""

print_success "Setup script completed! 🚀"