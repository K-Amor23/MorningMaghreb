# ETL IR Reports DAG

A comprehensive Apache Airflow DAG for extracting, transforming, and loading Investor Relations (IR) reports from company websites.

## Overview

This DAG automates the daily process of:
1. **Extract**: Download IR PDFs from company websites
2. **Transform**: Parse PDFs and extract structured financial data
3. **Load**: Store processed data in PostgreSQL database

## Features

- ✅ **Daily Schedule**: Runs at 02:00 AM America/New_York timezone
- ✅ **SLA Monitoring**: 6:00 AM deadline with automatic alerts
- ✅ **Error Handling**: Retries with exponential backoff
- ✅ **Notifications**: Email and Slack alerts for success/failure
- ✅ **Celery Integration**: Distributed PDF parsing
- ✅ **XCom Data Passing**: Efficient data flow between tasks
- ✅ **Comprehensive Logging**: Detailed execution logs

## DAG Structure

```
start → extract → parse → load → end
```

### Tasks

1. **start**: Logs ETL pipeline start
2. **extract**: Downloads IR PDFs from company websites
3. **parse**: Triggers Celery tasks to parse PDFs
4. **load**: Inserts parsed data into PostgreSQL
5. **end**: Logs completion and sends success notification

## Prerequisites

- Apache Airflow 2.0+
- PostgreSQL database (Supabase)
- Redis (for Celery)
- Python 3.8+

## Installation

### 1. Copy DAG File

Copy `etl_ir_reports.py` to your `$AIRFLOW_HOME/dags` directory:

```bash
cp etl_ir_reports.py $AIRFLOW_HOME/dags/
```

### 2. Install Dependencies

Install required Python packages:

```bash
pip install -r requirements_etl.txt
```

### 3. Set Up Database Connection

In Airflow UI → Admin → Connections:

**Connection ID**: `supabase_postgres`
- **Connection Type**: Postgres
- **Host**: Your Supabase PostgreSQL host
- **Schema**: public
- **Login**: Your database username
- **Password**: Your database password
- **Port**: 5432

### 4. Configure Airflow Variables

In Airflow UI → Admin → Variables:

#### SLACK_WEBHOOK_URL
Your Slack webhook URL for notifications:
```
https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
```

#### ALERT_EMAILS
JSON array of email addresses:
```json
["admin@example.com", "ops@example.com"]
```

#### IR_REPORT_PATHS
JSON array of common IR report URL paths:
```json
[
    "/investors/annual-report.pdf",
    "/investors/reports/annual-report.pdf",
    "/investor-relations/annual-report.pdf",
    "/financial-reports/annual-report.pdf",
    "/documents/annual-report.pdf",
    "/investors/",
    "/investor-relations/",
    "/financial-reports/"
]
```

### 5. Database Schema

Ensure your PostgreSQL database has the required table:

```sql
CREATE TABLE IF NOT EXISTS financial_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) REFERENCES companies(ticker),
    period VARCHAR(20) NOT NULL,
    report_type VARCHAR(20) CHECK (report_type IN ('quarterly', 'annual')),
    filing_date DATE,
    ifrs_data JSONB,
    gaap_data JSONB,
    pdf_url VARCHAR(500),
    processed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(ticker, period)
);
```

### 6. Start Celery Workers

Start Celery workers for PDF parsing:

```bash
# Start Celery worker
celery -A etl.celery_app worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A etl.celery_app beat --loglevel=info
```

## Usage

### Manual Trigger

1. Open Airflow UI
2. Navigate to DAGs → etl_ir_reports
3. Click "Trigger DAG" to run manually

### Automatic Schedule

The DAG runs automatically at 02:00 AM America/New_York timezone daily.

### Monitoring

- **SLA**: 6:00 AM deadline
- **Logs**: Check task logs in Airflow UI
- **Notifications**: Email/Slack alerts for failures
- **Metrics**: Track successful downloads and processing

## Configuration

### DAG Parameters

- **Schedule**: `0 2 * * *` (Daily at 02:00 AM EST)
- **SLA**: 4 hours (6:00 AM EST)
- **Retries**: 3 with exponential backoff
- **Max Active Runs**: 1

### Task-Specific Settings

#### Extract Task
- Downloads PDFs to `/tmp/ir_reports/{date}/`
- Tries multiple URL paths per company
- Handles redirects and timeouts
- Logs download statistics

#### Parse Task
- Triggers Celery tasks for each PDF
- Supports distributed processing
- Handles parsing failures gracefully
- Extracts financial data using regex patterns

#### Load Task
- Upserts data into PostgreSQL
- Handles JSON data serialization
- Validates data before insertion
- Reports loading statistics

## Data Flow

### Extract Phase
1. Query companies table for active companies
2. Attempt downloads from website_url/investor_relations_url
3. Try multiple common IR report paths
4. Save PDFs with timestamped filenames
5. Pass file list via XCom

