# 🚀 Casablanca Insights - Complete Deployment Guide

## 📋 Overview

This guide walks you through deploying the complete Casablanca Insights pipeline to production. All steps are automated with scripts, but you can also run them manually.

## 🛠️ Prerequisites

### Required Tools
- **Vercel CLI**: `npm i -g vercel`
- **GitHub CLI**: Install from https://cli.github.com/
- **Supabase CLI**: `npm install -g supabase`

### Required Environment Variables
Create a `.env.local` file with:

```bash
# Required
SUPABASE_URL=postgresql://postgres:[password]@[host]:5432/postgres
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Optional (for notifications)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook
SMTP_HOST=your_smtp_host
SMTP_PORT=587
SMTP_USER=your_smtp_user
SMTP_PASSWORD=your_smtp_password
```

## 🚀 Quick Deployment

### Option 1: Automated Deployment (Recommended)
```bash
# Run the master deployment script
./scripts/deploy_all.sh
```

This will guide you through all deployment steps with a menu interface.

### Option 2: Step-by-Step Deployment

#### Step 1: Smoke Tests
```bash
./scripts/smoke_test_pipeline.sh
```
This validates all components before deployment.

#### Step 2: Deploy to Vercel
```bash
# Sync environment variables to Vercel
./scripts/deploy_to_vercel.sh
```

#### Step 3: Sync to GitHub Secrets
```bash
# Create GitHub Actions secrets from .env.local
./scripts/sync_github_secrets.sh
```

#### Step 4: Deploy Supabase Migrations
```bash
# Apply database migrations
./scripts/deploy_supabase_migrations.sh
```

#### Step 5: Setup Airflow DAG
```bash
# Configure Airflow with DAG and connections
./scripts/setup_airflow_dag.sh
```

## 📊 Manual Deployment Steps

### 1. Sync to Vercel

If you have the Vercel CLI set up and your project linked:

```bash
# Pull current environment variables
vercel env pull .env.local

# Push local variables to Vercel
vercel env import .env.local
```

### 2. Sync to GitHub Secrets

Using GitHub CLI:

```bash
# Loop through .env.local and create secrets
while IFS='=' read -r name value; do
  # Skip blank lines or comments
  [[ -z "$name" || "$name" =~ ^# ]] && continue
  
  # Create/update the secret
  gh secret set "$name" --body "$value"
done < .env.local
```

### 3. Deploy Migrations to Supabase

```bash
# Authenticate Supabase CLI
supabase login

# Link to your project
supabase link --project-ref YOUR_PROJECT_REF

# Apply migrations
supabase db push

# Verify schema
supabase db diff
```

### 4. Install & Configure Airflow DAG

#### Copy DAG to Airflow
```bash
# Copy the DAG to your Airflow dags folder
cp airflow/dags/master_dag.py /path/to/airflow/dags/
```

#### Add Supabase Connection
In Airflow UI or via CLI:
```bash
airflow connections add supabase_default \
  --conn-uri "postgresql://postgres:password@host:5432/postgres"
```

#### Add Variables
```bash
airflow variables set SUPABASE_URL "your_supabase_url"
airflow variables set SUPABASE_SERVICE_KEY "your_service_key"
airflow variables set SLACK_WEBHOOK_URL "your_slack_webhook"
```

#### Restart Airflow Services
```bash
systemctl restart airflow-scheduler
systemctl restart airflow-webserver
```

### 5. Enable CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci-cd.yml`) is already configured with:

- **Lint & Test**: Python/Node.js linting and unit tests
- **Migration Check**: Database migration validation
- **Security Scan**: Bandit and npm audit
- **Build Web**: Next.js build verification
- **Integration Tests**: End-to-end testing
- **Docs Build**: Documentation generation
- **Deploy**: Production deployment (main branch)
- **Performance Test**: Load testing
- **Dependency Update**: Automated dependency updates

### 6. Final Smoke Tests & Monitoring

#### End-to-End Run
1. In Airflow UI, trigger the `master_dag` manually
2. Watch all tasks complete successfully
3. Query Supabase to confirm new data

#### Health Check Endpoint
```bash
# Test health endpoint
curl $PIPELINE_URL/health
```

#### Test Alerts
```bash
# Run health checks
python3 scripts/monitoring_health_checks.py
```

## 🔍 Verification Checklist

### ✅ Environment Setup
- [ ] `.env.local` exists with all required variables
- [ ] Vercel CLI installed and authenticated
- [ ] GitHub CLI installed and authenticated
- [ ] Supabase CLI installed and authenticated

### ✅ Vercel Deployment
- [ ] Environment variables synced to Vercel
- [ ] Web application deploys successfully
- [ ] All environment variables available in Vercel dashboard

### ✅ GitHub Secrets
- [ ] All secrets created in GitHub repository
- [ ] CI/CD pipeline can access secrets
- [ ] GitHub Actions run without authentication errors

### ✅ Supabase Database
- [ ] Project linked to Supabase CLI
- [ ] All migrations applied successfully
- [ ] Database schema matches migrations
- [ ] Sample data inserted correctly

### ✅ Airflow DAG
- [ ] DAG file copied to Airflow dags folder
- [ ] Supabase connection configured
- [ ] All variables set in Airflow
- [ ] DAG appears in Airflow UI
- [ ] Manual trigger runs successfully

### ✅ CI/CD Pipeline
- [ ] GitHub Actions workflow enabled
- [ ] All jobs run successfully
- [ ] Migration checks pass
- [ ] Security scans complete
- [ ] Build process succeeds

### ✅ Monitoring & Alerts
- [ ] Health checks run successfully
- [ ] Monitoring script reports healthy status
- [ ] Alerts configured (Slack/email)
- [ ] Test alerts trigger correctly

## 🚨 Troubleshooting

### Common Issues

#### Vercel CLI Not Found
```bash
npm install -g vercel
vercel login
```

#### GitHub CLI Authentication
```bash
gh auth login
gh auth status
```

#### Supabase CLI Issues
```bash
npm install -g supabase
supabase login
supabase link --project-ref YOUR_PROJECT_REF
```

#### Airflow Connection Issues
- Verify Supabase URL format
- Check database credentials
- Ensure Airflow can reach Supabase host

#### Migration Failures
```bash
# Reset and reapply
supabase db reset
supabase db push
```

#### CI/CD Pipeline Failures
- Check GitHub secrets are set correctly
- Verify workflow file syntax
- Check for missing dependencies

## 📞 Support

### Useful Commands
```bash
# Check system health
python3 scripts/monitoring_health_checks.py

# Test scraper integration
python3 scripts/test_scraper_integration.py

# Run smoke tests
./scripts/smoke_test_pipeline.sh

# View deployment logs
tail -f logs/deployment.log

# Check Airflow DAG status
airflow dags list
airflow tasks list master_dag
```

### Monitoring URLs
- **Vercel**: Your project URL
- **GitHub Actions**: `https://github.com/your-repo/actions`
- **Supabase**: `https://supabase.com/dashboard/project/YOUR_PROJECT_REF`
- **Airflow**: Your Airflow UI URL

## 🎉 Success!

Once all steps are completed successfully, your Casablanca Insights pipeline will be:

- ✅ **Fully Automated**: Daily data collection and processing
- ✅ **Monitored**: Health checks and alerting
- ✅ **Scalable**: Modular architecture ready for growth
- ✅ **Reliable**: CI/CD pipeline with quality gates
- ✅ **Production Ready**: Comprehensive testing and validation

The system will automatically collect data daily, process it through the scrapers, store it in Supabase, and provide insights through the web application. 