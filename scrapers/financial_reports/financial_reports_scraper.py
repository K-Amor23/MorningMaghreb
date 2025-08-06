
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
Financial Reports Scraper

This scraper extracts financial reports (annual/quarterly) from:
1. Company IR pages
2. AMMC (Autorité Marocaine du Marché des Capitaux)
3. Bourse de Casablanca publications

Data Sources:
- Company websites (IR sections)
- https://www.ammc.ma
- https://www.casablanca-bourse.com
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import re
import time
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialReportsScraper:
    """Scraper for financial reports from various sources"""
    
    def __init__(self):
        self.session = None
        self.output_dir = Path("apps/backend/data/financial_reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Known company IR pages
        self.company_ir_pages = {
            'ATW': {
                'name': 'Attijariwafa Bank',
                'ir_url': 'https://www.attijariwafabank.com/fr/investisseurs',
                'base_url': 'https://www.attijariwafabank.com'
            },
            'IAM': {
                'name': 'Maroc Telecom',
                'ir_url': 'https://www.iam.ma/fr/investisseurs',
                'base_url': 'https://www.iam.ma'
            },
            'BCP': {
                'name': 'Banque Centrale Populaire',
                'ir_url': 'https://www.banquecentrale.ma/fr/investisseurs',
                'base_url': 'https://www.banquecentrale.ma'
            },
            'BMCE': {
                'name': 'BMCE Bank of Africa',
                'ir_url': 'https://www.bmcebank.ma/fr/investisseurs',
                'base_url': 'https://www.bmcebank.ma'
            },
            'CIH': {
                'name': 'CIH Bank',
                'ir_url': 'https://www.cihbank.ma/fr/investisseurs',
                'base_url': 'https://www.cihbank.ma'
            }
        }
        
        # Regulatory websites
        self.regulatory_sources = {
            'ammc': {
                'name': 'AMMC',
                'url': 'https://www.ammc.ma',
                'reports_url': 'https://www.ammc.ma/fr/publications'
            },
            'bourse': {
                'name': 'Bourse de Casablanca',
                'url': 'https://www.casablanca-bourse.com',
                'reports_url': 'https://www.casablanca-bourse.com/bourseweb/publications.aspx'
            }
        }
        
        logger.info("Financial Reports Scraper initialized")
    
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
    
    async def scrape_company_ir_page(self, ticker: str, company_info: Dict) -> List[Dict]:
        """Scrape financial reports from a company's IR page"""
        try:
            logger.info(f"Scraping IR page for {ticker}: {company_info['name']}")
            
            ir_url = company_info['ir_url']
            base_url = company_info['base_url']
            
            # Get the IR page
            async with self.session.get(ir_url) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch IR page for {ticker}: {response.status}")
                    return []
                
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                reports = []
                
                # Look for PDF links
                pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.IGNORECASE))
                
                for link in pdf_links:
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    
                    if href and text:
                        # Determine report type and year
                        report_info = self.analyze_report_link(text, href)
                        
                        if report_info:
                            full_url = urllib.parse.urljoin(base_url, href)
                            
                            report = {
                                'ticker': ticker,
                                'company_name': company_info['name'],
                                'title': text,
                                'url': full_url,
                                'report_type': report_info['type'],
                                'year': report_info['year'],
                                'quarter': report_info.get('quarter'),
                                'language': report_info.get('language', 'fr'),
                                'source': 'company_ir',
                                'scraped_at': datetime.now().isoformat()
                            }
                            
                            reports.append(report)
                
                # Also look for links with financial keywords
                financial_keywords = ['rapport', 'compte', 'resultat', 'financier', 'annual', 'quarterly', 'semestriel']
                
                for keyword in financial_keywords:
                    links = soup.find_all('a', text=re.compile(keyword, re.IGNORECASE))
                    for link in links:
                        href = link.get('href')
                        text = link.get_text(strip=True)
                        
                        if href and text and not any(r['url'] == href for r in reports):
                            report_info = self.analyze_report_link(text, href)
                            if report_info:
                                full_url = urllib.parse.urljoin(base_url, href)
                                
                                report = {
                                    'ticker': ticker,
                                    'company_name': company_info['name'],
                                    'title': text,
                                    'url': full_url,
                                    'report_type': report_info['type'],
                                    'year': report_info['year'],
                                    'quarter': report_info.get('quarter'),
                                    'language': report_info.get('language', 'fr'),
                                    'source': 'company_ir',
                                    'scraped_at': datetime.now().isoformat()
                                }
                                
                                reports.append(report)
                
                logger.info(f"Found {len(reports)} reports for {ticker}")
                return reports
                
        except Exception as e:
            logger.error(f"Error scraping IR page for {ticker}: {e}")
            return []
    
    def analyze_report_link(self, text: str, url: str) -> Optional[Dict]:
        """Analyze a report link to determine type, year, and quarter"""
        try:
            text_lower = text.lower()
            url_lower = url.lower()
            
            # Determine report type
            report_type = 'other'
            if any(keyword in text_lower for keyword in ['annual', 'annuel', 'rapport annuel']):
                report_type = 'annual'
            elif any(keyword in text_lower for keyword in ['quarterly', 'trimestriel', 'trimestre']):
                report_type = 'quarterly'
            elif any(keyword in text_lower for keyword in ['semester', 'semestriel', 'semestre']):
                report_type = 'semi_annual'
            elif any(keyword in text_lower for keyword in ['financial', 'financier', 'compte']):
                report_type = 'financial'
            
            # Extract year
            year_match = re.search(r'20\d{2}', text + ' ' + url)
            year = int(year_match.group()) if year_match else datetime.now().year
            
            # Extract quarter (if applicable)
            quarter = None
            if report_type in ['quarterly', 'trimestriel']:
                q_match = re.search(r'Q([1-4])|T([1-4])|trimestre\s*([1-4])', text_lower)
                if q_match:
                    quarter = int(q_match.group(1) or q_match.group(2) or q_match.group(3))
            
            # Determine language
            language = 'fr'  # Default to French
            if any(keyword in text_lower for keyword in ['english', 'en', 'anglais']):
                language = 'en'
            elif any(keyword in text_lower for keyword in ['arabic', 'ar', 'arabe']):
                language = 'ar'
            
            return {
                'type': report_type,
                'year': year,
                'quarter': quarter,
                'language': language
            }
            
        except Exception as e:
            logger.warning(f"Error analyzing report link: {e}")
            return None
    
    async def scrape_ammc_reports(self) -> List[Dict]:
        """Scrape financial reports from AMMC website"""
        try:
            logger.info("Scraping AMMC reports...")
            
            ammc_url = self.regulatory_sources['ammc']['reports_url']
            
            async with self.session.get(ammc_url) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch AMMC reports: {response.status}")
                    return []
                
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                reports = []
                
                # Look for publication links
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    
                    if href and text:
                        # Check if it's a financial report
                        if any(keyword in text.lower() for keyword in ['rapport', 'compte', 'financier', 'annual', 'quarterly']):
                            report_info = self.analyze_report_link(text, href)
                            
                            if report_info:
                                full_url = urllib.parse.urljoin(self.regulatory_sources['ammc']['url'], href)
                                
                                report = {
                                    'ticker': 'AMMC',  # Regulatory body
                                    'company_name': 'AMMC Publications',
                                    'title': text,
                                    'url': full_url,
                                    'report_type': report_info['type'],
                                    'year': report_info['year'],
                                    'quarter': report_info.get('quarter'),
                                    'language': report_info.get('language', 'fr'),
                                    'source': 'ammc',
                                    'scraped_at': datetime.now().isoformat()
                                }
                                
                                reports.append(report)
                
                logger.info(f"Found {len(reports)} AMMC reports")
                return reports
                
        except Exception as e:
            logger.error(f"Error scraping AMMC reports: {e}")
            return []
    
    async def scrape_bourse_publications(self) -> List[Dict]:
        """Scrape financial reports from Bourse de Casablanca"""
        try:
            logger.info("Scraping Bourse de Casablanca publications...")
            
            bourse_url = self.regulatory_sources['bourse']['reports_url']
            
            async with self.session.get(bourse_url) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch Bourse publications: {response.status}")
                    return []
                
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                reports = []
                
                # Look for publication links
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    
                    if href and text:
                        # Check if it's a financial report
                        if any(keyword in text.lower() for keyword in ['rapport', 'compte', 'financier', 'annual', 'quarterly', 'publication']):
                            report_info = self.analyze_report_link(text, href)
                            
                            if report_info:
                                full_url = urllib.parse.urljoin(self.regulatory_sources['bourse']['url'], href)
                                
                                report = {
                                    'ticker': 'BSE',  # Bourse de Casablanca
                                    'company_name': 'Bourse de Casablanca Publications',
                                    'title': text,
                                    'url': full_url,
                                    'report_type': report_info['type'],
                                    'year': report_info['year'],
                                    'quarter': report_info.get('quarter'),
                                    'language': report_info.get('language', 'fr'),
                                    'source': 'bourse',
                                    'scraped_at': datetime.now().isoformat()
                                }
                                
                                reports.append(report)
                
                logger.info(f"Found {len(reports)} Bourse publications")
                return reports
                
        except Exception as e:
            logger.error(f"Error scraping Bourse publications: {e}")
            return []
    
    async def scrape_all_financial_reports(self) -> Dict:
        """Scrape financial reports from all sources"""
        try:
            logger.info("Starting comprehensive financial reports scraping...")
            
            all_reports = []
            
            # Scrape company IR pages
            logger.info("Scraping company IR pages...")
            for ticker, company_info in self.company_ir_pages.items():
                try:
                    reports = await self.scrape_company_ir_page(ticker, company_info)
                    all_reports.extend(reports)
                    await asyncio.sleep(2)  # Be respectful
                except Exception as e:
                    logger.error(f"Error scraping {ticker}: {e}")
                    continue
            
            # Scrape regulatory sources
            logger.info("Scraping regulatory sources...")
            
            # AMMC reports
            try:
                ammc_reports = await self.scrape_ammc_reports()
                all_reports.extend(ammc_reports)
            except Exception as e:
                logger.error(f"Error scraping AMMC: {e}")
            
            # Bourse publications
            try:
                bourse_reports = await self.scrape_bourse_publications()
                all_reports.extend(bourse_reports)
            except Exception as e:
                logger.error(f"Error scraping Bourse: {e}")
            
            # Save data
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.output_dir / f"financial_reports_{timestamp}.json"
            
            result = {
                'success': True,
                'data': all_reports,
                'count': len(all_reports),
                'timestamp': datetime.now().isoformat(),
                'output_file': str(output_file),
                'summary': {
                    'by_source': {},
                    'by_type': {},
                    'by_year': {}
                }
            }
            
            # Generate summary statistics
            for report in all_reports:
                # By source
                source = report['source']
                result['summary']['by_source'][source] = result['summary']['by_source'].get(source, 0) + 1
                
                # By type
                report_type = report['report_type']
                result['summary']['by_type'][report_type] = result['summary']['by_type'].get(report_type, 0) + 1
                
                # By year
                year = report['year']
                result['summary']['by_year'][year] = result['summary']['by_year'].get(year, 0) + 1
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully scraped {len(all_reports)} financial reports")
            logger.info(f"Data saved to: {output_file}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in comprehensive financial reports scraping: {e}")
            return {'success': False, 'error': str(e)}

