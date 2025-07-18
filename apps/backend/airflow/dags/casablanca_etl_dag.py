"""
Casablanca Insights ETL Pipeline DAG

This DAG automates the daily financial data pipeline:
1. Fetch IR reports from company websites
2. Extract financial data from PDFs
3. Translate French labels to GAAP
4. Store processed data in database
5. Send success/failure alerts

Schedule: Daily at 6:00 AM UTC
"""

from datetime import datetime, timedelta
import asyncio
import aiohttp
import logging
import json
import os
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.models import Variable

# Configure logging
logger = logging.getLogger(__name__)

# Default arguments for the DAG
default_args = {
    'owner': 'casablanca_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
}

# DAG definition
dag = DAG(
    'casablanca_etl_pipeline',
    default_args=default_args,
    description='Daily ETL pipeline for Casablanca Insights financial data',
    schedule_interval='0 6 * * *',  # Daily at 6:00 AM UTC
    max_active_runs=1,
    tags=['etl', 'financial', 'morocco'],
)

def fetch_ir_reports_task(**context):
    """Task to fetch IR reports from company websites"""
    try:
        logger.info("Starting IR report fetching...")
        
        # Get companies to process (from Airflow variables or default)
        companies = Variable.get("etl_companies", deserialize_json=True, default_var=["ATW", "IAM", "BCP", "BMCE"])
        year = context['execution_date'].year
        
        logger.info(f"Fetching reports for companies: {companies}, year: {year}")
        
        # Simulate fetching reports (in production, this would use the actual fetcher)
        reports = []
        for company in companies:
            reports.append({
                'company': company,
                'year': year,
                'quarter': 1,
                'report_type': 'annual',
                'url': f'https://example.com/{company}/annual_report_{year}.pdf',
                'filename': f'{company}_annual_{year}.pdf'
            })
        
        # Simulate downloading files
        downloaded_files = [f'/tmp/{report["filename"]}' for report in reports]
        
        # Store results in XCom for next task
        context['task_instance'].xcom_push(
            key='downloaded_files',
            value=downloaded_files
        )
        
        context['task_instance'].xcom_push(
            key='reports_metadata',
            value=[{
                'company': r['company'],
                'year': r['year'],
                'quarter': r.get('quarter'),
                'report_type': r['report_type'],
                'url': r['url']
            } for r in reports]
        )
        
        logger.info(f"Successfully fetched {len(reports)} reports, downloaded {len(downloaded_files)} files")
        return len(downloaded_files)
        
    except Exception as e:
        logger.error(f"Error in fetch_ir_reports_task: {e}")
        raise

def extract_pdf_data_task(**context):
    """Task to extract financial data from PDFs"""
    try:
        logger.info("Starting PDF data extraction...")
        
        # Get downloaded files from previous task
        downloaded_files = context['task_instance'].xcom_pull(
            task_ids='fetch_ir_reports',
            key='downloaded_files'
        )
        
        reports_metadata = context['task_instance'].xcom_pull(
            task_ids='fetch_ir_reports',
            key='reports_metadata'
        )
        
        if not downloaded_files:
            logger.warning("No files to process")
            return 0
        
        # Simulate PDF extraction (in production, this would use the actual extractor)
        extracted_data = []
        
        for i, pdf_path in enumerate(downloaded_files):
            try:
                metadata = reports_metadata[i] if i < len(reports_metadata) else {}
                
                # Simulate extracted financial data
                financial_data = {
                    'company': metadata.get('company', 'UNKNOWN'),
                    'year': metadata.get('year', datetime.now().year),
                    'report_type': metadata.get('report_type', 'other'),
                    'quarter': metadata.get('quarter'),
                    'lines': [
                        {'label': 'Revenue', 'value': 1000000, 'currency': 'MAD'},
                        {'label': 'Net Income', 'value': 150000, 'currency': 'MAD'},
                        {'label': 'Total Assets', 'value': 5000000, 'currency': 'MAD'}
                    ]
                }
                
                extracted_data.append({
                    'pdf_path': pdf_path,
                    'financial_data': financial_data,
                    'metadata': metadata
                })
                
                logger.info(f"Extracted {len(financial_data['lines'])} lines from {pdf_path}")
                    
            except Exception as e:
                logger.error(f"Error extracting from {pdf_path}: {e}")
                continue
        
        # Store results in XCom
        context['task_instance'].xcom_push(
            key='extracted_data',
            value=extracted_data
        )
        
        logger.info(f"Successfully extracted data from {len(extracted_data)} PDFs")
        return len(extracted_data)
        
    except Exception as e:
        logger.error(f"Error in extract_pdf_data_task: {e}")
        raise

