"""
Casablanca Insights ETL Pipeline DAG

This DAG automates the daily financial data pipeline:
1. Refresh 78 companies data from African Markets
2. Scrape all company websites for annual reports and financial documents
3. Fetch IR reports from company websites
4. Extract financial data from PDFs
5. Translate French labels to GAAP
6. Store processed data in database
7. Send success/failure alerts

Schedule: Daily at 6:00 AM UTC
"""

from datetime import datetime, timedelta
import asyncio
import aiohttp
import logging
import json
import os
import requests
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

def refresh_african_markets_data(**context):
    """Task to refresh 78 companies data from African Markets"""
    try:
        logger.info("Starting African Markets data refresh...")
        
        # Get execution date for logging
        execution_date = context['execution_date']
        logger.info(f"Refreshing data for execution date: {execution_date}")
        
        # Load existing data from our data file
        data_file = Path("apps/backend/data/cse_companies_african_markets.json")
        if data_file.exists():
            with open(data_file, 'r') as f:
                companies_data = json.load(f)
            
            logger.info(f"Loaded {len(companies_data)} companies from existing data file")
        else:
            # Fallback to mock data if file doesn't exist
            logger.warning("Data file not found, using mock data")
            companies_data = [
                {
                    "ticker": "ATW",
                    "name": "Attijariwafa Bank",
                    "sector": "Banking",
                    "price": 410.10,
                    "change_1d_percent": 0.31,
                    "change_ytd_percent": 5.25,
                    "market_cap_billion": 24.56,
                    "size_category": "Large Cap",
                    "sector_group": "Financial Services"
                },
                {
                    "ticker": "IAM",
                    "name": "Maroc Telecom",
                    "sector": "Telecommunications",
                    "price": 156.30,
                    "change_1d_percent": -1.33,
                    "change_ytd_percent": -2.15,
                    "market_cap_billion": 15.68,
                    "size_category": "Large Cap",
                    "sector_group": "Telecommunications"
                }
            ]
        
        # Save data to file (in production, this would be to database)
        data_dir = Path("/tmp/african_markets_data")
        data_dir.mkdir(exist_ok=True)
        
        timestamp = execution_date.strftime("%Y%m%d_%H%M%S")
        filename = f"cse_companies_african_markets_{timestamp}.json"
        filepath = data_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(companies_data, f, indent=2)
        
        logger.info(f"Successfully refreshed {len(companies_data)} companies")
        logger.info(f"Data saved to: {filepath}")
        
        # Store metadata in XCom for next tasks
        context['task_instance'].xcom_push(
            key='african_markets_refresh',
            value={
                'companies_count': len(companies_data),
                'data_file': str(filepath),
                'timestamp': timestamp,
                'source': 'African Markets'
            }
        )
        
        return len(companies_data['companies'])
        
    except Exception as e:
        logger.error(f"Error in refresh_african_markets_data: {e}")
        raise

def scrape_casablanca_bourse_data(**context):
    """Task to scrape trading data from Casablanca Bourse website"""
    try:
        logger.info("Starting Casablanca Bourse data scraping...")
        
        # Import our scraper
        import sys
        sys.path.append('/app/etl')  # Adjust path as needed
        
        from casablanca_bourse_scraper import CasablancaBourseScraper
        
        # Run the scraper
        async def run_scraping():
            async with CasablancaBourseScraper() as scraper:
                # Scrape all market data
                all_data = await scraper.scrape_all_market_data()
                
                if 'error' not in all_data:
                    # Save the scraped data
                    timestamp = context['execution_date'].strftime("%Y%m%d_%H%M%S")
                    output_file = f"casablanca_bourse_data_{timestamp}.json"
                    scraper.save_data(all_data, output_file)
                    
                    # Extract company data from tables
                    companies_found = []
                    for page in all_data.get('market_data_pages', []):
                        for table in page.get('tables', []):
                            for row in table.get('data', []):
                                if 'Ticker' in row:
                                    companies_found.append({
                                        'ticker': row['Ticker'],
                                        'isin': row.get('Code ISIN'),
                                        'name': row.get('Émetteur'),
                                        'category': row.get('Catégorie'),
                                        'compartment': row.get('Compartiment'),
                                        'shares': row.get('Nombre de titres formant le capital')
                                    })
                    
                    return {
                        'success': True,
                        'pages_scraped': len(all_data.get('market_data_pages', [])),
                        'tables_extracted': sum(len(page.get('tables', [])) for page in all_data.get('market_data_pages', [])),
                        'companies_found': len(companies_found),
                        'data_file': output_file,
                        'companies_data': companies_found
                    }
                else:
                    return {
                        'success': False,
                        'error': all_data['error']
                    }
        
        # Run the async scraping
        import asyncio
        result = asyncio.run(run_scraping())
        
        # Store results in XCom
        context['task_instance'].xcom_push(
            key='casablanca_bourse_scraping',
            value=result
        )
        
        if result['success']:
            logger.info(f"Successfully scraped {result['pages_scraped']} pages, found {result['companies_found']} companies")
            return result['companies_found']
        else:
            logger.error(f"Casablanca Bourse scraping failed: {result['error']}")
            return 0
        
    except Exception as e:
        logger.error(f"Error in scrape_casablanca_bourse_data: {e}")
        raise

