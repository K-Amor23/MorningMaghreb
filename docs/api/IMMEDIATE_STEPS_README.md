# Casablanca Insights - Immediate Next Steps

This document provides instructions for executing the immediate next steps for the Casablanca Insights project: production deployment, performance testing, and end-to-end testing.

## 🚀 Quick Start

To run all immediate steps automatically:

```bash
# Set environment variables
export SUPABASE_URL="your_supabase_url"
export SUPABASE_SERVICE_ROLE_KEY="your_service_role_key"
export API_BASE_URL="http://localhost:8000"  # or your API URL
export WEB_BASE_URL="http://localhost:3000"  # or your web URL

# Run all steps
./scripts/run_immediate_steps.sh
```

## 📋 Prerequisites

### Required Software
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** for version control
- **PostgreSQL client** (pg_dump) for backups

### Required Environment Variables
```bash
# Supabase Configuration
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your_service_role_key"

# API Configuration
export API_BASE_URL="http://localhost:8000"  # FastAPI server
export WEB_BASE_URL="http://localhost:3000"  # Next.js frontend

# Optional: Alerting
export ALERT_WEBHOOK_URL="your_webhook_url"  # For deployment alerts
export HEALTH_CHECK_URL="http://localhost:8000/health"  # API health endpoint
```

### Python Dependencies
```bash
pip install requests asyncio aiohttp locust
```

### Node.js Dependencies
```bash
npm install -D @playwright/test
npx playwright install
```

## 🔧 Step-by-Step Execution

### Step 1: Production Deployment

#### Manual Execution
```bash
# Run production deployment
python3 scripts/deploy_production.py
```

#### What it does:
- ✅ **Pre-deployment verification**: Checks access, migration files, disk space
- ✅ **Production backup**: Creates database backup before changes
- ✅ **Schema migration**: Applies indexes and constraints
- ✅ **Schema verification**: Confirms changes were applied
- ✅ **Data verification**: Checks data migration success
- ✅ **Health checks**: Verifies API endpoints are working
- ✅ **Performance baseline**: Measures initial performance

#### Verification Commands
```bash
# Check schema changes
supabase db diff

# Verify data migration
curl -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
     "$SUPABASE_URL/rest/v1/companies?select=count"

# Check backups
ls -la backups/
```

### Step 2: Performance & Load Testing

#### Manual Execution
```bash
# Run performance testing
python3 scripts/performance_testing.py
```

#### What it does:
- ✅ **Basic performance tests**: Tests all endpoints with 78 companies
- ✅ **Load testing with Locust**: Simulates concurrent users
- ✅ **Database query analysis**: Identifies slow queries
- ✅ **Performance metrics**: P95, P99, success rates
- ✅ **Performance targets**: Validates against < 200ms P95 target

#### Performance Targets
- **P95 Response Time**: < 200ms
- **Success Rate**: > 99%
- **Average Response Time**: < 100ms

#### Load Test Configuration
```bash
# Locust configuration (generated automatically)
Users: 20
Spawn Rate: 5 users/second
Duration: 10 minutes
Endpoints: /summary, /trading, /reports, /news
```

### Step 3: End-to-End Testing

#### Manual Execution
```bash
cd apps/web

# Run E2E tests for specific companies
npx playwright test --grep "IAM"
npx playwright test --grep "ATW"
npx playwright test --grep "BCP"

# Run all E2E tests
npx playwright test

# View test report
npx playwright show-report
```

#### What it tests:
- ✅ **Company Summary Pages**: IAM, ATW, BCP
- ✅ **Trading Data Section**: Charts, price data, volume
- ✅ **Financial Reports Section**: Reports list, filtering
- ✅ **News Section**: News articles, sentiment filtering
- ✅ **Data Quality Badges**: Visual indicators
- ✅ **Error Handling**: Invalid tickers, network errors
- ✅ **Loading States**: Skeleton loaders, progress indicators
- ✅ **Responsive Design**: Mobile, tablet, desktop
- ✅ **Accessibility**: ARIA labels, keyboard navigation
- ✅ **Performance**: Load times, Core Web Vitals

## 📊 Expected Results

### Production Deployment
```
✅ Production deployment completed successfully!
✅ Schema verification passed
✅ Data migration verification passed (X companies found)
✅ Backups verification passed
✅ Health checks passed
✅ Performance baseline established
```

### Performance Testing
```
✅ Basic performance tests completed
✅ Load testing completed
✅ Query analysis completed

Performance Summary:
- Total Requests: 312 (78 companies × 4 endpoints)
- Success Rate: 99.5%
- Average Response Time: 85.2ms
- P95 Response Time: 156.7ms ✅ (meets target)
- P99 Response Time: 234.1ms
```

### End-to-End Testing
```
✅ E2E tests passed for IAM
✅ E2E tests passed for ATW
✅ E2E tests passed for BCP
✅ All E2E tests completed

Test Coverage:
- Company Summary Pages: ✅ 3/3 passed
- Trading Data Section: ✅ 6/6 passed
- Financial Reports Section: ✅ 6/6 passed
- News Section: ✅ 6/6 passed
- Error Handling: ✅ 2/2 passed
- Loading States: ✅ 1/1 passed
- Responsive Design: ✅ 2/2 passed
- Accessibility: ✅ 1/1 passed
- Performance: ✅ 1/1 passed
```

