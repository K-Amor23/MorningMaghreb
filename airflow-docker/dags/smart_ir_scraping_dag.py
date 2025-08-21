"""
Smart IR Report Scraping DAG

Production-ready DAG for intelligent IR report scraping with business logic:
- Only scrapes companies when reports are expected (based on fiscal calendar)
- Implements rotating User-Agents and proxy support
- Handles rate limiting and retries
- Provides comprehensive logging and notifications

Schedule: Daily at 2:00 AM ET
SLA: 6:00 AM ET

Business Logic:
- Q1 reports expected ~ mid-April
- Q2 reports expected ~ mid-July  
- Q3 reports expected ~ mid-October
- Q4 reports expected ~ mid-January
- Annual reports expected ~ March-April

Setup:
1. Add to $AIRFLOW_HOME/dags/
2. Configure database connection: 'supabase_postgres'
3. Set Airflow Variables:
   - SLACK_WEBHOOK_URL: Slack webhook for notifications
   - ALERT_EMAILS: JSON array of email addresses
   - PROXY_ENABLED: "true" to enable proxy rotation
   - TEST_MODE: "true" to limit to 5 companies
4. Verify DAG loads in Airflow UI
"""

from datetime import datetime, timedelta, date
import logging
import os
import json
import random
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import requests
from urllib.parse import urljoin, urlparse
import PyPDF2
import io

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models import Variable, Connection
from airflow.utils.email import send_email
from airflow.utils.session import provide_session
from airflow.utils.state import State

# Configure logging
logger = logging.getLogger(__name__)

# DAG configuration
default_args = {
    'owner': 'casablanca-insights',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(minutes=30),
}

# Schedule: Daily at 2:00 AM ET
dag = DAG(
    'smart_ir_scraping',
    default_args=default_args,
    description='Smart IR report scraping with business logic',
    schedule_interval='0 2 * * *',  # Daily at 2:00 AM ET
    catchup=False,
    max_active_runs=1,
    tags=['ir-scraping', 'production', 'smart-scheduling'],
)

# SLA: 6:00 AM ET
sla = timedelta(hours=4)

# User-Agent rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

# Common IR report paths
IR_REPORT_PATHS = [
    "/investors/annual-report.pdf",
    "/investors/reports/annual-report.pdf",
    "/investor-relations/annual-report.pdf",
    "/financial-reports/annual-report.pdf",
    "/documents/annual-report.pdf",
    "/investors/quarterly-report.pdf",
    "/investors/reports/quarterly-report.pdf",
    "/investor-relations/quarterly-report.pdf",
    "/financial-reports/quarterly-report.pdf",
    "/investors/",
    "/investor-relations/",
    "/financial-reports/",
    "/documents/",
]

def get_expected_release_date(company_ticker: str, current_date: date) -> Optional[date]:
    """
    Calculate expected release date based on fiscal calendar
    Returns None if no report is expected
    """
    try:
        # Get company fiscal year end from database
        pg_hook = PostgresHook(postgres_conn_id='supabase_postgres')
        
        query = """
        SELECT fiscal_year_end_month, fiscal_year_end_day
        FROM companies 
        WHERE ticker = %s
        """
        
        result = pg_hook.get_first(query, parameters=(company_ticker,))
        
        if not result:
            # Default to calendar year end
            fiscal_month = 12
            fiscal_day = 31
        else:
            fiscal_month = result[0] or 12
            fiscal_day = result[1] or 31
        
        # Calculate fiscal year end for current year
        fiscal_year_end = date(current_date.year, fiscal_month, fiscal_day)
        
        # If fiscal year end has passed, use next year
        if fiscal_year_end < current_date:
            fiscal_year_end = date(current_date.year + 1, fiscal_month, fiscal_day)
        
        # Expected release dates (typically 2-3 months after fiscal year end)
        expected_dates = {
            'annual': fiscal_year_end + timedelta(days=90),  # ~3 months after fiscal year end
            'q1': date(current_date.year, 4, 15),  # Mid-April
            'q2': date(current_date.year, 7, 15),  # Mid-July
            'q3': date(current_date.year, 10, 15),  # Mid-October
            'q4': date(current_date.year, 1, 15),   # Mid-January
        }
        
        # Check if any reports are expected within the next 30 days
        for report_type, expected_date in expected_dates.items():
            if expected_date <= current_date + timedelta(days=30):
                return expected_date
        
        return None
        
    except Exception as e:
        logger.error(f"Error calculating expected release date for {company_ticker}: {e}")
        return None