def translate_to_gaap_task(**context):
    """Task to translate French labels to GAAP"""
    try:
        logger.info("Starting GAAP translation...")
        
        # Get extracted data from previous task
        extracted_data = context['task_instance'].xcom_pull(
            task_ids='extract_pdf_data',
            key='extracted_data'
        )
        
        if not extracted_data:
            logger.warning("No data to translate")
            return 0
        
        # Simulate GAAP translation (in production, this would use the actual translator)
        translated_data = []
        
        for item in extracted_data:
            try:
                financial_data = item['financial_data']
                
                # Simulate GAAP translation
                gaap_data = {
                    'company': financial_data['company'],
                    'year': financial_data['year'],
                    'report_type': financial_data['report_type'],
                    'quarter': financial_data['quarter'],
                    'data': [
                        {'gaap_label': 'Revenue', 'value': financial_data['lines'][0]['value'], 'currency': 'MAD'},
                        {'gaap_label': 'Net Income', 'value': financial_data['lines'][1]['value'], 'currency': 'MAD'},
                        {'gaap_label': 'Total Assets', 'value': financial_data['lines'][2]['value'], 'currency': 'MAD'}
                    ]
                }
                
                translated_data.append({
                    'original_data': item,
                    'gaap_data': gaap_data,
                    'metadata': item['metadata']
                })
                
                logger.info(f"Translated {len(gaap_data['data'])} items for {item['metadata'].get('company')}")
                    
            except Exception as e:
                logger.error(f"Error translating {item['pdf_path']}: {e}")
                continue
        
        # Store results in XCom
        context['task_instance'].xcom_push(
            key='translated_data',
            value=translated_data
        )
        
        logger.info(f"Successfully translated {len(translated_data)} datasets")
        return len(translated_data)
        
    except Exception as e:
        logger.error(f"Error in translate_to_gaap_task: {e}")
        raise

def store_data_task(**context):
    """Task to store processed data in database"""
    try:
        logger.info("Starting data storage...")
        
        # Get translated data from previous task
        translated_data = context['task_instance'].xcom_pull(
            task_ids='translate_to_gaap',
            key='translated_data'
        )
        
        if not translated_data:
            logger.warning("No data to store")
            return 0
        
        # Simulate data storage (in production, this would use the actual database)
        stored_count = 0
        
        for item in translated_data:
            try:
                gaap_data = item['gaap_data']
                
                # Simulate database storage
                stored_count += 1
                logger.info(f"Stored data for {item['metadata'].get('company')}")
                
            except Exception as e:
                logger.error(f"Error storing data for {item['metadata'].get('company')}: {e}")
                continue
        
        # Store final count in XCom
        context['task_instance'].xcom_push(
            key='stored_count',
            value=stored_count
        )
        
        logger.info(f"Successfully stored {stored_count} datasets")
        return stored_count
        
    except Exception as e:
        logger.error(f"Error in store_data_task: {e}")
        raise

