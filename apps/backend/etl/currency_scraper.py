import httpx
import asyncio
from datetime import date, datetime
from decimal import Decimal
from typing import List, Dict, Optional
import logging
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class CurrencyScraper:
    def __init__(self):
        self.session = httpx.AsyncClient(timeout=30.0)
        
    async def close(self):
        await self.session.aclose()
    
    async def fetch_bam_rate(self, currency_pair: str = "USD/MAD") -> Optional[Dict]:
        """Fetch official BAM exchange rate"""
        try:
            # BAM official rate endpoint (mock for now - would need real BAM API)
            # In production, this would be the actual BAM API endpoint
            url = "https://www.bkam.ma/en/Markets/Foreign-exchange-market/Exchange-rates"
            
            # For now, return mock data
            # In production, implement actual BAM scraping
            mock_rate = {
                "currency_pair": currency_pair,
                "rate": Decimal("10.25"),  # Mock rate
                "rate_date": date.today(),
                "source": "BAM"
            }
            
            logger.info(f"Fetched BAM rate for {currency_pair}: {mock_rate['rate']}")
            return mock_rate
            
        except Exception as e:
            logger.error(f"Error fetching BAM rate: {e}")
            return None
    
    async def fetch_remitly_rate(self, currency_pair: str = "USD/MAD", amount: Decimal = Decimal("1000")) -> Optional[Dict]:
        """Scrape Remitly exchange rate"""
        try:
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
            
            logger.info(f"Fetched Remitly rate: {mock_rate['rate']}")
            return mock_rate
            
        except Exception as e:
            logger.error(f"Error fetching Remitly rate: {e}")
            return None
    
    async def fetch_wise_rate(self, currency_pair: str = "USD/MAD", amount: Decimal = Decimal("1000")) -> Optional[Dict]:
        """Scrape Wise exchange rate"""
        try:
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
            
            logger.info(f"Fetched Wise rate: {mock_rate['rate']}")
            return mock_rate
            
        except Exception as e:
            logger.error(f"Error fetching Wise rate: {e}")
            return None
    
    async def fetch_western_union_rate(self, currency_pair: str = "USD/MAD", amount: Decimal = Decimal("1000")) -> Optional[Dict]:
        """Scrape Western Union exchange rate"""
        try:
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
            
            logger.info(f"Fetched Western Union rate: {mock_rate['rate']}")
            return mock_rate
            
        except Exception as e:
            logger.error(f"Error fetching Western Union rate: {e}")
            return None

    async def fetch_transferwise_rate(self, currency_pair: str = "USD/MAD", amount: Decimal = Decimal("1000")) -> Optional[Dict]:
        """Scrape TransferWise exchange rate"""
        try:
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
            
            logger.info(f"Fetched TransferWise rate: {mock_rate['rate']}")
            return mock_rate
            
        except Exception as e:
            logger.error(f"Error fetching TransferWise rate: {e}")
            return None

    async def fetch_cih_bank_rate(self, currency_pair: str = "USD/MAD", amount: Decimal = Decimal("1000")) -> Optional[Dict]:
        """Scrape CIH Bank exchange rate"""
        try:
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
            
            logger.info(f"Fetched CIH Bank rate: {mock_rate['rate']}")
            return mock_rate
            
        except Exception as e:
            logger.error(f"Error fetching CIH Bank rate: {e}")
            return None

    async def fetch_attijari_bank_rate(self, currency_pair: str = "USD/MAD", amount: Decimal = Decimal("1000")) -> Optional[Dict]:
        """Scrape Attijari Bank exchange rate"""
        try:
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
            
            logger.info(f"Fetched Attijari Bank rate: {mock_rate['rate']}")
            return mock_rate
            
        except Exception as e:
            logger.error(f"Error fetching Attijari Bank rate: {e}")
            return None
    
    async def fetch_all_remittance_rates(self, currency_pair: str = "USD/MAD", amount: Decimal = Decimal("1000")) -> List[Dict]:
        """Fetch rates from all remittance services"""
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
        for r in results:
            if r is not None and not isinstance(r, Exception):
                rates.append(r)
        
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

async def main():
    """Test the currency scraper"""
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
            
    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(main()) 