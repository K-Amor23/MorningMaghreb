# Master Data Pipeline for Casablanca Insights

## 🎯 Overview

The Master Data Pipeline is a comprehensive ETL (Extract, Transform, Load) system that automatically scrapes financial data from multiple sources and stores it in Supabase for the Casablanca Insights website. This ensures your website always has fresh, real-time market data.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   Airflow DAG   │    │    Supabase     │
│                 │    │                 │    │                 │
│ • African       │───▶│ • Scrape Data   │───▶│ • company_prices│
│   Markets       │    │ • Process Data  │    │ • market_indices│
│ • Casablanca    │    │ • Validate Data │    │ • macro_indicators│
│   Bourse        │    │ • Store in DB   │    │ • company_news  │
│ • Bank Al-      │    │ • Send Notifications│ │ • monitoring    │
│   Maghrib       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Website       │
                       │                 │
                       │ • Real-time data│
                       │ • Market charts │
                       │ • News feed     │
                       └─────────────────┘
```

## 📊 Data Sources

### 1. African Markets Data
- **Companies**: ATW, IAM, BCP, and more
- **Data**: Price, volume, market cap, P/E ratio, dividend yield
- **Frequency**: Daily updates

### 2. Casablanca Bourse Indices
- **Indices**: MASI, MADEX
- **Data**: Index values, daily changes, volume
- **Frequency**: Daily updates

### 3. Macroeconomic Indicators
- **Source**: Bank Al-Maghrib
- **Data**: GDP growth, inflation rate, interest rates, exchange rates
- **Frequency**: Monthly updates

### 4. News and Sentiment
- **Sources**: Financial news outlets
- **Data**: Headlines, summaries, sentiment analysis
- **Frequency**: Real-time updates

## 🗄️ Database Schema

### Core Tables

#### `company_prices`
```sql
- ticker (VARCHAR) - Stock symbol
- company_name (VARCHAR) - Company name
- sector (VARCHAR) - Industry sector
- price (DECIMAL) - Current stock price
- change_1d_percent (DECIMAL) - Daily change %
- change_ytd_percent (DECIMAL) - Year-to-date change %
- market_cap_billion (DECIMAL) - Market capitalization
- volume (BIGINT) - Trading volume
- pe_ratio (DECIMAL) - Price-to-earnings ratio
- dividend_yield (DECIMAL) - Dividend yield %
- size_category (VARCHAR) - Large/Mid/Small cap
- sector_group (VARCHAR) - Sector classification
- date (DATE) - Data date
```

#### `market_indices`
```sql
- index_name (VARCHAR) - Index name (MASI, MADEX)
- value (DECIMAL) - Index value
- change_1d_percent (DECIMAL) - Daily change %
- change_ytd_percent (DECIMAL) - Year-to-date change %
- volume (BIGINT) - Trading volume
- market_cap_total (DECIMAL) - Total market cap
- date (DATE) - Data date
```

#### `macro_indicators`
```sql
- indicator (VARCHAR) - Indicator name
- value (DECIMAL) - Indicator value
- unit (VARCHAR) - Unit of measurement
- period (VARCHAR) - Time period
- source (VARCHAR) - Data source
- date (DATE) - Data date
```

#### `company_news`
```sql
- ticker (VARCHAR) - Stock symbol
- headline (TEXT) - News headline
- summary (TEXT) - News summary
- sentiment (VARCHAR) - Positive/neutral/negative
- source (VARCHAR) - News source
- published_at (TIMESTAMP) - Publication date
```

### Monitoring Tables

#### `data_quality_logs`
- Tracks pipeline execution and data quality metrics

#### `pipeline_notifications`
- Stores success/failure notifications

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Supabase account with service role key
- Environment variables set up

### 1. Set Environment Variables
```bash
export NEXT_PUBLIC_SUPABASE_URL="your_supabase_url"
export SUPABASE_SERVICE_ROLE_KEY="your_service_role_key"
```

### 2. Deploy the Pipeline
```bash
# Run the deployment script
./deploy_master_pipeline.sh
```

### 3. Access Airflow UI
- **URL**: http://localhost:8080
- **Username**: admin
- **Password**: admin123

## 📋 Pipeline Tasks

### 1. Scrape African Markets Data
- **Task ID**: `scrape_african_markets`
- **Function**: `scrape_african_markets_data()`
- **Output**: Company prices stored in `company_prices` table

### 2. Scrape Casablanca Bourse Data
- **Task ID**: `scrape_casablanca_bourse`
- **Function**: `scrape_casablanca_bourse_data()`
- **Output**: Market indices stored in `market_indices` table

### 3. Scrape Macroeconomic Data
- **Task ID**: `scrape_macro_data`
- **Function**: `scrape_macro_economic_data()`
- **Output**: Macro indicators stored in `macro_indicators` table

### 4. Scrape News and Sentiment
- **Task ID**: `scrape_news_sentiment`
- **Function**: `scrape_news_and_sentiment()`
- **Output**: News articles stored in `company_news` table

### 5. Validate Data Quality
- **Task ID**: `validate_data_quality`
- **Function**: `validate_data_quality()`
- **Output**: Quality metrics stored in `data_quality_logs` table

### 6. Send Notifications
- **Success Task ID**: `send_success_notification`
- **Failure Task ID**: `send_failure_notification`
- **Output**: Notifications stored in `pipeline_notifications` table

## ⏰ Schedule

The pipeline runs **daily at 6:00 AM UTC** with the following schedule:

```python
schedule_interval='0 6 * * *'  # Daily at 6:00 AM UTC
```

## 🔧 Management Commands

### Start Airflow
```bash
cd apps/backend/airflow
airflow webserver --port 8080 --daemon
airflow scheduler --daemon
```

### Stop Airflow
```bash
pkill -f airflow
```

### Check Pipeline Status
```bash
# List all DAGs
airflow dags list

