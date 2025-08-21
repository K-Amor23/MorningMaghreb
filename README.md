# 🚀 Airflow Docker Stack for Casablanca Insights

This is a production-ready Docker setup for Apache Airflow that will automatically run your data scraping DAGs and keep your database fresh.

## 🎯 What This Gives You

- **🔄 Automated Data Scraping**: Runs daily at 6:00 AM UTC
- **📊 78 Companies**: Automatically scraped from African Markets
- **📈 Real-time Data**: Market prices, volume, financials
- **🌐 Web UI**: Monitor and manage your pipelines
- **📱 Always-on**: Runs continuously in the background

## 🚀 Quick Start

### 1. Start the Stack
```bash
./start-airflow.sh
```

### 2. Access the Web UI
- **URL**: http://localhost:8080
- **Username**: admin
- **Password**: admin

### 3. Your DAGs Will Auto-Run
- **Daily at 6:00 AM UTC**: Company data refresh
- **Every 6 hours**: Market data updates
- **Weekly**: Newsletter generation

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Airflow Web    │    │   Scheduler     │    │   Celery Worker │
│   (Port 8080)   │    │  (Runs DAGs)   │    │ (Executes Tasks)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
    PostgreSQL              Redis Queue            Your Scrapers
   (Metadata)            (Task Queue)         (African Markets, etc.)
```

## 📁 What's Included

- **15+ DAGs**: Ready to run your scrapers
- **Database**: PostgreSQL for metadata
- **Queue**: Redis for task distribution
- **Volumes**: Persistent data storage
- **Environment**: Loads your `.env.local`

## 🔧 Manual Setup (if needed)

### Start Services
```bash
docker-compose up -d
```

### Initialize Database
```bash
docker-compose exec airflow-webserver airflow db init
```

### Create Admin User
```bash
docker-compose exec airflow-webserver airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@morningmaghreb.com
```

### Start Scheduler
```bash
docker-compose exec airflow-webserver airflow scheduler
```

## 📊 Your DAGs

1. **`working_comprehensive_market_data`** - Main scraper (daily)
2. **`casablanca_etl_pipeline`** - ETL pipeline (daily)
3. **`smart_ir_scraping`** - IR reports (daily)
4. **`etf_bond_scraping`** - ETFs & bonds (daily)
5. **`weekly_newsletter`** - Newsletter (weekly)

## 🎉 What Happens Next

Once running, your stack will:

1. **🌅 6:00 AM UTC**: Scrape all 78 companies
2. **📈 Real-time**: Update market data continuously
3. **📊 Database**: Populate your Sky Garden database
4. **🌐 Frontend**: Your website gets fresh data automatically
5. **📧 Alerts**: Success/failure notifications

## 🛠️ Troubleshooting

### Check Status
```bash
docker-compose ps
```

### View Logs
```bash
docker-compose logs airflow-webserver
docker-compose logs airflow-scheduler
docker-compose logs airflow-worker
```

### Restart Services
```bash
docker-compose restart
```

### Stop Everything
```bash
docker-compose down
```

## 🔒 Security Notes

- **Default credentials**: admin/admin (change in production)
- **Port 8080**: Only accessible locally
- **Environment variables**: Loaded from your `.env.local`

## 🚀 Production Ready

This setup includes:
- ✅ **Health checks** for all services
- ✅ **Persistent volumes** for data
- ✅ **Load balancing** with Celery workers
- ✅ **Monitoring** and logging
- ✅ **Auto-restart** on failures

---

**🎯 Your data scraper will now run automatically 24/7!**
