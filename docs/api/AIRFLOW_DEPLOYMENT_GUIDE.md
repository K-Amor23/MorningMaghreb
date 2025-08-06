# 🚀 Airflow ETL Pipeline Deployment Guide

## **First Milestone: Automated Daily ETL Pipeline with Airflow**

This guide will help you deploy an **Apache Airflow DAG** that automates your Casablanca Insights ETL pipeline with daily scheduling and success/failure alerts.

## 📋 **What We're Building**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Airflow DAG    │───▶│  Fetch Reports  │───▶│  Extract PDFs   │───▶│  Translate GAAP │
│  (Daily 6AM)    │    │  (IR Websites)  │    │  (Financial)    │    │  (French→US)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
    Success Alert          Downloaded Files        Extracted Data         GAAP Data
    Failure Alert         (Bronze Layer)          (Structured)           (Validated)
```

## 🎯 **Pipeline Tasks**

1. **`fetch_ir_reports`**: Scrape company IR pages, download PDFs
2. **`extract_pdf_data`**: Extract financial data from PDFs using your existing extractor
3. **`translate_to_gaap`**: Translate French labels to US GAAP using your translator
4. **`store_data`**: Store processed data in your database
5. **`validate_data`**: Run GAAP validation checks
6. **`send_success_alert`**: Send success notification (Slack/Email)
7. **`send_failure_alert`**: Send failure notification if any task fails

## 🛠️ **Prerequisites**

- Docker & Docker Compose
- 4GB RAM minimum (8GB recommended)
- 10GB disk space
- Internet connection for downloading reports

## 🚀 **Quick Start**

### **1. Navigate to Airflow Directory**

```bash
cd apps/backend/airflow
```

### **2. Run Setup Script**

```bash
chmod +x setup_airflow.sh
./setup_airflow.sh
```

This script will:
- ✅ Check dependencies
- ✅ Create necessary directories
- ✅ Set up environment variables
- ✅ Initialize Airflow database
- ✅ Start all services
- ✅ Configure Airflow variables
- ✅ Test the DAG

### **3. Access Airflow UI**

- **URL**: http://localhost:8080
- **Username**: `admin`
- **Password**: `admin`

## 📊 **DAG Configuration**

### **Schedule**
- **Frequency**: Daily at 6:00 AM UTC
- **Timezone**: UTC
- **Retries**: 3 attempts with 5-minute delays

### **Companies**
Default companies to process:
- ATW (Attijariwafa Bank)
- IAM (Maroc Telecom)
- BCP (Banque Centrale Populaire)
- BMCE (BMCE Bank)

### **Configuration Variables**
```bash
# Set via Airflow UI or CLI
ETL_COMPANIES=["ATW", "IAM", "BCP", "BMCE"]
ETL_BATCH_SIZE=10
ETL_MAX_RETRIES=3
ENVIRONMENT=production
```

## 🔧 **Manual Setup (Alternative)**

If you prefer manual setup:

### **1. Create Environment File**

```bash
# Create .env file
cat > .env << EOF
AIRFLOW_UID=50000
_AIRFLOW_WWW_USER_USERNAME=admin
_AIRFLOW_WWW_USER_PASSWORD=admin
ETL_COMPANIES=["ATW", "IAM", "BCP", "BMCE"]
ETL_BATCH_SIZE=10
ETL_MAX_RETRIES=3
SLACK_WEBHOOK_CONN_ID=slack_webhook
DATABASE_URL=postgresql://postgres:password@postgres:5432/casablanca_insights
REDIS_URL=redis://redis:6379
ENVIRONMENT=production
EOF
```

### **2. Create Directories**

```bash
mkdir -p dags logs plugins config
export AIRFLOW_UID=50000
```

### **3. Initialize Airflow**

```bash
docker-compose up airflow-init
```

### **4. Start Services**

```bash
docker-compose up -d
```

### **5. Configure Variables**

```bash
# Wait for services to be ready, then:
docker-compose exec airflow-webserver airflow variables set ETL_COMPANIES '["ATW", "IAM", "BCP", "BMCE"]'
docker-compose exec airflow-webserver airflow variables set ETL_BATCH_SIZE 10
docker-compose exec airflow-webserver airflow variables set ETL_MAX_RETRIES 3
docker-compose exec airflow-webserver airflow variables set ENVIRONMENT production
```

## 📈 **Monitoring & Alerts**

### **Success Alerts**
When the pipeline completes successfully, you'll receive:
- **Slack notification** (if configured)
- **Email notification** (if configured)
- **Pipeline metrics** (reports fetched, PDFs extracted, etc.)

### **Failure Alerts**
If any task fails:
- **Immediate Slack/Email alert**
- **Detailed error information**
- **DAG run ID for debugging**

### **Configure Slack Alerts**

1. **Create Slack App**:
   - Go to https://api.slack.com/apps
   - Create new app
   - Add "Incoming Webhooks" feature
   - Create webhook for your channel

2. **Add to Airflow**:
   ```bash
   # Via Airflow UI: Admin → Connections
   # Or via CLI:
   docker-compose exec airflow-webserver airflow connections add slack_webhook \
     --conn-type http \
     --conn-host https://hooks.slack.com \
     --conn-password /services/YOUR_WEBHOOK_URL
   ```

3. **Set Variable**:
   ```bash
   docker-compose exec airflow-webserver airflow variables set SLACK_WEBHOOK_CONN_ID slack_webhook
   ```

## 🔍 **Testing the Pipeline**

### **1. Manual Trigger**

1. Open Airflow UI: http://localhost:8080
2. Find `casablanca_etl_pipeline` DAG
3. Click "Play" button to trigger manual run
4. Monitor execution in "Graph" view

### **2. Check Task Logs**

```bash
# View scheduler logs
docker-compose logs -f airflow-scheduler

