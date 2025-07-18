import asyncio
import aiohttp
import aiofiles
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Dict, Optional, Set
import re
from datetime import datetime
import logging
from urllib.parse import urljoin, urlparse

from storage.local_fs import LocalFileStorage
from models.financials import ETLJob, JobType, JobStatus

logger = logging.getLogger(__name__)

class IRReportFetcher:
    """Fetches financial reports from company IR pages"""
    
    def __init__(self, storage: LocalFileStorage):
        self.storage = storage
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Moroccan companies with their IR pages
        self.company_ir_pages = {
            "ATW": {
                "base_url": "https://ir.attijariwafabank.com/financial-information/financial-results",
                "selectors": {
                    "reports": "a[href*='.pdf'], a[href*='/static-files/']",
                    "title": "h1, h2, h3, td",
                    "date": ".date, .published-date, td"
                }
            },
            "IAM": {
                "base_url": "https://www.iam.ma/fr/investisseurs/informations-financieres",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date"
                }
            },
            "BCP": {
                "base_url": "https://www.bcp.ma/fr/investisseurs/informations-financieres",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date"
                }
            },
            "BMCE": {
                "base_url": "https://www.bmcebankofafrica.com/fr/investisseurs",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date"
                }
            },
            "CIH": {
                "base_url": "https://www.cih.ma/fr/investisseurs",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date"
                }
            },
            "WAA": {
                "base_url": "https://www.wafaassurance.ma/fr/investisseurs",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date"
                }
            },
            "LBV": {
                "base_url": "https://www.labelvie.ma/fr/investisseurs",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date"
                }
            },
            "TMA": {
                "base_url": "https://www.taqamorocco.ma/fr/investisseurs",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date"
                }
            },
            "ADH": {
                "base_url": "https://www.addoha.ma/fr/investisseurs",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date"
                }
            },
            "LES": {
                "base_url": "https://www.lesieurcristal.ma/fr/investisseurs",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date"
                }
            },
            "SOT": {
                "base_url": "https://www.sothema.ma/fr/investisseurs",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date"
                }
            },
            "CTM": {
                "base_url": "https://www.ctm.ma/fr/investisseurs",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date"
                }
            }
        }
        
        # Default URL template for companies not explicitly mapped
        self.default_ir_url_template = "https://www.{company_name}.ma/fr/investisseurs"
        
        # Report type patterns
        self.report_patterns = {
            "pnl": [
                r"compte.*resultat",
                r"resultat.*exploitation",
                r"pnl",
                r"profit.*loss",
                r"compte.*exploitation"
            ],
            "balance": [
                r"bilan",
                r"balance.*sheet",
                r"situation.*financiere",
                r"actif.*passif"
            ],
            "cashflow": [
                r"flux.*tresorerie",
                r"cash.*flow",
                r"tableau.*flux",
                r"variation.*tresorerie"
            ]
        }
    
    async def __aenter__(self):
        import ssl
        # Create SSL context that doesn't verify certificates (for development)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=connector,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_company_reports(self, company: str, year: Optional[int] = None) -> List[Dict]:
        """Fetch all available reports for a company"""
        company_config = self._get_company_config(company)
        if not company_config:
            logger.warning(f"No IR page configured for company: {company}")
            return []

        reports = []
        
        try:
            # Fetch the IR page
            async with self.session.get(company_config["base_url"]) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch IR page for {company}: {response.status}")
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract report links
                report_links = soup.select(company_config["selectors"]["reports"])
                
                for link in report_links:
                    href = link.get("href")
                    if not href or not isinstance(href, str):
                        continue
                        
                    # Convert relative URLs to absolute
                    if href.startswith("/"):
                        report_url = urljoin(company_config["base_url"], href)
                    elif href.startswith("http"):
                        report_url = href
                    else:
                        report_url = urljoin(company_config["base_url"], href)
                    
                    # Extract title and date
                    title = link.get_text(strip=True)
                    if not title:
                        # Try to find title in parent elements
                        parent = link.parent
                        if parent:
                            title = parent.get_text(strip=True)
                    
                    # Try to extract date from various selectors
                    date_text = None
                    parent_element = link.find_parent()
                    if parent_element:
                        try:
                            date_element = parent_element.find(class_="date")
                            if date_element:
                                date_text = date_element.get_text(strip=True)
                        except:
                            pass
                    
                    # Only include PDF reports
                    if report_url and isinstance(report_url, str) and (report_url.endswith('.pdf') or '/static-files/' in report_url):
                        reports.append({
                            "url": report_url,
                            "title": title or "Financial Report",
                            "date": date_text or "Unknown",
                            "company": company,
                            "type": "financial_report"
                        })
        
        except Exception as e:
            logger.error(f"Error fetching reports for {company}: {e}")
        
        return reports
    
    def _get_company_config(self, company: str) -> Optional[Dict]:
        """Get company IR page configuration with fallback to default template"""
        if company in self.company_ir_pages:
            return self.company_ir_pages[company]
        
        # Fallback to default template
        company_name_lower = company.lower()
        fallback_url = self.default_ir_url_template.format(company_name=company_name_lower)
        
        return {
            "base_url": fallback_url,
            "selectors": {
                "reports": "a[href*='.pdf']",
                "title": "h1, h2, h3",
                "date": ".date, .published-date"
            }
        }
    
    async def _extract_report_info(self, link_element, pdf_url: str, company: str) -> Optional[Dict]:
        """Extract report information from link element"""
        try:
            # Get link text and title
            link_text = link_element.get_text(strip=True)
            title = link_element.get('title', link_text)
            
            # Try to extract year from text
            year_match = re.search(r'20\d{2}', title + link_text)
            year = int(year_match.group()) if year_match else datetime.now().year
            
            # Determine report type
            report_type = self._classify_report_type(title + link_text)
            
            # Extract quarter if present
            quarter = self._extract_quarter(title + link_text)
            
            return {
                "company": company,
                "year": year,
                "quarter": quarter,
                "report_type": report_type,
                "title": title,
                "url": pdf_url,
                "filename": self._generate_filename(company, year, quarter, report_type)
            }
        
        except Exception as e:
            logger.error(f"Error extracting report info: {e}")
            return None
    
    def _classify_report_type(self, text: str) -> str:
        """Classify report type based on text content"""
        text_lower = text.lower()
        
        for report_type, patterns in self.report_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return report_type
        
        return "other"
    
    def _extract_quarter(self, text: str) -> Optional[int]:
        """Extract quarter number from text"""
        quarter_patterns = [
            r'T(\d)',  # T1, T2, T3, T4
            r'Q(\d)',  # Q1, Q2, Q3, Q4
            r'(\d)er.*trimestre',  # 1er trimestre
            r'(\d)ème.*trimestre',  # 2ème trimestre
            r'(\d)rd.*trimestre',   # 3rd trimestre
            r'(\d)th.*trimestre'    # 4th trimestre
        ]
        
        for pattern in quarter_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                quarter = int(match.group(1))
                if 1 <= quarter <= 4:
                    return quarter
        
        return None
    
    def _generate_filename(self, company: str, year: int, quarter: Optional[int], report_type: str) -> str:
        """Generate standardized filename"""
        filename = f"{company}_{year}"
        if quarter:
            filename += f"_Q{quarter}"
        filename += f"_{report_type}.pdf"
        return filename
    
    async def download_report(self, report_info: Dict) -> Optional[str]:
        """Download a single report"""
        try:
            async with self.session.get(report_info["url"]) as response:
                if response.status != 200:
                    logger.error(f"Failed to download {report_info['url']}: {response.status}")
                    return None
                
                content = await response.read()
                
                # Save to local storage
                file_path = await self.storage.save_pdf(
                    content=content,
                    filename=report_info["filename"],
                    company=report_info["company"],
                    year=report_info["year"]
                )
                
                logger.info(f"Downloaded {report_info['filename']} to {file_path}")
                return file_path
        
        except Exception as e:
            logger.error(f"Error downloading {report_info['url']}: {e}")
            return None
    
    async def fetch_all_reports(self, companies: Optional[List[str]] = None, year: Optional[int] = None) -> List[Dict]:
        """Fetch reports for all companies or specified companies"""
        if companies is None:
            companies = list(self.company_ir_pages.keys())
        
        all_reports = []
        
        async with self:
            for company in companies:
                logger.info(f"Fetching reports for {company}")
                company_reports = await self.fetch_company_reports(company, year)
                all_reports.extend(company_reports)
        
        return all_reports
    
    async def download_all_reports(self, reports: List[Dict]) -> List[str]:
        """Download all reports in the list"""
        downloaded_files = []
        
        async with self:
            for report in reports:
                file_path = await self.download_report(report)
                if file_path:
                    downloaded_files.append(file_path)
        
        return downloaded_files

# Example usage
async def main():
    """Example usage of the IR Report Fetcher"""
    storage = LocalFileStorage()
    
    async with IRReportFetcher(storage) as fetcher:
        # Fetch reports for ATW for 2024
        reports = await fetcher.fetch_company_reports("ATW", 2024)
        print(f"Found {len(reports)} reports for ATW")
        
        # Download all reports
        downloaded = await fetcher.download_all_reports(reports)
        print(f"Downloaded {len(downloaded)} files")

if __name__ == "__main__":
    asyncio.run(main()) 