## 🔍 Monitoring & Verification

### Real-time Monitoring
```bash
# Monitor API health
curl $API_BASE_URL/health

# Monitor database performance
python3 -c "
import requests
headers = {'apikey': '$SUPABASE_SERVICE_ROLE_KEY'}
response = requests.get('$SUPABASE_URL/rest/v1/companies/IAM/summary', headers=headers)
print(f'Response time: {response.elapsed.total_seconds() * 1000:.2f}ms')
"
```

### Data Quality Verification
```bash
# Check data quality for specific company
curl -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
     "$SUPABASE_URL/rest/v1/companies?ticker=eq.IAM&select=data_quality"
```

### Performance Monitoring
```bash
# Monitor slow queries
python3 -c "
import requests
headers = {'apikey': '$SUPABASE_SERVICE_ROLE_KEY'}
response = requests.post('$SUPABASE_URL/rest/v1/rpc/exec_sql', 
                        headers=headers,
                        json={'sql': 'SELECT query, mean_time FROM pg_stat_statements WHERE mean_time > 100 ORDER BY mean_time DESC LIMIT 5;'})
print('Slow queries:', response.json())
"
```

## 🚨 Troubleshooting

### Common Issues

#### Production Deployment Fails
```bash
# Check Supabase credentials
curl -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" "$SUPABASE_URL/rest/v1/"

# Check disk space
df -h

# Check migration file
ls -la database/migration_001_indexes_constraints.sql
```

#### Performance Tests Fail
```bash
# Check API server is running
curl $API_BASE_URL/health

# Check network connectivity
ping $(echo $API_BASE_URL | sed 's|http://||' | sed 's|https://||' | cut -d: -f1)

# Check API response times manually
time curl $API_BASE_URL/api/companies/IAM/summary
```

#### E2E Tests Fail
```bash
# Check web server is running
curl $WEB_BASE_URL

# Check Playwright installation
npx playwright --version

# Run tests with debug output
npx playwright test --debug
```

### Performance Issues

#### High Response Times
1. **Check database indexes**: Verify migration was applied
2. **Check query plans**: Analyze slow queries
3. **Check connection pooling**: Monitor database connections
4. **Check caching**: Verify Redis/application caching

#### High Error Rates
1. **Check API logs**: Monitor error logs
2. **Check database connectivity**: Verify Supabase connection
3. **Check rate limiting**: Verify API limits
4. **Check data availability**: Verify company data exists

## 📈 Post-Deployment Monitoring

### 24-Hour Monitoring Checklist
- [ ] Monitor API response times every hour
- [ ] Check error rates and logs
- [ ] Verify data quality badges are accurate
- [ ] Monitor database performance
- [ ] Check Airflow DAG execution
- [ ] Verify backup creation

### Weekly Monitoring
- [ ] Run performance tests
- [ ] Analyze slow queries
- [ ] Review error logs
- [ ] Update monitoring dashboards
- [ ] Plan capacity scaling

## 📁 Generated Files

After running the scripts, you'll find:

```
Casablanca-Insights/
├── deployment.log                    # Production deployment logs
├── production_deployment_history.json # Deployment history
├── backups/                          # Database backups
│   ├── prod_backup_20240101_120000.sql
│   └── ...
├── performance_results/              # Performance test results
│   ├── basic_performance_20240101_120000.json
│   ├── query_analysis_20240101_120000.json
│   └── ...
├── load_test_results.html           # Locust load test report
├── load_test_results.csv            # Load test metrics
├── test_results/                    # Test results
│   └── immediate_steps_summary.md   # Summary report
└── apps/web/
    └── playwright-report/           # E2E test reports
        ├── index.html
        └── ...
```

## 🎯 Success Criteria

### Production Deployment ✅
- [ ] Schema migration applied successfully
- [ ] All indexes and constraints created
- [ ] Data migration verified
- [ ] Backups created and stored
- [ ] Health checks passed
- [ ] Performance baseline established

### Performance Testing ✅
- [ ] P95 response time < 200ms
- [ ] Success rate > 99%
- [ ] Load testing completed
- [ ] Slow queries identified
- [ ] Performance recommendations generated

### End-to-End Testing ✅
- [ ] All company pages load correctly (IAM, ATW, BCP)
- [ ] Charts render properly
- [ ] Reports and news sections populate
- [ ] Data quality badges match database status
- [ ] Error handling works correctly
- [ ] Responsive design functions
- [ ] Accessibility standards met

## 🔄 Next Steps After Completion

1. **Set up automated monitoring**
   - Configure alerts for performance degradation
   - Set up dashboards for key metrics
   - Implement automated health checks

2. **Expand test coverage**
   - Add more companies to E2E tests
   - Implement automated testing in CI/CD
   - Add integration tests for new features

3. **Performance optimization**
   - Implement caching strategies
   - Optimize database queries
   - Add CDN for static assets

4. **Scale infrastructure**
   - Plan for increased load
   - Implement horizontal scaling
   - Add load balancers

---

**Last Updated**: January 2024  
**Version**: 1.0  
**Status**: Ready for Execution 