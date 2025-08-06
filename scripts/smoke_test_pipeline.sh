#!/bin/bash
# Smoke Test Pipeline
# This script runs comprehensive tests to verify the entire pipeline

set -e

echo "🧪 Running Smoke Tests"
echo "======================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0
SKIPPED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local required="$3"
    
    echo ""
    echo "🔍 Testing: $test_name"
    echo "Command: $test_command"
    
    if eval "$test_command" 2>/dev/null; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((FAILED++))
        if [ "$required" = "true" ]; then
            echo "This is a required test. Pipeline may not work correctly."
        fi
    fi
}

# Function to run a test with output capture
run_test_with_output() {
    local test_name="$1"
    local test_command="$2"
    local required="$3"
    
    echo ""
    echo "🔍 Testing: $test_name"
    echo "Command: $test_command"
    
    if output=$(eval "$test_command" 2>&1); then
        echo -e "${GREEN}✅ PASS${NC}"
        echo "Output: $output"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}"
        echo "Error: $output"
        ((FAILED++))
        if [ "$required" = "true" ]; then
            echo "This is a required test. Pipeline may not work correctly."
        fi
    fi
}

echo "📋 Test Categories:"
echo "1. Environment Setup"
echo "2. Database Connectivity"
echo "3. Scraper Integration"
echo "4. Airflow DAG"
echo "5. Health Checks"
echo "6. CI/CD Pipeline"
echo ""

# 1. Environment Setup Tests
echo "🏗️  1. Environment Setup Tests"
echo "=============================="

run_test "Check .env.local exists" "[ -f .env.local ]" "true"
run_test "Check required env vars" "grep -q 'SUPABASE_URL' .env.local && grep -q 'SUPABASE_SERVICE_ROLE_KEY' .env.local" "true"
run_test "Check Vercel CLI" "command -v vercel" "false"
run_test "Check GitHub CLI" "command -v gh" "false"
run_test "Check Supabase CLI" "command -v supabase" "false"

# 2. Database Connectivity Tests
echo ""
echo "🗄️  2. Database Connectivity Tests"
echo "================================="

if [ -f .env.local ]; then
    source .env.local
    run_test "Check Supabase URL format" "echo '$SUPABASE_URL' | grep -q 'https://'" "true"
    run_test "Check Supabase service key exists" "[ ! -z '$SUPABASE_SERVICE_ROLE_KEY' ]" "true"
else
    echo "⚠️  Skipping database tests - .env.local not found"
    ((SKIPPED+=2))
fi

# 3. Scraper Integration Tests
echo ""
echo "🕷️  3. Scraper Integration Tests"
echo "================================"

run_test "Check scrapers directory" "[ -d scrapers ]" "true"
run_test "Check orchestrator exists" "[ -f scrapers/orchestrator.py ]" "true"
run_test "Check base interface" "[ -f scrapers/base/scraper_interface.py ]" "true"
run_test "Check utilities" "[ -d scrapers/utils ]" "true"

# Run Python integration test if available
if [ -f scripts/test_scraper_integration.py ]; then
    run_test_with_output "Run scraper integration test" "python3 scripts/test_scraper_integration.py" "false"
else
    echo "⚠️  Skipping scraper integration test - script not found"
    ((SKIPPED++))
fi

# 4. Airflow DAG Tests
echo ""
echo "🛫 4. Airflow DAG Tests"
echo "======================="

run_test "Check DAG file exists" "[ -f airflow/dags/master_dag.py ]" "true"
run_test "Check DAG syntax" "python3 -c \"import sys; sys.path.append('airflow/dags'); import master_dag\"" "false"

# 5. Health Check Tests
echo ""
echo "🏥 5. Health Check Tests"
echo "======================="

run_test "Check health check script" "[ -f scripts/monitoring_health_checks.py ]" "true"

# Run health check if environment is available
if [ -f .env.local ]; then
    run_test_with_output "Run health check" "python3 scripts/monitoring_health_checks.py" "false"
else
    echo "⚠️  Skipping health check - .env.local not found"
    ((SKIPPED++))
fi

# 6. CI/CD Pipeline Tests
echo ""
echo "🔄 6. CI/CD Pipeline Tests"
echo "=========================="

run_test "Check GitHub Actions workflow" "[ -f .github/workflows/ci-cd.yml ]" "true"
run_test "Check migration CI hook" "[ -f database/ci_hook.sh ]" "true"
run_test "Check migration runner" "[ -f database/run_migrations.py ]" "true"

# 7. Migration Tests
echo ""
echo "🗃️  7. Migration Tests"
echo "======================"

run_test "Check migrations directory" "[ -d database/migrations ]" "true"
run_test "Check up migrations" "[ -d database/migrations/up ]" "true"
run_test "Check down migrations" "[ -d database/migrations/down ]" "true"
run_test "Check migration files exist" "ls database/migrations/up/*.sql >/dev/null 2>&1" "true"

# Summary
echo ""
echo "📊 Test Summary"
echo "==============="
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"
echo -e "${YELLOW}⚠️  Skipped: $SKIPPED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All required tests passed! Pipeline is ready for deployment.${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Please fix the issues before deploying.${NC}"
    echo ""
    echo "🔧 Next steps:"
    echo "1. Fix failed tests above"
    echo "2. Run smoke tests again"
    echo "3. Deploy to production"
    exit 1
fi 