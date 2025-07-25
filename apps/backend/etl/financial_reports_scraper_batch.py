#!/usr/bin/env python3
"""
Enhanced Financial Reports Scraper - Batch Processing

This scraper processes 78 companies in batches of 10, scraping their IR pages,
downloading the 2 latest PDF reports, and inserting metadata into Postgres.

Features:
- Batch processing (10 companies at a time)
- Asyncio + aiohttp for concurrency
- PDF download and metadata extraction
- Postgres integration
- Retry logic and error handling
"""

import asyncio
import aiohttp
import json
import logging
import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from bs4 import BeautifulSoup
import re
import time
import urllib.parse
import csv

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from supabase import create_client, Client
except ImportError:
    print("⚠️  Supabase client not available, will save to JSON only")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('financial_reports_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BatchFinancialReportsScraper:
    """Enhanced scraper for financial reports with batch processing"""
    
    def __init__(self, batch_size: int = 10, max_concurrent: int = 10):
        self.session = None
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent
        self.output_dir = Path("../data/financial_reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load company IR pages from JSON file first
        self.company_ir_pages = self.load_company_ir_pages()
        
        # Load companies from African Markets data
        self.companies = self.load_companies()
        
        # Supabase client
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if self.supabase_url and self.supabase_key:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            self.service_client = create_client(self.supabase_url, self.supabase_service_key)
            logger.info("✅ Supabase client initialized")
        else:
            self.supabase = None
            self.service_client = None
            logger.warning("⚠️  Supabase credentials not found, will save to JSON only")
        
        logger.info(f"✅ Batch Financial Reports Scraper initialized with {len(self.companies)} companies")
    
    def load_company_ir_pages(self) -> Dict:
        """Load company IR pages from JSON file"""
        try:
            ir_pages_file = "../data/company_ir_pages.json"
            
            if not os.path.exists(ir_pages_file):
                logger.error(f"❌ Company IR pages file not found: {ir_pages_file}")
                raise FileNotFoundError(f"Company IR pages file not found: {ir_pages_file}")
            
            with open(ir_pages_file, 'r', encoding='utf-8') as f:
                company_ir_pages = json.load(f)
            
            # Validate that each company has required fields
            missing_urls = []
            for ticker, info in company_ir_pages.items():
                if not info.get('ir_url'):
                    missing_urls.append(ticker)
            
            if missing_urls:
                logger.error(f"❌ Missing IR URLs for companies: {missing_urls}")
                raise ValueError(f"Missing IR URLs for companies: {missing_urls}")
            
            logger.info(f"✅ Loaded {len(company_ir_pages)} company IR pages from JSON")
            return company_ir_pages
            
        except Exception as e:
            logger.error(f"❌ Error loading company IR pages: {str(e)}")
            raise
    
    def load_companies(self) -> List[Dict]:
        """Load companies from African Markets data"""
        try:
            african_markets_file = "../data/cse_companies_african_markets.json"
            
            if not os.path.exists(african_markets_file):
                logger.warning(f"African Markets data not found: {african_markets_file}")
                return []
            
            with open(african_markets_file, 'r', encoding='utf-8') as f:
                companies_data = json.load(f)
            
            # Filter companies with tickers
            companies = []
            for company in companies_data:
                if company.get('ticker'):
                    ticker = company['ticker'].upper()
                    ir_info = self.company_ir_pages.get(ticker, {})
                    companies.append({
                        'ticker': ticker,
                        'name': company.get('name') or company.get('company_name', ''),
                        'sector': company.get('sector', ''),
                        'ir_url': ir_info.get('ir_url'),
                        'base_url': ir_info.get('base_url')
                    })
            
            logger.info(f"✅ Loaded {len(companies)} companies from African Markets data")
            return companies
            
        except Exception as e:
            logger.error(f"❌ Error loading companies: {str(e)}")
            return []
    
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=self.max_concurrent, limit_per_host=5)
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60),
            connector=connector,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def fetch_page(self, url: str, retries: int = 3) -> Optional[str]:
        """Fetch a web page with retry logic"""
        for attempt in range(retries):
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    elif response.status == 404:
                        logger.warning(f"Page not found: {url}")
                        return None
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        logger.error(f"❌ Failed to fetch {url} after {retries} attempts")
        return None
    
    async def download_pdf(self, url: str, filename: str) -> bool:
        """Download a PDF file"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Save PDF file
                    pdf_path = self.output_dir / filename
                    with open(pdf_path, 'wb') as f:
                        f.write(content)
                    
                    logger.info(f"✅ Downloaded PDF: {filename}")
                    return True
                else:
                    logger.warning(f"Failed to download PDF {url}: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error downloading PDF {url}: {str(e)}")
            return False
    
    def extract_report_metadata(self, text: str, url: str) -> Optional[Dict]:
        """Extract metadata from report text"""
        try:
            # Common patterns for financial reports
            patterns = {
                'annual_report': r'(annual|annuel|rapport annuel|annual report)',
                'quarterly_report': r'(quarterly|trimestriel|rapport trimestriel|quarterly report)',
                'financial_statement': r'(financial statement|état financier|comptes)',
                'earnings': r'(earnings|bénéfices|résultats)',
                'date': r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})',
                'year': r'(20\d{2})',
                'quarter': r'(Q[1-4]|T[1-4])'
            }
            
            metadata = {
                'url': url,
                'title': '',
                'type': 'unknown',
                'date': None,
                'year': None,
                'quarter': None
            }
            
            # Extract title from URL or text
            if 'annual' in text.lower() or 'annuel' in text.lower():
                metadata['type'] = 'annual_report'
            elif 'quarterly' in text.lower() or 'trimestriel' in text.lower():
                metadata['type'] = 'quarterly_report'
            elif 'financial' in text.lower() or 'financier' in text.lower():
                metadata['type'] = 'financial_statement'
            
            # Extract date
            date_match = re.search(patterns['date'], text)
            if date_match:
                metadata['date'] = date_match.group(1)
            
            # Extract year
            year_match = re.search(patterns['year'], text)
            if year_match:
                metadata['year'] = year_match.group(1)
            
            # Extract quarter
            quarter_match = re.search(patterns['quarter'], text)
            if quarter_match:
                metadata['quarter'] = quarter_match.group(1)
            
            # Generate title
            title_parts = []
            if metadata['type'] != 'unknown':
                title_parts.append(metadata['type'].replace('_', ' ').title())
            if metadata['year']:
                title_parts.append(metadata['year'])
            if metadata['quarter']:
                title_parts.append(metadata['quarter'])
            
            metadata['title'] = ' '.join(title_parts) if title_parts else 'Financial Report'
            
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Error extracting metadata: {str(e)}")
            return None
    
    async def scrape_company_reports(self, company: Dict) -> List[Dict]:
        """Scrape financial reports for a single company"""
        ticker = company['ticker']
        name = company['name']
        ir_url = company.get('ir_url')
        
        logger.info(f"📊 Scraping reports for {ticker} ({name})")
        
        if not ir_url:
            logger.warning(f"⚠️  No IR URL for {ticker}")
            return []
        
        try:
            # Fetch IR page
            html = await self.fetch_page(ir_url)
            if not html:
                return []
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find PDF links
            pdf_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').lower()
                text = link.get_text().lower()
                
                # Check for PDF links
                if ('.pdf' in href or 
                    'rapport' in text or 'report' in text or
                    'financier' in text or 'financial' in text or
                    'annuel' in text or 'annual' in text or
                    'trimestriel' in text or 'quarterly' in text):
                    
                    # Make URL absolute
                    if href.startswith('/'):
                        base_url = company.get('base_url', ir_url)
                        full_url = urllib.parse.urljoin(base_url, href)
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        full_url = urllib.parse.urljoin(ir_url, href)
                    
                    pdf_links.append({
                        'url': full_url,
                        'text': link.get_text().strip(),
                        'href': href
                    })
            
            # Sort by relevance and take the 2 latest
            pdf_links.sort(key=lambda x: (
                'annual' in x['text'].lower() or 'annuel' in x['text'].lower(),
                'quarterly' in x['text'].lower() or 'trimestriel' in x['text'].lower(),
                'financial' in x['text'].lower() or 'financier' in x['text'].lower()
            ), reverse=True)
            
            reports = []
            for i, pdf_link in enumerate(pdf_links[:2]):  # Take 2 latest
                try:
                    # Extract metadata
                    metadata = self.extract_report_metadata(pdf_link['text'], pdf_link['url'])
                    if not metadata:
                        continue
                    
                    # Generate filename
                    filename = f"{ticker}_{metadata['type']}_{metadata.get('year', 'unknown')}_{i+1}.pdf"
                    
                    # Download PDF
                    downloaded = await self.download_pdf(pdf_link['url'], filename)
                    
                    if downloaded:
                        report_data = {
                            'ticker': ticker,
                            'company_name': name,
                            'title': metadata['title'],
                            'type': metadata['type'],
                            'date': metadata['date'],
                            'year': metadata['year'],
                            'quarter': metadata['quarter'],
                            'url': pdf_link['url'],
                            'filename': filename,
                            'scraped_at': datetime.now().isoformat()
                        }
                        
                        reports.append(report_data)
                        logger.info(f"✅ Found report: {metadata['title']} for {ticker}")
                
                except Exception as e:
                    logger.error(f"❌ Error processing PDF link for {ticker}: {str(e)}")
                    continue
            
            return reports
            
        except Exception as e:
            logger.error(f"❌ Error scraping reports for {ticker}: {str(e)}")
            return []
    
    async def process_batch(self, companies_batch: List[Dict]) -> List[Dict]:
        """Process a batch of companies concurrently"""
        logger.info(f"🔄 Processing batch of {len(companies_batch)} companies")
        
        # Create tasks for concurrent processing
        tasks = [self.scrape_company_reports(company) for company in companies_batch]
        
        # Execute tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results and handle exceptions
        all_reports = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"❌ Exception in batch processing: {str(result)}")
            else:
                all_reports.extend(result)
        
        logger.info(f"✅ Batch completed: {len(all_reports)} reports found")
        return all_reports
    
    async def insert_reports_to_supabase(self, reports: List[Dict]) -> bool:
        """Insert reports metadata into Supabase"""
        if not self.service_client:
            logger.warning("⚠️  Supabase not configured, skipping database insertion")
            return False
        
        try:
            # Prepare data for insertion
            records = []
            for report in reports:
                records.append({
                    'ticker': report['ticker'],
                    'company_name': report['company_name'],
                    'title': report['title'],
                    'report_type': report['type'],
                    'report_date': report['date'],
                    'report_year': report['year'],
                    'report_quarter': report['quarter'],
                    'url': report['url'],
                    'filename': report['filename'],
                    'scraped_at': report['scraped_at']
                })
            
            # Insert in batches
            batch_size = 50
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                
                result = self.service_client.table('financial_reports').upsert(
                    batch,
                    on_conflict='ticker,url'
                ).execute()
                
                if hasattr(result, 'error') and result.error:
                    logger.error(f"❌ Error inserting batch: {result.error}")
                    return False
            
            logger.info(f"✅ Successfully inserted {len(records)} reports to Supabase")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inserting to Supabase: {str(e)}")
            return False
    
    def save_reports_to_json(self, reports: List[Dict], batch_num: int) -> str:
        """Save reports to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"financial_reports_batch_{batch_num}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(reports, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Saved {len(reports)} reports to {filename}")
        return str(filepath)
    
    def create_supabase_table(self) -> bool:
        """Create financial_reports table in Supabase"""
        if not self.service_client:
            return False
        
        try:
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS financial_reports (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(10) NOT NULL,
                company_name VARCHAR(255) NOT NULL,
                title VARCHAR(500) NOT NULL,
                report_type VARCHAR(50),
                report_date VARCHAR(50),
                report_year VARCHAR(4),
                report_quarter VARCHAR(10),
                url TEXT NOT NULL,
                filename VARCHAR(255),
                scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_financial_reports_ticker ON financial_reports(ticker);
            CREATE INDEX IF NOT EXISTS idx_financial_reports_type ON financial_reports(report_type);
            CREATE INDEX IF NOT EXISTS idx_financial_reports_year ON financial_reports(report_year);
            
            ALTER TABLE financial_reports ADD CONSTRAINT unique_ticker_url UNIQUE (ticker, url);
            """
            
            # Note: This would need to be executed via Supabase dashboard
            logger.info("📋 SQL for creating financial_reports table:")
            logger.info(create_table_sql)
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating table: {str(e)}")
            return False
    
    async def run_batch_scraping(self) -> Dict:
        """Run the complete batch scraping process"""
        logger.info("🚀 Starting Batch Financial Reports Scraping")
        logger.info(f"📊 Total companies: {len(self.companies)}")
        logger.info(f"🔄 Batch size: {self.batch_size}")
        logger.info(f"⚡ Max concurrent: {self.max_concurrent}")
        
        start_time = time.time()
        all_reports = []
        batch_results = []
        
        # Create Supabase table if needed
        if self.service_client:
            self.create_supabase_table()
        
        # Process companies in batches
        for i in range(0, len(self.companies), self.batch_size):
            batch_num = (i // self.batch_size) + 1
            batch = self.companies[i:i + self.batch_size]
            
            logger.info(f"\n🔄 Processing Batch {batch_num}/{(len(self.companies) + self.batch_size - 1) // self.batch_size}")
            logger.info(f"📋 Companies in batch: {[c['ticker'] for c in batch]}")
            
            # Process batch
            batch_reports = await self.process_batch(batch)
            all_reports.extend(batch_reports)
            
            # Save batch results
            batch_file = self.save_reports_to_json(batch_reports, batch_num)
            
            # Insert to Supabase
            if self.service_client:
                await self.insert_reports_to_supabase(batch_reports)
            
            batch_results.append({
                'batch_num': batch_num,
                'companies': len(batch),
                'reports_found': len(batch_reports),
                'file': batch_file
            })
            
            # Small delay between batches
            await asyncio.sleep(2)
        
        # Save final results
        final_results = {
            'timestamp': datetime.now().isoformat(),
            'total_companies': len(self.companies),
            'total_reports': len(all_reports),
            'batch_size': self.batch_size,
            'max_concurrent': self.max_concurrent,
            'batch_results': batch_results,
            'reports': all_reports
        }
        
        final_file = self.output_dir / f"financial_reports_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(final_file, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, indent=2, ensure_ascii=False)
        
        elapsed_time = time.time() - start_time
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ BATCH SCRAPING COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"📊 Total companies processed: {len(self.companies)}")
        logger.info(f"📄 Total reports found: {len(all_reports)}")
        logger.info(f"⏱️  Total time: {elapsed_time:.2f} seconds")
        logger.info(f"📁 Final results saved to: {final_file}")
        
        return final_results

async def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Batch Financial Reports Scraper')
    parser.add_argument('--batch-size', type=int, default=10, 
                       help='Number of companies to process in each batch (default: 10)')
    parser.add_argument('--max-concurrent', type=int, default=10,
                       help='Maximum concurrent requests (default: 10)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run mode - validate configuration without scraping')
    
    args = parser.parse_args()
    
    # Initialize scraper
    scraper = BatchFinancialReportsScraper(batch_size=args.batch_size, max_concurrent=args.max_concurrent)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - Validating configuration...")
        print(f"   Total companies: {len(scraper.companies)}")
        print(f"   Companies with IR URLs: {len(scraper.company_ir_pages)}")
        print(f"   Batch size: {args.batch_size}")
        print(f"   Max concurrent: {args.max_concurrent}")
        
        # Check for missing IR URLs
        missing_ir = []
        for company in scraper.companies:
            ticker = company['ticker']
            if ticker not in scraper.company_ir_pages:
                missing_ir.append(ticker)
        
        if missing_ir:
            print(f"   ⚠️  Companies missing IR URLs: {missing_ir}")
        else:
            print("   ✅ All companies have IR URLs configured")
        
        return
    
    async with scraper:
        results = await scraper.run_batch_scraping()
        
        # Print summary
        print("\n📋 SCRAPING SUMMARY:")
        print(f"   Companies processed: {results['total_companies']}")
        print(f"   Reports found: {results['total_reports']}")
        print(f"   Batches completed: {len(results['batch_results'])}")
        
        if results['reports']:
            print("\n📄 SAMPLE REPORTS:")
            for report in results['reports'][:5]:
                print(f"   {report['ticker']}: {report['title']} ({report['type']})")

if __name__ == "__main__":
    asyncio.run(main()) 