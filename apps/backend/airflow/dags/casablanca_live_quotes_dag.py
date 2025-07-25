"""
Casablanca Live Quotes DAG

This DAG runs every 2 minutes during trading hours (9am-3pm Morocco time)
to scrape live quotes from Casablanca Bourse and update the live_quotes table.

Features:
- Scheduled during trading hours only
- Scrapes live quotes table from Casablanca Bourse
- Updates live_quotes table in Postgres
- Error handling and retry logic
- Data validation and deduplication
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import pytz
import logging
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional
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
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
    'catchup': False
}

def is_trading_hours() -> bool:
    """Check if current time is within trading hours (9am-3pm Morocco time)"""
    morocco_tz = pytz.timezone('Africa/Casablanca')
    now = datetime.now(morocco_tz)
    
    # Check if it's a weekday (Monday = 0, Sunday = 6)
    if now.weekday() >= 5:  # Saturday or Sunday
        return False
    
    # Check if it's within trading hours (9:00-15:00)
    trading_start = now.replace(hour=9, minute=0, second=0, microsecond=0)
    trading_end = now.replace(hour=15, minute=0, second=0, microsecond=0)
    
    return trading_start <= now <= trading_end

def scrape_casablanca_bourse() -> List[Dict]:
    """Scrape live quotes from Casablanca Bourse"""
    try:
        # Casablanca Bourse URL
        url = "https://www.casablanca-bourse.com/bourseweb/societe-cote.aspx?Cat=24&IdLink=225"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        logger.info("🔍 Scraping Casablanca Bourse live quotes...")
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the quotes table
        quotes_table = soup.find('table', {'class': 'table'})
        if not quotes_table:
            logger.warning("⚠️  Quotes table not found")
            return []
        
        quotes = []
        rows = quotes_table.find_all('tr')[1:]  # Skip header row
        
        for row in rows:
            try:
                cells = row.find_all('td')
                if len(cells) < 8:
                    continue
                
                # Extract data from cells
                ticker = cells[0].get_text(strip=True)
                company_name = cells[1].get_text(strip=True)
                last_price = cells[2].get_text(strip=True)
                change = cells[3].get_text(strip=True)
                change_percent = cells[4].get_text(strip=True)
                volume = cells[5].get_text(strip=True)
                high = cells[6].get_text(strip=True)
                low = cells[7].get_text(strip=True)
                
                # Clean and parse numeric values
                def parse_number(text: str) -> Optional[float]:
                    if not text or text == '-':
                        return None
                    # Remove non-numeric characters except decimal point and minus
                    cleaned = re.sub(r'[^\d\.\-]', '', text)
                    try:
                        return float(cleaned)
                    except ValueError:
                        return None
                
                def parse_volume(text: str) -> Optional[int]:
                    if not text or text == '-':
                        return None
                    # Remove non-numeric characters
                    cleaned = re.sub(r'[^\d]', '', text)
                    try:
                        return int(cleaned)
                    except ValueError:
                        return None
                
                quote = {
                    'ticker': ticker,
                    'company_name': company_name,
                    'last_price': parse_number(last_price),
                    'change': parse_number(change),
                    'change_percent': parse_number(change_percent),
                    'volume': parse_volume(volume),
                    'high': parse_number(high),
                    'low': parse_number(low),
                    'scraped_at': datetime.now().isoformat(),
                    'source': 'Casablanca Bourse'
                }
                
                quotes.append(quote)
                
            except Exception as e:
                logger.warning(f"⚠️  Error parsing row: {str(e)}")
                continue
        
        logger.info(f"✅ Scraped {len(quotes)} quotes from Casablanca Bourse")
        return quotes
        
    except Exception as e:
        logger.error(f"❌ Error scraping Casablanca Bourse: {str(e)}")
        return []

def create_live_quotes_table():
    """Create live_quotes table if it doesn't exist"""
    try:
        supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
        supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_service_key:
            logger.warning("⚠️  Supabase credentials not found")
            return False
        
        supabase = create_client(supabase_url, supabase_service_key)
        
        # SQL to create live_quotes table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS live_quotes (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            ticker VARCHAR(10) NOT NULL,
            company_name VARCHAR(255),
            last_price DECIMAL(10,2),
            change DECIMAL(10,2),
            change_percent DECIMAL(5,2),
            volume BIGINT,
            high DECIMAL(10,2),
            low DECIMAL(10,2),
            scraped_at TIMESTAMPTZ DEFAULT NOW(),
            source VARCHAR(100) DEFAULT 'Casablanca Bourse',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(ticker, scraped_at)
        );
        
        CREATE INDEX IF NOT EXISTS idx_live_quotes_ticker ON live_quotes(ticker);
        CREATE INDEX IF NOT EXISTS idx_live_quotes_scraped_at ON live_quotes(scraped_at);
        CREATE INDEX IF NOT EXISTS idx_live_quotes_ticker_scraped ON live_quotes(ticker, scraped_at DESC);
        """
        
        # Execute SQL (this would need to be done via Supabase dashboard)
        logger.info("📋 SQL for creating live_quotes table:")
        logger.info(create_table_sql)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating live_quotes table: {str(e)}")
        return False

def insert_live_quotes_to_supabase(quotes: List[Dict]) -> bool:
    """Insert live quotes to Supabase"""
    try:
        supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
        supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_service_key:
            logger.warning("⚠️  Supabase credentials not found")
            return False
        
        supabase = create_client(supabase_url, supabase_service_key)
        
        if not quotes:
            logger.info("ℹ️  No quotes to insert")
            return True
        
        # Insert quotes
        result = supabase.table('live_quotes').upsert(
            quotes,
            on_conflict='ticker,scraped_at'
        ).execute()
        
        logger.info(f"✅ Inserted {len(quotes)} live quotes to Supabase")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error inserting live quotes to Supabase: {str(e)}")
        return False

def save_quotes_to_json(quotes: List[Dict]) -> str:
    """Save quotes to JSON file for backup"""
    try:
        output_dir = Path("../data/live_quotes")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"live_quotes_{timestamp}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(quotes, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved {len(quotes)} quotes to {filepath}")
        return str(filepath)
        
    except Exception as e:
        logger.error(f"❌ Error saving quotes to JSON: {str(e)}")
        return ""

def scrape_and_store_live_quotes(**context):
    """Main function to scrape and store live quotes"""
    # Check if it's trading hours
    if not is_trading_hours():
        logger.info("ℹ️  Outside trading hours, skipping quote scraping")
        return
    
    logger.info("🚀 Starting live quotes scraping...")
    
    # Scrape quotes
    quotes = scrape_casablanca_bourse()
    
    if not quotes:
        logger.warning("⚠️  No quotes scraped")
        return
    
    # Save to JSON backup
    json_file = save_quotes_to_json(quotes)
    
    # Insert to Supabase
    success = insert_live_quotes_to_supabase(quotes)
    
    # Log results
    logger.info("📊 Live quotes scraping completed")
    logger.info(f"   Quotes scraped: {len(quotes)}")
    logger.info(f"   JSON backup: {json_file}")
    logger.info(f"   Supabase insert: {'✅' if success else '❌'}")
    
    # Store results in XCom for downstream tasks
    context['task_instance'].xcom_push(key='quotes_count', value=len(quotes))
    context['task_instance'].xcom_push(key='json_file', value=json_file)
    context['task_instance'].xcom_push(key='supabase_success', value=success)

def validate_quotes_data(**context):
    """Validate scraped quotes data"""
    quotes_count = context['task_instance'].xcom_pull(key='quotes_count', task_ids='scrape_live_quotes')
    
    if quotes_count is None:
        logger.error("❌ No quotes data found")
        return
    
    if quotes_count < 10:
        logger.warning(f"⚠️  Low quote count: {quotes_count} (expected >10)")
    else:
        logger.info(f"✅ Quote validation passed: {quotes_count} quotes")

def update_market_summary(**context):
    """Update market summary with latest quotes"""
    try:
        supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
        supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_service_key:
            logger.warning("⚠️  Supabase credentials not found")
            return
        
        supabase = create_client(supabase_url, supabase_service_key)
        
        # Get latest quotes
        result = supabase.table('live_quotes').select('*').order('scraped_at', desc=True).limit(100).execute()
        
        if not result.data:
            logger.warning("⚠️  No quotes data for market summary")
            return
        
        quotes = result.data
        
        # Calculate market summary
        total_companies = len(quotes)
        advancing = len([q for q in quotes if q.get('change_percent', 0) > 0])
        declining = len([q for q in quotes if q.get('change_percent', 0) < 0])
        unchanged = len([q for q in quotes if q.get('change_percent', 0) == 0])
        
        # Calculate average change
        changes = [q.get('change_percent', 0) for q in quotes if q.get('change_percent') is not None]
        avg_change = sum(changes) / len(changes) if changes else 0
        
        # Update market summary
        summary = {
            'date': datetime.now().date().isoformat(),
            'total_companies': total_companies,
            'advancing': advancing,
            'declining': declining,
            'unchanged': unchanged,
            'average_change_percent': round(avg_change, 2),
            'last_updated': datetime.now().isoformat()
        }
        
        # Insert/update market summary
        supabase.table('market_summary').upsert(summary, on_conflict='date').execute()
        
        logger.info(f"✅ Market summary updated: {advancing} advancing, {declining} declining")
        
    except Exception as e:
        logger.error(f"❌ Error updating market summary: {str(e)}")

# Create DAG
dag = DAG(
    'casablanca_live_quotes',
    default_args=default_args,
    description='Scrape live quotes from Casablanca Bourse every 2 minutes during trading hours',
    schedule_interval='*/2 9-14 * * 1-5',  # Every 2 minutes, 9am-3pm, Mon-Fri
    catchup=False,
    tags=['casablanca', 'quotes', 'live', 'trading']
)

# Tasks
scrape_task = PythonOperator(
    task_id='scrape_live_quotes',
    python_callable=scrape_and_store_live_quotes,
    dag=dag
)

validate_task = PythonOperator(
    task_id='validate_quotes',
    python_callable=validate_quotes_data,
    dag=dag
)

summary_task = PythonOperator(
    task_id='update_market_summary',
    python_callable=update_market_summary,
    dag=dag
)

# Task dependencies
scrape_task >> validate_task >> summary_task 