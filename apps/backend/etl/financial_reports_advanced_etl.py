#!/usr/bin/env python3
"""
Advanced Financial Reports ETL Pipeline
Handles all 78 Casablanca Stock Exchange companies with continuous processing
"""

import asyncio
import aiohttp
import logging
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import aiofiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import hashlib
import time

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from database.connection import get_db_session
from models.company import ReportType, ReportData

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('financial_reports_etl.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ETLConfig:
    """ETL Configuration"""
    batch_size: int = 10
    max_concurrent_requests: int = 5
    retry_attempts: int = 3
    retry_delay: int = 5
    timeout: int = 30
    progress_file: str = "etl_progress.json"
    checkpoint_interval: int = 50

@dataclass
class CompanyInfo:
    """Company information for ETL processing"""
    ticker: str
    name: str
    sector: str
    ir_website: Optional[str] = None
    last_report_date: Optional[datetime] = None
    status: str = "pending"  # pending, processing, completed, failed

class AdvancedFinancialReportsETL:
    """Advanced ETL pipeline for financial reports"""
    
    def __init__(self, config: ETLConfig):
        self.config = config
        self.session = None
        self.progress = self._load_progress()
        self.companies = self._get_all_companies()
        self.semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        
    def _load_progress(self) -> Dict[str, Any]:
        """Load ETL progress from file"""
        try:
            if os.path.exists(self.config.progress_file):
                with open(self.config.progress_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load progress file: {e}")
        
        return {
            "started_at": datetime.now().isoformat(),
            "total_companies": 0,
            "processed_companies": 0,
            "failed_companies": 0,
            "total_reports": 0,
            "last_checkpoint": None,
            "company_status": {}
        }
    
    def _save_progress(self):
        """Save ETL progress to file"""
        try:
            self.progress["last_updated"] = datetime.now().isoformat()
            with open(self.config.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save progress: {e}")
    
    async def _get_all_companies(self) -> List[CompanyInfo]:
        """Get all 78 companies from database"""
        async with get_db_session() as session:
            result = await session.execute(
                text("SELECT ticker, name, sector FROM companies WHERE is_active = TRUE ORDER BY ticker")
            )
            companies = []
            for row in result.fetchall():
                companies.append(CompanyInfo(
                    ticker=row.ticker,
                    name=row.name,
                    sector=row.sector
                ))
            return companies
    
    async def run_etl_pipeline(self):
        """Main ETL pipeline execution"""
        logger.info(f"🚀 Starting Advanced Financial Reports ETL for {len(self.companies)} companies")
        
        start_time = time.time()
        self.progress["total_companies"] = len(self.companies)
        self.progress["started_at"] = datetime.now().isoformat()
        
        try:
            # Process companies in batches
            for i in range(0, len(self.companies), self.config.batch_size):
                batch = self.companies[i:i + self.config.batch_size]
                logger.info(f"Processing batch {i//self.config.batch_size + 1}: {[c.ticker for c in batch]}")
                
                # Process batch concurrently
                tasks = [self._process_company(company) for company in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Update progress
                for company, result in zip(batch, results):
                    if isinstance(result, Exception):
                        company.status = "failed"
                        self.progress["failed_companies"] += 1
                        logger.error(f"Failed to process {company.ticker}: {result}")
                    else:
                        company.status = "completed"
                        self.progress["processed_companies"] += 1
                        self.progress["total_reports"] += result.get("reports_found", 0)
                
                # Save checkpoint
                if (i + self.config.batch_size) % self.config.checkpoint_interval == 0:
                    self._save_progress()
                    logger.info(f"Checkpoint saved: {self.progress['processed_companies']}/{self.progress['total_companies']} companies processed")
            
            # Final progress save
            self._save_progress()
            
            # Generate final report
            await self._generate_etl_report(start_time)
            
        except Exception as e:
            logger.error(f"ETL pipeline failed: {e}")
            self.progress["status"] = "failed"
            self.progress["error"] = str(e)
            self._save_progress()
            raise
    
    async def _process_company(self, company: CompanyInfo) -> Dict[str, Any]:
        """Process a single company's financial reports"""
        async with self.semaphore:
            logger.info(f"Processing {company.ticker}: {company.name}")
            
            try:
                # Update company status
                company.status = "processing"
                self.progress["company_status"][company.ticker] = "processing"
                
                # Get company's IR website
                ir_website = await self._get_ir_website(company.ticker)
                if not ir_website:
                    logger.warning(f"No IR website found for {company.ticker}")
                    return {"reports_found": 0, "status": "no_website"}
                
                # Scrape financial reports
                reports = await self._scrape_financial_reports(company.ticker, ir_website)
                
                # Process and store reports
                processed_reports = await self._process_reports(company, reports)
                
                # Update company status
                company.status = "completed"
                self.progress["company_status"][company.ticker] = "completed"
                
                logger.info(f"✅ {company.ticker}: {len(processed_reports)} reports processed")
                return {
                    "reports_found": len(reports),
                    "processed_reports": len(processed_reports),
                    "status": "success"
                }
                
            except Exception as e:
                company.status = "failed"
                self.progress["company_status"][company.ticker] = "failed"
                logger.error(f"❌ {company.ticker}: {e}")
                raise
    
    async def _get_ir_website(self, ticker: str) -> Optional[str]:
        """Get company's IR website from database"""
        async with get_db_session() as session:
            result = await session.execute(
                text("SELECT ir_website FROM companies WHERE ticker = :ticker"),
                {"ticker": ticker}
            )
            row = result.fetchone()
            return row.ir_website if row else None
    
    async def _scrape_financial_reports(self, ticker: str, ir_website: str) -> List[Dict[str, Any]]:
        """Scrape financial reports from company's IR website"""
        reports = []
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.timeout)) as session:
                # Get the main IR page
                async with session.get(ir_website) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to access IR website for {ticker}: {response.status}")
                        return reports
                    
                    html_content = await response.text()
                    
                    # Extract report links (simplified - you'd implement proper scraping logic)
                    report_links = self._extract_report_links(html_content, ir_website)
                    
                    # Process each report link
                    for link in report_links:
                        report_info = await self._process_report_link(session, ticker, link)
                        if report_info:
                            reports.append(report_info)
                
        except Exception as e:
            logger.error(f"Error scraping reports for {ticker}: {e}")
        
        return reports
    
    def _extract_report_links(self, html_content: str, base_url: str) -> List[str]:
        """Extract financial report links from HTML content"""
        # This is a simplified implementation
        # In production, you'd use proper HTML parsing and company-specific logic
        
        import re
        
        # Common patterns for financial reports
        patterns = [
            r'href=["\']([^"\']*annual[^"\']*\.pdf)["\']',
            r'href=["\']([^"\']*quarterly[^"\']*\.pdf)["\']',
            r'href=["\']([^"\']*financial[^"\']*\.pdf)["\']',
            r'href=["\']([^"\']*report[^"\']*\.pdf)["\']',
        ]
        
        links = []
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if match.startswith('http'):
                    links.append(match)
                else:
                    links.append(f"{base_url.rstrip('/')}/{match.lstrip('/')}")
        
        return list(set(links))  # Remove duplicates
    
    async def _process_report_link(self, session: aiohttp.ClientSession, ticker: str, link: str) -> Optional[Dict[str, Any]]:
        """Process a single report link"""
        try:
            # Get report metadata
            async with session.head(link) as response:
                if response.status != 200:
                    return None
                
                content_type = response.headers.get('content-type', '')
                content_length = response.headers.get('content-length', 0)
                
                # Extract report type and date from URL/filename
                filename = link.split('/')[-1]
                report_type = self._determine_report_type(filename)
                report_date = self._extract_report_date(filename, link)
                
                # Generate report hash for deduplication
                report_hash = hashlib.md5(f"{ticker}_{link}".encode()).hexdigest()
                
                return {
                    "ticker": ticker,
                    "url": link,
                    "filename": filename,
                    "report_type": report_type,
                    "report_date": report_date,
                    "content_type": content_type,
                    "content_length": content_length,
                    "report_hash": report_hash,
                    "scraped_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error processing report link {link}: {e}")
            return None
    
    def _determine_report_type(self, filename: str) -> str:
        """Determine report type from filename"""
        filename_lower = filename.lower()
        
        if any(word in filename_lower for word in ['annual', 'annuel']):
            return ReportType.ANNUAL_REPORT
        elif any(word in filename_lower for word in ['quarterly', 'trimestriel']):
            return ReportType.QUARTERLY_REPORT
        elif any(word in filename_lower for word in ['interim', 'semestriel']):
            return ReportType.INTERIM_REPORT
        elif any(word in filename_lower for word in ['financial', 'financier']):
            return ReportType.FINANCIAL_STATEMENT
        else:
            return ReportType.OTHER
    
    def _extract_report_date(self, filename: str, url: str) -> Optional[datetime]:
        """Extract report date from filename or URL"""
        import re
        
        # Try to extract date from filename
        date_patterns = [
            r'(\d{4})[-_](\d{1,2})[-_](\d{1,2})',  # YYYY-MM-DD or YYYY_MM_DD
            r'(\d{1,2})[-_](\d{1,2})[-_](\d{4})',  # MM-DD-YYYY or MM_DD_YYYY
            r'(\d{4})(\d{2})(\d{2})',  # YYYYMMDD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                try:
                    if len(match.group(1)) == 4:  # YYYY-MM-DD format
                        return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
                    else:  # MM-DD-YYYY format
                        return datetime(int(match.group(3)), int(match.group(1)), int(match.group(2)))
                except ValueError:
                    continue
        
        # If no date found, use current date
        return datetime.now()
    
    async def _process_reports(self, company: CompanyInfo, reports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and store reports in database"""
        processed_reports = []
        
        async with get_db_session() as session:
            for report in reports:
                try:
                    # Check if report already exists
                    existing = await session.execute(
                        text("SELECT id FROM company_reports WHERE report_hash = :hash"),
                        {"hash": report["report_hash"]}
                    )
                    
                    if existing.fetchone():
                        logger.debug(f"Report already exists for {company.ticker}: {report['filename']}")
                        continue
                    
                    # Insert new report
                    result = await session.execute(
                        text("""
                            INSERT INTO company_reports 
                            (company_id, report_type, title, url, published_date, file_size, report_hash, created_at)
                            VALUES (
                                (SELECT id FROM companies WHERE ticker = :ticker),
                                :report_type,
                                :title,
                                :url,
                                :published_date,
                                :file_size,
                                :report_hash,
                                NOW()
                            ) RETURNING id
                        """),
                        {
                            "ticker": company.ticker,
                            "report_type": report["report_type"],
                            "title": report["filename"],
                            "url": report["url"],
                            "published_date": report["report_date"],
                            "file_size": report["content_length"],
                            "report_hash": report["report_hash"]
                        }
                    )
                    
                    report_id = result.fetchone().id
                    processed_reports.append({
                        "id": report_id,
                        "filename": report["filename"],
                        "report_type": report["report_type"]
                    })
                    
                    logger.debug(f"Stored report for {company.ticker}: {report['filename']}")
                    
                except Exception as e:
                    logger.error(f"Error storing report for {company.ticker}: {e}")
                    continue
            
            await session.commit()
        
        return processed_reports
    
    async def _generate_etl_report(self, start_time: float):
        """Generate ETL completion report"""
        end_time = time.time()
        duration = end_time - start_time
        
        report = {
            "etl_completion_report": {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": duration,
                "duration_formatted": str(timedelta(seconds=int(duration))),
                "total_companies": self.progress["total_companies"],
                "processed_companies": self.progress["processed_companies"],
                "failed_companies": self.progress["failed_companies"],
                "success_rate": (self.progress["processed_companies"] / self.progress["total_companies"]) * 100 if self.progress["total_companies"] > 0 else 0,
                "total_reports_found": self.progress["total_reports"],
                "companies_per_second": self.progress["processed_companies"] / duration if duration > 0 else 0,
                "company_status_summary": {
                    "completed": len([c for c in self.companies if c.status == "completed"]),
                    "failed": len([c for c in self.companies if c.status == "failed"]),
                    "pending": len([c for c in self.companies if c.status == "pending"])
                }
            }
        }
        
        # Save report
        report_file = f"etl_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 ETL Report generated: {report_file}")
        logger.info(f"✅ ETL completed in {duration:.2f} seconds")
        logger.info(f"📈 Success rate: {report['etl_completion_report']['success_rate']:.1f}%")
        logger.info(f"📄 Total reports found: {self.progress['total_reports']}")

async def main():
    """Main ETL execution function"""
    config = ETLConfig(
        batch_size=10,
        max_concurrent_requests=5,
        retry_attempts=3,
        retry_delay=5,
        timeout=30
    )
    
    etl = AdvancedFinancialReportsETL(config)
    
    try:
        await etl.run_etl_pipeline()
        logger.info("🎉 Advanced Financial Reports ETL completed successfully!")
    except Exception as e:
        logger.error(f"💥 ETL failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 