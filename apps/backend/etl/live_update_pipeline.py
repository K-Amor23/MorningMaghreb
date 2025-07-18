"""
Casablanca Insights Live Update Pipeline

This script orchestrates the complete ETL pipeline:
1. Scrape IR Reports
2. Parse & Ingest PDFs
3. GAAP Translation & Ratios
4. Versioning & Change Detection
5. API Cache Refresh
6. Success/Failure Notification
"""

import asyncio
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
import requests

# Add the backend directory to Python path
backend_path = Path(__file__).parent.parent
sys.path.append(str(backend_path))

from etl.fetch_ir_reports import IRReportFetcher
from etl.extract_from_pdf import PDFExtractor
from etl.translate_labels import LabelTranslator
from etl.compute_ratios import RatioCalculator
from etl.etl_orchestrator import ETLOrchestrator
from storage.local_fs import LocalFileStorage
from models.financials import ETLJob, JobType, JobStatus

logger = logging.getLogger(__name__)

class LiveUpdatePipeline:
    """Orchestrates the complete live update pipeline"""
    
    def __init__(self, database_url: str, redis_url: str = "redis://localhost:6379"):
        self.database_url = database_url
        self.redis_url = redis_url
        self.storage = LocalFileStorage()
        self.start_time = datetime.now()
        self.pipeline_stats = {
            'reports_fetched': 0,
            'pdfs_processed': 0,
            'financial_records_parsed': 0,
            'gaap_records_translated': 0,
            'ratios_calculated': 0,
            'records_upserted': 0,
            'cache_refreshed': False,
            'errors': []
        }
    
    async def run_pipeline(self) -> Dict:
        """Run the complete pipeline"""
        logger.info("🚀 Starting Casablanca Insights Live Update Pipeline")
        
        try:
            # Step 1: Scrape IR Reports
            await self.step_1_scrape_ir_reports()
            
            # Step 2: Parse & Ingest PDFs
            await self.step_2_parse_pdfs()
            
            # Step 3: GAAP Translation & Ratios
            await self.step_3_gaap_translation()
            
            # Step 4: Versioning & Change Detection
            await self.step_4_versioning()
            
            # Step 5: API Cache Refresh
            await self.step_5_cache_refresh()
            
            # Step 6: Success Notification
            await self.step_6_notification(success=True)
            
            logger.info("✅ Pipeline completed successfully")
            return self.pipeline_stats
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            self.pipeline_stats['errors'].append(str(e))
            await self.step_6_notification(success=False)
            raise
    
    async def step_1_scrape_ir_reports(self):
        """Step 1: Scrape IR Reports"""
        logger.info("📊 Step 1: Scraping IR Reports...")
        
        try:
            # Get companies from database
            companies = await self.get_companies_from_db()
            if not companies:
                logger.warning("No companies found in database")
                return
            
            # Initialize fetcher
            fetcher = IRReportFetcher(self.storage)
            
            async with fetcher:
                # Fetch reports for current year
                current_year = datetime.now().year
                reports = await fetcher.fetch_all_reports(companies, current_year)
                
                # Download reports
                downloaded_files = await fetcher.download_all_reports(reports)
                
                self.pipeline_stats['reports_fetched'] = len(reports)
                self.pipeline_stats['pdfs_processed'] = len(downloaded_files)
                
                logger.info(f"✅ Fetched {len(reports)} reports, downloaded {len(downloaded_files)} files")
                
        except Exception as e:
            logger.error(f"Error in step 1: {e}")
            self.pipeline_stats['errors'].append(f"Step 1: {e}")
            raise
    
    async def step_2_parse_pdfs(self):
        """Step 2: Parse & Ingest PDFs"""
        logger.info("📄 Step 2: Parsing PDFs...")
        
        try:
            # Get downloaded files from storage
            pdf_files = self.storage.list_files("reports", "*.pdf")
            
            if not pdf_files:
                logger.warning("No PDF files found to process")
                return
            
            extractor = PDFExtractor()
            parsed_records = 0
            
            for pdf_path in pdf_files:
                try:
                    # Extract company info from filename
                    filename = Path(pdf_path).name
                    company = self._extract_company_from_filename(filename)
                    
                    # Extract financial data
                    financial_data = extractor.extract_from_pdf(
                        pdf_path=pdf_path,
                        company=company,
                        year=datetime.now().year,
                        report_type='annual'
                    )
                    
                    if financial_data and financial_data.lines:
                        # Store in database
                        await self.store_financial_raw(financial_data)
                        parsed_records += 1
                        logger.info(f"Parsed {len(financial_data.lines)} lines from {filename}")
                    
                except Exception as e:
                    logger.error(f"Error parsing {pdf_path}: {e}")
                    continue
            
            self.pipeline_stats['financial_records_parsed'] = parsed_records
            logger.info(f"✅ Parsed {parsed_records} financial records")
            
        except Exception as e:
            logger.error(f"Error in step 2: {e}")
            self.pipeline_stats['errors'].append(f"Step 2: {e}")
            raise
    
    async def step_3_gaap_translation(self):
        """Step 3: GAAP Translation & Ratios"""
        logger.info("🔄 Step 3: GAAP Translation & Ratios...")
        
        try:
            # Get raw financial data from database
            raw_data = await self.get_raw_financial_data()
            
            if not raw_data:
                logger.warning("No raw financial data found")
                return
            
            translator = LabelTranslator()
            ratio_calculator = RatioCalculator()
            
            translated_records = 0
            ratio_records = 0
            
            for record in raw_data:
                try:
                    # Translate to GAAP
                    gaap_data = translator.translate_financial_data(record)
                    
                    if gaap_data and gaap_data.data:
                        # Calculate ratios
                        ratios = ratio_calculator.calculate_ratios(gaap_data)
                        
                        # Store GAAP data and ratios
                        await self.store_gaap_financial(gaap_data, ratios)
                        
                        translated_records += 1
                        ratio_records += len(ratios) if ratios else 0
                        
                        logger.info(f"Translated and calculated ratios for {record.company}")
                    
                except Exception as e:
                    logger.error(f"Error processing {record.company}: {e}")
                    continue
            
            self.pipeline_stats['gaap_records_translated'] = translated_records
            self.pipeline_stats['ratios_calculated'] = ratio_records
            
            logger.info(f"✅ Translated {translated_records} records, calculated {ratio_records} ratios")
            
        except Exception as e:
            logger.error(f"Error in step 3: {e}")
            self.pipeline_stats['errors'].append(f"Step 3: {e}")
            raise
    
    async def step_4_versioning(self):
        """Step 4: Versioning & Change Detection"""
        logger.info("📝 Step 4: Versioning & Change Detection...")
        
        try:
            # Get latest GAAP data
            latest_gaap = await self.get_latest_gaap_data()
            
            if not latest_gaap:
                logger.warning("No GAAP data found for versioning")
                return
            
            upserted_records = 0
            
            for gaap_record in latest_gaap:
                try:
                    # Check if record exists and has changes
                    existing = await self.get_existing_gaap_record(gaap_record.company, gaap_record.year)
                    
                    if existing:
                        # Compare and version if changed
                        if self._has_changes(existing, gaap_record):
                            await self.version_record(existing, gaap_record)
                            upserted_records += 1
                            logger.info(f"Versioned changes for {gaap_record.company}")
                    else:
                        # New record
                        await self.insert_new_gaap_record(gaap_record)
                        upserted_records += 1
                        logger.info(f"Inserted new record for {gaap_record.company}")
                
                except Exception as e:
                    logger.error(f"Error versioning {gaap_record.company}: {e}")
                    continue
            
            self.pipeline_stats['records_upserted'] = upserted_records
            logger.info(f"✅ Versioned/Upserted {upserted_records} records")
            
        except Exception as e:
            logger.error(f"Error in step 4: {e}")
            self.pipeline_stats['errors'].append(f"Step 4: {e}")
            raise
    
    async def step_5_cache_refresh(self):
        """Step 5: API Cache Refresh"""
        logger.info("🔄 Step 5: Refreshing API Cache...")
        
        try:
            # Clear Redis cache
            redis_client = redis.from_url(self.redis_url)
            redis_client.flushdb()
            logger.info("Cleared Redis cache")
            
            # Hit refresh endpoint
            try:
                response = requests.post("http://localhost:8000/refresh-cache", timeout=30)
                if response.status_code == 200:
                    logger.info("API cache refresh successful")
                    self.pipeline_stats['cache_refreshed'] = True
                else:
                    logger.warning(f"API cache refresh returned status {response.status_code}")
            except Exception as e:
                logger.warning(f"Could not hit refresh endpoint: {e}")
            
        except Exception as e:
            logger.error(f"Error in step 5: {e}")
            self.pipeline_stats['errors'].append(f"Step 5: {e}")
            # Don't fail the pipeline for cache issues
    
    async def step_6_notification(self, success: bool):
        """Step 6: Success/Failure Notification"""
        logger.info("📢 Step 6: Sending Notification...")
        
        try:
            # Log ETL job status
            job_status = JobStatus.SUCCESS if success else JobStatus.FAILED
            await self.log_etl_job(job_status)
            
            # Create notification message
            message = self._create_notification_message(success)
            
            # Log the message (in production, this would send to Slack/email)
            logger.info(message)
            
            # Print summary
            self._print_summary()
            
        except Exception as e:
            logger.error(f"Error in step 6: {e}")
            self.pipeline_stats['errors'].append(f"Step 6: {e}")
    
    # Helper methods
    async def get_companies_from_db(self) -> List[str]:
        """Get companies from database"""
        try:
            with psycopg2.connect(self.database_url) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT ticker FROM cse_companies ORDER BY ticker")
                    return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting companies: {e}")
            return ["ATW", "IAM", "BCP", "BMCE"]  # Fallback
    
    def _extract_company_from_filename(self, filename: str) -> str:
        """Extract company ticker from filename"""
        # Example: ATW_annual_2025.pdf -> ATW
        parts = filename.split('_')
        return parts[0] if parts else "UNKNOWN"
    
    async def store_financial_raw(self, financial_data):
        """Store raw financial data in database"""
        # This would store in financials_raw table
        # For now, just log
        logger.debug(f"Would store raw data for {financial_data.company}")
    
    async def get_raw_financial_data(self):
        """Get raw financial data from database"""
        # This would query financials_raw table
        # For now, return empty list
        return []
    
    async def store_gaap_financial(self, gaap_data, ratios):
        """Store GAAP financial data and ratios"""
        # This would store in financials_gaap table
        # For now, just log
        logger.debug(f"Would store GAAP data for {gaap_data.company}")
    
    async def get_latest_gaap_data(self):
        """Get latest GAAP data from database"""
        # This would query financials_gaap table
        # For now, return empty list
        return []
    
    async def get_existing_gaap_record(self, company: str, year: int):
        """Get existing GAAP record"""
        # This would query financials_gaap table
        # For now, return None
        return None
    
    def _has_changes(self, existing, new):
        """Check if record has changes"""
        # This would compare existing and new records
        # For now, return True to simulate changes
        return True
    
    async def version_record(self, existing, new):
        """Version a changed record"""
        # This would create a new version of the record
        logger.debug(f"Would version record for {new.company}")
    
    async def insert_new_gaap_record(self, record):
        """Insert new GAAP record"""
        # This would insert a new record
        logger.debug(f"Would insert new record for {record.company}")
    
    async def log_etl_job(self, status: JobStatus):
        """Log ETL job status"""
        try:
            with psycopg2.connect(self.database_url) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO etl_jobs (job_type, status, started_at, completed_at, metadata)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        JobType.LIVE_UPDATE.value,
                        status.value,
                        self.start_time,
                        datetime.now(),
                        json.dumps(self.pipeline_stats)
                    ))
                    conn.commit()
        except Exception as e:
            logger.error(f"Error logging ETL job: {e}")
    
    def _create_notification_message(self, success: bool) -> str:
        """Create notification message"""
        if success:
            return f"""
🎉 Casablanca Insights Live Update Pipeline Completed Successfully!

📊 Pipeline Results:
• Reports Fetched: {self.pipeline_stats['reports_fetched']}
• PDFs Processed: {self.pipeline_stats['pdfs_processed']}
• Financial Records Parsed: {self.pipeline_stats['financial_records_parsed']}
• GAAP Records Translated: {self.pipeline_stats['gaap_records_translated']}
• Ratios Calculated: {self.pipeline_stats['ratios_calculated']}
• Records Upserted: {self.pipeline_stats['records_upserted']}
• Cache Refreshed: {'✅ Yes' if self.pipeline_stats['cache_refreshed'] else '❌ No'}

⏱️ Duration: {datetime.now() - self.start_time}
🔗 API: http://localhost:8000
            """
        else:
            return f"""
❌ Casablanca Insights Live Update Pipeline Failed!

🚨 Errors:
{chr(10).join(f'• {error}' for error in self.pipeline_stats['errors'])}

⏱️ Duration: {datetime.now() - self.start_time}
🔗 Check logs for details
            """
    
    def _print_summary(self):
        """Print pipeline summary"""
        print("\n" + "=" * 80)
        print("🎯 CASABLANCA INSIGHTS LIVE UPDATE PIPELINE SUMMARY")
        print("=" * 80)
        
        print(f"\n📊 Pipeline Statistics:")
        print(f"  • Reports Fetched: {self.pipeline_stats['reports_fetched']}")
        print(f"  • PDFs Processed: {self.pipeline_stats['pdfs_processed']}")
        print(f"  • Financial Records Parsed: {self.pipeline_stats['financial_records_parsed']}")
        print(f"  • GAAP Records Translated: {self.pipeline_stats['gaap_records_translated']}")
        print(f"  • Ratios Calculated: {self.pipeline_stats['ratios_calculated']}")
        print(f"  • Records Upserted: {self.pipeline_stats['records_upserted']}")
        print(f"  • Cache Refreshed: {'✅ Yes' if self.pipeline_stats['cache_refreshed'] else '❌ No'}")
        
        print(f"\n⏱️ Performance:")
        duration = datetime.now() - self.start_time
        print(f"  • Total Duration: {duration}")
        print(f"  • Average Time per Step: {duration / 6}")
        
        if self.pipeline_stats['errors']:
            print(f"\n❌ Errors Encountered:")
            for error in self.pipeline_stats['errors']:
                print(f"  • {error}")
        else:
            print(f"\n✅ No Errors Encountered")
        
        print(f"\n🔗 Access Points:")
        print(f"  • API: http://localhost:8000")
        print(f"  • Database: {self.database_url}")
        print(f"  • Redis: {self.redis_url}")
        
        print("\n" + "=" * 80)

async def main():
    """Main function to run the pipeline"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Configuration
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/casablanca_insights')
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # Run pipeline
    pipeline = LiveUpdatePipeline(database_url, redis_url)
    
    try:
        stats = await pipeline.run_pipeline()
        return stats
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        return pipeline.pipeline_stats

if __name__ == "__main__":
    asyncio.run(main()) 