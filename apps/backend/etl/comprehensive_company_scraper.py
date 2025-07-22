"""
Comprehensive Company Website Scraper

This module automatically discovers and scrapes all 78 companies' websites
to find their annual reports, financial statements, and other IR documents.
"""

import asyncio
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
import re
from datetime import datetime
import logging
from urllib.parse import urljoin, urlparse, parse_qs
import json
import time
from dataclasses import dataclass
from enum import Enum

from storage.local_fs import LocalFileStorage
from models.financials import ETLJob, JobType, JobStatus

logger = logging.getLogger(__name__)

class ReportType(Enum):
    ANNUAL_REPORT = "annual_report"
    QUARTERLY_REPORT = "quarterly_report"
    FINANCIAL_STATEMENTS = "financial_statements"
    PRESENTATION = "presentation"
    PROSPECTUS = "prospectus"
    OTHER = "other"

@dataclass
class CompanyWebsite:
    ticker: str
    name: str
    base_url: str
    ir_url: Optional[str] = None
    investor_relations_url: Optional[str] = None
    financial_reports_url: Optional[str] = None
    annual_reports_url: Optional[str] = None
    quarterly_reports_url: Optional[str] = None
    language: str = "fr"  # Default to French for Moroccan companies

@dataclass
class DiscoveredReport:
    company: str
    title: str
    url: str
    report_type: ReportType
    year: Optional[int] = None
    quarter: Optional[int] = None
    language: str = "fr"
    file_size: Optional[int] = None
    discovered_at: datetime = None
    
    def __post_init__(self):
        if self.discovered_at is None:
            self.discovered_at = datetime.now()

