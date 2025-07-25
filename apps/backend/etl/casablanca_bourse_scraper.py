"""
Casablanca Bourse Web Scraper

This module scrapes trading data from the official Casablanca Stock Exchange website.
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
import json
import logging
from datetime import datetime, date
from typing import List, Dict, Optional
import re
from pathlib import Path
import time
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class CasablancaBourseScraper:
    """Scraper for Casablanca Stock Exchange website"""
    
    def __init__(self):
        self.base_url = "https://www.casablanca-bourse.com"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Headers to mimic browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def is_html_page(self, url: str, content_type: str = None) -> bool:
        """Check if URL points to an HTML page"""
        # Check file extension
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        
        # Skip PDFs, images, and other non-HTML files
        skip_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.doc', '.docx', '.xls', '.xlsx']
        for ext in skip_extensions:
            if path.endswith(ext):
                return False
        
        # Check content type if provided
        if content_type:
            return 'text/html' in content_type.lower()
        
        return True
    
    async def get_main_page(self) -> Optional[str]:
        """Get the main page content"""
        try:
            logger.info("Fetching main page from Casablanca Bourse...")
            
            async with self.session.get(self.base_url, timeout=30) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    if self.is_html_page(self.base_url, content_type):
                        content = await response.text()
                        logger.info(f"Successfully fetched main page ({len(content)} bytes)")
                        return content
                    else:
                        logger.warning(f"Main page is not HTML: {content_type}")
                        return None
                else:
                    logger.error(f"Failed to fetch main page: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching main page: {e}")
            return None
    
    async def find_market_data_links(self, content: str) -> List[str]:
        """Find links to market data pages"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            links = []
            
            # Look for common market data link patterns
            link_patterns = [
                'cours', 'cotations', 'market', 'bourse', 'trading',
                'prix', 'actions', 'valeurs', 'indices'
            ]
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').lower()
                text = link.get_text().lower()
                
                # Check if link contains market data keywords
                for pattern in link_patterns:
                    if pattern in href or pattern in text:
                        full_url = self.base_url + link['href'] if link['href'].startswith('/') else link['href']
                        
                        # Only include HTML pages
                        if self.is_html_page(full_url):
                            links.append(full_url)
                            logger.info(f"Found market data link: {full_url}")
                        else:
                            logger.debug(f"Skipping non-HTML link: {full_url}")
                        break
            
            # Remove duplicates
            links = list(set(links))
            logger.info(f"Found {len(links)} potential HTML market data links")
            return links
            
        except Exception as e:
            logger.error(f"Error finding market data links: {e}")
            return []
    
    async def scrape_market_data_page(self, url: str) -> Optional[Dict]:
        """Scrape a specific market data page"""
        try:
            logger.info(f"Scraping market data from: {url}")
            
            async with self.session.get(url, timeout=30) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch {url}: HTTP {response.status}")
                    return None
                
                content_type = response.headers.get('content-type', '')
                if not self.is_html_page(url, content_type):
                    logger.debug(f"Skipping non-HTML page: {url} ({content_type})")
                    return None
                
                try:
                    content = await response.text()
                except UnicodeDecodeError as e:
                    logger.warning(f"Unicode decode error for {url}: {e}")
                    return None
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # Look for table data
                tables = soup.find_all('table')
                market_data = {
                    'url': url,
                    'scraped_at': datetime.now().isoformat(),
                    'tables': []
                }
                
                for i, table in enumerate(tables):
                    try:
                        table_data = self.extract_table_data(table)
                        if table_data:
                            market_data['tables'].append({
                                'table_index': i,
                                'data': table_data
                            })
                    except Exception as e:
                        logger.warning(f"Error extracting table {i}: {e}")
                
                logger.info(f"Extracted {len(market_data['tables'])} tables from {url}")
                return market_data
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def extract_table_data(self, table) -> Optional[List[Dict]]:
        """Extract data from an HTML table"""
        try:
            rows = table.find_all('tr')
            if not rows:
                return None
            
            # Extract headers
            headers = []
            header_row = rows[0]
            for th in header_row.find_all(['th', 'td']):
                headers.append(th.get_text(strip=True))
            
            if not headers:
                return None
            
            # Extract data rows
            data = []
            for row in rows[1:]:  # Skip header row
                cells = row.find_all(['td', 'th'])
                if len(cells) == len(headers):
                    row_data = {}
                    for i, cell in enumerate(cells):
                        cell_text = cell.get_text(strip=True)
                        # Try to convert to number if possible
                        try:
                            if re.match(r'^\d+\.?\d*$', cell_text):
                                row_data[headers[i]] = float(cell_text)
                            else:
                                row_data[headers[i]] = cell_text
                        except:
                            row_data[headers[i]] = cell_text
                    data.append(row_data)
            
            return data if data else None
            
        except Exception as e:
            logger.warning(f"Error extracting table data: {e}")
            return None
    
    async def search_for_stock_data(self, ticker: str) -> Optional[Dict]:
        """Search for specific stock data"""
        try:
            logger.info(f"Searching for stock data: {ticker}")
            
            # Try different search patterns
            search_patterns = [
                f"{ticker}",
                f"{ticker.lower()}",
                f"{ticker.upper()}"
            ]
            
            for pattern in search_patterns:
                # Search in the main page first
                main_content = await self.get_main_page()
                if main_content and pattern in main_content:
                    logger.info(f"Found {pattern} in main page")
                    
                    # Extract surrounding context
                    context = self.extract_context_around_pattern(main_content, pattern)
                    if context:
                        return {
                            'ticker': ticker,
                            'pattern_found': pattern,
                            'context': context,
                            'scraped_at': datetime.now().isoformat()
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching for {ticker}: {e}")
            return None
    
    def extract_context_around_pattern(self, content: str, pattern: str, context_size: int = 200) -> Optional[str]:
        """Extract text context around a pattern"""
        try:
            index = content.lower().find(pattern.lower())
            if index != -1:
                start = max(0, index - context_size)
                end = min(len(content), index + len(pattern) + context_size)
                return content[start:end].strip()
            return None
        except Exception as e:
            logger.warning(f"Error extracting context: {e}")
            return None
    
    async def scrape_all_market_data(self) -> Dict:
        """Scrape all available market data"""
        try:
            logger.info("Starting comprehensive market data scraping...")
            
            # Get main page
            main_content = await self.get_main_page()
            if not main_content:
                return {'error': 'Failed to fetch main page'}
            
            # Find market data links
            market_links = await self.find_market_data_links(main_content)
            
            # Scrape each market data page
            all_data = {
                'scraped_at': datetime.now().isoformat(),
                'main_page_size': len(main_content),
                'market_links_found': len(market_links),
                'market_data_pages': []
            }
            
            for link in market_links:
                page_data = await self.scrape_market_data_page(link)
                if page_data:
                    all_data['market_data_pages'].append(page_data)
                
                # Rate limiting
                await asyncio.sleep(2)
            
            logger.info(f"Scraped {len(all_data['market_data_pages'])} market data pages")
            return all_data
            
        except Exception as e:
            logger.error(f"Error in comprehensive scraping: {e}")
            return {'error': str(e)}
    
    def save_data(self, data: Dict, output_file: str = None) -> str:
        """Save scraped data to file"""
        try:
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"casablanca_bourse_data_{timestamp}.json"
            
            output_path = Path(output_file)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Data saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            raise

async def main():
    """Main function to test the scraper"""
    print("🔍 Testing Casablanca Bourse Scraper")
    print("=" * 50)
    
    async with CasablancaBourseScraper() as scraper:
        # Test comprehensive scraping
        print("Scraping all market data...")
        all_data = await scraper.scrape_all_market_data()
        
        if 'error' not in all_data:
            print(f"✅ Successfully scraped {len(all_data['market_data_pages'])} pages")
            
            # Save data
            output_file = scraper.save_data(all_data)
            print(f"📁 Data saved to: {output_file}")
            
            # Show summary
            total_tables = sum(len(page.get('tables', [])) for page in all_data['market_data_pages'])
            print(f"📊 Total tables extracted: {total_tables}")
            
        else:
            print(f"❌ Error: {all_data['error']}")
        
        # Test specific stock search
        print("\nSearching for specific stocks...")
        test_tickers = ["ATW", "IAM", "BCP"]
        
        for ticker in test_tickers:
            stock_data = await scraper.search_for_stock_data(ticker)
            if stock_data:
                print(f"✅ Found data for {ticker}")
            else:
                print(f"❌ No data found for {ticker}")

if __name__ == "__main__":
    asyncio.run(main()) 