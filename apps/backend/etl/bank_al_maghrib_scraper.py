#!/usr/bin/env python3
"""
Bank Al-Maghrib (Moroccan Central Bank) Data Scraper

This scraper fetches comprehensive economic and financial data from Bank Al-Maghrib
including exchange rates, interest rates, monetary statistics, and economic indicators.
"""

import asyncio
import aiohttp
import ssl
import json
import csv
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pathlib import Path
import logging
from bs4 import BeautifulSoup
import pandas as pd

logger = logging.getLogger(__name__)

class BankAlMaghribScraper:
    """Comprehensive scraper for Bank Al-Maghrib economic data"""
    
    def __init__(self):
        self.session = None
        self.base_url = "https://www.bkam.ma"
        self.api_base_url = "https://www.bkam.ma/api"  # Potential API endpoint
        
        # Key data endpoints
        self.endpoints = {
            # Exchange rates
            "exchange_rates": "/en/Markets/Key-indicators/Foreign-exchange-market/Foreign-exchange-rates/Transfer-exchange-rate",
            "reference_rates": "/Marches/Principaux-indicateurs/Marche-des-changes/Cours-de-change/Cours-de-reference",
            "indicative_rates": "/en/Markets/Key-indicators/Foreign-exchange-market/Foreign-exchange-rates/Indicative-exchange-rate-against-the-dirham",
            
            # Interest rates
            "interbank_rates": "/en/Markets/Key-indicators/Money-market/Reference-rate-of-the-interbank-market",
            "lending_rates": "/en/Markets/Other-rates/Lending-rates",
            "deposit_rates": "/en/Markets/Other-rates/Rates-on-term-deposits",
            
            # Monetary statistics
            "monetary_stats": "/en/Statistics/Monetary-statistics/Key-indicators-of-monetary-statistics",
            "weekly_indicators": "/en/Statistics/Key-figures-of-the-national-economy/Weekly-indicators",
            
            # Banking sector
            "banking_dashboard": "/en/Statistics/Banking-sector-statistics/Dashboard",
            "banking_structure": "/en/Statistics/Banking-sector-statistics/Structure-of-the-banking-system",
            
            # Economic indicators
            "inflation": "/en/Statistics/Prices/Real-estate-price-index",
            "reserves": "/en/Statistics/Official-reserve-assets",
            
            # Market operations
            "market_interventions": "/en/Monetary-policy/Operational-framework/Bank-al-maghrib-intervention-mechanism-in-the-money-market/Outstanding-amount-of-interventions",
        }
        
        # CSV download endpoints (these often provide direct data access)
        self.csv_endpoints = {
            "exchange_rates_csv": "/Marches/Principaux-indicateurs/Marche-des-changes/Cours-de-change/Cours-de-reference",
            "interbank_rates_csv": "/en/Markets/Key-indicators/Money-market/Reference-rate-of-the-interbank-market",
        }
        
    async def __aenter__(self):
        """Setup async HTTP session"""
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=connector,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Referer": "https://www.bkam.ma/"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup session"""
        if self.session:
            await self.session.close()
    
    async def fetch_page(self, endpoint: str, params: Dict = None) -> Optional[str]:
        """Fetch a page from BAM website"""
        try:
            url = f"{self.base_url}{endpoint}"
            logger.info(f"Fetching: {url}")
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching {endpoint}: {e}")
            return None
    
    async def try_api_endpoint(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Try to access potential API endpoints"""
        try:
            url = f"{self.api_base_url}{endpoint}"
            logger.info(f"Trying API: {url}")
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'application/json' in content_type:
                        return await response.json()
                    else:
                        return {"text": await response.text()}
                else:
                    logger.debug(f"API endpoint {url} returned {response.status}")
                    return None
        except Exception as e:
            logger.debug(f"API endpoint {endpoint} failed: {e}")
            return None
    
    def parse_exchange_rates_table(self, html: str) -> List[Dict]:
        """Parse exchange rates from HTML table"""
        rates = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for exchange rate tables
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) < 2:
                continue
                
            # Check if this looks like an exchange rate table
            headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
            
            if any(header.lower() in ['devises', 'currencies', 'currency'] for header in headers):
                logger.info(f"Found exchange rate table with headers: {headers}")
                
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        try:
                            currency = cells[0].get_text(strip=True)
                            
                            # Extract rates from subsequent columns
                            rate_data = {
                                "currency": currency,
                                "scraped_at": datetime.now().isoformat(),
                                "source": "Bank Al-Maghrib"
                            }
                            
                            # Parse rate values
                            for i, cell in enumerate(cells[1:], 1):
                                rate_text = cell.get_text(strip=True)
                                if rate_text and rate_text != '-':
                                    try:
                                        # Clean and convert rate
                                        rate_clean = rate_text.replace(',', '.')
                                        rate_value = float(rate_clean)
                                        
                                        # Determine column type based on header
                                        if i < len(headers):
                                            column_name = headers[i].lower()
                                            if 'moyen' in column_name or 'average' in column_name:
                                                rate_data["rate"] = rate_value
                                            elif any(date_indicator in column_name for date_indicator in ['2025', '2024', '/']):
                                                rate_data[f"rate_{headers[i]}"] = rate_value
                                            else:
                                                rate_data[f"rate_col_{i}"] = rate_value
                                        else:
                                            rate_data[f"rate_col_{i}"] = rate_value
                                    except ValueError:
                                        continue
                            
                            if len(rate_data) > 3:  # More than just currency, scraped_at, source
                                rates.append(rate_data)
                                
                        except Exception as e:
                            logger.warning(f"Error parsing exchange rate row: {e}")
                            continue
        
        return rates
    
    def parse_interest_rates_table(self, html: str) -> List[Dict]:
        """Parse interest rates from HTML table"""
        rates = []
        soup = BeautifulSoup(html, 'html.parser')
        
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) < 2:
                continue
                
            headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
            
            if any(header.lower() in ['maturités', 'maturity', 'taux', 'rate'] for header in headers):
                logger.info(f"Found interest rate table with headers: {headers}")
                
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        try:
                            maturity = cells[0].get_text(strip=True)
                            
                            rate_data = {
                                "maturity": maturity,
                                "scraped_at": datetime.now().isoformat(),
                                "source": "Bank Al-Maghrib"
                            }
                            
                            # Parse rate values
                            for i, cell in enumerate(cells[1:], 1):
                                rate_text = cell.get_text(strip=True)
                                if rate_text and rate_text != '-':
                                    try:
                                        # Remove % sign and convert
                                        rate_clean = rate_text.replace('%', '').replace(',', '.')
                                        rate_value = float(rate_clean)
                                        
                                        if i < len(headers):
                                            column_name = headers[i].lower()
                                            if 'bid' in column_name:
                                                rate_data["bid_rate"] = rate_value
                                            elif 'ask' in column_name:
                                                rate_data["ask_rate"] = rate_value
                                            else:
                                                rate_data[f"rate_{headers[i]}"] = rate_value
                                        else:
                                            rate_data[f"rate_col_{i}"] = rate_value
                                    except ValueError:
                                        continue
                            
                            if len(rate_data) > 3:
                                rates.append(rate_data)
                                
                        except Exception as e:
                            logger.warning(f"Error parsing interest rate row: {e}")
                            continue
        
        return rates
    
    def parse_monetary_statistics(self, html: str) -> List[Dict]:
        """Parse monetary statistics from HTML"""
        stats = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for key indicators or statistics
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) < 2:
                continue
                
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    try:
                        indicator = cells[0].get_text(strip=True)
                        value_text = cells[1].get_text(strip=True)
                        
                        if indicator and value_text:
                            stat_data = {
                                "indicator": indicator,
                                "value_text": value_text,
                                "scraped_at": datetime.now().isoformat(),
                                "source": "Bank Al-Maghrib"
                            }
                            
                            # Try to extract numeric value
                            try:
                                # Look for numbers in the value
                                numbers = re.findall(r'[\d,]+\.?\d*', value_text)
                                if numbers:
                                    numeric_value = float(numbers[0].replace(',', ''))
                                    stat_data["numeric_value"] = numeric_value
                            except:
                                pass
                            
                            stats.append(stat_data)
                    except Exception as e:
                        logger.warning(f"Error parsing monetary stat: {e}")
                        continue
        
        return stats
    
    async def fetch_exchange_rates(self) -> List[Dict]:
        """Fetch current exchange rates"""
        logger.info("🔄 Fetching exchange rates...")
        all_rates = []
        
        # Try multiple endpoints
        for endpoint_name, endpoint in [
            ("reference_rates", self.endpoints["reference_rates"]),
            ("exchange_rates", self.endpoints["exchange_rates"]),
            ("indicative_rates", self.endpoints["indicative_rates"])
        ]:
            html = await self.fetch_page(endpoint)
            if html:
                rates = self.parse_exchange_rates_table(html)
                for rate in rates:
                    rate["endpoint"] = endpoint_name
                all_rates.extend(rates)
        
        logger.info(f"✅ Found {len(all_rates)} exchange rate entries")
        return all_rates
    
    async def fetch_interest_rates(self) -> List[Dict]:
        """Fetch current interest rates"""
        logger.info("🔄 Fetching interest rates...")
        all_rates = []
        
        # Try multiple endpoints
        for endpoint_name, endpoint in [
            ("interbank_rates", self.endpoints["interbank_rates"]),
            ("lending_rates", self.endpoints["lending_rates"]),
            ("deposit_rates", self.endpoints["deposit_rates"])
        ]:
            html = await self.fetch_page(endpoint)
            if html:
                rates = self.parse_interest_rates_table(html)
                for rate in rates:
                    rate["endpoint"] = endpoint_name
                all_rates.extend(rates)
        
        logger.info(f"✅ Found {len(all_rates)} interest rate entries")
        return all_rates
    
    async def fetch_monetary_statistics(self) -> List[Dict]:
        """Fetch monetary statistics"""
        logger.info("🔄 Fetching monetary statistics...")
        all_stats = []
        
        # Try multiple endpoints
        for endpoint_name, endpoint in [
            ("monetary_stats", self.endpoints["monetary_stats"]),
            ("weekly_indicators", self.endpoints["weekly_indicators"]),
            ("reserves", self.endpoints["reserves"])
        ]:
            html = await self.fetch_page(endpoint)
            if html:
                stats = self.parse_monetary_statistics(html)
                for stat in stats:
                    stat["endpoint"] = endpoint_name
                all_stats.extend(stats)
        
        logger.info(f"✅ Found {len(all_stats)} monetary statistics")
        return all_stats
    
    async def fetch_banking_data(self) -> List[Dict]:
        """Fetch banking sector data"""
        logger.info("🔄 Fetching banking sector data...")
        all_data = []
        
        # Try banking endpoints
        for endpoint_name, endpoint in [
            ("banking_dashboard", self.endpoints["banking_dashboard"]),
            ("banking_structure", self.endpoints["banking_structure"])
        ]:
            html = await self.fetch_page(endpoint)
            if html:
                data = self.parse_monetary_statistics(html)  # Same parsing logic
                for item in data:
                    item["endpoint"] = endpoint_name
                    item["category"] = "banking"
                all_data.extend(data)
        
        logger.info(f"✅ Found {len(all_data)} banking data points")
        return all_data
    
    async def fetch_market_operations(self) -> List[Dict]:
        """Fetch market operations data"""
        logger.info("🔄 Fetching market operations...")
        all_ops = []
        
        html = await self.fetch_page(self.endpoints["market_interventions"])
        if html:
            ops = self.parse_monetary_statistics(html)
            for op in ops:
                op["category"] = "market_operations"
            all_ops.extend(ops)
        
        logger.info(f"✅ Found {len(all_ops)} market operations")
        return all_ops
    
    async def export_data(self, data: Dict[str, List[Dict]], output_dir: Path):
        """Export all collected data"""
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export each category separately
        for category, items in data.items():
            if not items:
                continue
                
            # CSV export
            csv_file = output_dir / f"bam_{category}_{timestamp}.csv"
            if items:
                df = pd.DataFrame(items)
                df.to_csv(csv_file, index=False, encoding='utf-8')
                logger.info(f"📄 Exported {len(items)} {category} to {csv_file}")
            
            # JSON export
            json_file = output_dir / f"bam_{category}_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
        
        # Combined export
        combined_file = output_dir / f"bam_all_data_{timestamp}.json"
        combined_data = {
            "metadata": {
                "source": "Bank Al-Maghrib",
                "scraped_at": datetime.now().isoformat(),
                "total_records": sum(len(items) for items in data.values()),
                "categories": list(data.keys())
            },
            "data": data
        }
        
        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Combined export saved to {combined_file}")
        
        return combined_data
    
    async def scrape_all(self) -> Dict[str, List[Dict]]:
        """Main scraping method - fetch all available data"""
        logger.info("🚀 Starting comprehensive Bank Al-Maghrib data scraping")
        
        # Fetch all data categories
        data = {}
        
        try:
            data["exchange_rates"] = await self.fetch_exchange_rates()
        except Exception as e:
            logger.error(f"Error fetching exchange rates: {e}")
            data["exchange_rates"] = []
        
        try:
            data["interest_rates"] = await self.fetch_interest_rates()
        except Exception as e:
            logger.error(f"Error fetching interest rates: {e}")
            data["interest_rates"] = []
        
        try:
            data["monetary_statistics"] = await self.fetch_monetary_statistics()
        except Exception as e:
            logger.error(f"Error fetching monetary statistics: {e}")
            data["monetary_statistics"] = []
        
        try:
            data["banking_data"] = await self.fetch_banking_data()
        except Exception as e:
            logger.error(f"Error fetching banking data: {e}")
            data["banking_data"] = []
        
        try:
            data["market_operations"] = await self.fetch_market_operations()
        except Exception as e:
            logger.error(f"Error fetching market operations: {e}")
            data["market_operations"] = []
        
        return data

async def main():
    """Main function"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logger.info("🏦 Bank Al-Maghrib Comprehensive Data Scraper")
    logger.info("=" * 60)
    
    output_dir = Path("data/bank_al_maghrib")
    
    async with BankAlMaghribScraper() as scraper:
        data = await scraper.scrape_all()
        
        # Export data
        combined_data = await scraper.export_data(data, output_dir)
        
        # Print summary
        logger.info(f"\n📊 SCRAPING SUMMARY:")
        logger.info(f"Total data points: {combined_data['metadata']['total_records']}")
        
        for category, items in data.items():
            if items:
                logger.info(f"  - {category}: {len(items)} items")
        
        # Show sample data
        logger.info(f"\n📋 SAMPLE DATA:")
        for category, items in data.items():
            if items:
                logger.info(f"\n{category.upper()}:")
                for i, item in enumerate(items[:3]):  # Show first 3 items
                    logger.info(f"  {i+1}. {item}")
                if len(items) > 3:
                    logger.info(f"  ... and {len(items) - 3} more")
        
        logger.info(f"\n🎉 Bank Al-Maghrib data scraping completed!")
        logger.info(f"📁 Data saved to: {output_dir}")

if __name__ == "__main__":
    asyncio.run(main()) 