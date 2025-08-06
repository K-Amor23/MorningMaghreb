"""
Master Airflow DAG for Casablanca Insights
Coordinates all data collection and processing tasks
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.hooks.base import BaseHook
from airflow.models import Variable
import os
import sys
import logging

# Add project root to path
sys.path.append('/opt/airflow/dags')

# Default arguments
default_args = {
    'owner': 'casablanca-insights',
    'depends_on_past': False,
    'start_date': datetime(2025, 8, 6),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False
}

# DAG definition
dag = DAG(
    'casablanca_insights_master',
    default_args=default_args,
    description='Master DAG for Casablanca Insights data pipeline',
    schedule_interval='0 6 * * *',  # Daily at 6 AM
    max_active_runs=1,
    tags=['casablanca', 'data', 'scraping']
)

def get_supabase_connection():
    """Get Supabase connection details from Airflow"""
    try:
        connection = BaseHook.get_connection("supabase")
        return {
            'url': connection.host,
            'key': connection.password,
            'service_role_key': connection.extra_dejson.get('service_role_key')
        }
    except Exception as e:
        logging.warning(f"Could not get Supabase connection: {e}")
        return None

def run_orchestrator(**context):
    """Run the master orchestrator"""
    import subprocess
    import json
    from datetime import datetime
    
    # Get execution date
    execution_date = context['execution_date']
    
    # Set environment variables
    supabase_config = get_supabase_connection()
    if supabase_config:
        os.environ['NEXT_PUBLIC_SUPABASE_URL'] = supabase_config['url']
        os.environ['NEXT_PUBLIC_SUPABASE_ANON_KEY'] = supabase_config['key']
        os.environ['SUPABASE_SERVICE_ROLE_KEY'] = supabase_config['service_role_key']
    
    # Set other required environment variables
    os.environ['OPENAI_API_KEY'] = Variable.get("openai_api_key", default_var="")
    os.environ['SENDGRID_API_KEY'] = Variable.get("sendgrid_api_key", default_var="")
    os.environ['STRIPE_SECRET_KEY'] = Variable.get("stripe_secret_key", default_var="")
    
    try:
        # Run orchestrator
        result = subprocess.run([
            'python', '/opt/airflow/dags/scripts/run_orchestrator.py'
        ], capture_output=True, text=True, cwd='/opt/airflow/dags')
        
        if result.returncode == 0:
            logging.info("Orchestrator completed successfully")
            return "SUCCESS"
        else:
            logging.error(f"Orchestrator failed: {result.stderr}")
            raise Exception(f"Orchestrator failed: {result.stderr}")
            
    except Exception as e:
        logging.error(f"Error running orchestrator: {e}")
        raise

def validate_data_quality(**context):
    """Validate data quality after scraping"""
    import pandas as pd
    from supabase import create_client, Client
    
    # Get Supabase connection
    supabase_config = get_supabase_connection()
    if not supabase_config:
        raise Exception("Supabase connection not available")
    
    supabase: Client = create_client(
        supabase_config['url'], 
        supabase_config['service_role_key']
    )
    
    # Check data quality metrics
    quality_checks = []
    
    # Check companies table
    try:
        companies_response = supabase.table('companies').select('*').execute()
        companies_count = len(companies_response.data)
        quality_checks.append(f"Companies: {companies_count} records")
        
        if companies_count < 10:
            raise Exception(f"Too few companies: {companies_count}")
            
    except Exception as e:
        logging.error(f"Companies quality check failed: {e}")
        raise
    
    # Check market data
    try:
        market_data_response = supabase.table('market_data').select('*').execute()
        market_data_count = len(market_data_response.data)
        quality_checks.append(f"Market data: {market_data_count} records")
        
        if market_data_count < 50:
            raise Exception(f"Too little market data: {market_data_count}")
            
    except Exception as e:
        logging.error(f"Market data quality check failed: {e}")
        raise
    
    # Check for recent data
    try:
        today = datetime.now().date()
        recent_data = supabase.table('market_data').select('*').gte('date', str(today)).execute()
        
        if len(recent_data.data) == 0:
            logging.warning("No recent market data found")
        else:
            quality_checks.append(f"Recent data: {len(recent_data.data)} records")
            
    except Exception as e:
        logging.warning(f"Recent data check failed: {e}")
    
    logging.info(f"Data quality checks: {'; '.join(quality_checks)}")
    return "SUCCESS"

def send_notification(**context):
    """Send notification about pipeline status"""
    task_instance = context['task_instance']
    
    # Get task results
    orchestrator_result = task_instance.xcom_pull(task_ids='run_orchestrator')
    validation_result = task_instance.xcom_pull(task_ids='validate_data_quality')
    
    # Determine overall status
    if orchestrator_result == "SUCCESS" and validation_result == "SUCCESS":
        subject = "✅ Casablanca Insights Pipeline - SUCCESS"
        html_content = """
        <h2>Pipeline Completed Successfully</h2>
        <p>The Casablanca Insights data pipeline has completed successfully.</p>
        <ul>
            <li>✅ Orchestrator completed</li>
            <li>✅ Data quality validated</li>
        </ul>
        <p>All data sources have been updated.</p>
        """
    else:
        subject = "❌ Casablanca Insights Pipeline - FAILED"
        html_content = """
        <h2>Pipeline Failed</h2>
        <p>The Casablanca Insights data pipeline has failed.</p>
        <ul>
            <li>Orchestrator: {}</li>
            <li>Validation: {}</li>
        </ul>
        <p>Please check the Airflow logs for details.</p>
        """.format(orchestrator_result, validation_result)
    
    return {
        'subject': subject,
        'html_content': html_content
    }

# Task definitions
run_orchestrator_task = PythonOperator(
    task_id='run_orchestrator',
    python_callable=run_orchestrator,
    provide_context=True,
    dag=dag
)

validate_data_task = PythonOperator(
    task_id='validate_data_quality',
    python_callable=validate_data_quality,
    provide_context=True,
    dag=dag
)

send_notification_task = PythonOperator(
    task_id='send_notification',
    python_callable=send_notification,
    provide_context=True,
    dag=dag
)

# Task dependencies
run_orchestrator_task >> validate_data_task >> send_notification_task

# Email notification task
email_task = EmailOperator(
    task_id='send_email_notification',
    to=Variable.get("notification_email", default_var="admin@casablanca-insights.com"),
    subject="{{ task_instance.xcom_pull(task_ids='send_notification')['subject'] }}",
    html_content="{{ task_instance.xcom_pull(task_ids='send_notification')['html_content'] }}",
    dag=dag
)

send_notification_task >> email_task 