class ComprehensiveCompanyScraper:
    """Comprehensive scraper for all 78 companies' websites"""
    
    def __init__(self, storage: LocalFileStorage):
        self.storage = storage
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Common IR page patterns for Moroccan companies
        self.ir_page_patterns = [
            "/investisseurs",
            "/investors", 
            "/relations-investisseurs",
            "/investor-relations",
            "/informations-financieres",
            "/financial-information",
            "/resultats-financiers",
            "/financial-results",
            "/rapports-annuels",
            "/annual-reports",
            "/documents-financiers",
            "/financial-documents"
        ]
        
        # Common report file patterns
        self.report_patterns = {
            ReportType.ANNUAL_REPORT: [
                r"rapport.*annuel.*(\d{4})",
                r"annual.*report.*(\d{4})",
                r"comptes.*annuels.*(\d{4})",
                r"annual.*accounts.*(\d{4})",
                r"exercice.*(\d{4})",
                r"year.*(\d{4})"
            ],
            ReportType.QUARTERLY_REPORT: [
                r"trimestre.*(\d{4})",
                r"quarter.*(\d{4})",
                r"q[1-4].*(\d{4})",
                r"t[1-4].*(\d{4})"
            ],
            ReportType.FINANCIAL_STATEMENTS: [
                r"etats.*financiers.*(\d{4})",
                r"financial.*statements.*(\d{4})",
                r"comptes.*(\d{4})",
                r"accounts.*(\d{4})"
            ]
        }
        
        # File extensions to look for
        self.document_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx']
        
        # Initialize company websites database
        self.company_websites = self._initialize_company_websites()
    
    def _initialize_company_websites(self) -> Dict[str, CompanyWebsite]:
        """Initialize the database of company websites"""
        return {
            # Banking Sector
            "ATW": CompanyWebsite(
                ticker="ATW",
                name="Attijariwafa Bank",
                base_url="https://www.attijariwafabank.com",
                ir_url="https://ir.attijariwafabank.com"
            ),
            "BCP": CompanyWebsite(
                ticker="BCP", 
                name="Banque Centrale Populaire",
                base_url="https://www.bcp.ma"
            ),
            "BMCE": CompanyWebsite(
                ticker="BMCE",
                name="BMCE Bank of Africa", 
                base_url="https://www.bmcebankofafrica.com"
            ),
            "CIH": CompanyWebsite(
                ticker="CIH",
                name="CIH Bank",
                base_url="https://www.cih.ma"
            ),
            
            # Telecommunications
            "IAM": CompanyWebsite(
                ticker="IAM",
                name="Maroc Telecom",
                base_url="https://www.iam.ma"
            ),
            
            # Energy
            "GAZ": CompanyWebsite(
                ticker="GAZ",
                name="Afriquia Gaz",
                base_url="https://www.afriquia-gaz.ma"
            ),
            "TMA": CompanyWebsite(
                ticker="TMA",
                name="Taqa Morocco",
                base_url="https://www.taqamorocco.ma"
            ),
            
            # Materials
            "CMT": CompanyWebsite(
                ticker="CMT",
                name="Ciments du Maroc",
                base_url="https://www.cimentsdumaroc.com"
            ),
            "LAFA": CompanyWebsite(
                ticker="LAFA",
                name="Lafarge Ciments",
                base_url="https://www.lafargeholcim.ma"
            ),
            "MNG": CompanyWebsite(
                ticker="MNG",
                name="Managem",
                base_url="https://www.managemgroup.com"
            ),
            
            # Insurance
            "AMA": CompanyWebsite(
                ticker="AMA",
                name="Alliance Marocaine de l'Assurance",
                base_url="https://www.ama.ma"
            ),
            "WAA": CompanyWebsite(
                ticker="WAA",
                name="Wafa Assurance",
                base_url="https://www.wafaassurance.ma"
            ),
            
            # Real Estate
            "RISM": CompanyWebsite(
                ticker="RISM",
                name="Risma",
                base_url="https://www.risma.ma"
            ),
            "ADH": CompanyWebsite(
                ticker="ADH",
                name="Addoha",
                base_url="https://www.addoha.ma"
            ),
            
            # Distribution
            "LBV": CompanyWebsite(
                ticker="LBV",
                name="Label'Vie",
                base_url="https://www.labelvie.ma"
            ),
            
            # Add more companies as needed...
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def discover_all_companies(self) -> List[CompanyWebsite]:
        """Discover IR pages for all companies"""
        discovered_companies = []
        
        for ticker, company in self.company_websites.items():
            try:
                logger.info(f"Discovering IR pages for {ticker} ({company.name})")
                discovered_company = await self._discover_company_ir_pages(company)
                discovered_companies.append(discovered_company)
                
                # Be respectful with rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error discovering {ticker}: {e}")
                discovered_companies.append(company)  # Add original company data
        
        return discovered_companies
    
    async def _discover_company_ir_pages(self, company: CompanyWebsite) -> CompanyWebsite:
        """Discover IR pages for a specific company"""
        try:
            # Try to find IR pages by checking common patterns
            base_url = company.base_url
            
            # Check if base URL is accessible
            if not await self._is_url_accessible(base_url):
                logger.warning(f"Base URL not accessible for {company.ticker}: {base_url}")
                return company
            
            # Try to find IR pages
            ir_urls = await self._find_ir_pages(base_url)
            
            if ir_urls:
                # Update company with discovered URLs
                company.ir_url = ir_urls.get('ir')
                company.investor_relations_url = ir_urls.get('investor_relations')
                company.financial_reports_url = ir_urls.get('financial_reports')
                company.annual_reports_url = ir_urls.get('annual_reports')
                company.quarterly_reports_url = ir_urls.get('quarterly_reports')
                
                logger.info(f"Discovered IR pages for {company.ticker}: {ir_urls}")
            
            return company
            
        except Exception as e:
            logger.error(f"Error discovering IR pages for {company.ticker}: {e}")
            return company
    
    async def _find_ir_pages(self, base_url: str) -> Dict[str, str]:
        """Find IR pages by checking common patterns"""
        ir_urls = {}
        
        try:
            # Get the main page
            async with self.session.get(base_url) as response:
                if response.status != 200:
                    return ir_urls
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find all links
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link.get('href', '').lower()
                    text = link.get_text().lower()
                    
                    # Check for IR page patterns
                    for pattern in self.ir_page_patterns:
                        if pattern in href or pattern in text:
                            full_url = urljoin(base_url, link['href'])
                            
                            if 'investisseurs' in href or 'investors' in href:
                                ir_urls['ir'] = full_url
                            elif 'financier' in href or 'financial' in href:
                                ir_urls['financial_reports'] = full_url
                            elif 'annuel' in href or 'annual' in href:
                                ir_urls['annual_reports'] = full_url
                            elif 'trimestre' in href or 'quarter' in href:
                                ir_urls['quarterly_reports'] = full_url
                
        except Exception as e:
            logger.error(f"Error finding IR pages for {base_url}: {e}")
        
        return ir_urls
    
    async def _is_url_accessible(self, url: str) -> bool:
        """Check if a URL is accessible"""
        try:
            async with self.session.head(url, allow_redirects=True) as response:
                return response.status == 200
        except:
            return False
    
    async def scrape_all_companies_reports(self, companies: Optional[List[str]] = None, 
                                         year: Optional[int] = None) -> List[DiscoveredReport]:
        """Scrape reports from all companies"""
        all_reports = []
        
        target_companies = companies or list(self.company_websites.keys())
        
        for ticker in target_companies:
            if ticker not in self.company_websites:
                logger.warning(f"Company {ticker} not found in database")
                continue
            
            try:
                logger.info(f"Scraping reports for {ticker}")
                company_reports = await self._scrape_company_reports(
                    self.company_websites[ticker], year
                )
                all_reports.extend(company_reports)
                
                # Rate limiting
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error scraping reports for {ticker}: {e}")
        
        return all_reports
    
    async def _scrape_company_reports(self, company: CompanyWebsite, 
                                    year: Optional[int] = None) -> List[DiscoveredReport]:
        """Scrape reports from a specific company"""
        reports = []
        
        # Try different IR URLs
        ir_urls = [
            company.ir_url,
            company.investor_relations_url,
            company.financial_reports_url,
            company.annual_reports_url,
            company.quarterly_reports_url
        ]
        
        for ir_url in ir_urls:
            if not ir_url:
                continue
            
            try:
                company_reports = await self._scrape_reports_from_url(ir_url, company, year)
                reports.extend(company_reports)
                
            except Exception as e:
                logger.error(f"Error scraping from {ir_url}: {e}")
        
        return reports
    
    async def _scrape_reports_from_url(self, url: str, company: CompanyWebsite, 
                                     year: Optional[int] = None) -> List[DiscoveredReport]:
        """Scrape reports from a specific URL"""
        reports = []
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return reports
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find all links
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link.get('href', '')
                    text = link.get_text().strip()
                    
                    # Check if it's a document link
                    if self._is_document_link(href):
                        report = await self._process_document_link(
                            link, url, company, year
                        )
                        if report:
                            reports.append(report)
                
                # Also check for embedded PDFs or iframes
                embedded_reports = await self._find_embedded_documents(soup, url, company, year)
                reports.extend(embedded_reports)
                
        except Exception as e:
            logger.error(f"Error scraping from {url}: {e}")
        
        return reports
    
    def _is_document_link(self, href: str) -> bool:
        """Check if a link points to a document"""
        href_lower = href.lower()
        
        # Check for document extensions
        for ext in self.document_extensions:
            if ext in href_lower:
                return True
        
        # Check for common document patterns
        document_patterns = [
            'pdf', 'doc', 'xls', 'download', 'telecharger',
            'rapport', 'report', 'comptes', 'accounts'
        ]
        
        return any(pattern in href_lower for pattern in document_patterns)
    
    async def _process_document_link(self, link_element, base_url: str, 
                                   company: CompanyWebsite, year: Optional[int] = None) -> Optional[DiscoveredReport]:
        """Process a document link and extract report information"""
        try:
            href = link_element.get('href', '')
            text = link_element.get_text().strip()
            
            # Build full URL
            full_url = urljoin(base_url, href)
            
            # Determine report type
            report_type = self._classify_report_type(text, href)
            
            # Extract year and quarter
            extracted_year, quarter = self._extract_year_and_quarter(text, href)
            
            # Use provided year if not found in text
            if year and not extracted_year:
                extracted_year = year
            
            # Get file size if possible
            file_size = await self._get_file_size(full_url)
            
            return DiscoveredReport(
                company=company.ticker,
                title=text or f"Report for {company.ticker}",
                url=full_url,
                report_type=report_type,
                year=extracted_year,
                quarter=quarter,
                language=company.language,
                file_size=file_size
            )
            
        except Exception as e:
            logger.error(f"Error processing document link: {e}")
            return None
    
    def _classify_report_type(self, text: str, href: str) -> ReportType:
        """Classify the type of report based on text and URL"""
        text_lower = text.lower()
        href_lower = href.lower()
        
        # Annual report patterns
        annual_patterns = ['rapport annuel', 'annual report', 'comptes annuels', 'annual accounts']
        if any(pattern in text_lower for pattern in annual_patterns):
            return ReportType.ANNUAL_REPORT
        
        # Quarterly report patterns
        quarterly_patterns = ['trimestre', 'quarter', 'q1', 'q2', 'q3', 'q4', 't1', 't2', 't3', 't4']
        if any(pattern in text_lower for pattern in quarterly_patterns):
            return ReportType.QUARTERLY_REPORT
        
        # Financial statements patterns
        financial_patterns = ['etats financiers', 'financial statements', 'comptes', 'accounts']
        if any(pattern in text_lower for pattern in financial_patterns):
            return ReportType.FINANCIAL_STATEMENTS
        
        # Presentation patterns
        presentation_patterns = ['presentation', 'présentation', 'slide']
        if any(pattern in text_lower for pattern in presentation_patterns):
            return ReportType.PRESENTATION
        
        # Default to other
        return ReportType.OTHER
    
    def _extract_year_and_quarter(self, text: str, href: str) -> Tuple[Optional[int], Optional[int]]:
        """Extract year and quarter from text and URL"""
        year = None
        quarter = None
        
        # Look for year patterns
        year_patterns = [
            r'(\d{4})',  # Basic 4-digit year
            r'20(\d{2})',  # 20xx format
        ]
        
        for pattern in year_patterns:
            matches = re.findall(pattern, text + ' ' + href)
            if matches:
                year = int(matches[0]) if len(matches[0]) == 4 else int('20' + matches[0])
                break
        
        # Look for quarter patterns
        quarter_patterns = [
            r'q(\d)',  # Q1, Q2, etc.
            r't(\d)',  # T1, T2, etc.
            r'(\d)er?\s*trimestre',  # 1er trimestre, etc.
            r'(\d)(st|nd|rd|th)\s*quarter'  # 1st quarter, etc.
        ]
        
        for pattern in quarter_patterns:
            matches = re.findall(pattern, text + ' ' + href, re.IGNORECASE)
            if matches:
                quarter = int(matches[0][0] if isinstance(matches[0], tuple) else matches[0])
                break
        
        return year, quarter
    
    async def _get_file_size(self, url: str) -> Optional[int]:
        """Get file size from URL"""
        try:
            async with self.session.head(url) as response:
                if response.status == 200:
                    return int(response.headers.get('content-length', 0))
        except:
            pass
        return None
    
    async def _find_embedded_documents(self, soup: BeautifulSoup, base_url: str, 
                                     company: CompanyWebsite, year: Optional[int] = None) -> List[DiscoveredReport]:
        """Find embedded documents (PDFs in iframes, etc.)"""
        reports = []
        
        # Look for iframes with PDFs
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src', '')
            if '.pdf' in src.lower():
                full_url = urljoin(base_url, src)
                report = DiscoveredReport(
                    company=company.ticker,
                    title=f"Embedded PDF for {company.ticker}",
                    url=full_url,
                    report_type=ReportType.OTHER,
                    year=year,
                    language=company.language
                )
                reports.append(report)
        
        return reports
    
    async def download_reports(self, reports: List[DiscoveredReport], 
                             output_dir: str = "/tmp/company_reports") -> List[str]:
        """Download discovered reports"""
        downloaded_files = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for report in reports:
            try:
                filename = self._generate_filename(report)
                filepath = output_path / filename
                
                logger.info(f"Downloading {report.title} to {filepath}")
                
                async with self.session.get(report.url) as response:
                    if response.status == 200:
                        async with aiofiles.open(filepath, 'wb') as f:
                            await f.write(await response.read())
                        
                        downloaded_files.append(str(filepath))
                        logger.info(f"Successfully downloaded {filename}")
                    else:
                        logger.warning(f"Failed to download {report.url}: {response.status}")
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error downloading {report.url}: {e}")
        
        return downloaded_files
    
    def _generate_filename(self, report: DiscoveredReport) -> str:
        """Generate filename for downloaded report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Clean title for filename
        clean_title = re.sub(r'[^\w\s-]', '', report.title)
        clean_title = re.sub(r'[-\s]+', '_', clean_title)
        
        filename_parts = [
            report.company,
            clean_title[:50],  # Limit title length
            str(report.year) if report.year else "unknown_year",
            f"Q{report.quarter}" if report.quarter else "",
            timestamp
        ]
        
        filename = "_".join(filter(None, filename_parts)) + ".pdf"
        return filename
    
    async def save_discovery_results(self, companies: List[CompanyWebsite], 
                                   reports: List[DiscoveredReport], 
                                   output_file: str = "/tmp/company_discovery_results.json"):
        """Save discovery results to JSON file"""
        try:
            results = {
                "discovery_date": datetime.now().isoformat(),
                "companies_discovered": len(companies),
                "reports_discovered": len(reports),
                "companies": [
                    {
                        "ticker": c.ticker,
                        "name": c.name,
                        "base_url": c.base_url,
                        "ir_url": c.ir_url,
                        "investor_relations_url": c.investor_relations_url,
                        "financial_reports_url": c.financial_reports_url,
                        "annual_reports_url": c.annual_reports_url,
                        "quarterly_reports_url": c.quarterly_reports_url,
                        "language": c.language
                    }
                    for c in companies
                ],
                "reports": [
                    {
                        "company": r.company,
                        "title": r.title,
                        "url": r.url,
                        "report_type": r.report_type.value,
                        "year": r.year,
                        "quarter": r.quarter,
                        "language": r.language,
                        "file_size": r.file_size,
                        "discovered_at": r.discovered_at.isoformat()
                    }
                    for r in reports
                ]
            }
            
            async with aiofiles.open(output_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(results, indent=2, ensure_ascii=False))
            
            logger.info(f"Discovery results saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving discovery results: {e}")

async def main():
    """Main function to run the comprehensive scraper"""
    storage = LocalFileStorage()
    
    async with ComprehensiveCompanyScraper(storage) as scraper:
        logger.info("Starting comprehensive company website discovery...")
        
        # Discover IR pages for all companies
        discovered_companies = await scraper.discover_all_companies()
        logger.info(f"Discovered IR pages for {len(discovered_companies)} companies")
        
        # Scrape reports from all companies
        all_reports = await scraper.scrape_all_companies_reports()
        logger.info(f"Discovered {len(all_reports)} reports")
        
        # Download reports
        downloaded_files = await scraper.download_reports(all_reports)
        logger.info(f"Downloaded {len(downloaded_files)} files")
        
        # Save discovery results
        await scraper.save_discovery_results(discovered_companies, all_reports)
        
        logger.info("Comprehensive scraping completed!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main()) 