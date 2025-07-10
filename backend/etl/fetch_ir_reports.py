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
                "base_url": "https://www.attijariwafabank.com/fr/investisseurs",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date"
                }
            },
            "IAM": {
                "base_url": "https://www.iam.ma/fr/investisseurs",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date"
                }
            },
            "BCP": {
                "base_url": "https://www.banquecentralepopulaire.ma/fr/investisseurs",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date"
                }
            },
            "BMCE": {
                "base_url": "https://www.bmcebank.ma/fr/investisseurs",
                "selectors": {
                    "reports": "a[href*='.pdf']",
                    "title": "h1, h2, h3",
                    "date": ".date, .published-date"
                }
            }
        }
        
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
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
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
        if company not in self.company_ir_pages:
            logger.warning(f"No IR page configured for company: {company}")
            return []
        
        company_config = self.company_ir_pages[company]
        reports = []
        
        try:
            # Fetch the IR page
            async with self.session.get(company_config["base_url"]) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch IR page for {company}: {response.status}")
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find PDF links
                pdf_links = soup.select(company_config["selectors"]["reports"])
                
                for link in pdf_links:
                    href = link.get('href')
                    if not href:
                        continue
                    
                    # Make URL absolute
                    pdf_url = urljoin(company_config["base_url"], href)
                    
                    # Extract report info
                    report_info = await self._extract_report_info(link, pdf_url, company)
                    
                    if report_info and (year is None or report_info.get('year') == year):
                        reports.append(report_info)
        
        except Exception as e:
            logger.error(f"Error fetching reports for {company}: {e}")
        
        return reports
    
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