### Parse Phase
1. Get downloaded file list from XCom
2. Trigger Celery task for each PDF
3. Extract text using PyPDF2
4. Parse financial data using regex patterns
5. Return structured JSON data

### Load Phase
1. Get parsing results from Celery tasks
2. Transform data to database format
3. Insert/upsert into financial_reports table
4. Handle conflicts and errors
5. Report loading statistics

## Financial Data Extraction

The DAG extracts the following financial metrics:

- **Revenue** (Chiffre d'affaires)
- **Net Income** (Bénéfice net)
- **Total Assets** (Actifs totaux)
- **Total Liabilities** (Passifs totaux)
- **Equity** (Capitaux propres)

### Supported Languages
- English
- French (for Moroccan companies)

### Currency Detection
- Automatically detects currency (MAD, USD, EUR, etc.)
- Defaults to MAD for Moroccan companies

## Error Handling

### Retry Logic
- **Extract**: 3 retries, 5-minute delay, exponential backoff
- **Parse**: 2 retries, 5-minute delay, exponential backoff
- **Load**: 3 retries, 5-minute delay, exponential backoff

### Failure Scenarios
1. **Network Issues**: Retry with exponential backoff
2. **PDF Download Failures**: Log warning, continue with other companies
3. **Parsing Errors**: Log error, skip problematic PDFs
4. **Database Errors**: Retry with backoff, log detailed errors

### Notifications
- **Success**: Summary of processed data
- **Failure**: Task details, error messages, execution context
- **SLA Miss**: Automatic alert when deadline exceeded

## Monitoring and Alerts

### Success Notifications
```
🎉 ETL IR Reports Pipeline Completed Successfully!

📊 Pipeline Results:
• Companies Processed: 15
• PDFs Downloaded: 12
• Data Records Loaded: 12
• Errors: 0

📅 Execution Details:
• Execution Date: 2024-01-15
• DAG: etl_ir_reports
• Duration: 1800 seconds
```

### Failure Notifications
```
❌ ETL IR Reports Pipeline Failed!

🚨 Failure Details:
• DAG: etl_ir_reports
• Failed Task: extract
• Execution Date: 2024-01-15
• Error: Connection timeout
```

## Troubleshooting

### Common Issues

#### 1. Connection Errors
**Problem**: Cannot connect to PostgreSQL
**Solution**: 
- Verify connection settings in Airflow UI
- Check network connectivity
- Ensure database is running

#### 2. PDF Download Failures
**Problem**: PDFs not downloading
**Solution**:
- Check company URLs in database
- Verify network access to external sites
- Review IR_REPORT_PATHS variable

#### 3. Parsing Errors
**Problem**: PDF parsing fails
**Solution**:
- Ensure PyPDF2 is installed
- Check PDF file integrity
- Verify PDFs are text-based (not scanned images)

#### 4. Celery Task Failures
**Problem**: Celery tasks not executing
**Solution**:
- Check Celery worker status
- Verify Redis connection
- Review Celery configuration

#### 5. Database Errors
**Problem**: Data not loading
**Solution**:
- Verify table schema
- Check database permissions
- Review JSON data format

### Log Locations
- **Airflow logs**: `$AIRFLOW_HOME/logs/`
- **Celery logs**: Check Celery worker output
- **PDF storage**: `/tmp/ir_reports/`

### Debug Mode

Enable debug logging by setting Airflow log level:

```bash
export AIRFLOW__LOGGING__LOGGING_LEVEL=DEBUG
```

## Performance Optimization

### Parallel Processing
- Celery workers handle PDF parsing in parallel
- Multiple workers can process different PDFs simultaneously
- Configure worker count based on available resources

### Resource Management
- PDF files are stored temporarily in `/tmp/ir_reports/`
- Implement cleanup job to remove old files
- Monitor disk space usage

### Database Optimization
- Use upsert operations to avoid duplicates
- Index on (ticker, period) for fast lookups
- Consider partitioning for large datasets

## Security Considerations

### Data Protection
- PDFs contain sensitive financial information
- Implement proper access controls
- Consider encryption for stored files

### Network Security
- Use HTTPS for all external downloads
- Implement rate limiting for web scraping
- Monitor for suspicious activity

### Database Security
- Use connection pooling
- Implement proper user permissions
- Regular security audits

## Maintenance

### Regular Tasks
1. **Cleanup**: Remove old PDF files
2. **Monitoring**: Check SLA compliance
3. **Updates**: Keep dependencies current
4. **Backup**: Regular database backups

### Health Checks
- Monitor Celery worker health
- Check disk space usage
- Verify database connectivity
- Review error rates

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review Airflow and Celery logs
3. Verify configuration settings
4. Test with manual trigger

## License

This DAG is part of the Casablanca Insights project. 