def validate_data_task(**context):
    """Task to validate stored data"""
    try:
        logger.info("Starting data validation...")
        
        # Get stored count from previous task
        stored_count = context['task_instance'].xcom_pull(
            task_ids='store_data',
            key='stored_count'
        )
        
        if stored_count == 0:
            logger.warning("No data to validate")
            return False
        
        # Simulate validation checks
        validation_passed = True
        
        # Check if we have data for all expected companies
        companies = Variable.get("etl_companies", deserialize_json=True, default_var=["ATW", "IAM", "BCP", "BMCE"])
        if stored_count < len(companies):
            logger.warning(f"Expected data for {len(companies)} companies, but only stored {stored_count}")
            validation_passed = False
        
        # Store validation result
        context['task_instance'].xcom_push(
            key='validation_passed',
            value=validation_passed
        )
        
        logger.info(f"Data validation {'passed' if validation_passed else 'failed'}")
        return validation_passed
        
    except Exception as e:
        logger.error(f"Error in validate_data_task: {e}")
        raise

def send_success_alert(**context):
    """Task to send success alert"""
    try:
        logger.info("Sending success alert...")
        
        # Get pipeline results
        stored_count = context['task_instance'].xcom_pull(
            task_ids='store_data',
            key='stored_count'
        )
        
        validation_passed = context['task_instance'].xcom_pull(
            task_ids='validate_data',
            key='validation_passed'
        )
        
        # Create success message
        message = f"""
🎉 Casablanca Insights ETL Pipeline Completed Successfully!

📊 Pipeline Results:
• Reports Processed: {stored_count}
• Data Validation: {'✅ Passed' if validation_passed else '❌ Failed'}
• Execution Date: {context['execution_date']}

🔗 Access Points:
• Airflow UI: http://localhost:8080
• Casablanca API: http://localhost:8000
        """
        
        logger.info(message)
        
        # In production, this would send to Slack, email, etc.
        # For now, just log the message
        
        return True
        
    except Exception as e:
        logger.error(f"Error in send_success_alert: {e}")
        raise

def send_failure_alert(**context):
    """Task to send failure alert"""
    try:
        logger.error("Sending failure alert...")
        
        # Get failure information
        task_instance = context['task_instance']
        dag_id = context['dag'].dag_id
        task_id = context['task'].task_id
        execution_date = context['execution_date']
        
        # Create failure message
        message = f"""
❌ Casablanca Insights ETL Pipeline Failed!

🚨 Failure Details:
• DAG: {dag_id}
• Failed Task: {task_id}
• Execution Date: {execution_date}
• Error: {context.get('exception', 'Unknown error')}

🔗 Access Points:
• Airflow UI: http://localhost:8080
• Check logs for detailed error information
        """
        
        logger.error(message)
        
        # In production, this would send to Slack, email, etc.
        # For now, just log the message
        
        return True
        
    except Exception as e:
        logger.error(f"Error in send_failure_alert: {e}")
        raise

# Define tasks
fetch_reports = PythonOperator(
    task_id='fetch_ir_reports',
    python_callable=fetch_ir_reports_task,
    dag=dag,
)

extract_pdf = PythonOperator(
    task_id='extract_pdf_data',
    python_callable=extract_pdf_data_task,
    dag=dag,
)

translate_gaap = PythonOperator(
    task_id='translate_to_gaap',
    python_callable=translate_to_gaap_task,
    dag=dag,
)

store_data = PythonOperator(
    task_id='store_data',
    python_callable=store_data_task,
    dag=dag,
)

validate_data = PythonOperator(
    task_id='validate_data',
    python_callable=validate_data_task,
    dag=dag,
)

success_alert = PythonOperator(
    task_id='send_success_alert',
    python_callable=send_success_alert,
    dag=dag,
    trigger_rule='all_success',
)

failure_alert = PythonOperator(
    task_id='send_failure_alert',
    python_callable=send_failure_alert,
    dag=dag,
    trigger_rule='one_failed',
)

# Define task dependencies
fetch_reports >> extract_pdf >> translate_gaap >> store_data >> validate_data >> [success_alert, failure_alert] 