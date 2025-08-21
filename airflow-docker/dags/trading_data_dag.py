"""
Trading Data Pipeline DAG

This DAG fetches historical trading data for all 78 CSE companies using yfinance API.
This is an immediate win to get the website functional with real trading data.

Schedule: Daily at 8:00 AM UTC (weekdays)
"""

from datetime import datetime, timedelta
import logging
import pandas as pd
import yfinance as yf
import json
from pathlib import Path
from typing import List, Dict, Optional
import time

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
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
    'trading_data_pipeline',
    default_args=default_args,
    description='Daily trading data pipeline for CSE companies using yfinance',
    schedule_interval='0 8 * * 1-5',  # Weekdays at 8:00 AM UTC
    max_active_runs=1,
    tags=['trading', 'yfinance', 'morocco'],
)

# Load company data
def load_cse_companies() -> List[Dict]:
    """Load the list of CSE companies from our data file"""
    try:
        data_file = Path("apps/backend/data/cse_companies_african_markets.json")
        with open(data_file, 'r') as f:
            companies = json.load(f)
        
        logger.info(f"Loaded {len(companies)} companies from data file")
        return companies
        
    except Exception as e:
        logger.error(f"Error loading companies: {e}")
        # Fallback to core companies if file not found
        return [
            {"ticker": "ATW", "name": "Attijariwafa Bank"},
            {"ticker": "IAM", "name": "Maroc Telecom"},
            {"ticker": "BCP", "name": "Banque Centrale Populaire"},
            {"ticker": "BMCE", "name": "BMCE Bank of Africa"},
            {"ticker": "CIH", "name": "CIH Bank"},
            {"ticker": "CDM", "name": "Crédit du Maroc"},
            {"ticker": "WAA", "name": "Wafa Assurance"},
            {"ticker": "SAH", "name": "Saham Assurance"},
            {"ticker": "ADH", "name": "Alliance Holding"},
            {"ticker": "RDS", "name": "Risma"}
        ]

def fetch_trading_data_batch(tickers: List[str], **context) -> Dict:
    """Fetch trading data for a batch of tickers"""
    try:
        logger.info(f"Fetching trading data for batch: {tickers}")
        
        batch_results = []
        failed_tickers = []
        
        for ticker in tickers:
            try:
                # Add .MA suffix for Moroccan stocks on yfinance
                yf_ticker = f"{ticker}.MA"
                logger.info(f"Fetching data for {yf_ticker}")
                
                # Fetch 90 days of daily data
                df = yf.download(
                    yf_ticker, 
                    period="90d", 
                    interval="1d",
                    progress=False,
                    show_errors=False
                )
                
                if df.empty:
                    logger.warning(f"No data found for {yf_ticker}")
                    failed_tickers.append(ticker)
                    continue
                
                # Reset index to make date a column
                df.reset_index(inplace=True)
                df['ticker'] = ticker
                df['yf_ticker'] = yf_ticker
                
                # Convert to dict for storage
                ticker_data = {
                    'ticker': ticker,
                    'yf_ticker': yf_ticker,
                    'data_points': len(df),
                    'date_range': {
                        'start': df['Date'].min().isoformat() if not df.empty else None,
                        'end': df['Date'].max().isoformat() if not df.empty else None
                    },
                    'latest_price': float(df['Close'].iloc[-1]) if not df.empty else None,
                    'data': df.to_dict('records')
                }
                
                batch_results.append(ticker_data)
                logger.info(f"Successfully fetched {len(df)} data points for {ticker}")
                
                # Rate limiting to avoid API issues
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error fetching data for {ticker}: {e}")
                failed_tickers.append(ticker)
                continue
        
        # Store results in XCom
        context['task_instance'].xcom_push(
            key='batch_results',
            value=batch_results
        )
        
        context['task_instance'].xcom_push(
            key='failed_tickers',
            value=failed_tickers
        )
        
        logger.info(f"Batch completed: {len(batch_results)} successful, {len(failed_tickers)} failed")
        
        return {
            'successful': len(batch_results),
            'failed': len(failed_tickers),
            'total_tickers': len(tickers)
        }
        
    except Exception as e:
        logger.error(f"Error in fetch_trading_data_batch: {e}")
        raise

def validate_trading_data(**context) -> bool:
    """Validate the quality of fetched trading data"""
    try:
        logger.info("Validating trading data quality...")
        
        # Get batch results from previous task
        batch_results = context['task_instance'].xcom_pull(
            task_ids='fetch_trading_data',
            key='batch_results'
        )
        
        if not batch_results:
            logger.warning("No trading data to validate")
            return False
        
        validation_results = []
        
        for ticker_data in batch_results:
            ticker = ticker_data['ticker']
            data = ticker_data['data']
            
            # Basic validation checks
            checks = {
                'has_data': len(data) > 0,
                'has_recent_data': False,
                'has_price_data': False,
                'has_volume_data': False,
                'price_range_valid': False
            }
            
            if len(data) > 0:
                latest_record = data[-1]
                
                # Check for recent data (within last 7 days)
                latest_date = pd.to_datetime(latest_record['Date'])
                days_old = (datetime.now() - latest_date).days
                checks['has_recent_data'] = days_old <= 7
                
                # Check for price data
                checks['has_price_data'] = (
                    latest_record.get('Close') is not None and 
                    latest_record.get('Close') > 0
                )
                
                # Check for volume data
                checks['has_volume_data'] = latest_record.get('Volume') is not None
                
                # Check price range (should be reasonable for MAD)
                if checks['has_price_data']:
                    price = latest_record['Close']
                    checks['price_range_valid'] = 0 < price < 10000  # Reasonable MAD range
            
            validation_results.append({
                'ticker': ticker,
                'checks': checks,
                'passed': all(checks.values())
            })
        
        # Store validation results
        context['task_instance'].xcom_push(
            key='validation_results',
            value=validation_results
        )
        
        # Calculate overall validation score
        passed_count = sum(1 for r in validation_results if r['passed'])
        total_count = len(validation_results)
        validation_score = passed_count / total_count if total_count > 0 else 0
        
        logger.info(f"Validation complete: {passed_count}/{total_count} tickers passed ({validation_score:.1%})")
        
        return validation_score >= 0.8  # Require 80% pass rate
        
    except Exception as e:
        logger.error(f"Error in validate_trading_data: {e}")
        raise

