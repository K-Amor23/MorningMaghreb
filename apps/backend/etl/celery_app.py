from celery import Celery
from celery.schedules import crontab
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import os

# Configure logging
logger = logging.getLogger(__name__)

# Celery configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Create Celery app
celery_app = Celery(
    'casablanca_insights',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['etl.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    'fetch-currency-rates-daily': {
        'task': 'etl.tasks.fetch_currency_rates',
        'schedule': crontab(hour='6', minute='0'),  # Daily at 6 AM
    },
    'fetch-economic-data-weekly': {
        'task': 'etl.tasks.fetch_economic_data',
        'schedule': crontab(day_of_week='1', hour='7', minute='0'),  # Every Monday at 7 AM
    },
    'fetch-financial-reports-monthly': {
        'task': 'etl.tasks.fetch_financial_reports',
        'schedule': crontab(day='1', hour='8', minute='0'),  # First day of month at 8 AM
    },
    'cleanup-old-data-weekly': {
        'task': 'etl.tasks.cleanup_old_data',
        'schedule': crontab(day_of_week='0', hour='2', minute='0'),  # Sunday at 2 AM
    },
}

@celery_app.task(bind=True, max_retries=3)
def fetch_currency_rates(self, currency_pair: str = "USD/MAD", amount: float = 1000.0):
    """Fetch currency rates from all sources"""
    try:
        logger.info(f"Starting currency rate fetch for {currency_pair}")
        
        # Import here to avoid circular imports
        from etl.currency_scraper import CurrencyScraper
        import asyncio
        
        async def fetch_rates():
            scraper = CurrencyScraper()
            try:
                # Fetch BAM rate
                bam_rate = await scraper.fetch_bam_rate(currency_pair)
                
                # Fetch all remittance rates
                from decimal import Decimal
                remittance_rates = await scraper.fetch_all_remittance_rates(currency_pair, Decimal(str(amount)))
                
                # Calculate best rate
                best_rate = None
                if bam_rate and remittance_rates:
                    best_rate = scraper.find_best_rate(remittance_rates, bam_rate['rate'])
                
                # Get metrics
                metrics = scraper.get_metrics_summary()
                
                return {
                    'bam_rate': bam_rate,
                    'remittance_rates': remittance_rates,
                    'best_rate': best_rate,
                    'metrics': metrics,
                    'timestamp': datetime.utcnow().isoformat()
                }
            finally:
                await scraper.close()
        
        result = asyncio.run(fetch_rates())
        logger.info(f"Currency rate fetch completed successfully")
        return result
        
    except Exception as exc:
        logger.error(f"Currency rate fetch failed: {exc}")
        # Retry with exponential backoff
        raise self.retry(countdown=60 * (2 ** self.request.retries), max_retries=3, exc=exc)

@celery_app.task(bind=True, max_retries=2)
def fetch_economic_data(self, data_types: Optional[list] = None):
    """Fetch economic data from BAM"""
    try:
        logger.info(f"Starting economic data fetch for types: {data_types}")
        
        # Import here to avoid circular imports
        from etl.fetch_economic_data import EconomicDataFetcher
        from storage.local_fs import LocalFileStorage
        import asyncio
        
        async def fetch_data():
            storage = LocalFileStorage()
            fetcher = EconomicDataFetcher(storage)
            
            result = await fetcher.fetch_all_economic_data(data_types)
            return result
        
        result = asyncio.run(fetch_data())
        logger.info(f"Economic data fetch completed successfully")
        return result
        
    except Exception as exc:
        logger.error(f"Economic data fetch failed: {exc}")
        raise self.retry(countdown=300 * (2 ** self.request.retries), max_retries=2, exc=exc)

@celery_app.task(bind=True, max_retries=2)
def fetch_financial_reports(self, companies: Optional[list] = None, year: Optional[int] = None):
    """Fetch financial reports from company websites"""
    try:
        logger.info(f"Starting financial reports fetch for companies: {companies}, year: {year}")
        
        # Import here to avoid circular imports
        from etl.etl_orchestrator import ETLOrchestrator
        from storage.local_fs import LocalFileStorage
        import asyncio
        
        async def fetch_reports():
            storage = LocalFileStorage()
            orchestrator = ETLOrchestrator(storage)
            
            result = await orchestrator.run_full_pipeline(companies, year)
            return result
        
        result = asyncio.run(fetch_reports())
        logger.info(f"Financial reports fetch completed successfully")
        return result
        
    except Exception as exc:
        logger.error(f"Financial reports fetch failed: {exc}")
        raise self.retry(countdown=600 * (2 ** self.request.retries), max_retries=2, exc=exc)