# View specific task logs
docker-compose exec airflow-webserver airflow tasks logs casablanca_etl_pipeline fetch_ir_reports latest
```

### **3. Test Individual Tasks**

```bash
# Test DAG parsing
docker-compose exec airflow-webserver airflow dags test casablanca_etl_pipeline $(date +%Y-%m-%d)

# Test specific task
docker-compose exec airflow-webserver airflow tasks test casablanca_etl_pipeline fetch_ir_reports $(date +%Y-%m-%d)
```

## 🗄️ **Data Flow**

### **Task Dependencies**
```
fetch_ir_reports >> extract_pdf_data >> translate_to_gaap >> store_data >> validate_data >> success_alert
[fetch_ir_reports, extract_pdf_data, translate_to_gaap, store_data, validate_data] >> failure_alert
```

### **Data Passing**
- **XCom**: Tasks pass data between each other
- **Files**: Downloaded PDFs stored in shared volume
- **Database**: Final GAAP data stored in PostgreSQL

### **Error Handling**
- **Retries**: 3 attempts per task
- **Failure Propagation**: Any task failure triggers failure alert
- **Partial Success**: Individual task failures don't stop pipeline

## 📊 **Monitoring Dashboards**

### **Airflow UI**
- **DAGs**: View all DAGs and their status
- **Graph**: Visual representation of task dependencies
- **Tree**: Historical view of DAG runs
- **Gantt**: Timeline view of task execution

### **Flower (Celery Monitoring)**
- **URL**: http://localhost:5555
- **Purpose**: Monitor Celery workers and tasks
- **Features**: Worker status, task history, resource usage

### **Logs**
```bash
# View all logs
docker-compose logs

# Follow specific service
docker-compose logs -f airflow-scheduler

# View task logs
docker-compose exec airflow-webserver airflow tasks logs casablanca_etl_pipeline fetch_ir_reports latest
```

## 🔧 **Troubleshooting**

### **Common Issues**

1. **DAG Not Loading**
   ```bash
   # Check DAG file syntax
   docker-compose exec airflow-webserver python -c "import sys; sys.path.append('/opt/airflow'); exec(open('/opt/airflow/dags/casablanca_etl_dag.py').read())"
   ```

2. **Permission Issues**
   ```bash
   # Fix permissions (Linux)
   sudo chown -R 50000:0 dags logs plugins config
   sudo chmod -R 755 dags logs plugins config
   ```

3. **Database Connection Issues**
   ```bash
   # Check database health
   docker-compose exec postgres pg_isready -U airflow
   ```

4. **Task Failures**
   ```bash
   # Check task logs
   docker-compose exec airflow-webserver airflow tasks logs casablanca_etl_pipeline TASK_NAME latest
   ```

### **Debug Commands**

```bash
# Check Airflow status
docker-compose exec airflow-webserver airflow db check

# List DAGs
docker-compose exec airflow-webserver airflow dags list

# Check variables
docker-compose exec airflow-webserver airflow variables list

# Check connections
docker-compose exec airflow-webserver airflow connections list
```

## 🚀 **Production Deployment**

### **1. Environment Variables**
```bash
# Production .env
AIRFLOW_UID=50000
_AIRFLOW_WWW_USER_USERNAME=your_admin_user
_AIRFLOW_WWW_USER_PASSWORD=your_secure_password
AIRFLOW__CORE__FERNET_KEY=your_fernet_key
DATABASE_URL=your_production_db_url
REDIS_URL=your_production_redis_url
```

### **2. Security**
- Change default passwords
- Use SSL/TLS for database connections
- Configure firewall rules
- Set up proper authentication

### **3. Scaling**
```bash
# Scale workers
docker-compose up -d --scale airflow-worker=3

# Scale API
docker-compose up -d --scale casablanca-api=2
```

### **4. Backup**
```bash
# Backup Airflow database
docker-compose exec postgres pg_dump -U airflow airflow > airflow_backup.sql

# Backup DAGs
tar -czf dags_backup.tar.gz dags/
```

## 📚 **Next Steps**

### **Immediate Actions**
1. ✅ Deploy Airflow DAG
2. ✅ Test manual execution
3. ✅ Configure alerts
4. ✅ Monitor first automated run

### **Future Enhancements**
1. **GAAP Validation**: Add balance sheet equality checks
2. **Change Detection**: Implement record-level versioning
3. **API Caching**: Add Redis caching layer
4. **Advanced Monitoring**: Integrate with Prometheus/Grafana
5. **Multi-environment**: Set up staging/production environments

## 🆘 **Support**

### **Useful Commands**
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### **Documentation**
- [Airflow Documentation](https://airflow.apache.org/docs/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Casablanca Insights ETL Documentation](../README_ETL.md)

Your automated ETL pipeline is now ready! 🎉 