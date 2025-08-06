#!/bin/bash
# Simple Smoke Test
# Quick validation of key components

set -e

echo "🧪 Simple Smoke Test"
echo "==================="

# Test 1: Environment
echo "1. Testing Environment..."
if [ -f .env.local ]; then
    echo "✅ .env.local exists"
    if grep -q 'SUPABASE_URL' .env.local && grep -q 'SUPABASE_SERVICE_ROLE_KEY' .env.local; then
        echo "✅ Required environment variables found"
    else
        echo "❌ Missing required environment variables"
        exit 1
    fi
else
    echo "❌ .env.local not found"
    exit 1
fi

# Test 2: Scrapers
echo ""
echo "2. Testing Scrapers..."
if [ -d scrapers ]; then
    echo "✅ scrapers directory exists"
    if [ -f scrapers/orchestrator.py ]; then
        echo "✅ orchestrator.py exists"
    else
        echo "❌ orchestrator.py not found"
        exit 1
    fi
else
    echo "❌ scrapers directory not found"
    exit 1
fi

# Test 3: Database migrations
echo ""
echo "3. Testing Database Migrations..."
if [ -d database/migrations ]; then
    echo "✅ migrations directory exists"
    if ls database/migrations/up/*.sql >/dev/null 2>&1; then
        echo "✅ migration files found"
    else
        echo "❌ no migration files found"
        exit 1
    fi
else
    echo "❌ migrations directory not found"
    exit 1
fi

# Test 4: Airflow DAG
echo ""
echo "4. Testing Airflow DAG..."
if [ -f airflow/dags/master_dag.py ]; then
    echo "✅ master_dag.py exists"
else
    echo "❌ master_dag.py not found"
    exit 1
fi

# Test 5: CI/CD
echo ""
echo "5. Testing CI/CD..."
if [ -f .github/workflows/ci-cd.yml ]; then
    echo "✅ CI/CD workflow exists"
else
    echo "❌ CI/CD workflow not found"
    exit 1
fi

# Test 6: Health checks
echo ""
echo "6. Testing Health Checks..."
if [ -f scripts/monitoring_health_checks.py ]; then
    echo "✅ health checks script exists"
else
    echo "❌ health checks script not found"
    exit 1
fi

echo ""
echo "🎉 All smoke tests passed!"
echo "System is ready for deployment." 