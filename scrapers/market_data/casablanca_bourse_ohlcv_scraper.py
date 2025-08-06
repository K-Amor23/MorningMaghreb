
from ..base.scraper_interface import BaseScraper
from ..utils.http_helpers import make_request, add_delay
from ..utils.date_parsers import parse_date, extract_date_from_text
from ..utils.config_loader import get_scraper_config
from ..utils.data_validators import validate_dataframe, clean_dataframe
import pandas as pd
import logging
from typing import Dict, Any, Optional
#!/usr/bin/env python3
"""
Casablanca Bourse OHLCV Data Scraper

This scraper extracts daily OHLCV (Open, High, Low, Close, Volume) data
from the official Casablanca Stock Exchange website.

Data Source: https://www.casablanca-bourse.com
"""

import asyncio
import aiohttp
import pandas as pd
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import re
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CasablancaBourseOHLCVScraper:
    """Scraper for daily OHLCV data from Casablanca Bourse"""
    
    def __init__(self):
        self.base_url = "https://www.casablanca-bourse.com"
        self.session = None
        self.output_dir = Path("apps/backend/data/casablanca_bourse")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Trading session times (Morocco time)
        self.trading_hours = {
            'start': '09:00',
            'end': '16:30'
        }
        
        logger.info("Casablanca Bourse OHLCV Scraper initialized")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_main_page(self) -> Optional[str]:
        """Get the main page of Casablanca Bourse"""
        try:
            url = f"{self.base_url}/bourseweb/societe-cote.aspx"
            logger.info(f"Fetching main page: {url}")
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    logger.info("Successfully fetched main page")
                    return content
                else:
                    logger.error(f"Failed to fetch main page: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching main page: {e}")
            return None
    
    async def get_market_data_page(self) -> Optional[str]:
        """Get the market data page with daily quotes"""
        try:
            # Try different possible URLs for market data
            urls = [
                f"{self.base_url}/bourseweb/cours.aspx",
                f"{self.base_url}/bourseweb/marche-cours.aspx",
                f"{self.base_url}/bourseweb/cours-jour.aspx",
                f"{self.base_url}/bourseweb/quotations.aspx"
            ]
            
            for url in urls:
                logger.info(f"Trying market data URL: {url}")
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            content = await response.text()
                            logger.info(f"Successfully fetched market data from: {url}")
                            return content
                except Exception as e:
                    logger.warning(f"Failed to fetch from {url}: {e}")
                    continue
            
            logger.error("All market data URLs failed")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching market data page: {e}")
            return None
    
    def parse_ohlcv_table(self, html_content: str) -> List[Dict]:
        """Parse OHLCV data from HTML table"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            ohlcv_data = []
            
            # Look for tables with market data
            tables = soup.find_all('table')
            
            for table in tables:
                # Check if this table contains OHLCV data
                headers = table.find_all('th')
                header_text = ' '.join([h.get_text(strip=True) for h in headers]).lower()
                
                if any(keyword in header_text for keyword in ['cours', 'prix', 'volume', 'valeur', 'ouverture', 'plus haut', 'plus bas']):
                    logger.info("Found OHLCV table")
                    
                    rows = table.find_all('tr')[1:]  # Skip header row
                    
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 6:  # Expecting: Ticker, Open, High, Low, Close, Volume
                            try:
                                ticker = cells[0].get_text(strip=True)
                                
                                # Extract numeric values
                                open_price = self.extract_number(cells[1].get_text(strip=True))
                                high_price = self.extract_number(cells[2].get_text(strip=True))
                                low_price = self.extract_number(cells[3].get_text(strip=True))
                                close_price = self.extract_number(cells[4].get_text(strip=True))
                                volume = self.extract_number(cells[5].get_text(strip=True))
                                
                                if ticker and close_price:
                                    ohlcv_record = {
                                        'ticker': ticker,
                                        'date': datetime.now().strftime('%Y-%m-%d'),
                                        'open': open_price,
                                        'high': high_price,
                                        'low': low_price,
                                        'close': close_price,
                                        'volume': volume,
                                        'timestamp': datetime.now().isoformat(),
                                        'source': 'casablanca_bourse'
                                    }
                                    ohlcv_data.append(ohlcv_record)
                                    
                            except (IndexError, ValueError) as e:
                                logger.warning(f"Error parsing row: {e}")
                                continue
            
            logger.info(f"Parsed {len(ohlcv_data)} OHLCV records")
            return ohlcv_data
            
        except Exception as e:
            logger.error(f"Error parsing OHLCV table: {e}")
            return []
    
    def extract_number(self, text: str) -> Optional[float]:
        """Extract numeric value from text"""
        try:
            # Remove common non-numeric characters
            cleaned = re.sub(r'[^\d.,]', '', text)
            if cleaned:
                # Handle different decimal separators
                if ',' in cleaned and '.' in cleaned:
                    # Format like "1,234.56"
                    return float(cleaned.replace(',', ''))
                elif ',' in cleaned:
                    # Format like "1234,56" (European)
                    return float(cleaned.replace(',', '.'))
                else:
                    return float(cleaned)
            return None
        except (ValueError, AttributeError):
            return None
    
    async def get_company_detail_page(self, ticker: str) -> Optional[Dict]:
        """Get detailed OHLCV data for a specific company"""
        try:
            # Try different URL patterns for company details
            urls = [
                f"{self.base_url}/bourseweb/societe-cote.aspx?code={ticker}",
                f"{self.base_url}/bourseweb/societe.aspx?code={ticker}",
                f"{self.base_url}/bourseweb/cours-societe.aspx?code={ticker}"
            ]
            
            for url in urls:
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            content = await response.text()
                            
                            # Parse the detail page
                            soup = BeautifulSoup(content, 'html.parser')
                            
                            # Extract current price and basic info
                            current_price = None
                            company_name = None
                            
                            # Look for price information
                            price_elements = soup.find_all(text=re.compile(r'\d+[,.]\d+'))
                            for element in price_elements:
                                if self.extract_number(element):
                                    current_price = self.extract_number(element)
                                    break
                            
                            # Look for company name
                            title_elements = soup.find_all(['h1', 'h2', 'h3'])
                            for element in title_elements:
                                text = element.get_text(strip=True)
                                if text and len(text) > 3 and not text.isdigit():
                                    company_name = text
                                    break
                            
                            return {
                                'ticker': ticker,
                                'company_name': company_name,
                                'current_price': current_price,
                                'date': datetime.now().strftime('%Y-%m-%d'),
                                'timestamp': datetime.now().isoformat(),
                                'source': 'casablanca_bourse'
                            }
                            
                except Exception as e:
                    logger.warning(f"Failed to fetch detail page for {ticker} from {url}: {e}")
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting company detail for {ticker}: {e}")
            return None
    
    async def scrape_all_ohlcv_data(self) -> Dict:
        """Scrape all available OHLCV data"""
        try:
            logger.info("Starting comprehensive OHLCV data scraping...")
            
            # Get main market data page
            market_data_html = await self.get_market_data_page()
            if not market_data_html:
                logger.error("Failed to get market data page")
                return {'success': False, 'error': 'Failed to get market data page'}
            
            # Parse OHLCV data
            ohlcv_data = self.parse_ohlcv_table(market_data_html)
            
            if not ohlcv_data:
                logger.warning("No OHLCV data found in main table, trying alternative approach")
                
                # Try to get data for known tickers
                known_tickers = ['ATW', 'IAM', 'BCP', 'BMCE', 'CIH', 'WAA', 'CTM', 'MNG', 'MADESA', 'SOTHEMA']
                ohlcv_data = []
                
                for ticker in known_tickers:
                    logger.info(f"Trying to get data for {ticker}")
                    detail_data = await self.get_company_detail_page(ticker)
                    if detail_data:
                        ohlcv_data.append(detail_data)
                    await asyncio.sleep(1)  # Be respectful
            
            # Save data
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.output_dir / f"ohlcv_data_{timestamp}.json"
            
            result = {
                'success': True,
                'data': ohlcv_data,
                'count': len(ohlcv_data),
                'timestamp': datetime.now().isoformat(),
                'output_file': str(output_file)
            }
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully scraped {len(ohlcv_data)} OHLCV records")
            logger.info(f"Data saved to: {output_file}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in comprehensive OHLCV scraping: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_historical_data_urls(self) -> List[str]:
        """Get URLs for historical data downloads"""
        try:
            # Try to find historical data links
            urls = [
                f"{self.base_url}/bourseweb/historique.aspx",
                f"{self.base_url}/bourseweb/telechargement.aspx",
                f"{self.base_url}/bourseweb/archives.aspx"
            ]
            
            historical_urls = []
            for url in urls:
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            content = await response.text()
                            soup = BeautifulSoup(content, 'html.parser')
                            
                            # Look for download links
                            links = soup.find_all('a', href=True)
                            for link in links:
                                href = link['href']
                                if any(keyword in href.lower() for keyword in ['csv', 'xls', 'historique', 'cours']):
                                    full_url = f"{self.base_url}{href}" if href.startswith('/') else href
                                    historical_urls.append(full_url)
                                    
                except Exception as e:
                    logger.warning(f"Failed to check {url}: {e}")
                    continue
            
            return historical_urls
            
        except Exception as e:
            logger.error(f"Error getting historical data URLs: {e}")
            return []

async def main():
    """Main function to run the scraper"""
    print("🔄 Starting Casablanca Bourse OHLCV Scraper")
    print("=" * 60)
    
    async with CasablancaBourseOHLCVScraper() as scraper:
        # Scrape all OHLCV data
        result = await scraper.scrape_all_ohlcv_data()
        
        if result['success']:
            print(f"✅ Successfully scraped {result['count']} OHLCV records")
            print(f"📁 Data saved to: {result['output_file']}")
            
            # Show sample data
            if result['data']:
                print("\n📊 Sample OHLCV Data:")
                print("-" * 40)
                for i, record in enumerate(result['data'][:5]):
                    print(f"{i+1}. {record['ticker']}: {record.get('close', 'N/A')} MAD")
                    if 'volume' in record and record['volume']:
                        print(f"   Volume: {record['volume']:,}")
        else:
            print(f"❌ Scraping failed: {result.get('error', 'Unknown error')}")
        
        # Try to get historical data URLs
        print("\n🔍 Checking for historical data URLs...")
        historical_urls = await scraper.get_historical_data_urls()
        if historical_urls:
            print(f"✅ Found {len(historical_urls)} historical data URLs:")
            for url in historical_urls[:3]:  # Show first 3
                print(f"   - {url}")
        else:
            print("⚠️ No historical data URLs found")
    
    print("\n✅ OHLCV scraping completed")

if __name__ == "__main__":
    asyncio.run(main()) 

class CasablancaBourseOhlcvScraperScraper(BaseScraper):
    """Casablanca Bourse Ohlcv Scraper Scraper"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.config = get_scraper_config("casablanca_bourse_ohlcv_scraper")
    
    def fetch(self) -> pd.DataFrame:
        """Fetch data from source"""
        # TODO: Implement fetch logic
        return pd.DataFrame()
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate fetched data"""
        # TODO: Implement validation logic
        return True
