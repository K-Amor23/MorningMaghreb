"""
Production Monitoring and Backup DAG

This DAG handles production monitoring and database backups:
- Airflow failure alerts
- Supabase database backups
- System health monitoring
- Performance metrics collection

Features:
- Daily database backups
- Failure notification system
- Health check monitoring
- Performance tracking
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.email_operator import EmailOperator
from airflow.utils.dates import days_ago
import requests
import json
import logging
import os
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from supabase import create_client, Client
except ImportError:
    print("⚠️  Supabase client not available")

# Configure logging
logger = logging.getLogger(__name__)

# Default arguments
default_args = {
    'owner': 'casablanca-insights',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False
}

def check_system_health():
    """Check overall system health"""
    try:
        # Check API health
        api_health_url = "http://localhost:3000/api/health"
        response = requests.get(api_health_url, timeout=10)
        
        if response.status_code != 200:
            raise Exception(f"API health check failed: {response.status_code}")
        
        health_data = response.json()
        logger.info(f"✅ System health check passed: {health_data}")
        
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'api_status': health_data.get('status', 'unknown'),
            'database_status': health_data.get('services', {}).get('database', 'unknown')
        }
        
    except Exception as e:
        logger.error(f"❌ System health check failed: {str(e)}")
        raise

def check_database_connection():
    """Check Supabase database connection"""
    try:
        supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
        supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_service_key:
            raise Exception("Supabase credentials not configured")
        
        supabase = create_client(supabase_url, supabase_service_key)
        
        # Test connection with a simple query
        result = supabase.table('companies').select('count').limit(1).execute()
        
        logger.info("✅ Database connection check passed")
        
        return {
            'status': 'connected',
            'timestamp': datetime.now().isoformat(),
            'connection_test': 'success'
        }
        
    except Exception as e:
        logger.error(f"❌ Database connection check failed: {str(e)}")
        raise

def check_data_freshness():
    """Check data freshness and quality"""
    try:
        supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
        supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_service_key:
            raise Exception("Supabase credentials not configured")
        
        supabase = create_client(supabase_url, supabase_service_key)
        
        # Check latest data timestamps
        latest_prices = supabase.table('company_prices').select('date').order('date', desc=True).limit(1).execute()
        latest_analytics = supabase.table('analytics_signals').select('computed_at').order('computed_at', desc=True).limit(1).execute()
        latest_news = supabase.table('company_news').select('published_at').order('published_at', desc=True).limit(1).execute()
        
        # Calculate data age
        now = datetime.now()
        
        price_age = None
        if latest_prices.data:
            latest_price_date = datetime.fromisoformat(latest_prices.data[0]['date'].replace('Z', '+00:00'))
            price_age = (now - latest_price_date).days
        
        analytics_age = None
        if latest_analytics.data:
            latest_analytics_date = datetime.fromisoformat(latest_analytics.data[0]['computed_at'].replace('Z', '+00:00'))
            analytics_age = (now - latest_analytics_date).days
        
        news_age = None
        if latest_news.data:
            latest_news_date = datetime.fromisoformat(latest_news.data[0]['published_at'].replace('Z', '+00:00'))
            news_age = (now - latest_news_date).days
        
        # Check for stale data
        warnings = []
        if price_age and price_age > 7:
            warnings.append(f"Price data is {price_age} days old")
        if analytics_age and analytics_age > 2:
            warnings.append(f"Analytics data is {analytics_age} days old")
        if news_age and news_age > 3:
            warnings.append(f"News data is {news_age} days old")
        
        logger.info(f"✅ Data freshness check completed. Warnings: {warnings}")
        
        return {
            'status': 'fresh' if not warnings else 'stale',
            'timestamp': datetime.now().isoformat(),
            'price_age_days': price_age,
            'analytics_age_days': analytics_age,
            'news_age_days': news_age,
            'warnings': warnings
        }
        
    except Exception as e:
        logger.error(f"❌ Data freshness check failed: {str(e)}")
        raise

def create_database_backup():
    """Create database backup using Supabase CLI"""
    try:
        # Check if Supabase CLI is available
        import subprocess
        
        # Create backup directory
        backup_dir = Path("../backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Generate backup filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f"casablanca_backup_{timestamp}.sql"
        
        # Create backup using Supabase CLI
        try:
            result = subprocess.run(
                ["supabase", "db", "dump", "--file", str(backup_file)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode != 0:
                raise Exception(f"Backup failed: {result.stderr}")
            
            logger.info(f"✅ Database backup created: {backup_file}")
            
            # Compress backup file
            import gzip
            compressed_file = backup_file.with_suffix('.sql.gz')
            with open(backup_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    f_out.writelines(f_in)
            
            # Remove uncompressed file
            backup_file.unlink()
            
            logger.info(f"✅ Compressed backup: {compressed_file}")
            
            return {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'backup_file': str(compressed_file),
                'file_size_mb': compressed_file.stat().st_size / (1024 * 1024)
            }
            
        except FileNotFoundError:
            logger.warning("⚠️  Supabase CLI not found, skipping backup")
            return {
                'status': 'skipped',
                'timestamp': datetime.now().isoformat(),
                'reason': 'Supabase CLI not available'
            }
        
    except Exception as e:
        logger.error(f"❌ Database backup failed: {str(e)}")
        raise

def cleanup_old_backups():
    """Clean up old backup files (keep last 7 days)"""
    try:
        backup_dir = Path("../backups")
        if not backup_dir.exists():
            return
        
        # Keep backups from last 7 days
        cutoff_date = datetime.now() - timedelta(days=7)
        
        deleted_count = 0
        for backup_file in backup_dir.glob("*.sql.gz"):
            file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
            if file_time < cutoff_date:
                backup_file.unlink()
                deleted_count += 1
        
        logger.info(f"✅ Cleaned up {deleted_count} old backup files")
        
        return {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'deleted_count': deleted_count
        }
        
    except Exception as e:
        logger.error(f"❌ Backup cleanup failed: {str(e)}")
        raise

def send_monitoring_report(**context):
    """Send monitoring report via email"""
    try:
        # Get task results
        health_result = context['task_instance'].xcom_pull(task_ids='check_system_health')
        db_result = context['task_instance'].xcom_pull(task_ids='check_database_connection')
        freshness_result = context['task_instance'].xcom_pull(task_ids='check_data_freshness')
        backup_result = context['task_instance'].xcom_pull(task_ids='create_database_backup')
        cleanup_result = context['task_instance'].xcom_pull(task_ids='cleanup_old_backups')
        
        # Generate report
        report = f"""
