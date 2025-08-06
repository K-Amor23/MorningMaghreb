
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
African Markets Scraper for Casablanca Stock Exchange

This scraper fetches ALL companies from the Casablanca Stock Exchange (BVC)
using the African Markets website which has comprehensive data.
"""

import asyncio
import aiohttp
import ssl
import json
import csv
import re
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class AfricanMarketsScraper:
    """Scraper for African Markets BVC listed companies"""
    
    def __init__(self):
        self.session = None
        self.base_url = "https://www.african-markets.com"
        self.companies_url = "https://www.african-markets.com/en/stock-markets/bvc/listed-companies"
        
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
                "Referer": "https://www.african-markets.com/"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup session"""
        if self.session:
            await self.session.close()
    
    def extract_ticker_from_url(self, url: str) -> str:
        """Extract ticker from company URL"""
        # URLs like: listed-companies/company?code=ATW
        match = re.search(r'code=([A-Z0-9.]+)', url)
        if match:
            ticker = match.group(1)
            # Clean up ticker (remove .MA suffix if present)
            return ticker.replace('.MA', '')
        return ""
    
    def clean_financial_value(self, value: str) -> Optional[float]:
        """Clean and convert financial values"""
        if not value or value == '-':
            return None
        
        # Remove % sign and convert
        value = value.replace('%', '').replace('+', '').replace(',', '')
        try:
            return float(value)
        except:
            return None
    
    def clean_volume_value(self, value: str) -> Optional[int]:
        """Clean and convert volume values"""
        if not value or value == '-':
            return None
        
        # Remove common volume suffixes and convert
        value = value.replace(',', '').replace(' ', '').upper()
        
        # Handle different volume formats (K, M, B)
        multipliers = {
            'K': 1000,
            'M': 1000000,
            'B': 1000000000
        }
        
        for suffix, multiplier in multipliers.items():
            if value.endswith(suffix):
                try:
                    return int(float(value[:-1]) * multiplier)
                except:
                    pass
        
        # Try direct conversion
        try:
            return int(float(value))
        except:
            return None
    
    async def scrape_companies_table(self) -> List[Dict]:
        """Scrape the main companies table"""
        companies = []
        
        try:
            logger.info(f"🔍 Scraping companies from: {self.companies_url}")
            
            async with self.session.get(self.companies_url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch companies page: HTTP {response.status}")
                    return companies
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find the companies table
                # Look for table with company data
                tables = soup.find_all('table')
                
                for table in tables:
                    rows = table.find_all('tr')
                    
                    # Skip if no rows or too few columns
                    if len(rows) < 2:
                        continue
                    
                    # Check if this looks like the companies table
                    header_row = rows[0]
                    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                    
                    # Look for expected headers
                    if any(header.lower() in ['company', 'sector', 'price'] for header in headers):
                        logger.info(f"Found companies table with headers: {headers}")
                        
                        # Process data rows
                        for row in rows[1:]:
                            cells = row.find_all(['td', 'th'])
                            
                            if len(cells) >= 6:  # Company, Sector, Price, %1D, %YTD, M.Cap
                                try:
                                    # Extract company name and ticker
                                    company_cell = cells[0]
                                    company_link = company_cell.find('a')
                                    
                                    if company_link:
                                        company_name = company_link.get_text(strip=True)
                                        company_url = company_link.get('href', '')
                                        ticker = self.extract_ticker_from_url(company_url)
                                    else:
                                        company_name = company_cell.get_text(strip=True)
                                        ticker = ""
                                    
                                    # Extract other data
                                    sector = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                                    price_text = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                                    change_1d_text = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                                    change_ytd_text = cells[4].get_text(strip=True) if len(cells) > 4 else ""
                                    mcap_text = cells[5].get_text(strip=True) if len(cells) > 5 else ""
                                    volume_text = cells[6].get_text(strip=True) if len(cells) > 6 else ""
                                    
                                    # Clean up price (remove commas, convert to float)
                                    price = self.clean_financial_value(price_text)
                                    change_1d = self.clean_financial_value(change_1d_text)
                                    change_ytd = self.clean_financial_value(change_ytd_text)
                                    
                                    # Market cap might be in billions (B) or millions (M)
                                    mcap = None
                                    if mcap_text and mcap_text != '-':
                                        mcap_clean = mcap_text.replace(',', '')
                                        try:
                                            mcap = float(mcap_clean)
                                        except:
                                            pass
                                    
                                    # Clean up volume data
                                    volume = self.clean_volume_value(volume_text)
                                    
                                    if company_name and ticker:
                                        company_data = {
                                            "ticker": ticker.upper(),
                                            "name": company_name,
                                            "sector": sector,
                                            "price": price,
                                            "change_1d_percent": change_1d,
                                            "change_ytd_percent": change_ytd,
                                            "market_cap_billion": mcap,
                                            "volume": volume,
                                            "source": "African Markets",
                                            "url": self.companies_url,
                                            "company_url": f"{self.base_url}/{company_url}" if company_url else "",
                                            "exchange": "Casablanca Stock Exchange (BVC)",
                                            "country": "Morocco",
                                            "scraped_at": datetime.now().isoformat()
                                        }
                                        
                                        companies.append(company_data)
                                        logger.info(f"✅ Found: {ticker} - {company_name} ({sector})")
                                
                                except Exception as e:
                                    logger.warning(f"Error processing row: {e}")
                                    continue
                
                logger.info(f"📊 Successfully scraped {len(companies)} companies from African Markets")
                
        except Exception as e:
            logger.error(f"Error scraping companies: {e}")
        
        return companies
    
    async def enhance_company_data(self, companies: List[Dict]) -> List[Dict]:
        """Enhance company data with additional information"""
        enhanced_companies = []
        
        for company in companies:
            enhanced_company = company.copy()
            
            # Add additional metadata
            enhanced_company["data_source"] = "African Markets BVC"
            enhanced_company["last_updated"] = datetime.now().isoformat()
            
            # Classify company size based on market cap
            mcap = company.get("market_cap_billion", 0)
            if mcap and mcap > 0:
                if mcap > 50:
                    enhanced_company["size_category"] = "Large Cap"
                elif mcap > 10:
                    enhanced_company["size_category"] = "Mid Cap"
                elif mcap > 1:
                    enhanced_company["size_category"] = "Small Cap"
                else:
                    enhanced_company["size_category"] = "Micro Cap"
            else:
                enhanced_company["size_category"] = "Unknown"
            
            # Add sector classification
            sector = company.get("sector", "").lower()
            if "financial" in sector or "bank" in sector:
                enhanced_company["sector_group"] = "Financial Services"
            elif "industrial" in sector or "construction" in sector:
                enhanced_company["sector_group"] = "Industrials"
            elif "consumer" in sector or "retail" in sector:
                enhanced_company["sector_group"] = "Consumer"
            elif "oil" in sector or "gas" in sector or "energy" in sector:
                enhanced_company["sector_group"] = "Energy"
            elif "telecom" in sector or "technology" in sector:
                enhanced_company["sector_group"] = "Technology & Telecom"
            else:
                enhanced_company["sector_group"] = "Other"
            
            enhanced_companies.append(enhanced_company)
        
        return enhanced_companies
    
    async def export_companies(self, companies: List[Dict], output_dir: Path):
        """Export companies to various formats"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export to CSV
        csv_file = output_dir / "cse_companies_african_markets.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if companies:
                writer = csv.DictWriter(f, fieldnames=companies[0].keys())
                writer.writeheader()
                writer.writerows(companies)
        
        # Export to JSON
        json_file = output_dir / "cse_companies_african_markets.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(companies, f, indent=2, ensure_ascii=False)
        
        # Export database format
        db_file = output_dir / "cse_companies_african_markets_database.json"
        db_format = {
            "metadata": {
                "source": "African Markets",
                "url": self.companies_url,
                "total_companies": len(companies),
                "scraped_at": datetime.now().isoformat(),
                "exchange": "Casablanca Stock Exchange (BVC)",
                "country": "Morocco"
            },
            "companies": companies
        }
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(db_format, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Exported {len(companies)} companies to:")
        logger.info(f"  - CSV: {csv_file}")
        logger.info(f"  - JSON: {json_file}")
        logger.info(f"  - Database: {db_file}")
        
        return companies
    
    async def scrape_all(self) -> List[Dict]:
        """Main scraping method"""
        logger.info("🚀 Starting African Markets scraper for Casablanca Stock Exchange")
        
        # Scrape companies table
        companies = await self.scrape_companies_table()
        
        if not companies:
            logger.warning("No companies found - trying alternative methods")
            return []
        
        # Enhance company data
        enhanced_companies = await self.enhance_company_data(companies)
        
        return enhanced_companies

async def main():
    """Main function"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logger.info("🚀 African Markets Scraper for Casablanca Stock Exchange")
    logger.info("=" * 70)
    
    output_dir = Path("data")
    
    async with AfricanMarketsScraper() as scraper:
        companies = await scraper.scrape_all()
        
        if not companies:
            logger.error("❌ No companies found!")
            return
        
        logger.info(f"\n📊 SCRAPING RESULTS:")
        logger.info(f"Total companies found: {len(companies)}")
        
        # Show breakdown by sector
        sectors = {}
        for company in companies:
            sector = company.get("sector", "Unknown")
            sectors[sector] = sectors.get(sector, 0) + 1
        
        logger.info(f"\n📈 Companies by sector:")
        for sector, count in sorted(sectors.items()):
            logger.info(f"  - {sector}: {count}")
        
        # Show breakdown by size
        sizes = {}
        for company in companies:
            size = company.get("size_category", "Unknown")
            sizes[size] = sizes.get(size, 0) + 1
        
        logger.info(f"\n📊 Companies by size:")
        for size, count in sorted(sizes.items()):
            logger.info(f"  - {size}: {count}")
        
        # Export results
        await scraper.export_companies(companies, output_dir)
        
        logger.info(f"\n📋 Sample companies (first 15):")
        for i, company in enumerate(companies[:15]):
            mcap = company.get("market_cap_billion", 0)
            mcap_str = f"{mcap:.1f}B" if mcap else "N/A"
            logger.info(f"  {i+1:2d}. {company['ticker']:6s} - {company['name'][:40]:40s} ({company['sector'][:15]:15s}) - {mcap_str}")
        
        logger.info(f"\n🎉 Successfully scraped {len(companies)} companies from African Markets!")

if __name__ == "__main__":
    asyncio.run(main()) 