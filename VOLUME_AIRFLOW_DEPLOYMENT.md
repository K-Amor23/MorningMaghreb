# Volume Scraper Airflow Integration - Deployment Guide

## 🎯 Overview

This guide explains how to deploy the volume scraper integration with Airflow for automated daily volume data collection.

## 📁 File Structure

```
apps/backend/airflow/dags/
├── casablanca_etl_with_volume_dag.py    # Enhanced DAG with volume data
├── etl/                                 # ETL modules for Airflow
│   ├── __init__.py
│   ├── volume_scraper.py
│   ├── volume_data_integration.py
│   └── african_markets_scraper.py
└── test_volume_integration.py           # Test script
```

## 🚀 Deployment Steps

### 1. Copy Files to Airflow

```bash
# Copy ETL files to Airflow DAGs directory
cp apps/backend/etl/volume_scraper.py apps/backend/airflow/dags/etl/
cp apps/backend/etl/volume_data_integration.py apps/backend/airflow/dags/etl/
cp apps/backend/etl/african_markets_scraper.py apps/backend/airflow/dags/etl/

# Copy the enhanced DAG
cp apps/backend/airflow/dags/casablanca_etl_with_volume_dag.py /path/to/airflow/dags/
```

### 2. Set Environment Variables

Add these to your Airflow environment or `.env` file:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
```

### 3. Install Dependencies

Ensure these Python packages are installed in your Airflow environment:

```bash
pip install supabase aiohttp beautifulsoup4 pandas
```

### 4. Test the Integration

Run the test script to verify everything works:

```bash
cd apps/backend/airflow/dags
python test_volume_integration.py
```

### 5. Deploy to Airflow

1. Copy the DAG file to your Airflow DAGs directory
2. Restart Airflow scheduler
3. Check the Airflow UI for the new DAG: `casablanca_etl_with_volume_pipeline`

## 📊 DAG Tasks

The enhanced DAG includes these new tasks:

1. **refresh_african_markets_with_volume** - Scrapes company data with volume
2. **scrape_volume_data** - Scrapes volume data from multiple sources
3. **integrate_volume_data** - Integrates volume data with database

### Task Dependencies

```
refresh_african_markets_with_volume >> scrape_volume_data >> integrate_volume_data >> 
fetch_ir_reports >> extract_pdf_data >> translate_to_gaap >> store_data >> validate_data >> 
[success_alert, failure_alert]
```

## 🔧 Configuration

### Schedule
- **Frequency**: Daily at 6:00 AM UTC
- **Retries**: 3 attempts with 5-minute delays
- **Max Active Runs**: 1 (prevents overlapping executions)

### Data Sources
- **African Markets** - Primary source for CSE data
- **Wafabourse** - Moroccan financial portal
- **Investing.com** - International financial data

### Output Locations
- **Temporary Files**: `/tmp/volume_data_YYYYMMDD/`
- **Database**: Supabase tables (volume_analysis, market_data)
- **Logs**: Airflow task logs

## 🧪 Testing

### Manual Testing
```bash
# Test volume scraper
cd apps/backend/etl
python volume_scraper.py

# Test volume integration
python volume_data_integration.py

# Test Airflow integration
cd ../airflow/dags
python test_volume_integration.py
```

### Airflow Testing
1. Trigger the DAG manually in Airflow UI
2. Monitor task execution in real-time
3. Check task logs for any errors
4. Verify data is stored in Supabase

## 📈 Monitoring

### Key Metrics to Monitor
- **Volume records collected** per day
- **Data quality score** (should be > 0.9)
- **High volume alerts** generated
- **Database update success rate**
- **Task execution time**

### Alerts
- **Success alerts** sent when pipeline completes
- **Failure alerts** sent when any task fails
- **Volume spike alerts** for unusual trading activity

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure ETL files are copied to Airflow DAGs directory
   - Check Python path configuration

2. **Database Connection Errors**
   - Verify Supabase credentials
   - Check network connectivity

3. **Scraping Failures**
   - Check if source websites are accessible
   - Verify scraping logic hasn't changed

4. **Volume Data Issues**
   - Check if volume data format has changed
   - Verify volume cleaning functions

### Debug Steps

1. **Check Airflow logs** for specific error messages
2. **Run test script** to verify imports and configuration
3. **Test individual components** outside of Airflow
4. **Verify environment variables** are set correctly

## 📞 Support

If you encounter issues:

1. Check the Airflow task logs
2. Run the test script to verify setup
3. Review the troubleshooting section above
4. Check the volume scraper documentation

## 🎉 Success Criteria

The integration is successful when:

- ✅ DAG runs daily without errors
- ✅ Volume data is collected from all sources
- ✅ Data is stored in Supabase database
- ✅ Volume alerts are generated
- ✅ Success notifications are sent
- ✅ Data quality score remains high

---

**Last Updated**: $(date)
**Version**: 1.0
