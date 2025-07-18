#!/usr/bin/env python3
"""
Casablanca Insights Live Update Pipeline Demo

This script demonstrates the complete ETL pipeline without requiring
database or Redis connections.
"""

import asyncio
import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import sys

# Add the backend directory to Python path
backend_path = Path(__file__).parent
sys.path.append(str(backend_path))

from etl.fetch_ir_reports import IRReportFetcher
from storage.local_fs import LocalFileStorage
from models.financials import JobType, JobStatus

logger = logging.getLogger(__name__)

class DemoLiveUpdatePipeline:
    """Demo version of the live update pipeline"""
    
    def __init__(self):
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
        """Run the complete demo pipeline"""
        logger.info("🚀 Starting Casablanca Insights Live Update Pipeline Demo")
        
        try:
            # Step 1: Scrape IR Reports
            await self.step_1_scrape_ir_reports()
            
            # Step 2: Parse & Ingest PDFs (simulated)
            await self.step_2_parse_pdfs()
            
            # Step 3: GAAP Translation & Ratios (simulated)
            await self.step_3_gaap_translation()
            
            # Step 4: Versioning & Change Detection (simulated)
            await self.step_4_versioning()
            
            # Step 5: API Cache Refresh (simulated)
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
            # Get companies from our known list
            companies = ["ATW", "IAM", "BCP", "BMCE", "CIH", "WAA"]
            
            # Initialize fetcher
            fetcher = IRReportFetcher(self.storage)
            
            # Fetch reports for current year
            current_year = datetime.now().year
            reports = await fetcher.fetch_all_reports(companies, current_year)
            
            # Simulate downloading (we'll just log what we found)
            self.pipeline_stats['reports_fetched'] = len(reports)
            
            logger.info(f"✅ Found {len(reports)} potential reports")
            
            # Log some sample reports
            for i, report in enumerate(reports[:3]):
                logger.info(f"  Report {i+1}: {report.get('filename', 'Unknown')} - {report.get('company', 'Unknown')}")
                
        except Exception as e:
            logger.error(f"Error in step 1: {e}")
            self.pipeline_stats['errors'].append(f"Step 1: {e}")
            # Don't raise, continue with demo
    
    async def step_2_parse_pdfs(self):
        """Step 2: Parse & Ingest PDFs (simulated)"""
        logger.info("📄 Step 2: Parsing PDFs...")
        
        try:
            # Get downloaded files from storage
            pdf_files = self.storage.list_files("raw_pdfs", "*.pdf")
            
            logger.info(f"Found {len(pdf_files)} PDF files to process")
            
            # Simulate parsing
            parsed_records = min(len(pdf_files), 10)  # Simulate up to 10 records
            self.pipeline_stats['financial_records_parsed'] = parsed_records
            
            logger.info(f"✅ Simulated parsing {parsed_records} financial records")
            
        except Exception as e:
            logger.error(f"Error in step 2: {e}")
            self.pipeline_stats['errors'].append(f"Step 2: {e}")
    
    async def step_3_gaap_translation(self):
        """Step 3: GAAP Translation & Ratios (simulated)"""
        logger.info("🔄 Step 3: GAAP Translation & Ratios...")
        
        try:
            # Simulate translation
            records_to_translate = self.pipeline_stats['financial_records_parsed']
            translated_records = int(records_to_translate * 0.8)  # 80% success rate
            
            self.pipeline_stats['gaap_records_translated'] = translated_records
            self.pipeline_stats['ratios_calculated'] = translated_records * 5  # 5 ratios per record
            
            logger.info(f"✅ Translated {translated_records} records to GAAP")
            logger.info(f"✅ Calculated {self.pipeline_stats['ratios_calculated']} financial ratios")
            
        except Exception as e:
            logger.error(f"Error in step 3: {e}")
            self.pipeline_stats['errors'].append(f"Step 3: {e}")
    
    async def step_4_versioning(self):
        """Step 4: Versioning & Change Detection (simulated)"""
        logger.info("📝 Step 4: Versioning & Change Detection...")
        
        try:
            # Simulate upsert
            records_to_upsert = self.pipeline_stats['gaap_records_translated']
            self.pipeline_stats['records_upserted'] = records_to_upsert
            
            logger.info(f"✅ Upserted {records_to_upsert} records with versioning")
            
        except Exception as e:
            logger.error(f"Error in step 4: {e}")
            self.pipeline_stats['errors'].append(f"Step 4: {e}")
    
    async def step_5_cache_refresh(self):
        """Step 5: API Cache Refresh (simulated)"""
        logger.info("🔄 Step 5: Refreshing API Cache...")
        
        try:
            # Simulate cache refresh
            self.pipeline_stats['cache_refreshed'] = True
            logger.info("✅ API cache refresh simulated")
            
        except Exception as e:
            logger.error(f"Error in step 5: {e}")
            self.pipeline_stats['errors'].append(f"Step 5: {e}")
    
    async def step_6_notification(self, success: bool):
        """Step 6: Success/Failure Notification"""
        logger.info("📢 Step 6: Sending Notification...")
        
        try:
            # Create notification message
            message = self._create_notification_message(success)
            
            # Log the message
            logger.info(message)
            
            # Print summary
            self._print_summary()
            
        except Exception as e:
            logger.error(f"Error in step 6: {e}")
            self.pipeline_stats['errors'].append(f"Step 6: {e}")
    
    def _create_notification_message(self, success: bool) -> str:
        """Create notification message"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        duration = (datetime.now() - self.start_time).total_seconds()
        
        message = f"""
{status} - Casablanca Insights ETL Pipeline

Duration: {duration:.2f} seconds
Reports Fetched: {self.pipeline_stats['reports_fetched']}
Records Parsed: {self.pipeline_stats['financial_records_parsed']}
GAAP Translated: {self.pipeline_stats['gaap_records_translated']}
Ratios Calculated: {self.pipeline_stats['ratios_calculated']}
Records Upserted: {self.pipeline_stats['records_upserted']}
Cache Refreshed: {self.pipeline_stats['cache_refreshed']}
Errors: {len(self.pipeline_stats['errors'])}
"""
        return message
    
    def _print_summary(self):
        """Print pipeline summary"""
        print("\n" + "=" * 60)
        print("📊 PIPELINE SUMMARY")
        print("=" * 60)
        
        duration = (datetime.now() - self.start_time).total_seconds()
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📈 Reports Fetched: {self.pipeline_stats['reports_fetched']}")
        print(f"📄 Records Parsed: {self.pipeline_stats['financial_records_parsed']}")
        print(f"🔄 GAAP Translated: {self.pipeline_stats['gaap_records_translated']}")
        print(f"📊 Ratios Calculated: {self.pipeline_stats['ratios_calculated']}")
        print(f"💾 Records Upserted: {self.pipeline_stats['records_upserted']}")
        print(f"🔄 Cache Refreshed: {self.pipeline_stats['cache_refreshed']}")
        print(f"❌ Errors: {len(self.pipeline_stats['errors'])}")
        
        if self.pipeline_stats['errors']:
            print("\n🚨 Errors:")
            for error in self.pipeline_stats['errors']:
                print(f"  • {error}")
        
        print("\n" + "=" * 60)

async def main():
    """Main function to run the demo pipeline"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Run pipeline
    pipeline = DemoLiveUpdatePipeline()
    
    try:
        stats = await pipeline.run_pipeline()
        return stats
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        return pipeline.pipeline_stats

if __name__ == "__main__":
    asyncio.run(main()) 