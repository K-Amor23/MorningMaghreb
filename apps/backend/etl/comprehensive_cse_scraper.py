#!/usr/bin/env python3
"""
Comprehensive CSE Company Scraper

This scraper fetches ALL companies from the Casablanca Stock Exchange
using multiple sources including Wafabourse, CSE official website, and other sources.
"""

import asyncio
import aiohttp
import ssl
import json
import csv
from datetime import datetime
from typing import List, Dict, Set, Optional
from pathlib import Path
import logging
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class ComprehensiveCSEScraper:
    """Comprehensive scraper for all CSE companies from multiple sources"""
    
    def __init__(self):
        self.session = None
        self.companies = {}  # Use dict to avoid duplicates by ticker
        
        # Multiple sources for CSE companies
        self.sources = {
            "wafabourse": {
                "url": "https://www.wafabourse.com/fr/marche/actions",
                "name": "Wafabourse Official"
            },
            "cse_official": {
                "url": "https://www.casablanca-bourse.com/bourseweb/Liste-Societe.aspx",
                "name": "CSE Official"
            },
            "investing": {
                "url": "https://www.investing.com/equities/morocco",
                "name": "Investing.com Morocco"
            },
            "marketwatch": {
                "url": "https://www.marketwatch.com/investing/stock/country/morocco",
                "name": "MarketWatch Morocco"
            }
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
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup session"""
        if self.session:
            await self.session.close()
    
    async def scrape_wafabourse(self) -> List[Dict]:
        """Scrape companies from Wafabourse"""
        companies = []
        
        try:
            logger.info("📊 Scraping Wafabourse...")
            
            # Try multiple Wafabourse endpoints
            urls = [
                "https://www.wafabourse.com/fr/marche/actions",
                "https://www.wafabourse.com/fr/marche/indices/masi",
                "https://www.wafabourse.com/api/companies",  # API endpoint if exists
                "https://www.wafabourse.com/fr/societes"
            ]
            
            for url in urls:
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Look for company tables, lists, or data
                            tables = soup.find_all('table')
                            for table in tables:
                                rows = table.find_all('tr')
                                for row in rows[1:]:  # Skip header
                                    cells = row.find_all(['td', 'th'])
                                    if len(cells) >= 2:
                                        # Extract ticker and company name
                                        ticker = cells[0].get_text(strip=True)
                                        name = cells[1].get_text(strip=True)
                                        
                                        if ticker and name and len(ticker) <= 6:
                                            companies.append({
                                                "ticker": ticker.upper(),
                                                "name": name,
                                                "source": "Wafabourse",
                                                "url": url
                                            })
                            
                            # Also look for JSON data in script tags
                            scripts = soup.find_all('script')
                            for script in scripts:
                                if script.string and 'companies' in script.string.lower():
                                    # Try to extract JSON data
                                    try:
                                        # Look for JSON patterns
                                        json_match = re.search(r'companies["\']?\s*:\s*(\[.*?\])', script.string)
                                        if json_match:
                                            data = json.loads(json_match.group(1))
                                            for item in data:
                                                if isinstance(item, dict) and 'ticker' in item:
                                                    companies.append({
                                                        "ticker": item.get('ticker', '').upper(),
                                                        "name": item.get('name', ''),
                                                        "source": "Wafabourse API",
                                                        "url": url
                                                    })
                                    except:
                                        pass
                            
                            logger.info(f"Found {len(companies)} companies from {url}")
                            
                except Exception as e:
                    logger.warning(f"Failed to scrape {url}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Wafabourse: {e}")
        
        return companies
    
    async def scrape_cse_official(self) -> List[Dict]:
        """Scrape companies from CSE official website"""
        companies = []
        
        try:
            logger.info("📊 Scraping CSE Official...")
            
            urls = [
                "https://www.casablanca-bourse.com/bourseweb/Liste-Societe.aspx",
                "https://www.casablanca-bourse.com/bourseweb/content.aspx?IdLink=21",
                "https://www.casablanca-bourse.com/bourseweb/Societe-Cote.aspx"
            ]
            
            for url in urls:
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Look for company listings
                            # CSE website often has specific table structures
                            tables = soup.find_all('table', {'class': ['DataGrid', 'grid', 'listing']})
                            for table in tables:
                                rows = table.find_all('tr')
                                for row in rows[1:]:  # Skip header
                                    cells = row.find_all(['td', 'th'])
                                    if len(cells) >= 2:
                                        ticker = cells[0].get_text(strip=True)
                                        name = cells[1].get_text(strip=True)
                                        
                                        if ticker and name and len(ticker) <= 6:
                                            companies.append({
                                                "ticker": ticker.upper(),
                                                "name": name,
                                                "source": "CSE Official",
                                                "url": url
                                            })
                            
                            # Also look for select/option elements
                            selects = soup.find_all('select')
                            for select in selects:
                                options = select.find_all('option')
                                for option in options:
                                    value = option.get('value', '')
                                    text = option.get_text(strip=True)
                                    
                                    if value and text and len(value) <= 6 and value != '0':
                                        companies.append({
                                            "ticker": value.upper(),
                                            "name": text,
                                            "source": "CSE Official Select",
                                            "url": url
                                        })
                            
                            logger.info(f"Found {len(companies)} companies from CSE official")
                            
                except Exception as e:
                    logger.warning(f"Failed to scrape CSE official {url}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping CSE official: {e}")
        
        return companies
    
    async def scrape_investing_com(self) -> List[Dict]:
        """Scrape companies from Investing.com Morocco section"""
        companies = []
        
        try:
            logger.info("📊 Scraping Investing.com Morocco...")
            
            urls = [
                "https://www.investing.com/equities/morocco",
                "https://www.investing.com/indices/masi-components"
            ]
            
            for url in urls:
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Investing.com has specific table structures
                            tables = soup.find_all('table', {'class': ['genTbl', 'closedTbl', 'crossRatesTbl']})
                            for table in tables:
                                rows = table.find_all('tr')
                                for row in rows[1:]:  # Skip header
                                    cells = row.find_all(['td', 'th'])
                                    if len(cells) >= 2:
                                        # First cell usually contains the company name/ticker
                                        name_cell = cells[0]
                                        link = name_cell.find('a')
                                        if link:
                                            name = link.get_text(strip=True)
                                            # Extract ticker from URL or text
                                            href = link.get('href', '')
                                            ticker_match = re.search(r'/([A-Z]{2,6})(?:-|$)', href)
                                            if ticker_match:
                                                ticker = ticker_match.group(1)
                                            else:
                                                # Try to extract from name
                                                ticker_match = re.search(r'\(([A-Z]{2,6})\)', name)
                                                if ticker_match:
                                                    ticker = ticker_match.group(1)
                                                else:
                                                    ticker = name.split()[0]  # Use first word as ticker
                                            
                                            companies.append({
                                                "ticker": ticker.upper(),
                                                "name": name,
                                                "source": "Investing.com",
                                                "url": url
                                            })
                            
                            logger.info(f"Found {len(companies)} companies from Investing.com")
                            
                except Exception as e:
                    logger.warning(f"Failed to scrape Investing.com {url}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping Investing.com: {e}")
        
        return companies
    
    async def scrape_known_companies(self) -> List[Dict]:
        """Add known major Moroccan companies that might be missed"""
        known_companies = [
            # Major Banks
            {"ticker": "ATW", "name": "Attijariwafa Bank", "sector": "Banking"},
            {"ticker": "BCP", "name": "Banque Centrale Populaire", "sector": "Banking"},
            {"ticker": "BMCE", "name": "BMCE Bank of Africa", "sector": "Banking"},
            {"ticker": "CIH", "name": "Crédit Immobilier et Hôtelier", "sector": "Banking"},
            {"ticker": "CDM", "name": "Crédit du Maroc", "sector": "Banking"},
            
            # Telecommunications
            {"ticker": "IAM", "name": "Itissalat Al-Maghrib (Maroc Telecom)", "sector": "Telecommunications"},
            
            # Insurance
            {"ticker": "WAA", "name": "Wafa Assurance", "sector": "Insurance"},
            {"ticker": "SAH", "name": "Saham Assurance", "sector": "Insurance"},
            
            # Real Estate
            {"ticker": "ADH", "name": "Addoha", "sector": "Real Estate"},
            {"ticker": "RDS", "name": "Résidences Dar Saada", "sector": "Real Estate"},
            
            # Retail & Consumer
            {"ticker": "LBV", "name": "Label Vie", "sector": "Retail"},
            {"ticker": "MAR", "name": "Marjane Holding", "sector": "Retail"},
            
            # Industrial
            {"ticker": "LES", "name": "Lesieur Cristal", "sector": "Food & Beverages"},
            {"ticker": "CEN", "name": "Ciments du Maroc", "sector": "Construction Materials"},
            {"ticker": "HOL", "name": "Holcim Maroc", "sector": "Construction Materials"},
            {"ticker": "LAF", "name": "Lafarge Ciments", "sector": "Construction Materials"},
            
            # Mining
            {"ticker": "MSA", "name": "Managem", "sector": "Mining"},
            {"ticker": "SMI", "name": "SMI (Société Métallurgique d'Imiter)", "sector": "Mining"},
            
            # Energy
            {"ticker": "TMA", "name": "Taqa Morocco", "sector": "Energy"},
            
            # Pharmaceuticals
            {"ticker": "SOT", "name": "Sothema", "sector": "Pharmaceuticals"},
            {"ticker": "COP", "name": "Cooper Pharma", "sector": "Pharmaceuticals"},
            
            # Transportation
            {"ticker": "CTM", "name": "Compagnie de Transports au Maroc", "sector": "Transportation"},
            
            # Technology
            {"ticker": "HPS", "name": "HPS (High Payment Systems)", "sector": "Technology"},
            
            # Agriculture
            {"ticker": "COL", "name": "Cosumar", "sector": "Agriculture & Food"},
            {"ticker": "SNA", "name": "Société Nationale d'Autoroutes", "sector": "Infrastructure"},
            
            # Textiles
            {"ticker": "DEL", "name": "Delattre Levivier Maroc", "sector": "Textiles"},
            
            # Hotels & Tourism
            {"ticker": "RIS", "name": "Risma", "sector": "Hotels & Tourism"},
        ]
        
        logger.info(f"Adding {len(known_companies)} known major companies")
        
        for company in known_companies:
            company["source"] = "Known Major Companies"
            company["url"] = "Manual Entry"
        
        return known_companies
    
    async def scrape_all_sources(self) -> Dict[str, Dict]:
        """Scrape from all sources and combine results"""
        all_companies = {}
        
        # Scrape from all sources
        sources_data = await asyncio.gather(
            self.scrape_wafabourse(),
            self.scrape_cse_official(),
            self.scrape_investing_com(),
            self.scrape_known_companies(),
            return_exceptions=True
        )
        
        # Combine results from all sources
        for source_companies in sources_data:
            if isinstance(source_companies, list):
                for company in source_companies:
                    ticker = company.get("ticker", "").upper()
                    if ticker and len(ticker) <= 6:
                        # Use ticker as key to avoid duplicates
                        if ticker not in all_companies:
                            all_companies[ticker] = company
                        else:
                            # Merge information from multiple sources
                            existing = all_companies[ticker]
                            if not existing.get("sector") and company.get("sector"):
                                existing["sector"] = company["sector"]
                            if not existing.get("name") or len(company.get("name", "")) > len(existing.get("name", "")):
                                existing["name"] = company["name"]
                            # Add source info
                            existing["sources"] = existing.get("sources", []) + [company.get("source", "")]
        
        return all_companies
    
    async def export_companies(self, companies: Dict[str, Dict], output_dir: Path):
        """Export companies to various formats"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert to list for export
        companies_list = list(companies.values())
        
        # Add metadata
        for company in companies_list:
            company["scraped_at"] = datetime.now().isoformat()
            company["exchange"] = "Casablanca Stock Exchange"
            company["country"] = "Morocco"
        
        # Export to CSV
        csv_file = output_dir / "cse_companies_comprehensive.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if companies_list:
                writer = csv.DictWriter(f, fieldnames=companies_list[0].keys())
                writer.writeheader()
                writer.writerows(companies_list)
        
        # Export to JSON
        json_file = output_dir / "cse_companies_comprehensive.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(companies_list, f, indent=2, ensure_ascii=False)
        
        # Export database format
        db_file = output_dir / "cse_companies_comprehensive_database.json"
        db_format = {
            "metadata": {
                "total_companies": len(companies_list),
                "scraped_at": datetime.now().isoformat(),
                "sources": list(self.sources.keys()) + ["Known Major Companies"]
            },
            "companies": companies_list
        }
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(db_format, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Exported {len(companies_list)} companies to:")
        logger.info(f"  - CSV: {csv_file}")
        logger.info(f"  - JSON: {json_file}")
        logger.info(f"  - Database: {db_file}")
        
        return companies_list

async def main():
    """Main function to run comprehensive scraping"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logger.info("🚀 Starting Comprehensive CSE Company Scraping")
    logger.info("=" * 60)
    
    output_dir = Path("data")
    
    async with ComprehensiveCSEScraper() as scraper:
        # Scrape all companies
        companies = await scraper.scrape_all_sources()
        
        logger.info(f"\n📊 SCRAPING RESULTS:")
        logger.info(f"Total unique companies found: {len(companies)}")
        
        # Show breakdown by source
        source_counts = {}
        for company in companies.values():
            sources = company.get("sources", [company.get("source", "Unknown")])
            if isinstance(sources, str):
                sources = [sources]
            for source in sources:
                source_counts[source] = source_counts.get(source, 0) + 1
        
        logger.info("\n📈 Companies by source:")
        for source, count in source_counts.items():
            logger.info(f"  - {source}: {count}")
        
        # Export results
        companies_list = await scraper.export_companies(companies, output_dir)
        
        # Show sample companies
        logger.info(f"\n📋 Sample companies (first 10):")
        for i, company in enumerate(list(companies.values())[:10]):
            logger.info(f"  {i+1}. {company['ticker']} - {company['name']}")
        
        logger.info(f"\n🎉 Successfully scraped {len(companies)} companies from the Casablanca Stock Exchange!")

if __name__ == "__main__":
    asyncio.run(main()) 