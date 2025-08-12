# 🚀 Production Deployment Guide - Casablanca Insights

This guide provides step-by-step instructions for deploying Casablanca Insights to production with comprehensive monitoring and alerting.

## 📋 Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended) or macOS
- **CPU**: 4+ cores
- **RAM**: 8GB+ 
- **Storage**: 50GB+ available space
- **Network**: Stable internet connection

### Software Requirements
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Python**: 3.8+
- **Node.js**: 16+
- **Git**: Latest version

### Environment Variables
```bash
# Required
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
export SUPABASE_ANON_KEY="your-anon-key"

# Optional but recommended
export ALERT_WEBHOOK_URL="https://hooks.slack.com/services/your/webhook"
export SENTRY_DSN="https://your-sentry-dsn"
export API_BASE_URL="https://your-api-domain.com"
export WEB_BASE_URL="https://your-web-domain.com"
```

## 🎯 Deployment Steps

### Step 1: Pre-Flight Checks

Run comprehensive pre-deployment verification:

```bash
# Clone repository (if not already done)
git clone https://github.com/your-org/casablanca-insights.git
cd casablanca-insights

# Run pre-flight checks
python3 scripts/deploy_production.py --dry-run
```

**Expected Output:**
```
🔍 DRY RUN MODE - Validating configuration...
   Total companies: 78
   Companies with IR URLs: 78
   Batch size: 10
   Max concurrent: 10
   ✅ All companies have IR URLs configured
```

### Step 2: Production Deployment

Deploy the complete application stack:

```bash
# Run production deployment
python3 scripts/deploy_production.py
```

**This will:**
- ✅ Create production backups
- ✅ Run database migrations
- ✅ Verify schema changes
- ✅ Validate data migration
- ✅ Run health checks
- ✅ Establish performance baseline

### Step 3: Performance Testing

Verify performance meets production standards:

```bash
# Run comprehensive performance tests
python3 scripts/performance_testing.py
```

**Success Criteria:**
- ✅ P95 response time < 200ms
- ✅ Success rate > 99%
- ✅ All endpoints responding correctly

### Step 4: End-to-End Validation

Run complete E2E testing:

```bash
# Execute immediate steps for validation
./scripts/run_immediate_steps.sh
```

**This validates:**
- ✅ Production deployment
- ✅ Performance benchmarks
- ✅ E2E functionality
- ✅ Data quality

### Step 5: Monitoring Setup

Deploy comprehensive monitoring infrastructure:

```bash
# Setup complete monitoring
./scripts/deploy_monitoring.sh
```

**This deploys:**
- 📊 **Grafana**: Dashboards and visualization
- 📈 **Prometheus**: Metrics collection
- 📝 **Elasticsearch + Kibana**: Log analysis
- 🔔 **Alerting**: Slack/email notifications
- 🏥 **Health Checks**: Automated monitoring

## 📊 Monitoring & Alerting

### Access Points

| Service | URL | Credentials | Purpose |
|---------|-----|-------------|---------|
| **Grafana** | http://localhost:3001 | admin/admin | Dashboards & Metrics |
| **Kibana** | http://localhost:5601 | - | Log Analysis |
| **Prometheus** | http://localhost:9090 | - | Metrics Storage |
| **Airflow** | http://localhost:8080 | admin/admin | ETL Pipeline |
| **API Health** | http://localhost:8000/health | - | API Status |

### Key Dashboards

1. **API Performance Dashboard**
   - Response times by endpoint
   - Request rates and error rates
   - P95/P99 latency metrics

2. **Database Performance Dashboard**
   - Query performance
   - Connection pool status
   - Slow query analysis

3. **ETL Pipeline Dashboard**
   - DAG success rates
   - Job duration trends
   - Data freshness metrics

4. **WebSocket Dashboard**
   - Connection counts
   - Message rates
   - Latency metrics

### Automated Alerts

#### Critical Alerts (Immediate Action Required)
- 🔴 **API Down**: Service unavailable
- 🔴 **Database Connection Failed**: Cannot connect to Supabase
- 🔴 **ETL Pipeline Failure**: DAG execution failed
- 🔴 **High Error Rate**: >5% error rate for 5 minutes

#### Warning Alerts (Monitor Closely)
- 🟡 **High Response Time**: P95 > 200ms
- 🟡 **High CPU/Memory**: >80% resource usage
- 🟡 **SLA Miss**: ETL pipeline exceeded deadline
- 🟡 **Data Freshness**: Data older than 24 hours

#### Info Alerts (For Awareness)
- 🔵 **Successful Deployment**: New version deployed
- 🔵 **Backup Completed**: Database backup successful
- 🔵 **Performance Target Met**: P95 < 200ms achieved

## 🔧 Configuration

### Environment Configuration

Create `.env` file in project root:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key

# API Configuration
API_BASE_URL=https://your-api-domain.com
WEB_BASE_URL=https://your-web-domain.com

# Monitoring Configuration
ALERT_WEBHOOK_URL=https://hooks.slack.com/services/your/webhook
SENTRY_DSN=https://your-sentry-dsn

# Airflow Configuration
AIRFLOW_UID=50000
AIRFLOW_GID=0

# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/postgres

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
```

### Monitoring Configuration

Update monitoring thresholds in `monitoring/health_checks.json`:

```json
{
  "checks": [
    {
      "name": "API Response Time",
      "type": "performance",
      "threshold_ms": 200
    },
    {
      "name": "Database Connectivity",
      "type": "connectivity",
      "timeout_seconds": 5
    },
    {
      "name": "Disk Space",
      "type": "system",
      "threshold_gb": 5.0
    }
  ]
}
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Production Deployment Fails

