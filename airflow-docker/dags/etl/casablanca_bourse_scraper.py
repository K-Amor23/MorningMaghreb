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
                
                # Check if link text or href contains market data patterns
                for pattern in link_patterns:
                    if pattern in href or pattern in text:
                        full_url = self.base_url + link['href'] if link['href'].startswith('/') else link['href']
                        if full_url not in links:
                            links.append(full_url)
                            logger.debug(f"Found market data link: {full_url}")
            
            logger.info(f"Found {len(links)} potential market data links")
            return links
            
        except Exception as e:
            logger.error(f"Error finding market data links: {e}")
            return []
    
    async def scrape_market_data(self, url: str) -> Optional[Dict]:
        """Scrape market data from a specific URL"""
        try:
            logger.info(f"Scraping market data from: {url}")
            
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Extract market data (this is a basic implementation)
                    data = {
                        'url': url,
                        'scraped_at': datetime.now().isoformat(),
                        'title': '',
                        'content_length': len(content)
                    }
                    
                    # Get page title
                    title_elem = soup.find('title')
                    if title_elem:
                        data['title'] = title_elem.get_text(strip=True)
                    
                    # Look for price/quote information
                    price_elements = soup.find_all(text=re.compile(r'\d+\.?\d*', re.I))
                    if price_elements:
                        data['price_data'] = [elem.strip() for elem in price_elements[:10]]
                    
                    logger.info(f"Successfully scraped data from {url}")
                    return data
                    
                else:
                    logger.warning(f"Failed to scrape {url}: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    async def scrape_all_market_data(self) -> List[Dict]:
        """Scrape market data from all available sources"""
        try:
            logger.info("Starting comprehensive market data scraping...")
            
            # Get main page
            main_content = await self.get_main_page()
            if not main_content:
                logger.error("Could not fetch main page")
                return []
            
            # Find market data links
            links = await self.find_market_data_links(main_content)
            if not links:
                logger.warning("No market data links found")
                return []
            
            # Scrape each link
            all_data = []
            for link in links[:5]:  # Limit to first 5 links to avoid overwhelming
                try:
                    data = await self.scrape_market_data(link)
                    if data:
                        all_data.append(data)
                    
                    # Add delay between requests
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error processing link {link}: {e}")
                    continue
            
            logger.info(f"Completed scraping {len(all_data)} market data sources")
            return all_data
            
        except Exception as e:
            logger.error(f"Error in comprehensive scraping: {e}")
            return []
    
    async def export_data(self, data: List[Dict], output_dir: Path = None) -> Path:
        """Export scraped data to JSON file"""
        if output_dir is None:
            output_dir = Path("data/casablanca_bourse")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"casablanca_bourse_data_{timestamp}.json"
        filepath = output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Data exported to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            raise

async def main():
    """Main function for testing"""
    async with CasablancaBourseScraper() as scraper:
        data = await scraper.scrape_all_market_data()
        
        if data:
            output_dir = Path("data/casablanca_bourse")
            await scraper.export_data(data, output_dir)
            print(f"✅ Scraping completed! Found {len(data)} data sources.")
        else:
            print("❌ No data was scraped.")

if __name__ == "__main__":
    asyncio.run(main())
