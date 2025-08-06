# 🚀 Production Deployment - Quick Reference

## 📋 Pre-Deployment Checklist

### Environment Variables
```bash
# Required
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
export SUPABASE_ANON_KEY="your-anon-key"

# Optional
export ALERT_WEBHOOK_URL="https://hooks.slack.com/services/your/webhook"
export SENTRY_DSN="https://your-sentry-dsn"
export API_BASE_URL="https://your-api-domain.com"
export WEB_BASE_URL="https://your-web-domain.com"
```

### Prerequisites Check
```bash
# Check required software
docker --version
docker-compose --version
python3 --version
node --version

# Check environment variables
env | grep -E "(SUPABASE|ALERT|SENTRY|API|WEB)"
```

## 🎯 Deployment Commands

### 1. Pre-Flight Checks
```bash
# Dry run to validate configuration
python3 scripts/deploy_production.py --dry-run
```

### 2. Production Deployment
```bash
# Full production deployment
python3 scripts/deploy_production.py
```

### 3. Performance Testing
```bash
# Verify performance targets
python3 scripts/performance_testing.py
```

### 4. End-to-End Validation
```bash
# Complete validation
./scripts/run_immediate_steps.sh
```

### 5. Monitoring Setup
```bash
# Deploy monitoring infrastructure
./scripts/deploy_monitoring.sh
```

## ✅ Success Criteria

### Performance Targets
- ✅ P95 response time < 200ms
- ✅ Success rate > 99%
- ✅ All endpoints responding

### Monitoring Verification
- ✅ Grafana: http://localhost:3001 (admin/admin)
- ✅ Kibana: http://localhost:5601
- ✅ Prometheus: http://localhost:9090
- ✅ Airflow: http://localhost:8080 (admin/admin)

### Health Checks
```bash
# Manual health check
python3 monitoring/health_monitor.py

# Performance check
python3 monitoring/performance_monitor.py

# WebSocket check
python3 monitoring/websocket_monitor.py
```

## 🚨 Emergency Commands

### Service Status
```bash
# Check all services
docker-compose ps

# View logs
docker-compose logs [service_name]

# Restart services
docker-compose restart [service_name]
```

### Database Health
```bash
# Test database connectivity
python3 -c "
import os
import requests
headers = {'apikey': os.environ['SUPABASE_SERVICE_ROLE_KEY']}
response = requests.get(f'{os.environ[\"SUPABASE_URL\"]}/rest/v1/', headers=headers)
print('Database accessible:', response.status_code == 200)
"
```

### Performance Analysis
```bash
# Check slow queries
python3 monitoring/supabase_monitor.py

# Analyze performance
python3 monitoring/performance_monitor.py

# View metrics
curl http://localhost:9090/api/v1/query?query=up
```

## 📊 Monitoring Access

| Service | URL | Credentials | Purpose |
|---------|-----|-------------|---------|
| **Grafana** | http://localhost:3001 | admin/admin | Dashboards |
| **Kibana** | http://localhost:5601 | - | Logs |
| **Prometheus** | http://localhost:9090 | - | Metrics |
| **Airflow** | http://localhost:8080 | admin/admin | ETL |
| **API Health** | http://localhost:8000/health | - | Status |

## 🔧 Quick Fixes

### Common Issues

#### Performance Below Target
```bash
# Check database indexes
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

#### Monitoring Services Down
```bash
# Restart monitoring stack
docker-compose restart prometheus grafana elasticsearch kibana

# Check service logs
docker-compose logs grafana | tail -50
```

#### ETL Pipeline Issues
```bash
# Check Airflow DAGs
docker-compose exec airflow-webserver airflow dags list

# View DAG logs
docker-compose exec airflow-webserver airflow tasks logs casablanca_etl_pipeline fetch_ir_reports latest
```

## 📞 Support Contacts

- **System Admin**: admin@casablanca-insights.com
- **Database Admin**: dba@casablanca-insights.com
- **DevOps Team**: devops@casablanca-insights.com

## 📁 Key Files

- **Deployment Log**: `production_deployment.log`
- **Performance Results**: `performance_results/`
- **Monitoring Config**: `monitoring/`
- **Health Check Logs**: `monitoring/health_checks.log`
- **Performance Logs**: `monitoring/performance.log`

## 🎯 Deployment Checklist

- [ ] Environment variables set
- [ ] Pre-flight checks passed
- [ ] Production deployment completed
- [ ] Performance targets met (P95 < 200ms)
- [ ] E2E validation passed
- [ ] Monitoring deployed and active
- [ ] Health checks passing
- [ ] Alerts configured and tested
- [ ] Documentation updated
- [ ] Team notified of deployment

---

**🎉 Deployment Complete!** Your Casablanca Insights platform is now production-ready. 