**Symptoms:**
- Migration errors
- Health check failures
- Performance below targets

**Solutions:**
```bash
# Check deployment logs
tail -f production_deployment.log

# Verify environment variables
env | grep SUPABASE

# Test database connectivity
python3 -c "
import os
import requests
headers = {'apikey': os.environ['SUPABASE_SERVICE_ROLE_KEY']}
response = requests.get(f'{os.environ[\"SUPABASE_URL\"]}/rest/v1/', headers=headers)
print('Database accessible:', response.status_code == 200)
"
```

#### 2. Performance Below Targets

**Symptoms:**
- P95 response time > 200ms
- High error rates
- Slow database queries

**Solutions:**
```bash
# Analyze slow queries
python3 monitoring/supabase_monitor.py

# Check performance metrics
python3 monitoring/performance_monitor.py

# Review database indexes
python3 -c "
import os
import requests
headers = {'apikey': os.environ['SUPABASE_SERVICE_ROLE_KEY']}
response = requests.post(
    f'{os.environ[\"SUPABASE_URL\"]}/rest/v1/rpc/exec_sql',
    headers=headers,
    json={'sql': 'SELECT indexname FROM pg_indexes WHERE schemaname = \\'public\\''}
)
print('Indexes:', response.json())
"
```

#### 3. Monitoring Services Not Starting

**Symptoms:**
- Grafana/Kibana not accessible
- Prometheus metrics missing
- Alerts not working

**Solutions:**
```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs grafana
docker-compose logs prometheus
docker-compose logs elasticsearch

# Restart monitoring services
docker-compose restart prometheus grafana elasticsearch kibana
```

#### 4. ETL Pipeline Failures

**Symptoms:**
- Airflow DAG failures
- Data not updating
- Missing financial reports

**Solutions:**
```bash
# Check Airflow status
docker-compose exec airflow-webserver airflow dags list

# View DAG logs
docker-compose exec airflow-webserver airflow tasks logs casablanca_etl_pipeline fetch_ir_reports latest

# Test individual tasks
docker-compose exec airflow-webserver airflow tasks test casablanca_etl_pipeline fetch_ir_reports $(date +%Y-%m-%d)
```

## 📈 Performance Optimization

### Database Optimization

1. **Index Optimization**
```sql
-- Add missing indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_companies_ticker ON companies(ticker);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_company_prices_ticker_date ON company_prices(ticker, date);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_company_reports_ticker_type ON company_reports(ticker, report_type);
```

2. **Query Optimization**
```sql
-- Analyze slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements 
WHERE mean_time > 100
ORDER BY mean_time DESC;
```

### API Optimization

1. **Caching Strategy**
```python
# Implement Redis caching
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_data(key, ttl=300):
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

def set_cached_data(key, data, ttl=300):
    redis_client.setex(key, ttl, json.dumps(data))
```

2. **Connection Pooling**
```python
# Optimize database connections
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

## 🔄 Maintenance

### Daily Tasks

1. **Health Check Review**
```bash
# Review health check logs
tail -100 monitoring/health_checks.log | grep -E "(ERROR|WARNING|CRITICAL)"
```

2. **Performance Review**
```bash
# Check performance trends
python3 monitoring/performance_monitor.py
```

3. **Alert Review**
```bash
# Check for active alerts
curl -s http://localhost:3001/api/alerts | jq '.[] | select(.state == "alerting")'
```

### Weekly Tasks

1. **Performance Analysis**
```bash
# Generate weekly performance report
python3 scripts/generate_performance_report.py --period=weekly
```

2. **Database Maintenance**
```sql
-- Analyze table statistics
ANALYZE companies;
ANALYZE company_prices;
ANALYZE company_reports;

-- Clean up old data
DELETE FROM company_prices WHERE date < NOW() - INTERVAL '2 years';
```

3. **Log Rotation**
```bash
# Rotate log files
logrotate /etc/logrotate.d/casablanca-insights
```

### Monthly Tasks

1. **Dashboard Review**
- Review and update Grafana dashboards
- Add new metrics as needed
- Optimize dashboard queries

2. **Alert Threshold Review**
- Review alert thresholds
- Adjust based on performance trends
- Add new alert rules if needed

3. **Capacity Planning**
- Review resource usage trends
- Plan for scaling if needed
- Update monitoring thresholds

## 📞 Support

### Emergency Contacts

- **System Administrator**: admin@casablanca-insights.com
- **Database Administrator**: dba@casablanca-insights.com
- **DevOps Team**: devops@casablanca-insights.com

### Escalation Procedures

1. **Level 1**: Automated monitoring detects issue
2. **Level 2**: Manual investigation required
3. **Level 3**: Emergency response team activated

### Documentation

- **API Documentation**: https://your-api-domain.com/docs
- **Monitoring Documentation**: `monitoring/monitoring_summary.md`
- **Troubleshooting Guide**: This document
- **Performance Reports**: `performance_results/`

## 🎉 Success Criteria

Your production deployment is successful when:

✅ **Performance Targets Met**
- P95 response time < 200ms
- Success rate > 99%
- All endpoints responding correctly

✅ **Monitoring Active**
- All monitoring services running
- Dashboards populated with data
- Alerts configured and tested

✅ **Data Quality**
- All 78 companies have data
- Financial reports up to date
- ETL pipeline running successfully

✅ **Operational Readiness**
- Health checks passing
- Backups configured
- Documentation complete

---

**🎯 Congratulations!** Your Casablanca Insights platform is now production-ready with comprehensive monitoring and alerting.

**📋 Next Steps:**
1. Monitor the system closely for the first 24 hours
2. Review performance metrics daily
3. Set up regular maintenance schedules
4. Plan for future scaling and enhancements 