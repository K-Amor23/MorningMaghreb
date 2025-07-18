# Casablanca Insights Data Pipeline - Deployment Guide

## 🚀 **Complete End-to-End Data Pipeline Overview**

Your existing Casablanca Insights scraper has been enhanced into a full production-ready data pipeline with the following components:

### **Pipeline Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Scraping  │───▶│  PDF Extraction │───▶│  GAAP Mapping   │───▶│   Data Storage  │
│   (Bronze Layer)│    │   & Cleaning    │    │   & Validation  │    │   (Silver Layer)│
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
    Local Storage           Structured Data         GAAP-Compliant         PostgreSQL
    (Raw HTML/PDF)         (Normalized)            Financial Data         + Redis Cache
```

### **Enhanced Components**

1. **✅ Scrape & Ingest**: Enhanced web scraping with robots.txt compliance
2. **✅ Parse & Structure**: Advanced PDF extraction with table recognition
3. **✅ PDF Extraction & GAAP Mapping**: French to US GAAP translation
4. **✅ Store & Version**: Database schema with audit trails
5. **✅ API Layer**: FastAPI with Redis caching
6. **✅ Deployment & Scheduling**: Docker + Cron/Airflow integration
7. **✅ Monitoring & Alerts**: Health checks and dashboards

## 📋 **Prerequisites**

### **System Requirements**
- Docker & Docker Compose
- 8GB RAM minimum (16GB recommended)
- 50GB storage space
- Python 3.9+

### **External Services**
- Supabase account (for authentication)
- Redis instance (or use included Docker container)
- PostgreSQL database (or use included Docker container)

## 🛠️ **Installation & Setup**

### **1. Environment Configuration**

Create `.env` file in `apps/backend/`:

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/casablanca_insights
REDIS_URL=redis://localhost:6379

# Supabase (for authentication)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=production

# ETL Configuration
ETL_BATCH_SIZE=10
ETL_MAX_RETRIES=3
ETL_TIMEOUT=300

# Monitoring
SENTRY_DSN=your_sentry_dsn
PROMETHEUS_PORT=9090

# Email (for alerts)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### **2. Install Dependencies**

```bash
cd apps/backend
pip install -r requirements_enhanced.txt
```

### **3. Database Setup**

```bash
# Run database migrations
alembic upgrade head

# Or manually run schema files
psql -d casablanca_insights -f database/schema.sql
psql -d casablanca_insights -f database/currency_schema.sql
```

## 🐳 **Docker Deployment**

### **Quick Start with Docker Compose**

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f api
```

### **Services Overview**

| Service | Port | Purpose |
|---------|------|---------|
| API | 8000 | FastAPI backend |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Caching |
| Celery Worker | - | Background tasks |
| Celery Beat | - | Scheduled tasks |
| Flower | 5555 | Celery monitoring |
| Nginx | 80/443 | Reverse proxy |
| Prometheus | 9090 | Metrics collection |
| Grafana | 3001 | Dashboards |
| Elasticsearch | 9200 | Log storage |
| Kibana | 5601 | Log visualization |

### **Production Deployment**

```bash
# Build and start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale workers if needed
docker-compose up -d --scale celery_worker=3
```

## 🔧 **Pipeline Configuration**

### **Scheduler Configuration**

The pipeline scheduler runs automatically with the following schedule:

- **Daily Scrape**: 6:00 AM - Check for new reports
- **Weekly Cleanup**: Sunday 2:00 AM - Clean old data
- **Monthly Full Sync**: 1st of month 3:00 AM - Complete refresh
- **Cache Refresh**: Every 30 minutes - Refresh API cache

### **ETL Pipeline Steps**

1. **Fetch Reports**: Scrape company IR pages
2. **Download PDFs**: Download financial reports
3. **Extract Data**: Parse tables and text from PDFs
4. **Clean & Normalize**: Standardize data formats
5. **Translate to GAAP**: Convert French labels to US GAAP
6. **Compute Ratios**: Calculate financial ratios
7. **Store Data**: Save to database with audit trail

## 📊 **Monitoring & Health Checks**

### **Health Check Endpoints**

```bash
# Overall health
curl http://localhost:8000/health

# ETL pipeline health
curl http://localhost:8000/api/etl/health

# Detailed dashboard
curl http://localhost:8000/api/etl/dashboard
```

### **Monitoring Dashboards**

- **Grafana**: http://localhost:3001 (admin/admin)
- **Flower**: http://localhost:5555 (Celery monitoring)
- **Kibana**: http://localhost:5601 (Log analysis)

### **Key Metrics**

- Pipeline success rate
- Data freshness
- API response times
- Storage usage
- Failed job count

## 🔌 **API Usage**

### **Trigger Pipeline**

```bash
# Trigger for specific companies
curl -X POST "http://localhost:8000/api/etl/trigger-pipeline" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"companies": ["ATW", "IAM"], "year": 2024}'

# Trigger for all companies
curl -X POST "http://localhost:8000/api/etl/trigger-pipeline" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Get Pipeline Status**

```bash
# List all jobs
curl "http://localhost:8000/api/etl/jobs" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get specific job
curl "http://localhost:8000/api/etl/jobs/job_id" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Get Financial Data**

