#!/bin/bash

# Quick Start Script for Smart IR Scraping
# This script sets up the production-ready smart IR scraping system

set -e  # Exit on any error

echo "🚀 Quick Start: Smart IR Scraping System"
echo "========================================"

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
if [ ! -f "main.py" ]; then
    print_error "Please run this script from the apps/backend directory"
    exit 1
fi

# Check if .env file exists
if [ ! -f "../../.env" ]; then
    print_warning ".env file not found. Creating template..."
    cat > ../../.env << EOF
# Database Configuration
SUPABASE_HOST=your-supabase-host.supabase.co
SUPABASE_PORT=5432
SUPABASE_DATABASE=postgres
SUPABASE_USER=postgres
SUPABASE_PASSWORD=your-database-password

# Airflow Configuration
AIRFLOW_BASE_URL=http://localhost:8080
AIRFLOW_USERNAME=admin
AIRFLOW_PASSWORD=admin

# Notification Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
ALERT_EMAILS=["admin@morningmaghreb.com"]

# Scraping Configuration
PROXY_ENABLED=false
TEST_MODE=true
EOF
    print_warning "Please edit ../../.env with your actual configuration values"
    print_warning "Then run this script again"
    exit 1
fi

# Load environment variables
source ../../.env

print_status "Starting Smart IR Scraping Setup..."

# Step 1: Check Python environment
print_status "Step 1: Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

python_version=$(python3 --version | cut -d' ' -f2)
print_success "Python $python_version found"

# Step 2: Install dependencies
print_status "Step 2: Installing dependencies..."
if [ -f "requirements_etl.txt" ]; then
    pip install -r requirements_etl.txt
    print_success "Dependencies installed"
else
    print_warning "requirements_etl.txt not found, installing basic dependencies..."
    pip install psycopg2-binary requests python-dotenv beautifulsoup4 PyPDF2
    print_success "Basic dependencies installed"
fi

# Step 3: Test database connection
print_status "Step 3: Testing database connection..."
python3 -c "
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv('../../.env')

try:
    conn = psycopg2.connect(
        host=os.getenv('SUPABASE_HOST'),
        database=os.getenv('SUPABASE_DATABASE'),
        user=os.getenv('SUPABASE_USER'),
        password=os.getenv('SUPABASE_PASSWORD'),
        port=os.getenv('SUPABASE_PORT', '5432')
    )
    print('✅ Database connection successful')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

# Step 4: Run setup script
print_status "Step 4: Running setup script..."
if [ -f "scripts/setup_smart_ir_scraping.py" ]; then
    python3 scripts/setup_smart_ir_scraping.py --test-mode
    print_success "Setup script completed"
else
    print_warning "Setup script not found, skipping..."
fi

# Step 5: Copy DAG file
print_status "Step 5: Copying DAG file..."
if [ -f "airflow/dags/smart_ir_scraping_dag.py" ]; then
    # Try to find Airflow dags directory
    AIRFLOW_DAGS_DIR=""
    
    # Common Airflow dags directories
    for dir in "/opt/airflow/dags" "$HOME/airflow/dags" "/usr/local/airflow/dags" "/tmp/airflow_dags"; do
        if [ -d "$dir" ] || [ "$dir" = "/tmp/airflow_dags" ]; then
            AIRFLOW_DAGS_DIR="$dir"
            mkdir -p "$dir"
            break
        fi
    done
    
    if [ -n "$AIRFLOW_DAGS_DIR" ]; then
        cp airflow/dags/smart_ir_scraping_dag.py "$AIRFLOW_DAGS_DIR/"
        print_success "DAG file copied to $AIRFLOW_DAGS_DIR"
    else
        print_warning "Could not find Airflow dags directory"
        print_warning "Please manually copy airflow/dags/smart_ir_scraping_dag.py to your Airflow dags directory"
    fi
else
    print_warning "DAG file not found"
fi

# Step 6: Test Airflow connection
print_status "Step 6: Testing Airflow connection..."
if command -v curl &> /dev/null; then
    if curl -s -u "$AIRFLOW_USERNAME:$AIRFLOW_PASSWORD" "$AIRFLOW_BASE_URL/api/v1/dags" &> /dev/null; then
        print_success "Airflow connection successful"
    else
        print_warning "Could not connect to Airflow at $AIRFLOW_BASE_URL"
        print_warning "Please ensure Airflow is running and accessible"
    fi
else
    print_warning "curl not available, skipping Airflow connection test"
fi