def get_companies_due_for_scraping(**context) -> List[Dict[str, Any]]:
    """
    Get companies that are due for scraping based on business logic
    """
    try:
        logger.info("Determining companies due for scraping...")
        
        execution_date = context['execution_date'].date()
        test_mode = Variable.get("TEST_MODE", default_var="false").lower() == "true"
        
        pg_hook = PostgresHook(postgres_conn_id='supabase_postgres')
        
        # Get all active companies
        query = """
        SELECT 
            ticker, 
            name, 
            website_url, 
            investor_relations_url,
            last_scraped_at,
            ir_expected_release_date
        FROM companies 
        WHERE is_active = 'Y' 
        AND (website_url IS NOT NULL OR investor_relations_url IS NOT NULL)
        ORDER BY ticker
        """
        
        companies = pg_hook.get_records(query)
        logger.info(f"Found {len(companies)} total companies")
        
        companies_due = []
        
        for company in companies:
            ticker, name, website_url, ir_url, last_scraped_at, expected_release_date = company
            
            # Check if company is due for scraping
            is_due = False
            reason = ""
            
            # Case 1: Never scraped before
            if last_scraped_at is None:
                is_due = True
                reason = "Never scraped before"
            
            # Case 2: Expected release date has passed
            elif expected_release_date and expected_release_date <= execution_date:
                if last_scraped_at.date() < expected_release_date:
                    is_due = True
                    reason = f"Expected release date {expected_release_date} has passed"
            
            # Case 3: Calculate expected release date based on fiscal calendar
            else:
                calculated_expected_date = get_expected_release_date(ticker, execution_date)
                if calculated_expected_date and calculated_expected_date <= execution_date:
                    if last_scraped_at.date() < calculated_expected_date:
                        is_due = True
                        reason = f"Calculated expected date {calculated_expected_date} has passed"
            
            if is_due:
                companies_due.append({
                    'ticker': ticker,
                    'name': name,
                    'website_url': website_url,
                    'ir_url': ir_url,
                    'last_scraped_at': last_scraped_at,
                    'expected_release_date': expected_release_date,
                    'reason': reason
                })
        
        # Apply test mode limit
        if test_mode and len(companies_due) > 5:
            companies_due = companies_due[:5]
            logger.info("Test mode enabled - limiting to 5 companies")
        
        logger.info(f"Found {len(companies_due)} companies due for scraping")
        
        # Store results in XCom
        context['task_instance'].xcom_push(
            key='companies_due_for_scraping',
            value=companies_due
        )
        
        return companies_due
        
    except Exception as e:
        logger.error(f"Error getting companies due for scraping: {e}")
        raise