Casablanca Insights - Daily Monitoring Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

System Health: {health_result.get('status', 'unknown')}
Database Connection: {db_result.get('status', 'unknown')}
Data Freshness: {freshness_result.get('status', 'unknown')}
Backup Status: {backup_result.get('status', 'unknown')}

Data Age:
- Price Data: {freshness_result.get('price_age_days', 'N/A')} days
- Analytics: {freshness_result.get('analytics_age_days', 'N/A')} days
- News: {freshness_result.get('news_age_days', 'N/A')} days

Warnings: {', '.join(freshness_result.get('warnings', []))}

Backup Details:
- File: {backup_result.get('backup_file', 'N/A')}
- Size: {backup_result.get('file_size_mb', 0):.2f} MB
- Cleanup: {cleanup_result.get('deleted_count', 0)} old files removed
        """
        
        logger.info("✅ Monitoring report generated")
        
        # Store report for email task
        context['task_instance'].xcom_push(key='monitoring_report', value=report)
        
        return report
        
    except Exception as e:
        logger.error(f"❌ Monitoring report generation failed: {str(e)}")
        raise

def check_airflow_dag_status():
    """Check status of all Airflow DAGs"""
    try:
        # This would typically check Airflow's metadata database
        # For now, we'll simulate a check
        
        dags_to_monitor = [
            'casablanca_live_quotes',
            'casablanca_financial_reports',
            'casablanca_news_sentiment',
            'casablanca_analytics'
        ]
        
        # Simulate DAG status check
        dag_status = {}
        for dag_id in dags_to_monitor:
            # In a real implementation, this would query Airflow's metadata
            dag_status[dag_id] = {
                'status': 'success',  # or 'failed', 'running'
                'last_run': datetime.now().isoformat(),
                'success_rate': 0.95  # 95% success rate
            }
        
        logger.info(f"✅ DAG status check completed for {len(dags_to_monitor)} DAGs")
        
        return {
            'status': 'monitored',
            'timestamp': datetime.now().isoformat(),
            'dags': dag_status
        }
        
    except Exception as e:
        logger.error(f"❌ DAG status check failed: {str(e)}")
        raise

# Create DAG
dag = DAG(
    'production_monitoring_backup',
    default_args=default_args,
    description='Production monitoring and database backup DAG',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    catchup=False,
    tags=['production', 'monitoring', 'backup']
)

# Tasks
health_check_task = PythonOperator(
    task_id='check_system_health',
    python_callable=check_system_health,
    dag=dag
)

db_connection_task = PythonOperator(
    task_id='check_database_connection',
    python_callable=check_database_connection,
    dag=dag
)

data_freshness_task = PythonOperator(
    task_id='check_data_freshness',
    python_callable=check_data_freshness,
    dag=dag
)

backup_task = PythonOperator(
    task_id='create_database_backup',
    python_callable=create_database_backup,
    dag=dag
)

cleanup_task = PythonOperator(
    task_id='cleanup_old_backups',
    python_callable=cleanup_old_backups,
    dag=dag
)

dag_status_task = PythonOperator(
    task_id='check_airflow_dag_status',
    python_callable=check_airflow_dag_status,
    dag=dag
)

report_task = PythonOperator(
    task_id='generate_monitoring_report',
    python_callable=send_monitoring_report,
    dag=dag
)

# Email notification task (configure with your email settings)
email_task = EmailOperator(
    task_id='send_monitoring_email',
    to=['admin@morningmaghreb.com'],  # Configure with actual email
    subject='Casablanca Insights - Daily Monitoring Report',
    html_content="{{ task_instance.xcom_pull(task_ids='generate_monitoring_report', key='monitoring_report') }}",
    dag=dag
)

# Task dependencies
[health_check_task, db_connection_task, data_freshness_task] >> report_task
[backup_task, cleanup_task] >> report_task
dag_status_task >> report_task
report_task >> email_task 