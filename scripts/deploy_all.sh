#!/bin/bash
# Master Deployment Script
# This script orchestrates the complete deployment process

set -e

echo "🚀 Casablanca Insights - Complete Deployment"
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to run a step
run_step() {
    local step_name="$1"
    local script_path="$2"
    local required="$3"
    
    echo ""
    echo -e "${BLUE}🔄 Step: $step_name${NC}"
    echo "================================"
    
    if [ -f "$script_path" ]; then
        if bash "$script_path"; then
            echo -e "${GREEN}✅ $step_name completed successfully${NC}"
        else
            echo -e "${RED}❌ $step_name failed${NC}"
            if [ "$required" = "true" ]; then
                echo "This is a required step. Deployment cannot continue."
                exit 1
            else
                echo "This step is optional. Continuing with deployment..."
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  Script not found: $script_path${NC}"
        echo "Skipping this step..."
    fi
}

# Function to check prerequisites
check_prerequisites() {
    echo "🔍 Checking Prerequisites"
    echo "========================"
    
    local missing=0
    
    # Check for .env.local
    if [ ! -f ".env.local" ]; then
        echo -e "${RED}❌ .env.local not found${NC}"
        echo "Please create .env.local with your environment variables:"
        echo "  SUPABASE_URL=your_supabase_url"
        echo "  SUPABASE_SERVICE_KEY=your_service_key"
        echo "  SLACK_WEBHOOK_URL=your_slack_webhook (optional)"
        echo "  SMTP_HOST=your_smtp_host (optional)"
        echo "  SMTP_PORT=your_smtp_port (optional)"
        echo "  SMTP_USER=your_smtp_user (optional)"
        echo "  SMTP_PASSWORD=your_smtp_password (optional)"
        missing=1
    else
        echo -e "${GREEN}✅ .env.local found${NC}"
    fi
    
    # Check for required CLI tools
    if ! command -v vercel &> /dev/null; then
        echo -e "${YELLOW}⚠️  Vercel CLI not found (optional)${NC}"
    else
        echo -e "${GREEN}✅ Vercel CLI found${NC}"
    fi
    
    if ! command -v gh &> /dev/null; then
        echo -e "${YELLOW}⚠️  GitHub CLI not found (optional)${NC}"
    else
        echo -e "${GREEN}✅ GitHub CLI found${NC}"
    fi
    
    if ! command -v supabase &> /dev/null; then
        echo -e "${YELLOW}⚠️  Supabase CLI not found (optional)${NC}"
    else
        echo -e "${GREEN}✅ Supabase CLI found${NC}"
    fi
    
    if [ $missing -eq 1 ]; then
        echo ""
        echo -e "${RED}❌ Prerequisites not met. Please fix the issues above and try again.${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}✅ All prerequisites met!${NC}"
}

# Function to show deployment menu
show_menu() {
    echo ""
    echo "📋 Deployment Options"
    echo "===================="
    echo "1. Run smoke tests only"
    echo "2. Deploy to Vercel (environment variables)"
    echo "3. Sync to GitHub Secrets"
    echo "4. Deploy migrations to Supabase"
    echo "5. Setup Airflow DAG and connections"
    echo "6. Run complete deployment (all steps)"
    echo "7. Exit"
    echo ""
    read -p "Select an option (1-7): " choice
}

# Function to run complete deployment
run_complete_deployment() {
    echo ""
    echo -e "${BLUE}🚀 Starting Complete Deployment${NC}"
    echo "====================================="
    
    # Step 1: Smoke Tests
    run_step "Smoke Tests" "scripts/smoke_test_pipeline.sh" "true"
    
    # Step 2: Deploy to Vercel
    run_step "Deploy to Vercel" "scripts/deploy_to_vercel.sh" "false"
    
    # Step 3: Sync to GitHub Secrets
    run_step "Sync to GitHub Secrets" "scripts/sync_github_secrets.sh" "false"
    
    # Step 4: Deploy Supabase Migrations
    run_step "Deploy Supabase Migrations" "scripts/deploy_supabase_migrations.sh" "false"
    
    # Step 5: Setup Airflow
    run_step "Setup Airflow DAG" "scripts/setup_airflow_dag.sh" "false"
    
    echo ""
    echo -e "${GREEN}🎉 Deployment completed!${NC}"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Verify Vercel deployment at your project URL"
    echo "2. Check GitHub Actions for CI/CD pipeline"
    echo "3. Verify Supabase migrations in your database"
    echo "4. Test Airflow DAG in the Airflow UI"
    echo "5. Monitor health checks and alerts"
    echo ""
    echo "🔗 Useful Commands:"
    echo "  - View logs: tail -f logs/deployment.log"
    echo "  - Check health: python3 scripts/monitoring_health_checks.py"
    echo "  - Test scrapers: python3 scripts/test_scraper_integration.py"
    echo "  - Run migrations: python3 database/run_migrations.py up"
}

# Main script
main() {
    echo "Welcome to Casablanca Insights Deployment"
    echo "========================================"
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    # Show menu
    while true; do
        show_menu
        
        case $choice in
            1)
                run_step "Smoke Tests" "scripts/smoke_test_pipeline.sh" "true"
                ;;
            2)
                run_step "Deploy to Vercel" "scripts/deploy_to_vercel.sh" "false"
                ;;
            3)
                run_step "Sync to GitHub Secrets" "scripts/sync_github_secrets.sh" "false"
                ;;
            4)
                run_step "Deploy Supabase Migrations" "scripts/deploy_supabase_migrations.sh" "false"
                ;;
            5)
                run_step "Setup Airflow DAG" "scripts/setup_airflow_dag.sh" "false"
                ;;
            6)
                run_complete_deployment
                break
                ;;
            7)
                echo "Goodbye!"
                exit 0
                ;;
            *)
                echo "Invalid option. Please select 1-7."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run main function
main 