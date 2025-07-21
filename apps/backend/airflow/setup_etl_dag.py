#!/usr/bin/env python3
"""
Setup script for ETL IR Reports DAG

This script helps configure the Airflow environment for the ETL IR Reports DAG.
It sets up connections, variables, and validates the configuration.

Usage:
    python setup_etl_dag.py
"""

import os
import sys
import json
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def setup_airflow_environment():
    """Set up Airflow environment for ETL DAG"""
    
    print("🚀 Setting up Airflow environment for ETL IR Reports DAG...")
    
    # Check if we're in an Airflow environment
    airflow_home = os.getenv('AIRFLOW_HOME')
    if not airflow_home:
        print("❌ AIRFLOW_HOME environment variable not set")
        print("Please set AIRFLOW_HOME to your Airflow installation directory")
        return False
    
    print(f"✅ AIRFLOW_HOME: {airflow_home}")
    
    # Check if DAG file exists
    dag_file = Path(airflow_home) / "dags" / "etl_ir_reports.py"
    if not dag_file.exists():
        print(f"❌ DAG file not found: {dag_file}")
        print("Please copy etl_ir_reports.py to your $AIRFLOW_HOME/dags directory")
        return False
    
    print(f"✅ DAG file found: {dag_file}")
    
    # Create configuration guide
    create_configuration_guide()
    
    # Validate dependencies
    validate_dependencies()
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Configure the supabase_postgres connection in Airflow UI")
    print("2. Set up Airflow Variables (SLACK_WEBHOOK_URL, ALERT_EMAILS, IR_REPORT_PATHS)")
    print("3. Install required Python packages")
    print("4. Start Celery workers for PDF parsing")
    print("5. Test the DAG with a manual trigger")
    
    return True

def create_configuration_guide():
    """Create a configuration guide file"""
    
    config_guide = """
# ETL IR Reports DAG Configuration Guide

## 1. Airflow Connections

### PostgreSQL Connection (supabase_postgres)
- Connection Id: supabase_postgres
- Connection Type: Postgres
- Host: Your Supabase PostgreSQL host
- Schema: public
- Login: Your database username
- Password: Your database password
- Port: 5432

### Celery Connection (optional, for distributed processing)
- Connection Id: celery_default
- Connection Type: Celery
- Host: Your Redis broker URL (e.g., redis://localhost:6379/0)

## 2. Airflow Variables

### SLACK_WEBHOOK_URL
Your Slack webhook URL for notifications
Example: https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX

### ALERT_EMAILS
JSON array of email addresses for alerts
Example: ["admin@example.com", "ops@example.com"]

### IR_REPORT_PATHS
JSON array of common IR report URL paths to try
Example: [
    "/investors/annual-report.pdf",
    "/investors/reports/annual-report.pdf",
    "/investor-relations/annual-report.pdf",
    "/financial-reports/annual-report.pdf",
    "/documents/annual-report.pdf",
    "/investors/",
    "/investor-relations/",
    "/financial-reports/"
]

## 3. Database Schema

Ensure your PostgreSQL database has the following table:

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

## 4. Python Dependencies

Install the required packages:

```bash
pip install -r requirements_etl.txt
```

## 5. Celery Setup

Start Celery workers for PDF parsing:

```bash
# Start Celery worker
celery -A etl.celery_app worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A etl.celery_app beat --loglevel=info
```

## 6. Testing

1. Verify DAG loads in Airflow UI
2. Test with manual trigger
3. Check logs for any errors
4. Verify data is loaded into database

## 7. Monitoring

- Set up SLA monitoring for 6 AM deadline
- Configure email/Slack alerts
- Monitor Celery worker health
- Check disk space for PDF storage

## 8. Troubleshooting

### Common Issues:
1. **Connection errors**: Verify PostgreSQL connection settings
2. **PDF download failures**: Check company URLs and network access
3. **Parsing errors**: Ensure PyPDF2 is installed and PDFs are readable
4. **Celery task failures**: Check Celery worker status and Redis connection
5. **Database errors**: Verify table schema and permissions

### Log Locations:
- Airflow logs: $AIRFLOW_HOME/logs/
- Celery logs: Check Celery worker output
- PDF storage: /tmp/ir_reports/
"""
    
    guide_path = Path("ETL_DAG_SETUP_GUIDE.md")
    with open(guide_path, 'w') as f:
        f.write(config_guide)
    
    print(f"✅ Configuration guide created: {guide_path}")

def validate_dependencies():
    """Validate that required dependencies are available"""
    
    print("\n🔍 Validating dependencies...")
    
    required_packages = [
        'requests',
        'PyPDF2', 
        'sqlalchemy',
        'psycopg2',
        'airflow',
        'celery'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT FOUND")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
    else:
        print("\n✅ All required packages are available")

def create_sample_variables():
    """Create sample Airflow variables configuration"""
    
    sample_variables = {
        "SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
        "ALERT_EMAILS": ["admin@yourcompany.com", "ops@yourcompany.com"],
        "IR_REPORT_PATHS": [
            "/investors/annual-report.pdf",
            "/investors/reports/annual-report.pdf",
            "/investor-relations/annual-report.pdf",
            "/financial-reports/annual-report.pdf",
            "/documents/annual-report.pdf",
            "/investors/",
            "/investor-relations/",
            "/financial-reports/"
        ]
    }
    
    variables_file = Path("sample_airflow_variables.json")
    with open(variables_file, 'w') as f:
        json.dump(sample_variables, f, indent=2)
    
    print(f"✅ Sample variables file created: {variables_file}")

if __name__ == "__main__":
    try:
        setup_airflow_environment()
        create_sample_variables()
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1) 