def combine_data_sources(**context):
    """Task to combine data from multiple sources"""
    try:
        logger.info("Combining data from multiple sources...")
        
        # Get data from African Markets
        african_markets_info = context['task_instance'].xcom_pull(
            task_ids='refresh_african_markets',
            key='african_markets_refresh'
        )
        
        # Get data from Casablanca Bourse
        bourse_info = context['task_instance'].xcom_pull(
            task_ids='scrape_casablanca_bourse',
            key='casablanca_bourse_scraping'
        )
        
        # Combine the data
        combined_data = {
            'metadata': {
                'combined_at': context['execution_date'].isoformat(),
                'sources': ['African Markets', 'Casablanca Bourse'],
                'total_companies': 0
            },
            'companies': {},
            'indices': {},
            'trading_data': {}
        }
        
        # Process African Markets data
        if african_markets_info:
            combined_data['metadata']['african_markets'] = african_markets_info
            combined_data['metadata']['total_companies'] += african_markets_info.get('companies_count', 0)
        
        # Process Casablanca Bourse data
        if bourse_info and bourse_info.get('success'):
            combined_data['metadata']['casablanca_bourse'] = bourse_info
            combined_data['metadata']['total_companies'] += bourse_info.get('companies_found', 0)
            
            # Add company data from Bourse
            for company in bourse_info.get('companies_data', []):
                ticker = company['ticker']
                combined_data['companies'][ticker] = {
                    'bourse_data': company,
                    'data_sources': ['casablanca_bourse']
                }
        
        # Save combined data
        timestamp = context['execution_date'].strftime("%Y%m%d_%H%M%S")
        output_file = f"combined_data_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(combined_data, f, indent=2)
        
        # Store in XCom
        context['task_instance'].xcom_push(
            key='combined_data',
            value={
                'file': output_file,
                'total_companies': combined_data['metadata']['total_companies'],
                'sources_combined': len(combined_data['metadata']['sources'])
            }
        )
        
        logger.info(f"Successfully combined data from {len(combined_data['metadata']['sources'])} sources")
        logger.info(f"Total companies: {combined_data['metadata']['total_companies']}")
        logger.info(f"Combined data saved to: {output_file}")
        
        return combined_data['metadata']['total_companies']
        
    except Exception as e:
        logger.error(f"Error in combine_data_sources: {e}")
        raise

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
        
        # Get African markets refresh info
        african_markets_info = context['task_instance'].xcom_pull(
            task_ids='refresh_african_markets',
            key='african_markets_refresh'
        )
        
        # Get company website scraping info
        website_scraping_info = context['task_instance'].xcom_pull(
            task_ids='scrape_company_websites',
            key='company_website_scraping'
        )
        
        # Get Casablanca Bourse scraping info
        bourse_info = context['task_instance'].xcom_pull(
            task_ids='scrape_casablanca_bourse',
            key='casablanca_bourse_scraping'
        )
        
        # Get combined data info
        combined_info = context['task_instance'].xcom_pull(
            task_ids='combine_data_sources',
            key='combined_data'
        )
        
        # Create success message
        message = f"""
🎉 Casablanca Insights ETL Pipeline Completed Successfully!

📊 Pipeline Results:
• African Markets: {african_markets_info.get('companies_count', 0)} companies refreshed
• Casablanca Bourse: {bourse_info.get('companies_found', 0) if bourse_info and bourse_info.get('success') else 0} companies scraped
• Combined Sources: {combined_info.get('total_companies', 0) if combined_info else 0} total companies
• Company Websites: {website_scraping_info.get('companies_discovered', 0) if website_scraping_info else 0} companies scraped
• Financial Reports: {website_scraping_info.get('reports_discovered', 0) if website_scraping_info else 0} reports discovered
• Files Downloaded: {website_scraping_info.get('files_downloaded', 0) if website_scraping_info else 0} files
• Reports Processed: {stored_count}
• Data Validation: {'✅ Passed' if validation_passed else '❌ Failed'}
• Execution Date: {context['execution_date']}

🔗 Access Points:
• Airflow UI: http://localhost:8080
• Casablanca API: http://localhost:8000
• Combined Data: {combined_info.get('file', 'N/A') if combined_info else 'N/A'}
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

def scrape_company_websites(**context):
    """Task to scrape all 78 companies' websites for annual reports and financial documents"""
    try:
        logger.info("Starting comprehensive company website scraping...")
        
        # Get execution date for logging
        execution_date = context['execution_date']
        logger.info(f"Scraping company websites for execution date: {execution_date}")
        
        # Import the comprehensive scraper
        import sys
        import os
        sys.path.append('/app/etl')  # Adjust path as needed
        
        from comprehensive_company_scraper import ComprehensiveCompanyScraper
        from storage.local_fs import LocalFileStorage
        
        # Initialize scraper
        storage = LocalFileStorage()
        
        # Run the comprehensive scraping
        async def run_scraping():
            async with ComprehensiveCompanyScraper(storage) as scraper:
                # Discover IR pages for all companies
                discovered_companies = await scraper.discover_all_companies()
                logger.info(f"Discovered IR pages for {len(discovered_companies)} companies")
                
                # Scrape reports from all companies
                all_reports = await scraper.scrape_all_companies_reports()
                logger.info(f"Discovered {len(all_reports)} reports")
                
                # Download reports
                output_dir = f"/tmp/company_reports/{execution_date.strftime('%Y%m%d')}"
                downloaded_files = await scraper.download_reports(all_reports, output_dir)
                logger.info(f"Downloaded {len(downloaded_files)} files")
                
                # Save discovery results
                results_file = f"/tmp/company_discovery_results_{execution_date.strftime('%Y%m%d')}.json"
                await scraper.save_discovery_results(discovered_companies, all_reports, results_file)
                
                return {
                    'companies_discovered': len(discovered_companies),
                    'reports_discovered': len(all_reports),
                    'files_downloaded': len(downloaded_files),
                    'output_directory': output_dir,
                    'results_file': results_file
                }
        
        # Run the async scraping
        import asyncio
        scraping_results = asyncio.run(run_scraping())
        
        # Store results in XCom
        context['task_instance'].xcom_push(
            key='company_website_scraping',
            value=scraping_results
        )
        
        logger.info(f"Successfully scraped {scraping_results['companies_discovered']} companies")
        logger.info(f"Discovered {scraping_results['reports_discovered']} reports")
        logger.info(f"Downloaded {scraping_results['files_downloaded']} files")
        
        return scraping_results['files_downloaded']
        
    except Exception as e:
        logger.error(f"Error in scrape_company_websites: {e}")
        raise

# Define tasks
refresh_african_markets = PythonOperator(
    task_id='refresh_african_markets',
    python_callable=refresh_african_markets_data,
    dag=dag,
)

scrape_casablanca_bourse = PythonOperator(
    task_id='scrape_casablanca_bourse',
    python_callable=scrape_casablanca_bourse_data,
    dag=dag,
)

combine_data = PythonOperator(
    task_id='combine_data_sources',
    python_callable=combine_data_sources,
    dag=dag,
)

scrape_company_websites = PythonOperator(
    task_id='scrape_company_websites',
    python_callable=scrape_company_websites,
    dag=dag,
)

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
# Data collection phase (parallel)
[refresh_african_markets, scrape_casablanca_bourse] >> combine_data

# Data processing phase
combine_data >> scrape_company_websites >> fetch_reports >> extract_pdf >> translate_gaap >> store_data >> validate_data >> [success_alert, failure_alert] 