def scrape_company_ir_reports(**context) -> Dict[str, Any]:
    """
    Scrape IR reports for companies due for scraping
    """
    try:
        logger.info("Starting smart IR report scraping...")
        
        execution_date = context['execution_date']
        companies_due = context['task_instance'].xcom_pull(
            task_ids='get_companies_due',
            key='companies_due_for_scraping'
        )
        
        if not companies_due:
            logger.info("No companies due for scraping")
            return {
                'total_companies': 0,
                'successful_scrapes': 0,
                'failed_scrapes': 0,
                'skipped_companies': 0,
                'scraped_reports': []
            }
        
        # Create output directory
        output_dir = Path(f"/tmp/ir_reports/{execution_date.strftime('%Y-%m-%d')}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get proxy configuration
        proxy_enabled = Variable.get("PROXY_ENABLED", default_var="false").lower() == "true"
        
        # Initialize results
        results = {
            'total_companies': len(companies_due),
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'skipped_companies': 0,
            'scraped_reports': [],
            'errors': []
        }
        
        for company in companies_due:
            ticker = company['ticker']
            name = company['name']
            website_url = company['website_url']
            ir_url = company['ir_url']
            
            logger.info(f"Processing company: {ticker} ({name})")
            
            try:
                # Determine base URL
                base_url = ir_url if ir_url else website_url
                if not base_url:
                    logger.warning(f"No URL found for company {ticker}")
                    results['skipped_companies'] += 1
                    continue
                
                # Ensure URL has scheme
                if not base_url.startswith(('http://', 'https://')):
                    base_url = f"https://{base_url}"
                
                # Scrape with retries and rate limiting
                scrape_result = scrape_single_company(
                    ticker=ticker,
                    name=name,
                    base_url=base_url,
                    output_dir=output_dir,
                    proxy_enabled=proxy_enabled
                )
                
                if scrape_result['success']:
                    results['successful_scrapes'] += 1
                    results['scraped_reports'].extend(scrape_result['reports'])
                    logger.info(f"Successfully scraped {ticker}: {len(scrape_result['reports'])} reports")
                else:
                    results['failed_scrapes'] += 1
                    results['errors'].append({
                        'ticker': ticker,
                        'error': scrape_result['error']
                    })
                    logger.error(f"Failed to scrape {ticker}: {scrape_result['error']}")
                
                # Random delay between requests (3-10 seconds)
                delay = random.uniform(3, 10)
                logger.info(f"Waiting {delay:.1f} seconds before next request...")
                time.sleep(delay)
                
            except Exception as e:
                logger.error(f"Error processing company {ticker}: {e}")
                results['failed_scrapes'] += 1
                results['errors'].append({
                    'ticker': ticker,
                    'error': str(e)
                })
                continue
        
        # Store results in XCom
        context['task_instance'].xcom_push(
            key='scraping_results',
            value=results
        )
        
        logger.info(f"Scraping completed: {results['successful_scrapes']} successful, {results['failed_scrapes']} failed, {results['skipped_companies']} skipped")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in scrape_company_ir_reports: {e}")
        raise

def scrape_single_company(
    ticker: str, 
    name: str, 
    base_url: str, 
    output_dir: Path, 
    proxy_enabled: bool
) -> Dict[str, Any]:
    """
    Scrape IR reports for a single company with retries and rate limiting
    """
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            # Rotate User-Agent
            user_agent = random.choice(USER_AGENTS)
            
            # Prepare headers
            headers = {
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Configure proxy if enabled
            proxies = None
            if proxy_enabled:
                # TODO: Implement proxy rotation
                # proxies = get_next_proxy()
                pass
            
            # Try different IR report paths
            scraped_reports = []
            
            for path in IR_REPORT_PATHS:
                try:
                    full_url = urljoin(base_url, path)
                    logger.debug(f"Attempting to scrape: {full_url}")
                    
                    # Make request
                    response = requests.get(
                        full_url,
                        headers=headers,
                        proxies=proxies,
                        timeout=30,
                        allow_redirects=True
                    )
                    
                    # Handle rate limiting
                    if response.status_code == 429:
                        retry_after = int(response.headers.get('Retry-After', retry_delay))
                        logger.warning(f"Rate limited for {ticker}, waiting {retry_after} seconds...")
                        time.sleep(retry_after)
                        continue
                    
                    # Handle other error codes
                    if response.status_code in [403, 404, 500, 502, 503]:
                        logger.debug(f"HTTP {response.status_code} for {full_url}")
                        continue
                    
                    # Check if response is a PDF
                    if response.status_code == 200:
                        content_type = response.headers.get('content-type', '').lower()
                        
                        if 'application/pdf' in content_type or full_url.lower().endswith('.pdf'):
                            # Save PDF
                            filename = f"{ticker}_ir_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                            filepath = output_dir / filename
                            
                            with open(filepath, 'wb') as f:
                                f.write(response.content)
                            
                            scraped_reports.append({
                                'ticker': ticker,
                                'name': name,
                                'url': full_url,
                                'filepath': str(filepath),
                                'filesize': len(response.content),
                                'scraped_at': datetime.now().isoformat(),
                                'user_agent': user_agent
                            })
                            
                            logger.info(f"Successfully scraped PDF: {filename} ({len(response.content)} bytes)")
                            
                        elif 'text/html' in content_type:
                            # Parse HTML for PDF links
                            from bs4 import BeautifulSoup
                            soup = BeautifulSoup(response.content, 'html.parser')
                            
                            # Find PDF links
                            pdf_links = soup.find_all('a', href=lambda href: href and href.lower().endswith('.pdf'))
                            
                            for link in pdf_links[:5]:  # Limit to first 5 PDFs
                                pdf_url = urljoin(full_url, link['href'])
                                
                                try:
                                    pdf_response = requests.get(
                                        pdf_url,
                                        headers=headers,
                                        proxies=proxies,
                                        timeout=30
                                    )
                                    
                                    if pdf_response.status_code == 200:
                                        filename = f"{ticker}_ir_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                                        filepath = output_dir / filename
                                        
                                        with open(filepath, 'wb') as f:
                                            f.write(pdf_response.content)
                                        
                                        scraped_reports.append({
                                            'ticker': ticker,
                                            'name': name,
                                            'url': pdf_url,
                                            'filepath': str(filepath),
                                            'filesize': len(pdf_response.content),
                                            'scraped_at': datetime.now().isoformat(),
                                            'user_agent': user_agent
                                        })
                                        
                                        logger.info(f"Successfully scraped PDF from HTML: {filename}")
                                        break  # Only take first PDF per page
                                        
                                except Exception as e:
                                    logger.debug(f"Error downloading PDF from {pdf_url}: {e}")
                                    continue
                
                except requests.exceptions.RequestException as e:
                    logger.debug(f"Request error for {full_url}: {e}")
                    continue
                
                except Exception as e:
                    logger.debug(f"Error processing {full_url}: {e}")
                    continue
            
            # Return success if we found any reports
            if scraped_reports:
                return {
                    'success': True,
                    'reports': scraped_reports,
                    'error': None
                }
            
            # If we get here, no reports were found
            return {
                'success': False,
                'reports': [],
                'error': 'No IR reports found'
            }
            
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for {ticker}: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
            else:
                return {
                    'success': False,
                    'reports': [],
                    'error': f'Failed after {max_retries} attempts: {str(e)}'
                }
    
    return {
        'success': False,
        'reports': [],
        'error': 'Max retries exceeded'
    }

def update_scraping_status(**context) -> Dict[str, Any]:
    """
    Update database with scraping results and status
    """
    try:
        logger.info("Updating scraping status in database...")
        
        execution_date = context['execution_date']
        scraping_results = context['task_instance'].xcom_pull(
            task_ids='scrape_reports',
            key='scraping_results'
        )
        
        if not scraping_results:
            logger.warning("No scraping results to update")
            return {'updated_companies': 0}
        
        pg_hook = PostgresHook(postgres_conn_id='supabase_postgres')
        
        updated_companies = 0
        
        for report in scraping_results['scraped_reports']:
            try:
                # Update last_scraped_at for successful scrapes
                update_query = """
                UPDATE companies 
                SET 
                    last_scraped_at = %s,
                    actual_release_date = %s,
                    scraping_status = 'success',
                    last_scraping_error = NULL
                WHERE ticker = %s
                """
                
                pg_hook.run(
                    update_query,
                    parameters=(
                        datetime.now(),
                        execution_date.date(),
                        report['ticker']
                    )
                )
                
                updated_companies += 1
                
            except Exception as e:
                logger.error(f"Error updating status for {report['ticker']}: {e}")
                continue
        
        # Update failed companies
        for error in scraping_results['errors']:
            try:
                update_query = """
                UPDATE companies 
                SET 
                    scraping_status = 'failed',
                    last_scraping_error = %s,
                    last_scraping_attempt = %s
                WHERE ticker = %s
                """
                
                pg_hook.run(
                    update_query,
                    parameters=(
                        error['error'][:500],  # Truncate long error messages
                        datetime.now(),
                        error['ticker']
                    )
                )
                
            except Exception as e:
                logger.error(f"Error updating error status for {error['ticker']}: {e}")
                continue
        
        logger.info(f"Updated scraping status for {updated_companies} companies")
        
        return {'updated_companies': updated_companies}
        
    except Exception as e:
        logger.error(f"Error updating scraping status: {e}")
        raise

def send_daily_summary(**context) -> Dict[str, Any]:
    """
    Send daily summary notification
    """
    try:
        logger.info("Sending daily scraping summary...")
        
        execution_date = context['execution_date']
        scraping_results = context['task_instance'].xcom_pull(
            task_ids='scrape_reports',
            key='scraping_results'
        )
        
        if not scraping_results:
            scraping_results = {
                'total_companies': 0,
                'successful_scrapes': 0,
                'failed_scrapes': 0,
                'skipped_companies': 0,
                'scraped_reports': [],
                'errors': []
            }
        
        # Prepare summary
        summary = {
            'date': execution_date.strftime('%Y-%m-%d'),
            'total_companies': scraping_results['total_companies'],
            'successful_scrapes': scraping_results['successful_scrapes'],
            'failed_scrapes': scraping_results['failed_scrapes'],
            'skipped_companies': scraping_results['skipped_companies'],
            'scraped_reports': len(scraping_results['scraped_reports']),
            'errors': len(scraping_results['errors'])
        }
        
        # Send Slack notification
        slack_webhook_url = Variable.get("SLACK_WEBHOOK_URL", default_var=None)
        if slack_webhook_url:
            try:
                slack_message = {
                    "text": f"📊 IR Scraping Summary - {summary['date']}",
                    "attachments": [
                        {
                            "color": "good" if summary['successful_scrapes'] > 0 else "warning",
                            "fields": [
                                {
                                    "title": "Total Companies",
                                    "value": summary['total_companies'],
                                    "short": True
                                },
                                {
                                    "title": "Successful Scrapes",
                                    "value": summary['successful_scrapes'],
                                    "short": True
                                },
                                {
                                    "title": "Failed Scrapes",
                                    "value": summary['failed_scrapes'],
                                    "short": True
                                },
                                {
                                    "title": "Skipped Companies",
                                    "value": summary['skipped_companies'],
                                    "short": True
                                },
                                {
                                    "title": "Reports Downloaded",
                                    "value": summary['scraped_reports'],
                                    "short": True
                                },
                                {
                                    "title": "Errors",
                                    "value": summary['errors'],
                                    "short": True
                                }
                            ]
                        }
                    ]
                }
                
                if summary['errors'] > 0:
                    error_details = "\n".join([f"• {error['ticker']}: {error['error'][:100]}..." for error in scraping_results['errors'][:5]])
                    slack_message["attachments"][0]["fields"].append({
                        "title": "Recent Errors",
                        "value": error_details,
                        "short": False
                    })
                
                response = requests.post(slack_webhook_url, json=slack_message)
                response.raise_for_status()
                
                logger.info("Slack notification sent successfully")
                
            except Exception as e:
                logger.error(f"Error sending Slack notification: {e}")
        
        # Send email notification
        alert_emails = Variable.get("ALERT_EMAILS", deserialize_json=True, default_var=[])
        if alert_emails:
            try:
                subject = f"IR Scraping Summary - {summary['date']}"
                
                body = f"""
                IR Scraping Daily Summary - {summary['date']}
                
                📊 Results:
                • Total Companies: {summary['total_companies']}
                • Successful Scrapes: {summary['successful_scrapes']}
                • Failed Scrapes: {summary['failed_scrapes']}
                • Skipped Companies: {summary['skipped_companies']}
                • Reports Downloaded: {summary['scraped_reports']}
                • Errors: {summary['errors']}
                
                📁 Downloaded Reports:
                """
                
                for report in scraping_results['scraped_reports']:
                    body += f"• {report['ticker']}: {report['name']} ({report['filesize']} bytes)\n"
                
                if summary['errors'] > 0:
                    body += f"\n❌ Errors:\n"
                    for error in scraping_results['errors'][:10]:  # Limit to first 10 errors
                        body += f"• {error['ticker']}: {error['error'][:200]}...\n"
                
                send_email(
                    to=alert_emails,
                    subject=subject,
                    html_content=body.replace('\n', '<br>')
                )
                
                logger.info("Email notification sent successfully")
                
            except Exception as e:
                logger.error(f"Error sending email notification: {e}")
        
        return summary
        
    except Exception as e:
        logger.error(f"Error sending daily summary: {e}")
        raise

def log_scraping_history(**context) -> Dict[str, Any]:
    """
    Log scraping history to tracking table
    """
    try:
        logger.info("Logging scraping history...")
        
        execution_date = context['execution_date']
        scraping_results = context['task_instance'].xcom_pull(
            task_ids='scrape_reports',
            key='scraping_results'
        )
        
        if not scraping_results:
            return {'logged_entries': 0}
        
        pg_hook = PostgresHook(postgres_conn_id='supabase_postgres')
        
        logged_entries = 0
        
        # Log successful scrapes
        for report in scraping_results['scraped_reports']:
            try:
                insert_query = """
                INSERT INTO ir_scraping_history (
                    company_ticker,
                    scraping_date,
                    report_url,
                    file_path,
                    file_size,
                    status,
                    error_message,
                    created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                pg_hook.run(
                    insert_query,
                    parameters=(
                        report['ticker'],
                        execution_date.date(),
                        report['url'],
                        report['filepath'],
                        report['filesize'],
                        'success',
                        None,
                        datetime.now()
                    )
                )
                
                logged_entries += 1
                
            except Exception as e:
                logger.error(f"Error logging success for {report['ticker']}: {e}")
                continue
        
        # Log failed scrapes
        for error in scraping_results['errors']:
            try:
                insert_query = """
                INSERT INTO ir_scraping_history (
                    company_ticker,
                    scraping_date,
                    report_url,
                    file_path,
                    file_size,
                    status,
                    error_message,
                    created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                pg_hook.run(
                    insert_query,
                    parameters=(
                        error['ticker'],
                        execution_date.date(),
                        None,
                        None,
                        None,
                        'failed',
                        error['error'][:500],  # Truncate long error messages
                        datetime.now()
                    )
                )
                
                logged_entries += 1
                
            except Exception as e:
                logger.error(f"Error logging failure for {error['ticker']}: {e}")
                continue
        
        logger.info(f"Logged {logged_entries} entries to scraping history")
        
        return {'logged_entries': logged_entries}
        
    except Exception as e:
        logger.error(f"Error logging scraping history: {e}")
        raise

# Define tasks
start = DummyOperator(
    task_id='start',
    dag=dag,
)

get_companies_due = PythonOperator(
    task_id='get_companies_due',
    python_callable=get_companies_due_for_scraping,
    sla=sla,
    dag=dag,
)

scrape_reports = PythonOperator(
    task_id='scrape_reports',
    python_callable=scrape_company_ir_reports,
    sla=sla,
    dag=dag,
)

update_status = PythonOperator(
    task_id='update_status',
    python_callable=update_scraping_status,
    sla=sla,
    dag=dag,
)

log_history = PythonOperator(
    task_id='log_history',
    python_callable=log_scraping_history,
    sla=sla,
    dag=dag,
)

send_summary = PythonOperator(
    task_id='send_summary',
    python_callable=send_daily_summary,
    sla=sla,
    dag=dag,
)

end = DummyOperator(
    task_id='end',
    dag=dag,
)

# Define task dependencies
start >> get_companies_due >> scrape_reports >> update_status >> log_history >> send_summary >> end 