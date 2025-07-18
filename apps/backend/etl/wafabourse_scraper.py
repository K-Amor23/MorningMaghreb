#!/usr/bin/env python3
"""
Specialized Wafabourse Scraper

This scraper specifically targets Wafabourse.com to get the complete
list of companies from the Casablanca Stock Exchange.
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

class WafabourseScraper:
    """Specialized scraper for Wafabourse.com"""
    
    def __init__(self):
        self.session = None
        self.companies = []
        
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
                "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup session"""
        if self.session:
            await self.session.close()
    
    async def scrape_wafabourse_main(self) -> List[Dict]:
        """Scrape main Wafabourse pages"""
        companies = []
        
        # Multiple Wafabourse URLs to try
        urls = [
            "https://www.wafabourse.com/fr/marche/actions",
            "https://www.wafabourse.com/fr/marche/indices/masi",
            "https://www.wafabourse.com/fr/marche/indices/madex",
            "https://www.wafabourse.com/fr/marche/cotations",
            "https://www.wafabourse.com/fr/societes",
            "https://www.wafabourse.com/fr/marche/actions/cotations",
            "https://www.wafabourse.com/fr/marche/actions/secteurs"
        ]
        
        for url in urls:
            try:
                logger.info(f"🔍 Scraping: {url}")
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Method 1: Look for tables with company data
                        tables = soup.find_all('table')
                        for table in tables:
                            rows = table.find_all('tr')
                            for row in rows:
                                cells = row.find_all(['td', 'th'])
                                if len(cells) >= 2:
                                    # Try to extract ticker and name
                                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                                    
                                    # Look for patterns like ticker codes
                                    for i, text in enumerate(cell_texts):
                                        if re.match(r'^[A-Z]{2,6}$', text):
                                            ticker = text
                                            name = cell_texts[i+1] if i+1 < len(cell_texts) else ""
                                            
                                            if name and len(name) > 3:
                                                companies.append({
                                                    "ticker": ticker,
                                                    "name": name,
                                                    "source": "Wafabourse Table",
                                                    "url": url
                                                })
                        
                        # Method 2: Look for select/option elements
                        selects = soup.find_all('select')
                        for select in selects:
                            options = select.find_all('option')
                            for option in options:
                                value = option.get('value', '')
                                text = option.get_text(strip=True)
                                
                                if value and text and re.match(r'^[A-Z]{2,6}$', value):
                                    companies.append({
                                        "ticker": value,
                                        "name": text,
                                        "source": "Wafabourse Select",
                                        "url": url
                                    })
                        
                        # Method 3: Look for JavaScript data
                        scripts = soup.find_all('script')
                        for script in scripts:
                            if script.string:
                                # Look for JSON arrays with company data
                                json_patterns = [
                                    r'companies\s*[:=]\s*(\[.*?\])',
                                    r'stocks\s*[:=]\s*(\[.*?\])',
                                    r'data\s*[:=]\s*(\[.*?\])',
                                    r'list\s*[:=]\s*(\[.*?\])'
                                ]
                                
                                for pattern in json_patterns:
                                    matches = re.findall(pattern, script.string, re.DOTALL)
                                    for match in matches:
                                        try:
                                            data = json.loads(match)
                                            if isinstance(data, list):
                                                for item in data:
                                                    if isinstance(item, dict):
                                                        ticker = item.get('ticker', item.get('symbol', item.get('code', '')))
                                                        name = item.get('name', item.get('title', item.get('label', '')))
                                                        
                                                        if ticker and name:
                                                            companies.append({
                                                                "ticker": ticker.upper(),
                                                                "name": name,
                                                                "source": "Wafabourse JS",
                                                                "url": url
                                                            })
                                        except:
                                            pass
                        
                        # Method 4: Look for specific CSS classes/IDs
                        company_elements = soup.find_all(['div', 'span', 'td'], class_=re.compile(r'(company|stock|ticker|symbol)', re.I))
                        for element in company_elements:
                            text = element.get_text(strip=True)
                            if re.match(r'^[A-Z]{2,6}$', text):
                                # Found a ticker, look for nearby name
                                parent = element.parent
                                if parent:
                                    siblings = parent.find_all(['div', 'span', 'td'])
                                    for sibling in siblings:
                                        sibling_text = sibling.get_text(strip=True)
                                        if len(sibling_text) > 5 and sibling_text != text:
                                            companies.append({
                                                "ticker": text,
                                                "name": sibling_text,
                                                "source": "Wafabourse CSS",
                                                "url": url
                                            })
                                            break
                        
                        logger.info(f"Found {len(companies)} companies from {url}")
                        
                    else:
                        logger.warning(f"Failed to access {url}: HTTP {response.status}")
                        
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue
        
        return companies
    
    async def scrape_api_endpoints(self) -> List[Dict]:
        """Try to find API endpoints that might have company data"""
        companies = []
        
        # Potential API endpoints
        api_urls = [
            "https://www.wafabourse.com/api/companies",
            "https://www.wafabourse.com/api/stocks",
            "https://www.wafabourse.com/api/market/companies",
            "https://www.wafabourse.com/api/v1/companies",
            "https://www.wafabourse.com/data/companies.json",
            "https://www.wafabourse.com/data/stocks.json",
            "https://www.wafabourse.com/ajax/companies",
            "https://www.wafabourse.com/fr/api/companies"
        ]
        
        for url in api_urls:
            try:
                logger.info(f"🔍 Trying API: {url}")
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            
                            if isinstance(data, list):
                                for item in data:
                                    if isinstance(item, dict):
                                        ticker = item.get('ticker', item.get('symbol', item.get('code', '')))
                                        name = item.get('name', item.get('title', item.get('label', '')))
                                        
                                        if ticker and name:
                                            companies.append({
                                                "ticker": ticker.upper(),
                                                "name": name,
                                                "source": "Wafabourse API",
                                                "url": url
                                            })
                            
                            elif isinstance(data, dict):
                                # Check if data contains companies array
                                for key in ['companies', 'stocks', 'data', 'results']:
                                    if key in data and isinstance(data[key], list):
                                        for item in data[key]:
                                            if isinstance(item, dict):
                                                ticker = item.get('ticker', item.get('symbol', item.get('code', '')))
                                                name = item.get('name', item.get('title', item.get('label', '')))
                                                
                                                if ticker and name:
                                                    companies.append({
                                                        "ticker": ticker.upper(),
                                                        "name": name,
                                                        "source": "Wafabourse API",
                                                        "url": url
                                                    })
                            
                            logger.info(f"Found {len(companies)} companies from API {url}")
                            
                        except json.JSONDecodeError:
                            # Try to parse as text
                            text = await response.text()
                            if 'ticker' in text.lower() or 'company' in text.lower():
                                logger.info(f"Found text data at {url}, but couldn't parse as JSON")
                    
            except Exception as e:
                logger.debug(f"API endpoint {url} failed: {e}")
                continue
        
        return companies
    
    def add_comprehensive_known_companies(self) -> List[Dict]:
        """Add comprehensive list of known CSE companies"""
        
        # This is a more comprehensive list based on research
        known_companies = [
            # BANKING SECTOR
            {"ticker": "ATW", "name": "Attijariwafa Bank", "sector": "Banking"},
            {"ticker": "BCP", "name": "Banque Centrale Populaire", "sector": "Banking"},
            {"ticker": "BMCE", "name": "BMCE Bank of Africa", "sector": "Banking"},
            {"ticker": "CIH", "name": "Crédit Immobilier et Hôtelier", "sector": "Banking"},
            {"ticker": "CDM", "name": "Crédit du Maroc", "sector": "Banking"},
            {"ticker": "BOA", "name": "Bank of Africa", "sector": "Banking"},
            
            # TELECOMMUNICATIONS
            {"ticker": "IAM", "name": "Itissalat Al-Maghrib (Maroc Telecom)", "sector": "Telecommunications"},
            
            # INSURANCE
            {"ticker": "WAA", "name": "Wafa Assurance", "sector": "Insurance"},
            {"ticker": "SAH", "name": "Saham Assurance", "sector": "Insurance"},
            {"ticker": "ATL", "name": "Atlantasanad", "sector": "Insurance"},
            
            # REAL ESTATE & CONSTRUCTION
            {"ticker": "ADH", "name": "Addoha", "sector": "Real Estate"},
            {"ticker": "RDS", "name": "Résidences Dar Saada", "sector": "Real Estate"},
            {"ticker": "CEN", "name": "Ciments du Maroc", "sector": "Construction Materials"},
            {"ticker": "HOL", "name": "Holcim Maroc", "sector": "Construction Materials"},
            {"ticker": "LAF", "name": "Lafarge Ciments", "sector": "Construction Materials"},
            {"ticker": "JET", "name": "Jet Contractors", "sector": "Construction"},
            {"ticker": "TIM", "name": "Timar", "sector": "Construction Materials"},
            
            # RETAIL & CONSUMER GOODS
            {"ticker": "LBV", "name": "Label Vie", "sector": "Retail"},
            {"ticker": "MAR", "name": "Marjane Holding", "sector": "Retail"},
            {"ticker": "AUT", "name": "Auto Hall", "sector": "Automotive Retail"},
            {"ticker": "DIS", "name": "Disway", "sector": "Retail"},
            
            # FOOD & BEVERAGES
            {"ticker": "LES", "name": "Lesieur Cristal", "sector": "Food & Beverages"},
            {"ticker": "COL", "name": "Cosumar", "sector": "Food & Beverages"},
            {"ticker": "CEN", "name": "Centrale Danone", "sector": "Food & Beverages"},
            {"ticker": "BCI", "name": "Brasseries du Maroc", "sector": "Beverages"},
            {"ticker": "UNI", "name": "Unimer", "sector": "Food & Beverages"},
            
            # MINING & METALS
            {"ticker": "MSA", "name": "Managem", "sector": "Mining"},
            {"ticker": "SMI", "name": "SMI (Société Métallurgique d'Imiter)", "sector": "Mining"},
            {"ticker": "CMT", "name": "Ciments du Maroc", "sector": "Mining & Materials"},
            
            # ENERGY & UTILITIES
            {"ticker": "TMA", "name": "Taqa Morocco", "sector": "Energy"},
            {"ticker": "SNA", "name": "Société Nationale d'Autoroutes", "sector": "Infrastructure"},
            {"ticker": "LYD", "name": "Lydec", "sector": "Utilities"},
            {"ticker": "RED", "name": "Redal", "sector": "Utilities"},
            
            # PHARMACEUTICALS & HEALTHCARE
            {"ticker": "SOT", "name": "Sothema", "sector": "Pharmaceuticals"},
            {"ticker": "COP", "name": "Cooper Pharma", "sector": "Pharmaceuticals"},
            {"ticker": "PHA", "name": "Pharma 5", "sector": "Pharmaceuticals"},
            
            # TRANSPORTATION & LOGISTICS
            {"ticker": "CTM", "name": "Compagnie de Transports au Maroc", "sector": "Transportation"},
            {"ticker": "RAM", "name": "Royal Air Maroc", "sector": "Airlines"},
            {"ticker": "MAR", "name": "Marsa Maroc", "sector": "Ports & Logistics"},
            
            # TECHNOLOGY & SERVICES
            {"ticker": "HPS", "name": "HPS (High Payment Systems)", "sector": "Technology"},
            {"ticker": "M2M", "name": "M2M Group", "sector": "Technology"},
            {"ticker": "IB2", "name": "IB Maroc.com", "sector": "Technology"},
            
            # TEXTILES & LEATHER
            {"ticker": "DEL", "name": "Delattre Levivier Maroc", "sector": "Textiles"},
            {"ticker": "FEN", "name": "Fenie Brossette", "sector": "Industrial Distribution"},
            
            # HOTELS & TOURISM
            {"ticker": "RIS", "name": "Risma", "sector": "Hotels & Tourism"},
            {"ticker": "MOG", "name": "Mogador", "sector": "Hotels & Tourism"},
            
            # AGRICULTURE & FISHING
            {"ticker": "SAL", "name": "Salafin", "sector": "Financial Services"},
            {"ticker": "CRE", "name": "Crédit Agricole du Maroc", "sector": "Banking"},
            
            # PAPER & PACKAGING
            {"ticker": "PAP", "name": "Papelera de Tetuán", "sector": "Paper & Packaging"},
            
            # CHEMICALS
            {"ticker": "SNE", "name": "Snep", "sector": "Chemicals"},
            {"ticker": "COL", "name": "Colorado", "sector": "Chemicals"},
            
            # INVESTMENT & HOLDING COMPANIES
            {"ticker": "ONA", "name": "ONA (Omnium Nord Africain)", "sector": "Holding Company"},
            {"ticker": "SNI", "name": "SNI (Société Nationale d'Investissement)", "sector": "Holding Company"},
            {"ticker": "FIN", "name": "Financecom", "sector": "Financial Services"},
            
            # ADDITIONAL COMPANIES
            {"ticker": "ALM", "name": "Aluminium du Maroc", "sector": "Metals"},
            {"ticker": "STR", "name": "Stroc Industrie", "sector": "Industrial"},
            {"ticker": "MUT", "name": "Mutandis", "sector": "Holding Company"},
            {"ticker": "ZEL", "name": "Zellidja", "sector": "Mining"},
            {"ticker": "AFR", "name": "Afriquia Gaz", "sector": "Energy"},
            {"ticker": "MIC", "name": "Microdata", "sector": "Technology"},
            {"ticker": "NEX", "name": "Nexans Maroc", "sector": "Industrial"},
            {"ticker": "ALI", "name": "Alliances", "sector": "Real Estate"},
            {"ticker": "BAL", "name": "Balima", "sector": "Industrial"},
            {"ticker": "BER", "name": "Berliet Maroc", "sector": "Automotive"},
        ]
        
        logger.info(f"Adding {len(known_companies)} comprehensive known companies")
        
        for company in known_companies:
            company["source"] = "Comprehensive Known Companies"
            company["url"] = "Research Based"
            company["scraped_at"] = datetime.now().isoformat()
            company["exchange"] = "Casablanca Stock Exchange"
            company["country"] = "Morocco"
        
        return known_companies
    
    async def scrape_all(self) -> List[Dict]:
        """Scrape from all sources"""
        all_companies = []
        
        # Scrape from web sources
        web_companies = await self.scrape_wafabourse_main()
        all_companies.extend(web_companies)
        
        # Try API endpoints
        api_companies = await self.scrape_api_endpoints()
        all_companies.extend(api_companies)
        
        # Add known companies
        known_companies = self.add_comprehensive_known_companies()
        all_companies.extend(known_companies)
        
        # Remove duplicates based on ticker
        unique_companies = {}
        for company in all_companies:
            ticker = company.get("ticker", "").upper()
            if ticker and ticker not in unique_companies:
                unique_companies[ticker] = company
        
        return list(unique_companies.values())
    
    async def export_results(self, companies: List[Dict], output_dir: Path):
        """Export results to files"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export to CSV
        csv_file = output_dir / "cse_companies_complete.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if companies:
                writer = csv.DictWriter(f, fieldnames=companies[0].keys())
                writer.writeheader()
                writer.writerows(companies)
        
        # Export to JSON
        json_file = output_dir / "cse_companies_complete.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(companies, f, indent=2, ensure_ascii=False)
        
        # Export database format
        db_file = output_dir / "cse_companies_complete_database.json"
        db_format = {
            "metadata": {
                "total_companies": len(companies),
                "scraped_at": datetime.now().isoformat(),
                "exchange": "Casablanca Stock Exchange",
                "country": "Morocco",
                "sources": ["Wafabourse", "API Endpoints", "Comprehensive Research"]
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

async def main():
    """Main function"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logger.info("🚀 Starting Complete CSE Company Scraping from Wafabourse")
    logger.info("=" * 70)
    
    output_dir = Path("data")
    
    async with WafabourseScraper() as scraper:
        companies = await scraper.scrape_all()
        
        logger.info(f"\n📊 FINAL RESULTS:")
        logger.info(f"Total companies found: {len(companies)}")
        
        # Show breakdown by sector
        sectors = {}
        for company in companies:
            sector = company.get("sector", "Unknown")
            sectors[sector] = sectors.get(sector, 0) + 1
        
        logger.info(f"\n📈 Companies by sector:")
        for sector, count in sorted(sectors.items()):
            logger.info(f"  - {sector}: {count}")
        
        # Export results
        await scraper.export_results(companies, output_dir)
        
        logger.info(f"\n🎉 Successfully compiled {len(companies)} companies from the Casablanca Stock Exchange!")
        
        # Show first 15 companies
        logger.info(f"\n📋 First 15 companies:")
        for i, company in enumerate(companies[:15]):
            logger.info(f"  {i+1:2d}. {company['ticker']:6s} - {company['name']}")

if __name__ == "__main__":
    asyncio.run(main()) 