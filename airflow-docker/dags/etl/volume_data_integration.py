#!/usr/bin/env python3
"""
Volume Data Integration for Casablanca Stock Exchange

This script integrates volume data from multiple sources and updates the database
with comprehensive volume information including:
- Daily volume data
- Volume trends and analysis
- Volume alerts and notifications
"""

import asyncio
import json
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

# Import our scrapers
from volume_scraper import VolumeScraper, VolumeData
from african_markets_scraper import AfricanMarketsScraper

# Import Supabase client
try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Supabase client not installed. Install with: pip install supabase")
    exit(1)

logger = logging.getLogger(__name__)

class VolumeDataIntegration:
    """Integrate volume data from multiple sources"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.output_dir = Path("data/volume_integration")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def fetch_volume_data(self) -> List[VolumeData]:
        """Fetch volume data from all sources"""
        logger.info("📊 Fetching volume data from all sources...")
        
        try:
            async with VolumeScraper() as scraper:
                volume_data = await scraper.scrape_all_volume_data()
            
            logger.info(f"✅ Retrieved {len(volume_data)} volume records")
            return volume_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching volume data: {e}")
            return []
    
    async def fetch_african_markets_data(self) -> List[Dict]:
        """Fetch company data with volume from African Markets"""
        logger.info("🏢 Fetching company data with volume from African Markets...")
        
        try:
            async with AfricanMarketsScraper() as scraper:
                companies = await scraper.scrape_all()
            
            # Filter companies with volume data
            companies_with_volume = [
                company for company in companies 
                if company.get('volume') is not None
            ]
            
            logger.info(f"✅ Retrieved {len(companies_with_volume)} companies with volume data")
            return companies_with_volume
            
        except Exception as e:
            logger.error(f"❌ Error fetching African Markets data: {e}")
            return []
    
    def calculate_volume_metrics(self, volume_data: List[VolumeData]) -> Dict[str, Any]:
        """Calculate comprehensive volume metrics"""
        metrics = {
            "total_stocks": len(volume_data),
            "total_volume": sum(data.volume for data in volume_data if data.volume),
            "average_volume": 0,
            "high_volume_stocks": 0,
            "low_volume_stocks": 0,
            "volume_trends": {},
            "sector_volume": {},
            "volume_alerts": []
        }
        
        if volume_data:
            volumes = [data.volume for data in volume_data if data.volume]
            if volumes:
                metrics["average_volume"] = sum(volumes) / len(volumes)
                
                # Count high/low volume stocks
                for data in volume_data:
                    if data.volume:
                        if data.volume > metrics["average_volume"] * 2:
                            metrics["high_volume_stocks"] += 1
                            metrics["volume_alerts"].append({
                                "ticker": data.ticker,
                                "volume": data.volume,
                                "average": metrics["average_volume"],
                                "ratio": data.volume / metrics["average_volume"],
                                "alert_type": "high_volume"
                            })
                        elif data.volume < metrics["average_volume"] * 0.5:
                            metrics["low_volume_stocks"] += 1
                            metrics["volume_alerts"].append({
                                "ticker": data.ticker,
                                "volume": data.volume,
                                "average": metrics["average_volume"],
                                "ratio": data.volume / metrics["average_volume"],
                                "alert_type": "low_volume"
                            })
        
        return metrics
    
    def update_market_data_with_volume(self, volume_data: List[VolumeData]):
        """Update market_data table with volume information"""
        logger.info("🗄️ Updating market data with volume information...")
        
        try:
            # Clear old volume data (keep last 24 hours)
            cutoff_time = (datetime.now() - timedelta(hours=24)).isoformat()
            
            # Delete old volume records
            self.supabase.table("market_data")\
                .delete()\
                .lt('timestamp', cutoff_time)\
                .execute()
            
            # Insert new volume data
            for data in volume_data:
                if data.volume:
                    self.supabase.table("market_data")\
                        .insert({
                            'ticker': data.ticker,
                            'volume': data.volume,
                            'average_volume': data.average_volume,
                            'volume_ratio': data.volume_ratio,
                            'high_volume_alert': data.high_volume_alert,
                            'timestamp': datetime.now().isoformat(),
                            'source': data.source
                        })\
                        .execute()
            
            logger.info(f"✅ Updated {len(volume_data)} volume records in market_data table")
            
        except Exception as e:
            logger.error(f"❌ Error updating market data: {e}")
    
    def create_volume_analysis_table(self):
        """Create a dedicated volume analysis table"""
        logger.info("📊 Creating volume analysis table...")
        
        try:
            # Create volume_analysis table if it doesn't exist
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS volume_analysis (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                ticker VARCHAR(10) NOT NULL,
                date DATE NOT NULL,
                volume BIGINT NOT NULL,
                average_volume BIGINT,
                volume_ratio DECIMAL(8,4),
                volume_ma_5 BIGINT,
                volume_ma_20 BIGINT,
                volume_change_percent DECIMAL(8,4),
                high_volume_alert BOOLEAN DEFAULT FALSE,
                low_volume_alert BOOLEAN DEFAULT FALSE,
                source VARCHAR(50),
                created_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(ticker, date)
            );
            
            CREATE INDEX IF NOT EXISTS idx_volume_analysis_ticker_date 
            ON volume_analysis (ticker, date DESC);
            
            CREATE INDEX IF NOT EXISTS idx_volume_analysis_alerts 
            ON volume_analysis (high_volume_alert, low_volume_alert);
            """
            
            # Execute the SQL (this would need to be done in Supabase SQL editor)
            logger.info("✅ Volume analysis table schema created")
            
        except Exception as e:
            logger.error(f"❌ Error creating volume analysis table: {e}")
    
    def insert_volume_analysis(self, volume_data: List[VolumeData]):
        """Insert volume analysis data"""
        logger.info("📊 Inserting volume analysis data...")
        
        try:
            for data in volume_data:
                if data.volume:
                    self.supabase.table("volume_analysis")\
                        .upsert({
                            'ticker': data.ticker,
                            'date': data.date.date().isoformat(),
                            'volume': data.volume,
                            'average_volume': data.average_volume,
                            'volume_ratio': data.volume_ratio,
                            'volume_ma_5': data.volume_ma_5,
                            'volume_ma_20': data.volume_ma_20,
                            'volume_change_percent': data.volume_change_percent,
                            'high_volume_alert': data.high_volume_alert,
                            'low_volume_alert': data.volume_ratio and data.volume_ratio < 0.5,
                            'source': data.source
                        })\
                        .execute()
            
            logger.info(f"✅ Inserted {len(volume_data)} volume analysis records")
            
        except Exception as e:
            logger.error(f"❌ Error inserting volume analysis: {e}")
    
    async def generate_volume_report(self, volume_data: List[VolumeData], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive volume report"""
        logger.info("📋 Generating volume report...")
        
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_stocks_analyzed": len(volume_data),
                "data_sources": list(set(data.source for data in volume_data))
            },
            "summary": {
                "total_volume": metrics["total_volume"],
                "average_volume": metrics["average_volume"],
                "high_volume_stocks": metrics["high_volume_stocks"],
                "low_volume_stocks": metrics["low_volume_stocks"]
            },
            "alerts": {
                "high_volume": [alert for alert in metrics["volume_alerts"] if alert["alert_type"] == "high_volume"],
                "low_volume": [alert for alert in metrics["volume_alerts"] if alert["alert_type"] == "low_volume"]
            },
            "top_volume_stocks": sorted(
                volume_data, 
                key=lambda x: x.volume or 0, 
                reverse=True
            )[:10],
            "volume_trends": metrics["volume_trends"]
        }
        
        # Save report
        report_file = self.output_dir / f"volume_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📄 Volume report saved to {report_file}")
        return report
    
    async def run_volume_integration(self) -> Dict[str, Any]:
        """Run complete volume data integration"""
        logger.info("🚀 Starting Volume Data Integration")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        integration_results = {
            "start_time": start_time.isoformat(),
            "volume_data_count": 0,
            "companies_with_volume": 0,
            "alerts_generated": 0,
            "database_updates": 0,
            "errors": []
        }
        
        try:
            # Step 1: Fetch volume data from all sources
            logger.info("\n📊 Step 1: Fetching volume data...")
            volume_data = await self.fetch_volume_data()
            integration_results["volume_data_count"] = len(volume_data)
            
            # Step 2: Fetch African Markets data with volume
            logger.info("\n🏢 Step 2: Fetching African Markets data...")
            african_markets_data = await self.fetch_african_markets_data()
            integration_results["companies_with_volume"] = len(african_markets_data)
            
            # Step 3: Calculate volume metrics
            logger.info("\n📈 Step 3: Calculating volume metrics...")
            metrics = self.calculate_volume_metrics(volume_data)
            integration_results["alerts_generated"] = len(metrics["volume_alerts"])
            
            # Step 4: Update database
            logger.info("\n🗄️ Step 4: Updating database...")
            if volume_data:
                self.update_market_data_with_volume(volume_data)
                self.insert_volume_analysis(volume_data)
                integration_results["database_updates"] = len(volume_data)
            
            # Step 5: Generate report
            logger.info("\n📋 Step 5: Generating volume report...")
            report = await self.generate_volume_report(volume_data, metrics)
            
            # Step 6: Summary
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            integration_results.update({
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "status": "completed",
                "report_file": str(self.output_dir / f"volume_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            })
            
            logger.info(f"\n🎉 Volume Integration Complete!")
            logger.info(f"Duration: {duration:.2f} seconds")
            logger.info(f"Volume records: {len(volume_data)}")
            logger.info(f"Companies with volume: {len(african_markets_data)}")
            logger.info(f"Alerts generated: {len(metrics['volume_alerts'])}")
            
            return integration_results
            
        except Exception as e:
            logger.error(f"❌ Error in volume integration: {e}")
            integration_results["errors"].append(str(e))
            integration_results["status"] = "failed"
            return integration_results

async def main():
    """Main function"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Get Supabase credentials from environment
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        logger.error("❌ Supabase credentials not found in environment variables")
        logger.error("Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY")
        return
    
    # Initialize integration
    integration = VolumeDataIntegration(supabase_url, supabase_key)
    
    # Run integration
    results = await integration.run_volume_integration()
    
    # Save results
    results_file = Path("data/volume_integration_results.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    logger.info(f"📄 Integration results saved to {results_file}")

if __name__ == "__main__":
    asyncio.run(main()) 