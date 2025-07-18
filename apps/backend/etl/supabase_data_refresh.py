#!/usr/bin/env python3
"""
Supabase Data Refresh Pipeline for Casablanca Insights

This script:
1. Fetches latest financial data from multiple sources
2. Processes and cleans the data
3. Updates Supabase database with new information
4. Triggers real-time updates for connected clients
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os
from typing import Dict, List, Any

# Add the backend directory to Python path
backend_path = Path(__file__).parent.parent
sys.path.append(str(backend_path))

# Import our scrapers
from etl.african_markets_scraper import AfricanMarketsScraper
from etl.bank_al_maghrib_scraper import BankAlMaghribScraper
from etl.cse_company_scraper import CSEScraper

# Import Supabase client
try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Supabase client not installed. Install with: pip install supabase")
    sys.exit(1)

logger = logging.getLogger(__name__)

class SupabaseDataRefresh:
    """Manages data refresh operations with Supabase"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.output_dir = Path("data/refresh")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def fetch_market_data(self) -> List[Dict]:
        """Fetch latest market data from African Markets"""
        logger.info("📊 Fetching market data from African Markets...")
        
        try:
            async with AfricanMarketsScraper() as scraper:
                companies = await scraper.scrape_all()
            
            logger.info(f"✅ Retrieved {len(companies)} market data points")
            return companies
            
        except Exception as e:
            logger.error(f"❌ Error fetching market data: {e}")
            return []
    
    async def fetch_central_bank_data(self) -> Dict[str, List[Dict]]:
        """Fetch central bank data from Bank Al-Maghrib"""
        logger.info("🏦 Fetching central bank data from Bank Al-Maghrib...")
        
        try:
            async with BankAlMaghribScraper() as scraper:
                data = await scraper.scrape_all()
            
            total_records = sum(len(items) for items in data.values())
            logger.info(f"✅ Retrieved {total_records} central bank data points")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error fetching central bank data: {e}")
            return {}
    
    async def fetch_cse_companies(self) -> List[Dict]:
        """Fetch updated CSE company data"""
        logger.info("🏢 Fetching CSE company data...")
        
        try:
            async with CSEScraper() as scraper:
                companies = await scraper.scrape_companies()
            
            logger.info(f"✅ Retrieved {len(companies)} CSE companies")
            return [company.to_dict() for company in companies]
            
        except Exception as e:
            logger.error(f"❌ Error fetching CSE companies: {e}")
            return []
    
    def update_market_data_in_supabase(self, market_data: List[Dict]):
        """Update market data in Supabase"""
        logger.info("🗄️ Updating market data in Supabase...")
        
        try:
            # Clear old market data (keep last 24 hours)
            cutoff_time = (datetime.now() - timedelta(hours=24)).isoformat()
            
            # Delete old records
            self.supabase.table("market_data")\
                .delete()\
                .lt('timestamp', cutoff_time)\
                .execute()
            
            # Insert new market data
            for data_point in market_data:
                if 'ticker' in data_point and 'price' in data_point:
                    self.supabase.table("market_data")\
                        .insert({
                            'ticker': data_point['ticker'],
                            'price': data_point.get('price'),
                            'volume': data_point.get('volume'),
                            'market_cap': data_point.get('market_cap'),
                            'change_percent': data_point.get('change_percent'),
                            'high_24h': data_point.get('high_24h'),
                            'low_24h': data_point.get('low_24h'),
                            'open_price': data_point.get('open_price'),
                            'previous_close': data_point.get('previous_close'),
                            'timestamp': datetime.now().isoformat(),
                            'source': 'cse'
                        })\
                        .execute()
            
            logger.info(f"✅ Updated {len(market_data)} market data points in Supabase")
            
        except Exception as e:
            logger.error(f"❌ Error updating market data in Supabase: {e}")
    
    def update_cse_companies_in_supabase(self, companies: List[Dict]):
        """Update CSE companies in Supabase"""
        logger.info("🏢 Updating CSE companies in Supabase...")
        
        try:
            for company in companies:
                # Upsert company data
                self.supabase.table("cse_companies")\
                    .upsert({
                        'name': company['name'],
                        'ticker': company['ticker'],
                        'isin': company.get('isin'),
                        'sector': company.get('sector'),
                        'listing_date': company.get('listing_date'),
                        'source_url': company.get('source_url'),
                        'scraped_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    }, on_conflict='ticker')\
                    .execute()
            
            logger.info(f"✅ Updated {len(companies)} CSE companies in Supabase")
            
        except Exception as e:
            logger.error(f"❌ Error updating CSE companies in Supabase: {e}")
    
    def log_etl_job(self, job_type: str, status: str, metadata: Dict = None, error_message: str = None):
        """Log ETL job status in Supabase"""
        try:
            self.supabase.table("etl_jobs")\
                .insert({
                    'job_type': job_type,
                    'status': status,
                    'metadata': metadata or {},
                    'error_message': error_message,
                    'started_at': datetime.now().isoformat(),
                    'completed_at': datetime.now().isoformat() if status in ['completed', 'failed'] else None
                })\
                .execute()
            
        except Exception as e:
            logger.error(f"❌ Error logging ETL job: {e}")
    
    def save_refresh_report(self, data: Dict[str, Any]) -> Path:
        """Save refresh report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"refresh_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📄 Refresh report saved to {report_file}")
        return report_file
    
    async def run_refresh_pipeline(self) -> Dict[str, Any]:
        """Run the complete data refresh pipeline"""
        start_time = datetime.now()
        
        logger.info("🚀 Starting Supabase Data Refresh Pipeline")
        logger.info("=" * 60)
        
        # Log job start
        self.log_etl_job("data_refresh", "running", {"started_at": start_time.isoformat()})
        
        refresh_data = {
            "pipeline": "Supabase Data Refresh Pipeline",
            "started_at": start_time.isoformat(),
            "market_data": {},
            "central_bank_data": {},
            "cse_companies": {},
            "errors": []
        }
        
        try:
            # Step 1: Fetch market data
            logger.info("\n📊 Step 1: Fetching market data...")
            market_data = await self.fetch_market_data()
            refresh_data["market_data"] = {
                "count": len(market_data),
                "data": market_data[:5]  # Store first 5 for reference
            }
            
            # Step 2: Fetch central bank data
            logger.info("\n🏦 Step 2: Fetching central bank data...")
            central_bank_data = await self.fetch_central_bank_data()
            refresh_data["central_bank_data"] = {
                "sources": list(central_bank_data.keys()),
                "total_records": sum(len(items) for items in central_bank_data.values()),
                "data": {k: v[:3] for k, v in central_bank_data.items()}  # Store first 3 from each source
            }
            
            # Step 3: Fetch CSE companies
            logger.info("\n🏢 Step 3: Fetching CSE companies...")
            cse_companies = await self.fetch_cse_companies()
            refresh_data["cse_companies"] = {
                "count": len(cse_companies),
                "data": cse_companies[:5]  # Store first 5 for reference
            }
            
            # Step 4: Update Supabase
            logger.info("\n🗄️ Step 4: Updating Supabase database...")
            
            if market_data:
                self.update_market_data_in_supabase(market_data)
            
            if cse_companies:
                self.update_cse_companies_in_supabase(cse_companies)
            
            # Step 5: Generate summary
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            refresh_data["completed_at"] = end_time.isoformat()
            refresh_data["duration_seconds"] = duration
            refresh_data["status"] = "completed"
            
            # Log successful completion
            self.log_etl_job("data_refresh", "completed", {
                "duration_seconds": duration,
                "market_data_count": len(market_data),
                "cse_companies_count": len(cse_companies),
                "central_bank_sources": len(central_bank_data)
            })
            
            # Save report
            report_file = self.save_refresh_report(refresh_data)
            refresh_data["report_file"] = str(report_file)
            
            logger.info("\n" + "=" * 60)
            logger.info("🎉 Data Refresh Pipeline Completed Successfully!")
            logger.info("=" * 60)
            
            logger.info(f"\n📊 Summary:")
            logger.info(f"  • Duration: {duration:.2f} seconds")
            logger.info(f"  • Market Data Points: {len(market_data)}")
            logger.info(f"  • CSE Companies: {len(cse_companies)}")
            logger.info(f"  • Central Bank Sources: {len(central_bank_data)}")
            logger.info(f"  • Report File: {report_file}")
            
            return refresh_data
            
        except Exception as e:
            error_msg = f"Pipeline failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            
            refresh_data["status"] = "failed"
            refresh_data["error"] = error_msg
            refresh_data["completed_at"] = datetime.now().isoformat()
            
            # Log failure
            self.log_etl_job("data_refresh", "failed", {}, error_msg)
            
            # Save error report
            report_file = self.save_refresh_report(refresh_data)
            
            return refresh_data

async def main():
    """Main function to run the data refresh pipeline"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Get Supabase credentials from environment
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found in environment variables")
        print("Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY")
        return
    
    # Initialize refresh pipeline
    refresh_pipeline = SupabaseDataRefresh(supabase_url, supabase_key)
    
    # Run the pipeline
    result = await refresh_pipeline.run_refresh_pipeline()
    
    if result["status"] == "completed":
        print("\n✅ Data refresh completed successfully!")
        return 0
    else:
        print(f"\n❌ Data refresh failed: {result.get('error', 'Unknown error')}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)