# Check specific DAG
airflow dags show master_data_pipeline

# View DAG runs
airflow dags backfill master_data_pipeline
```

### Manual Trigger
```bash
# Trigger a manual run
airflow dags trigger master_data_pipeline
```

## 📊 Monitoring

### Airflow UI
- **URL**: http://localhost:8080
- **Features**: 
  - View DAG runs
  - Check task logs
  - Monitor execution status
  - Trigger manual runs

### Data Quality Monitoring
- **Table**: `data_quality_logs`
- **Metrics**: Record counts, validation status
- **Frequency**: After each pipeline run

### Notifications
- **Table**: `pipeline_notifications`
- **Types**: Success, failure, warning
- **Content**: Detailed status messages

## 🔍 Troubleshooting

### Common Issues

#### 1. Airflow Not Starting
```bash
# Check if ports are in use
lsof -i :8080

# Kill existing processes
pkill -f airflow

# Restart Airflow
airflow webserver --port 8080 --daemon
airflow scheduler --daemon
```

#### 2. Database Connection Issues
```bash
# Check environment variables
echo $NEXT_PUBLIC_SUPABASE_URL
echo $SUPABASE_SERVICE_ROLE_KEY

# Test Supabase connection
python scripts/deploy_master_pipeline_tables.py
```

#### 3. DAG Not Loading
```bash
# Check DAG file location
ls ~/airflow/dags/

# Restart Airflow scheduler
pkill -f "airflow scheduler"
airflow scheduler --daemon
```

### Logs
- **Airflow Logs**: `~/airflow/logs/`
- **DAG Logs**: `~/airflow/logs/master_data_pipeline/`
- **Task Logs**: Available in Airflow UI

## 🛠️ Development

### Adding New Data Sources

1. **Create Scraping Function**
```python
def scrape_new_source_data(**context):
    # Your scraping logic here
    pass
```

2. **Add to DAG**
```python
new_task = PythonOperator(
    task_id='scrape_new_source',
    python_callable=scrape_new_source_data,
    dag=dag,
)
```

3. **Update Dependencies**
```python
[existing_tasks, new_task] >> validate_data_task
```

### Adding New Database Tables

1. **Create Table Schema**
```sql
CREATE TABLE IF NOT EXISTS new_table (
    -- your schema here
);
```

2. **Update Deployment Script**
```python
# Add to deploy_master_pipeline_tables.py
```

3. **Add to Validation**
```python
# Update verify_tables_created() function
```

## 📈 Performance Optimization

### Database Indexes
- All tables have appropriate indexes for fast queries
- Composite indexes for common query patterns
- Partitioning for large tables (future enhancement)

### Caching Strategy
- Supabase caching for frequently accessed data
- Redis caching for real-time data (future enhancement)

### Monitoring
- Data quality validation after each run
- Performance metrics tracking
- Alert system for failures

## 🔐 Security

### Row Level Security (RLS)
- All tables have RLS enabled
- Public read access for market data
- Service role access for Airflow operations

### Environment Variables
- Supabase credentials stored securely
- No hardcoded secrets in code
- Environment-specific configurations

## 📚 API Integration

### Website Integration
The website can access data through Supabase client:

```typescript
// Example: Fetch latest company prices
const { data, error } = await supabase
  .from('company_prices')
  .select('*')
  .order('date', { ascending: false })
  .limit(10);
```

### Real-time Updates
- Supabase real-time subscriptions
- WebSocket connections for live data
- Automatic UI updates

## 🎯 Next Steps

### Immediate
1. ✅ Deploy master pipeline
2. ✅ Test data flow
3. ✅ Monitor first run
4. ✅ Verify website integration

### Short-term
1. Add more data sources
2. Implement real-time scraping
3. Add data validation rules
4. Set up alerting system

### Long-term
1. Machine learning for data quality
2. Advanced analytics dashboard
3. Multi-region deployment
4. API rate limiting and optimization

## 📞 Support

For issues or questions:
1. Check Airflow logs first
2. Review this documentation
3. Check GitHub issues
4. Contact the development team

---

**🎉 Your master data pipeline is now ready to provide real-time financial data to your website!** 