@celery_app.task(bind=True)
def cleanup_old_data(self, days_to_keep: int = 90):
    """Clean up old data files and database records"""
    try:
        logger.info(f"Starting data cleanup, keeping {days_to_keep} days of data")
        
        # Import here to avoid circular imports
        from storage.local_fs import LocalFileStorage
        import asyncio
        from datetime import datetime, timedelta
        
        async def cleanup():
            storage = LocalFileStorage()
            
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Clean up old files (mock implementation)
            deleted_files = 0  # Would implement actual file cleanup based on cutoff_date
            
            # Clean up old database records (mock for now)
            deleted_records = 0  # Would implement actual database cleanup
            
            return {
                'deleted_files': deleted_files,
                'deleted_records': deleted_records,
                'cutoff_date': cutoff_date.isoformat(),
                'timestamp': datetime.utcnow().isoformat()
            }
        
        result = asyncio.run(cleanup())
        logger.info(f"Data cleanup completed successfully")
        return result
        
    except Exception as exc:
        logger.error(f"Data cleanup failed: {exc}")
        # Don't retry cleanup tasks as they're not critical
        return {'error': str(exc)}

@celery_app.task(bind=True, max_retries=3)
def process_export(self, export_id: str, export_type: str, filters: Dict[str, Any]):
    """Process data export in background"""
    try:
        logger.info(f"Starting export processing for ID: {export_id}")
        
        # Import here to avoid circular imports
        # Mock export processor (would implement actual ExportProcessor)
        import asyncio
        
        async def process():
            # Mock export processing
            await asyncio.sleep(2)  # Simulate processing time
            return {
                'export_id': export_id,
                'export_type': export_type,
                'status': 'completed',
                'file_path': f'/exports/{export_id}.csv',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        result = asyncio.run(process())
        logger.info(f"Export processing completed successfully")
        return result
        
    except Exception as exc:
        logger.error(f"Export processing failed: {exc}")
        raise self.retry(countdown=120 * (2 ** self.request.retries), max_retries=3, exc=exc)

@celery_app.task(bind=True)
def send_webhook_notification(self, webhook_url: str, payload: Dict[str, Any], secret_key: str):
    """Send webhook notification"""
    try:
        logger.info(f"Sending webhook notification to: {webhook_url}")
        
        # Import here to avoid circular imports
        import httpx
        import hashlib
        import hmac
        import json
        
        # Create signature
        payload_str = json.dumps(payload, separators=(',', ':'))
        signature = hmac.new(
            secret_key.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Send webhook
        async def send_webhook():
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    webhook_url,
                    json=payload,
                    headers={
                        'Content-Type': 'application/json',
                        'X-Casablanca-Signature': signature,
                        'User-Agent': 'Morning-Maghreb/1.0'
                    }
                )
                response.raise_for_status()
                return {
                    'status_code': response.status_code,
                    'response_time_ms': response.elapsed.total_seconds() * 1000
                }
        
        import asyncio
        result = asyncio.run(send_webhook())
        logger.info(f"Webhook notification sent successfully")
        return result
        
    except Exception as exc:
        logger.error(f"Webhook notification failed: {exc}")
        # Retry webhook delivery
        raise self.retry(countdown=60 * (2 ** self.request.retries), max_retries=3, exc=exc)

@celery_app.task(bind=True, max_retries=2)
def parse_ir_pdf(self, pdf_path: str, ticker: str, company_name: str, source_url: str):
    """Parse IR PDF and extract financial data"""
    try:
        logger.info(f"Starting PDF parsing for {ticker}: {pdf_path}")
        
        # Import here to avoid circular imports
        import PyPDF2
        import re
        import json
        from pathlib import Path
        from datetime import datetime
        
        # Check if file exists
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Read PDF
        extracted_text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract text from all pages
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        extracted_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
                    continue
        
        if not extracted_text.strip():
            raise ValueError("No text could be extracted from PDF")
        
        # Parse financial data (simplified example)
        # In production, you would use more sophisticated NLP/ML techniques
        financial_data = parse_financial_data_from_text(extracted_text, ticker)
        
        # Add metadata
        result = {
            'ticker': ticker,
            'company_name': company_name,
            'source_url': source_url,
            'pdf_path': pdf_path,
            'extraction_timestamp': datetime.now().isoformat(),
            'financial_data': financial_data,
            'text_length': len(extracted_text),
            'pages_processed': len(pdf_reader.pages)
        }
        
        logger.info(f"Successfully parsed PDF for {ticker}: {len(financial_data)} financial items found")
        return result
        
    except Exception as exc:
        logger.error(f"PDF parsing failed for {ticker}: {exc}")
        raise self.retry(countdown=300 * (2 ** self.request.retries), max_retries=2, exc=exc)

def parse_financial_data_from_text(text: str, ticker: str) -> Dict[str, Any]:
    """Extract financial data from PDF text using regex patterns"""
    
    # Common financial terms in multiple languages
    financial_patterns = {
        'revenue': [
            r'revenue[:\s]*([\d,]+\.?\d*)',
            r'chiffre d\'affaires[:\s]*([\d,]+\.?\d*)',
            r'ventes[:\s]*([\d,]+\.?\d*)',
            r'ca[:\s]*([\d,]+\.?\d*)',
        ],
        'net_income': [
            r'net income[:\s]*([\d,]+\.?\d*)',
            r'profit net[:\s]*([\d,]+\.?\d*)',
            r'bénéfice net[:\s]*([\d,]+\.?\d*)',
            r'resultat net[:\s]*([\d,]+\.?\d*)',
        ],
        'total_assets': [
            r'total assets[:\s]*([\d,]+\.?\d*)',
            r'actifs totaux[:\s]*([\d,]+\.?\d*)',
            r'total de l\'actif[:\s]*([\d,]+\.?\d*)',
        ],
        'total_liabilities': [
            r'total liabilities[:\s]*([\d,]+\.?\d*)',
            r'passifs totaux[:\s]*([\d,]+\.?\d*)',
            r'total du passif[:\s]*([\d,]+\.?\d*)',
        ],
        'equity': [
            r'equity[:\s]*([\d,]+\.?\d*)',
            r'capitaux propres[:\s]*([\d,]+\.?\d*)',
            r'fonds propres[:\s]*([\d,]+\.?\d*)',
        ]
    }
    
    extracted_data = {}
    
    for metric, patterns in financial_patterns.items():
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Take the first match and convert to number
                try:
                    value_str = matches[0].replace(',', '')
                    value = float(value_str)
                    extracted_data[metric] = value
                    break
                except ValueError:
                    continue
    
    # Add currency detection (simplified)
    currency_patterns = [
        r'([A-Z]{3})\s*[\d,]+\.?\d*',  # USD, EUR, MAD, etc.
        r'[\d,]+\.?\d*\s*([A-Z]{3})',  # 1,000 USD, etc.
    ]
    
    currency = 'MAD'  # Default for Moroccan companies
    for pattern in currency_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            currency = matches[0].upper()
            break
    
    extracted_data['currency'] = currency
    
    return extracted_data

# Task monitoring and health checks
@celery_app.task
def health_check():
    """Health check task for monitoring"""
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'worker_count': len(celery_app.control.inspect().active()),
        'queue_length': len(celery_app.control.inspect().reserved())
    }

# Task result monitoring
def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get status of a specific task"""
    try:
        result = celery_app.AsyncResult(task_id)
        return {
            'task_id': task_id,
            'status': result.status,
            'result': result.result if result.ready() else None,
            'info': result.info if hasattr(result, 'info') else None,
            'traceback': result.traceback if result.failed() else None
        }
    except Exception as e:
        return {
            'task_id': task_id,
            'status': 'error',
            'error': str(e)
        }

def get_queue_stats() -> Dict[str, Any]:
    """Get queue statistics"""
    try:
        inspector = celery_app.control.inspect()
        
        return {
            'active_tasks': len(inspector.active() or {}),
            'reserved_tasks': len(inspector.reserved() or {}),
            'scheduled_tasks': len(inspector.scheduled() or {}),
            'registered_tasks': len(inspector.registered() or {}),
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

if __name__ == '__main__':
    celery_app.start() 