#!/usr/bin/env python3
"""
Working Demo Pipeline for Casablanca Insights

This script demonstrates fetching real financial data from working IR websites.
"""

import asyncio
import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import sys
import aiohttp
import ssl
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# Add the backend directory to Python path
backend_path = Path(__file__).parent
sys.path.append(str(backend_path))

from storage.local_fs import LocalFileStorage

logger = logging.getLogger(__name__)

class WorkingIRFetcher:
    """Fetches real financial reports from working IR websites"""
    
    def __init__(self, storage: LocalFileStorage):
        self.storage = storage
        self.session = None
        
        # Working IR URLs discovered through research
        self.working_urls = {
            "ATW": {
                "name": "Attijariwafa Bank",
                "url": "https://ir.attijariwafabank.com/",
                "pdf_patterns": ["/static-files/", ".pdf"]
            },
            "IAM": {
                "name": "Maroc Telecom",
                "url": "https://www.marketscreener.com/quote/stock/ITISSALAT-AL-MAGHRIB-IAM--1408717/news/",
                "pdf_patterns": [".pdf"]
            }
        }
    
    async def __aenter__(self):
        """Setup async HTTP session with SSL handling"""
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=connector,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup session"""
        if self.session:
            await self.session.close()
    
    async def fetch_company_reports(self, company: str) -> List[Dict]:
        """Fetch financial reports for a specific company"""
        if company not in self.working_urls:
            logger.warning(f"No working URL configured for {company}")
            return []
        
        company_info = self.working_urls[company]
        reports = []
        
        try:
            logger.info(f"Fetching reports for {company_info['name']} from {company_info['url']}")
            
            async with self.session.get(company_info["url"]) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find all links that might be PDFs
                    all_links = soup.find_all('a', href=True)
                    
                    for link in all_links:
                        href = link.get('href')
                        if not href:
                            continue
                        
                        # Check if this looks like a financial report
                        if any(pattern in href for pattern in company_info["pdf_patterns"]):
                            # Make URL absolute
                            if href.startswith('/'):
                                full_url = urljoin(company_info["url"], href)
                            elif href.startswith('http'):
                                full_url = href
                            else:
                                full_url = urljoin(company_info["url"], href)
                            
                            # Extract title
                            title = link.get_text(strip=True)
                            if not title:
                                # Try parent element
                                parent = link.parent
                                if parent:
                                    title = parent.get_text(strip=True)
                            
                            # Extract date if possible
                            date_text = "Unknown"
                            # Look for date patterns in the text
                            text_content = link.get_text() + " " + (link.parent.get_text() if link.parent else "")
                            import re
                            date_match = re.search(r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|\d{4})', text_content)
                            if date_match:
                                date_text = date_match.group(1)
                            
                            reports.append({
                                "url": full_url,
                                "title": title or "Financial Report",
                                "date": date_text,
                                "company": company,
                                "type": "financial_report"
                            })
                            
                            logger.info(f"Found report: {title} - {full_url}")
                
                else:
                    logger.error(f"Failed to fetch {company_info['url']}: HTTP {response.status}")
                    
        except Exception as e:
            logger.error(f"Error fetching reports for {company}: {str(e)}")
        
        return reports
    
    async def download_report(self, report: Dict) -> Optional[str]:
        """Download a specific report"""
        try:
            logger.info(f"Downloading: {report['title']}")
            
            async with self.session.get(report["url"]) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Generate filename
                    filename = f"{report['company']}_{report['date']}_{report['title'][:50]}.pdf"
                    filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
                    
                    # Save to storage
                    file_path = await self.storage.save_raw_pdf(content, filename)
                    logger.info(f"Downloaded to: {file_path}")
                    return file_path
                else:
                    logger.error(f"Failed to download {report['url']}: HTTP {response.status}")
                    
        except Exception as e:
            logger.error(f"Error downloading report {report['url']}: {str(e)}")
        
        return None

class WorkingDemoPipeline:
    """Demo pipeline that fetches real data"""
    
    def __init__(self):
        self.storage = LocalFileStorage()
        self.results = {
            "companies_processed": 0,
            "reports_found": 0,
            "reports_downloaded": 0,
            "errors": []
        }
    
    async def run(self):
        """Run the complete pipeline"""
        logger.info("🚀 Starting Working Demo Pipeline")
        logger.info("=" * 50)
        
        try:
            async with WorkingIRFetcher(self.storage) as fetcher:
                # Process each company
                for company in fetcher.working_urls.keys():
                    logger.info(f"\n📊 Processing {company}...")
                    
                    try:
                        # Fetch reports
                        reports = await fetcher.fetch_company_reports(company)
                        self.results["reports_found"] += len(reports)
                        
                        logger.info(f"Found {len(reports)} reports for {company}")
                        
                        # Download first few reports (limit to avoid overwhelming)
                        for i, report in enumerate(reports[:3]):  # Limit to first 3
                            file_path = await fetcher.download_report(report)
                            if file_path:
                                self.results["reports_downloaded"] += 1
                        
                        self.results["companies_processed"] += 1
                        
                    except Exception as e:
                        error_msg = f"Error processing {company}: {str(e)}"
                        logger.error(error_msg)
                        self.results["errors"].append(error_msg)
        
        except Exception as e:
            error_msg = f"Pipeline error: {str(e)}"
            logger.error(error_msg)
            self.results["errors"].append(error_msg)
        
        # Report results
        self.report_results()
    
    def report_results(self):
        """Report pipeline results"""
        logger.info("\n" + "=" * 50)
        logger.info("📈 PIPELINE RESULTS")
        logger.info("=" * 50)
        logger.info(f"✅ Companies processed: {self.results['companies_processed']}")
        logger.info(f"📄 Reports found: {self.results['reports_found']}")
        logger.info(f"💾 Reports downloaded: {self.results['reports_downloaded']}")
        
        if self.results['errors']:
            logger.info(f"❌ Errors: {len(self.results['errors'])}")
            for error in self.results['errors']:
                logger.error(f"  - {error}")
        
        # Check downloaded files
        try:
            files = self.storage.list_files("raw_pdfs", "*.pdf")
            logger.info(f"📁 Files in storage: {len(files)}")
            for file in files[:5]:  # Show first 5
                logger.info(f"  - {file}")
        except Exception as e:
            logger.error(f"Error listing files: {e}")

async def main():
    """Main function"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    pipeline = WorkingDemoPipeline()
    await pipeline.run()

if __name__ == "__main__":
    asyncio.run(main()) 