```bash
# Get company financials
curl "http://localhost:8000/api/etl/financials/ATW" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get with filters
curl "http://localhost:8000/api/etl/financials/ATW?year=2024&quarter=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🚨 **Alerting & Notifications**

### **Alert Types**

- **Critical**: Pipeline failures, database connectivity issues
- **Warning**: Data freshness issues, high error rates
- **Info**: Successful completions, system updates

### **Alert Channels**

- Email notifications
- Slack webhooks
- SMS (via Twilio)
- Webhook endpoints

### **Configure Alerts**

```python
# Add custom alert handler
from monitoring.health_checks import health_monitor

async def custom_alert_handler(alert_message):
    # Send to your preferred channel
    pass

health_monitor.add_alert_handler(custom_alert_handler)
```

## 🔄 **Scheduling & Orchestration**

### **Manual Pipeline Execution**

```bash
# Start scheduler
curl -X POST "http://localhost:8000/api/etl/scheduler/start" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Stop scheduler
curl -X POST "http://localhost:8000/api/etl/scheduler/stop" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get scheduler status
curl "http://localhost:8000/api/etl/scheduler/status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Custom Scheduling**

```python
# Add custom scheduled job
from etl.scheduler import scheduler

async def custom_job():
    # Your custom logic
    pass

scheduler.scheduler.add_job(
    custom_job,
    'cron',
    hour=14,
    minute=30,
    id='custom_job'
)
```

## 🗄️ **Data Management**

### **Cache Management**

```bash
# Get cache stats
curl "http://localhost:8000/api/etl/cache/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Clear specific cache
curl -X POST "http://localhost:8000/api/etl/cache/clear?pattern=api:financials:*" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Clear all cache
curl -X POST "http://localhost:8000/api/etl/cache/clear" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Data Cleanup**

```bash
# Clean old data
curl -X POST "http://localhost:8000/api/etl/cleanup?days_old=30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔒 **Security & Authentication**

### **API Authentication**

All endpoints require Bearer token authentication:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/etl/jobs
```

### **Environment Security**

- Use strong database passwords
- Enable SSL/TLS in production
- Configure firewall rules
- Regular security updates

## 📈 **Performance Optimization**

### **Caching Strategy**

- **Market Data**: 1-5 minutes TTL
- **Financial Data**: 1 hour TTL
- **Company Profiles**: 24 hours TTL
- **ETL Jobs**: 5 minutes TTL

### **Database Optimization**

- Index frequently queried columns
- Partition large tables by date
- Regular VACUUM and ANALYZE
- Connection pooling

### **Scaling**

```bash
# Scale API instances
docker-compose up -d --scale api=3

# Scale Celery workers
docker-compose up -d --scale celery_worker=5

# Add Redis cluster for high availability
```

## 🐛 **Troubleshooting**

### **Common Issues**

1. **Pipeline Fails**
   ```bash
   # Check logs
   docker-compose logs celery_worker
   
   # Check job status
   curl "http://localhost:8000/api/etl/jobs?status=failed"
   ```

2. **Database Connection Issues**
   ```bash
   # Check database health
   docker-compose exec postgres pg_isready
   
   # Check connection string
   echo $DATABASE_URL
   ```

3. **Cache Issues**
   ```bash
   # Check Redis
   docker-compose exec redis redis-cli ping
   
   # Clear cache
   curl -X POST "http://localhost:8000/api/etl/cache/clear"
   ```

### **Log Analysis**

```bash
# View all logs
docker-compose logs

# Follow specific service
docker-compose logs -f api

# Search logs
docker-compose logs | grep "ERROR"
```

## 📚 **Next Steps**

### **Immediate Actions**

1. **Test the Pipeline**: Run a small test with one company
2. **Monitor Health**: Set up alerting for critical issues
3. **Configure Caching**: Optimize cache TTLs for your use case
4. **Set Up Monitoring**: Configure Grafana dashboards

### **Future Enhancements**

1. **Machine Learning**: Add ML models for data validation
2. **Real-time Processing**: Implement streaming data pipeline
3. **Advanced Analytics**: Add predictive analytics
4. **Multi-language Support**: Extend to other languages
5. **Cloud Deployment**: Deploy to AWS/GCP/Azure

### **Production Checklist**

- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] SSL certificates installed
- [ ] Monitoring dashboards set up
- [ ] Alerting configured
- [ ] Backup strategy implemented
- [ ] Security audit completed
- [ ] Performance testing done
- [ ] Documentation updated

## 🆘 **Support**

For issues and questions:

1. Check the logs: `docker-compose logs`
2. Review health status: `/api/etl/health`
3. Check monitoring dashboards
4. Review this documentation

The enhanced pipeline is now production-ready with full monitoring, scheduling, and caching capabilities! 