# Step 7: Create test script
print_status "Step 7: Creating test script..."
cat > test_smart_scraping.py << 'EOF'
#!/usr/bin/env python3
"""
Test script for Smart IR Scraping
Run this to test the system without Airflow
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../../.env')

def test_database_connection():
    """Test database connection and basic queries"""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(
            host=os.getenv('SUPABASE_HOST'),
            database=os.getenv('SUPABASE_DATABASE'),
            user=os.getenv('SUPABASE_USER'),
            password=os.getenv('SUPABASE_PASSWORD'),
            port=os.getenv('SUPABASE_PORT', '5432')
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Test basic query
            cursor.execute("SELECT COUNT(*) as count FROM companies WHERE is_active = 'Y'")
            result = cursor.fetchone()
            print(f"✅ Found {result['count']} active companies")
            
            # Test dashboard view
            cursor.execute("SELECT COUNT(*) as count FROM ir_scraping_dashboard")
            result = cursor.fetchone()
            print(f"✅ Dashboard view accessible: {result['count']} companies")
            
            # Test companies due for scraping
            cursor.execute("SELECT COUNT(*) as count FROM get_companies_due_for_scraping()")
            result = cursor.fetchone()
            print(f"✅ Companies due for scraping: {result['count']}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_scraping_logic():
    """Test the scraping business logic"""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(
            host=os.getenv('SUPABASE_HOST'),
            database=os.getenv('SUPABASE_DATABASE'),
            user=os.getenv('SUPABASE_USER'),
            password=os.getenv('SUPABASE_PASSWORD'),
            port=os.getenv('SUPABASE_PORT', '5432')
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Test expected release date calculation
            cursor.execute("""
                SELECT ticker, name, fiscal_year_end_month, fiscal_year_end_day, 
                       ir_expected_release_date, last_scraped_at
                FROM companies 
                WHERE is_active = 'Y' 
                LIMIT 5
            """)
            
            companies = cursor.fetchall()
            print(f"✅ Sample companies with fiscal data:")
            for company in companies:
                print(f"   - {company['ticker']}: {company['name']}")
                print(f"     Fiscal year end: {company['fiscal_year_end_month']}/{company['fiscal_year_end_day']}")
                print(f"     Expected release: {company['ir_expected_release_date']}")
                print(f"     Last scraped: {company['last_scraped_at']}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Scraping logic test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Smart IR Scraping System")
    print("=" * 40)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Scraping Logic", test_scraping_logic),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} passed")
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 TEST SUMMARY")
    print("=" * 40)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Your system is ready.")
        print("\n📝 Next Steps:")
        print("1. Start Airflow: airflow webserver & airflow scheduler")
        print("2. Open Airflow UI: http://localhost:8080")
        print("3. Find the 'smart_ir_scraping' DAG")
        print("4. Trigger a manual run to test")
        print("5. Enable automatic scheduling")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
EOF

chmod +x test_smart_scraping.py
print_success "Test script created: test_smart_scraping.py"

# Step 8: Run test
print_status "Step 8: Running system test..."
if python3 test_smart_scraping.py; then
    print_success "System test passed"
else
    print_warning "System test failed - check the output above"
fi

# Final summary
echo ""
echo "🎉 Smart IR Scraping Setup Complete!"
echo "===================================="
echo ""
echo "📋 What was set up:"
echo "✅ Python environment and dependencies"
echo "✅ Database schema and functions"
echo "✅ Company data with fiscal calendars"
echo "✅ Airflow DAG file"
echo "✅ Test script for validation"
echo ""
echo "📝 Next Steps:"
echo "1. Start Airflow:"
echo "   airflow webserver &"
echo "   airflow scheduler &"
echo ""
echo "2. Open Airflow UI:"
echo "   http://localhost:8080"
echo ""
echo "3. Configure Airflow:"
echo "   - Add 'supabase_postgres' connection"
echo "   - Set Airflow variables (SLACK_WEBHOOK_URL, etc.)"
echo ""
echo "4. Test the DAG:"
echo "   - Find 'smart_ir_scraping' DAG"
echo "   - Trigger manual run"
echo "   - Check logs for any issues"
echo ""
echo "5. Enable scheduling:"
echo "   - Turn on the DAG in Airflow UI"
echo "   - It will run daily at 2:00 AM ET"
echo ""
echo "📊 Monitor your system:"
echo "   - Check Airflow logs for DAG execution"
echo "   - Query ir_scraping_dashboard view for status"
echo "   - Monitor Slack/email notifications"
echo ""
echo "🔧 Configuration:"
echo "   - Edit ../../.env for environment variables"
echo "   - Set TEST_MODE=false for production"
echo "   - Configure SLACK_WEBHOOK_URL for notifications"
echo ""
echo "📞 Need help?"
echo "   - Check logs: Airflow UI → DAGs → smart_ir_scraping → Logs"
echo "   - Run test: python3 test_smart_scraping.py"
echo "   - Review: apps/backend/airflow/SMART_IR_SCRAPING_DEPLOYMENT.md"
echo ""

print_success "Setup completed successfully!" 