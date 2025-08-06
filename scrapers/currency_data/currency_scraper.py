
from ..base.scraper_interface import BaseScraper
from ..utils.http_helpers import make_request, add_delay
from ..utils.date_parsers import parse_date, extract_date_from_text
from ..utils.config_loader import get_scraper_config
from ..utils.data_validators import validate_dataframe, clean_dataframe
import pandas as pd
import logging
from typing import Dict, Any, Optional
import httpx
import asyncio
from datetime import date, datetime
from decimal import Decimal
from typing import List, Dict, Optional
import logging
from bs4 import BeautifulSoup
import re
import time
import random
from functools import wraps
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ScrapingStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"

@dataclass
class ScrapingMetrics:
    """Metrics for scraping operations"""
    start_time: datetime
    end_time: Optional[datetime] = None
    status: ScrapingStatus = ScrapingStatus.SUCCESS
    response_time_ms: Optional[float] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    data_points: int = 0

def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator for retrying operations with exponential backoff"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay:.2f}s")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}: {e}")
            
            if last_exception:
                raise last_exception
            else:
                raise RuntimeError("Unexpected error in retry decorator")
        return wrapper
    return decorator

class CurrencyScraper:
    def __init__(self, max_concurrent_requests: int = 5):
        self.session = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_connections=max_concurrent_requests),
            verify=False  # Disable SSL verification for development
        )
        self.metrics: List[ScrapingMetrics] = []
        self.rate_limit_delays = {
            'bam': 2.0,
            'remitly': 3.0,
            'wise': 2.5,
            'western_union': 3.0,
            'transferwise': 2.5,
            'cih_bank': 2.0,
            'attijari_bank': 2.0
        }
        
    async def close(self):
        await self.session.aclose()
    
    def log_metrics(self, metrics: ScrapingMetrics):
        """Log scraping metrics for monitoring"""
        self.metrics.append(metrics)
        
        if metrics.status == ScrapingStatus.SUCCESS:
            logger.info(f"Scraping successful: {metrics.response_time_ms:.2f}ms, {metrics.data_points} data points")
        else:
            logger.error(f"Scraping failed: {metrics.status.value}, {metrics.error_message}")
    
    def get_success_rate(self) -> float:
        """Calculate success rate from metrics"""
        if not self.metrics:
            return 0.0
        successful = sum(1 for m in self.metrics if m.status == ScrapingStatus.SUCCESS)
        return successful / len(self.metrics)
    
    def get_average_response_time(self) -> float:
        """Calculate average response time from metrics"""
        response_times = [m.response_time_ms for m in self.metrics if m.response_time_ms]
        return sum(response_times) / len(response_times) if response_times else 0.0
    
    @retry_with_backoff(max_retries=3, base_delay=2.0)
    async def fetch_bam_rate(self, currency_pair: str = "USD/MAD") -> Optional[Dict]:
        """Fetch official BAM exchange rate with enhanced error handling"""
        metrics = ScrapingMetrics(start_time=datetime.now())
        
        try:
            # Add delay to respect rate limits
            await asyncio.sleep(self.rate_limit_delays['bam'])
            
            # BAM official rate endpoint (mock for now - would need real BAM API)
            url = "https://www.bkam.ma/en/Markets/Foreign-exchange-market/Exchange-rates"
            
            # For now, return mock data
            # In production, implement actual BAM scraping
            mock_rate = {
                "currency_pair": currency_pair,
                "rate": Decimal("10.25"),  # Mock rate
                "rate_date": date.today(),
                "source": "BAM"
            }
            
            metrics.end_time = datetime.now()
            metrics.response_time_ms = (metrics.end_time - metrics.start_time).total_seconds() * 1000
            metrics.data_points = 1
            metrics.status = ScrapingStatus.SUCCESS
            
            logger.info(f"Fetched BAM rate for {currency_pair}: {mock_rate['rate']}")
            self.log_metrics(metrics)
            return mock_rate
            
        except httpx.TimeoutException as e:
            metrics.status = ScrapingStatus.TIMEOUT
            metrics.error_message = f"Timeout fetching BAM rate: {e}"
            self.log_metrics(metrics)
            raise
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                metrics.status = ScrapingStatus.RATE_LIMITED
                metrics.error_message = f"Rate limited by BAM: {e}"
            else:
                metrics.status = ScrapingStatus.FAILED
                metrics.error_message = f"HTTP error fetching BAM rate: {e}"
            self.log_metrics(metrics)
            raise
        except Exception as e:
            metrics.status = ScrapingStatus.FAILED
            metrics.error_message = f"Error fetching BAM rate: {e}"
            self.log_metrics(metrics)
            raise
    
    @retry_with_backoff(max_retries=2, base_delay=1.5)
    async def fetch_remitly_rate(self, currency_pair: str = "USD/MAD", amount: Decimal = Decimal("1000")) -> Optional[Dict]:
        """Scrape Remitly exchange rate with enhanced error handling"""
        metrics = ScrapingMetrics(start_time=datetime.now())
        
        try:
            # Add delay to respect rate limits
            await asyncio.sleep(self.rate_limit_delays['remitly'])
            
            # Mock Remitly scraping (in production, implement actual scraping)
            # This would involve navigating to Remitly's website and extracting rates
            mock_rate = {
                "service_name": "Remitly",
                "currency_pair": currency_pair,
                "rate": Decimal("10.15"),
                "fee_amount": Decimal("3.99"),
                "fee_currency": "USD",
                "fee_type": "fixed",
                "transfer_amount": amount,
                "effective_rate": Decimal("10.12"),
                "rate_date": date.today(),
                "scraped_at": datetime.now()
            }
            
            metrics.end_time = datetime.now()
            metrics.response_time_ms = (metrics.end_time - metrics.start_time).total_seconds() * 1000
            metrics.data_points = 1
            metrics.status = ScrapingStatus.SUCCESS
            
            logger.info(f"Fetched Remitly rate: {mock_rate['rate']}")
            self.log_metrics(metrics)
            return mock_rate
            
        except Exception as e:
            metrics.status = ScrapingStatus.FAILED
            metrics.error_message = f"Error fetching Remitly rate: {e}"
            self.log_metrics(metrics)
            raise
    
    @retry_with_backoff(max_retries=2, base_delay=1.5)
    async def fetch_wise_rate(self, currency_pair: str = "USD/MAD", amount: Decimal = Decimal("1000")) -> Optional[Dict]:
        """Scrape Wise exchange rate with enhanced error handling"""
        metrics = ScrapingMetrics(start_time=datetime.now())
        
        try:
            await asyncio.sleep(self.rate_limit_delays['wise'])
            
            # Mock Wise scraping
            mock_rate = {
                "service_name": "Wise",
                "currency_pair": currency_pair,
                "rate": Decimal("10.20"),
                "fee_amount": Decimal("5.50"),
                "fee_currency": "USD",
                "fee_type": "fixed",
                "transfer_amount": amount,
                "effective_rate": Decimal("10.15"),
                "rate_date": date.today(),
                "scraped_at": datetime.now()
            }
            
            metrics.end_time = datetime.now()
            metrics.response_time_ms = (metrics.end_time - metrics.start_time).total_seconds() * 1000
            metrics.data_points = 1
            metrics.status = ScrapingStatus.SUCCESS
            
            logger.info(f"Fetched Wise rate: {mock_rate['rate']}")
            self.log_metrics(metrics)
            return mock_rate
            
        except Exception as e:
            metrics.status = ScrapingStatus.FAILED
            metrics.error_message = f"Error fetching Wise rate: {e}"
            self.log_metrics(metrics)
            raise
    
    @retry_with_backoff(max_retries=2, base_delay=1.5)
    async def fetch_western_union_rate(self, currency_pair: str = "USD/MAD", amount: Decimal = Decimal("1000")) -> Optional[Dict]:
        """Scrape Western Union exchange rate with enhanced error handling"""
        metrics = ScrapingMetrics(start_time=datetime.now())
        
        try:
            await asyncio.sleep(self.rate_limit_delays['western_union'])
            
            # Mock Western Union scraping
            mock_rate = {
                "service_name": "Western Union",
                "currency_pair": currency_pair,
                "rate": Decimal("10.05"),
                "fee_amount": Decimal("8.00"),
                "fee_currency": "USD",
                "fee_type": "fixed",
                "transfer_amount": amount,
                "effective_rate": Decimal("9.97"),
                "rate_date": date.today(),
                "scraped_at": datetime.now()
            }
            
            metrics.end_time = datetime.now()
            metrics.response_time_ms = (metrics.end_time - metrics.start_time).total_seconds() * 1000
            metrics.data_points = 1
            metrics.status = ScrapingStatus.SUCCESS
            
            logger.info(f"Fetched Western Union rate: {mock_rate['rate']}")
            self.log_metrics(metrics)
            return mock_rate
            
        except Exception as e:
            metrics.status = ScrapingStatus.FAILED
            metrics.error_message = f"Error fetching Western Union rate: {e}"
            self.log_metrics(metrics)
            raise

    @retry_with_backoff(max_retries=2, base_delay=1.5)
    async def fetch_transferwise_rate(self, currency_pair: str = "USD/MAD", amount: Decimal = Decimal("1000")) -> Optional[Dict]:
        """Scrape TransferWise exchange rate with enhanced error handling"""
        metrics = ScrapingMetrics(start_time=datetime.now())
        
        try:
            await asyncio.sleep(self.rate_limit_delays['transferwise'])
            
            # Mock TransferWise scraping
            mock_rate = {
                "service_name": "TransferWise",
                "currency_pair": currency_pair,
                "rate": Decimal("10.18"),
                "fee_amount": Decimal("4.25"),
                "fee_currency": "USD",
                "fee_type": "fixed",
                "transfer_amount": amount,
                "effective_rate": Decimal("10.14"),
                "rate_date": date.today(),
                "scraped_at": datetime.now()
            }
            
            metrics.end_time = datetime.now()
            metrics.response_time_ms = (metrics.end_time - metrics.start_time).total_seconds() * 1000
            metrics.data_points = 1
            metrics.status = ScrapingStatus.SUCCESS
            
            logger.info(f"Fetched TransferWise rate: {mock_rate['rate']}")
            self.log_metrics(metrics)
            return mock_rate
            
        except Exception as e:
            metrics.status = ScrapingStatus.FAILED
            metrics.error_message = f"Error fetching TransferWise rate: {e}"
            self.log_metrics(metrics)
            raise

    @retry_with_backoff(max_retries=2, base_delay=1.5)
    async def fetch_cih_bank_rate(self, currency_pair: str = "USD/MAD", amount: Decimal = Decimal("1000")) -> Optional[Dict]:
        """Scrape CIH Bank exchange rate with enhanced error handling"""
        metrics = ScrapingMetrics(start_time=datetime.now())
        
        try:
            await asyncio.sleep(self.rate_limit_delays['cih_bank'])
            
            # Mock CIH Bank scraping
            mock_rate = {
                "service_name": "CIH Bank",
                "currency_pair": currency_pair,
                "rate": Decimal("10.22"),
                "fee_amount": Decimal("15.00"),
                "fee_currency": "MAD",
                "fee_type": "fixed",
                "transfer_amount": amount,
                "effective_rate": Decimal("10.07"),
                "rate_date": date.today(),
                "scraped_at": datetime.now()
            }
            
            metrics.end_time = datetime.now()
            metrics.response_time_ms = (metrics.end_time - metrics.start_time).total_seconds() * 1000
            metrics.data_points = 1
            metrics.status = ScrapingStatus.SUCCESS
            
            logger.info(f"Fetched CIH Bank rate: {mock_rate['rate']}")
            self.log_metrics(metrics)
            return mock_rate
            
        except Exception as e:
            metrics.status = ScrapingStatus.FAILED
            metrics.error_message = f"Error fetching CIH Bank rate: {e}"
            self.log_metrics(metrics)
            raise

    @retry_with_backoff(max_retries=2, base_delay=1.5)
    async def fetch_attijari_bank_rate(self, currency_pair: str = "USD/MAD", amount: Decimal = Decimal("1000")) -> Optional[Dict]:
        """Scrape Attijari Bank exchange rate with enhanced error handling"""
        metrics = ScrapingMetrics(start_time=datetime.now())
        
        try:
            await asyncio.sleep(self.rate_limit_delays['attijari_bank'])
            
            # Mock Attijari Bank scraping
            mock_rate = {
                "service_name": "Attijari Bank",
                "currency_pair": currency_pair,
                "rate": Decimal("10.24"),
                "fee_amount": Decimal("20.00"),
                "fee_currency": "MAD",
                "fee_type": "fixed",
                "transfer_amount": amount,
                "effective_rate": Decimal("10.04"),
                "rate_date": date.today(),
                "scraped_at": datetime.now()
            }
            
            metrics.end_time = datetime.now()
            metrics.response_time_ms = (metrics.end_time - metrics.start_time).total_seconds() * 1000
            metrics.data_points = 1
            metrics.status = ScrapingStatus.SUCCESS
            
            logger.info(f"Fetched Attijari Bank rate: {mock_rate['rate']}")
            self.log_metrics(metrics)
            return mock_rate
            
        except Exception as e:
            metrics.status = ScrapingStatus.FAILED
            metrics.error_message = f"Error fetching Attijari Bank rate: {e}"
            self.log_metrics(metrics)
            raise
    
    async def fetch_all_remittance_rates(self, currency_pair: str = "USD/MAD", amount: Decimal = Decimal("1000")) -> List[Dict]:
        """Fetch rates from all remittance services with enhanced error handling"""
        tasks = [
            self.fetch_remitly_rate(currency_pair, amount),
            self.fetch_wise_rate(currency_pair, amount),
            self.fetch_western_union_rate(currency_pair, amount),
            self.fetch_transferwise_rate(currency_pair, amount),
            self.fetch_cih_bank_rate(currency_pair, amount),
            self.fetch_attijari_bank_rate(currency_pair, amount)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        rates = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Service {i} failed: {result}")
            elif result is not None:
                rates.append(result)
        
        logger.info(f"Successfully fetched {len(rates)} out of {len(tasks)} rates")
        return rates
    
    def calculate_spread(self, remittance_rate: Decimal, bam_rate: Decimal) -> Decimal:
        """Calculate spread percentage from BAM rate"""
        if bam_rate == 0:
            return Decimal("0")
        
        spread = ((bam_rate - remittance_rate) / bam_rate) * 100
        return round(spread, 2)
    
    def find_best_rate(self, rates: List[Dict], bam_rate: Decimal) -> Dict:
        """Find the best rate among all services"""
        if not rates:
            return {}
        
        # Calculate spreads and find best effective rate
        for rate in rates:
            if rate.get('effective_rate'):
                rate['spread_percentage'] = self.calculate_spread(rate['effective_rate'], bam_rate)
        
        # Sort by effective rate (highest is best for USD->MAD)
        sorted_rates = sorted(rates, key=lambda x: x.get('effective_rate', 0), reverse=True)
        
        return sorted_rates[0] if sorted_rates else {}
    
    def get_metrics_summary(self) -> Dict:
        """Get summary of scraping metrics"""
        if not self.metrics:
            return {"message": "No metrics available"}
        
        total_requests = len(self.metrics)
        successful_requests = sum(1 for m in self.metrics if m.status == ScrapingStatus.SUCCESS)
        failed_requests = total_requests - successful_requests
        
        response_times = [m.response_time_ms for m in self.metrics if m.response_time_ms]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
            "average_response_time_ms": avg_response_time,
            "status_breakdown": {
                status.value: sum(1 for m in self.metrics if m.status == status)
                for status in ScrapingStatus
            }
        }

async def main():
    """Test the enhanced currency scraper"""
    scraper = CurrencyScraper()
    
    try:
        # Fetch BAM rate
        bam_rate = await scraper.fetch_bam_rate()
        print(f"BAM Rate: {bam_rate}")
        
        # Fetch all remittance rates
        remittance_rates = await scraper.fetch_all_remittance_rates()
        print(f"Remittance Rates: {remittance_rates}")
        
        # Find best rate
        if bam_rate and remittance_rates:
            best_rate = scraper.find_best_rate(remittance_rates, bam_rate['rate'])
            print(f"Best Rate: {best_rate}")
        
        # Print metrics summary
        metrics_summary = scraper.get_metrics_summary()
        print(f"Metrics Summary: {metrics_summary}")
            
    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(main()) 