def store_trading_data(**context) -> int:
    """Store validated trading data in database"""
    try:
        logger.info("Storing trading data in database...")
        
        # Get validated data
        batch_results = context['task_instance'].xcom_pull(
            task_ids='fetch_trading_data',
            key='batch_results'
        )
        
        validation_results = context['task_instance'].xcom_pull(
            task_ids='validate_trading_data',
            key='validation_results'
        )
        
        if not batch_results:
            logger.warning("No data to store")
            return 0
        
        # Create a mapping of validation results
        validation_map = {r['ticker']: r['passed'] for r in validation_results}
        
        stored_count = 0
        
        for ticker_data in batch_results:
            ticker = ticker_data['ticker']
            
            # Only store data that passed validation
            if not validation_map.get(ticker, False):
                logger.info(f"Skipping {ticker} - failed validation")
                continue
            
            try:
                # In production, this would insert into PostgreSQL
                # For now, save to JSON file
                data_dir = Path("/tmp/trading_data")
                data_dir.mkdir(exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"trading_data_{ticker}_{timestamp}.json"
                filepath = data_dir / filename
                
                with open(filepath, 'w') as f:
                    json.dump(ticker_data, f, indent=2)
                
                stored_count += 1
                logger.info(f"Stored trading data for {ticker}")
                
            except Exception as e:
                logger.error(f"Error storing data for {ticker}: {e}")
                continue
        
        # Store final count
        context['task_instance'].xcom_push(
            key='stored_count',
            value=stored_count
        )
        
        logger.info(f"Successfully stored trading data for {stored_count} companies")
        return stored_count
        
    except Exception as e:
        logger.error(f"Error in store_trading_data: {e}")
        raise

def send_trading_data_alert(**context) -> bool:
    """Send alert about trading data pipeline results"""
    try:
        logger.info("Sending trading data pipeline alert...")
        
        # Get pipeline results
        batch_result = context['task_instance'].xcom_pull(
            task_ids='fetch_trading_data'
        )
        
        stored_count = context['task_instance'].xcom_pull(
            task_ids='store_trading_data',
            key='stored_count'
        )
        
        validation_passed = context['task_instance'].xcom_pull(
            task_ids='validate_trading_data'
        )
        
        # Create alert message
        message = f"""
📈 Trading Data Pipeline Results

✅ Pipeline Status: {'Success' if validation_passed else 'Warning'}
📊 Data Fetched: {batch_result.get('successful', 0)} companies
💾 Data Stored: {stored_count} companies
❌ Failed: {batch_result.get('failed', 0)} companies
📅 Execution Date: {context['execution_date']}

🔗 Access Points:
• Airflow UI: http://localhost:8080
• Trading Data: /tmp/trading_data/
        """
        
        logger.info(message)
        
        # In production, this would send to Slack, email, etc.
        return True
        
    except Exception as e:
        logger.error(f"Error in send_trading_data_alert: {e}")
        raise

# Create dynamic tasks for each batch
def create_batch_tasks():
    """Create batch tasks for all companies"""
    companies = load_cse_companies()
    tickers = [c['ticker'] for c in companies]
    
    # Split into batches of 10
    BATCH_SIZE = 10
    batches = [tickers[i:i+BATCH_SIZE] for i in range(0, len(tickers), BATCH_SIZE)]
    
    logger.info(f"Created {len(batches)} batches for {len(tickers)} companies")
    
    # Create a task for each batch
    batch_tasks = []
    for i, batch in enumerate(batches):
        task = PythonOperator(
            task_id=f'fetch_batch_{i}',
            python_callable=fetch_trading_data_batch,
            op_kwargs={'tickers': batch},
            dag=dag,
        )
        batch_tasks.append(task)
    
    return batch_tasks

# Create the batch tasks
batch_tasks = create_batch_tasks()

# Define other tasks
validate_data = PythonOperator(
    task_id='validate_trading_data',
    python_callable=validate_trading_data,
    dag=dag,
)

store_data = PythonOperator(
    task_id='store_trading_data',
    python_callable=store_trading_data,
    dag=dag,
)

send_alert = PythonOperator(
    task_id='send_trading_data_alert',
    python_callable=send_trading_data_alert,
    dag=dag,
)

# Define task dependencies
# All batch tasks run in parallel, then validate, store, and alert
batch_tasks >> validate_data >> store_data >> send_alert 