async def main():
    """Main function to run the scraper"""
    print("🔄 Starting Financial Reports Scraper")
    print("=" * 60)
    
    async with FinancialReportsScraper() as scraper:
        # Scrape all financial reports
        result = await scraper.scrape_all_financial_reports()
        
        if result['success']:
            print(f"✅ Successfully scraped {result['count']} financial reports")
            print(f"📁 Data saved to: {result['output_file']}")
            
            # Show summary
            print("\n📊 Scraping Summary:")
            print("-" * 40)
            
            print("By Source:")
            for source, count in result['summary']['by_source'].items():
                print(f"  {source}: {count} reports")
            
            print("\nBy Type:")
            for report_type, count in result['summary']['by_type'].items():
                print(f"  {report_type}: {count} reports")
            
            print("\nBy Year:")
            for year, count in sorted(result['summary']['by_year'].items(), reverse=True):
                print(f"  {year}: {count} reports")
            
            # Show sample reports
            if result['data']:
                print("\n📋 Sample Reports:")
                print("-" * 40)
                for i, report in enumerate(result['data'][:5]):
                    print(f"{i+1}. {report['ticker']} - {report['title']}")
                    print(f"   Type: {report['report_type']}, Year: {report['year']}")
                    print(f"   Source: {report['source']}")
        else:
            print(f"❌ Scraping failed: {result.get('error', 'Unknown error')}")
    
    print("\n✅ Financial reports scraping completed")

if __name__ == "__main__":
    asyncio.run(main()) 