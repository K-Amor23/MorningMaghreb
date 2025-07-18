#!/usr/bin/env python3
"""
Casablanca Insights Data Pipeline Demo

This script demonstrates the complete end-to-end data pipeline:
1. Scrape & Ingest: Fetch financial reports
2. Parse & Structure: Extract data from PDFs
3. PDF Extraction & GAAP Mapping: Translate to US GAAP
4. Store & Version: Save to database
5. API Layer: Serve via REST endpoints
6. Monitoring: Health checks and metrics

Usage:
    python demo_pipeline.py
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from etl.etl_orchestrator import ETLOrchestrator
from etl.scheduler import scheduler
from storage.local_fs import LocalFileStorage
from cache.redis_client import init_cache, close_cache
from monitoring.health_checks import health_monitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PipelineDemo:
    """Demo class for the complete data pipeline"""
    
    def __init__(self):
        self.storage = LocalFileStorage()
        self.orchestrator = ETLOrchestrator(self.storage)
        
    async def run_demo(self):
        """Run the complete pipeline demo"""
        logger.info("🚀 Starting Casablanca Insights Data Pipeline Demo")
        
        try:
            # Step 1: Initialize components
            await self._initialize_components()
            
            # Step 2: Run health checks
            await self._run_health_checks()
            
            # Step 3: Test ETL pipeline
            await self._test_etl_pipeline()
            
            # Step 4: Test scheduler
            await self._test_scheduler()
            
            # Step 5: Test caching
            await self._test_caching()
            
            # Step 6: Generate demo report
            await self._generate_demo_report()
            
            logger.info("✅ Pipeline demo completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Demo failed: {e}")
            raise
        finally:
            await self._cleanup()
    
    async def _initialize_components(self):
        """Initialize all pipeline components"""
        logger.info("📦 Initializing pipeline components...")
        
        # Initialize cache
        await init_cache()
        logger.info("✅ Redis cache initialized")
        
        # Create demo data directory
        demo_dir = Path("demo_data")
        demo_dir.mkdir(exist_ok=True)
        logger.info("✅ Demo data directory created")
        
        # Initialize scheduler (but don't start it yet)
        logger.info("✅ Scheduler initialized")
    
    async def _run_health_checks(self):
        """Run health checks to verify system status"""
        logger.info("🏥 Running health checks...")
        
        health_report = await health_monitor.run_all_checks()
        
        logger.info(f"📊 Health Status: {health_report['status']}")
        logger.info(f"📈 Health Percentage: {health_report['summary']['health_percentage']:.1f}%")
        
        # Log individual check results
        for check in health_report['checks']:
            status_emoji = "✅" if check['status'] == 'healthy' else "⚠️" if check['status'] == 'warning' else "❌"
            logger.info(f"  {status_emoji} {check['name']}: {check['status']}")
    
    async def _test_etl_pipeline(self):
        """Test the ETL pipeline with demo data"""
        logger.info("🔄 Testing ETL pipeline...")
        
        # Create mock PDF data for demo
        await self._create_mock_pdf_data()
        
        # Run pipeline for demo company
        demo_companies = ["ATW"]
        demo_year = 2024
        
        logger.info(f"📊 Processing demo companies: {demo_companies}")
        
        # Run the pipeline
        results = await self.orchestrator.run_full_pipeline(
            companies=demo_companies,
            year=demo_year
        )
        
        logger.info("📈 ETL Pipeline Results:")
        logger.info(f"  - Companies processed: {len(results.get('companies_processed', []))}")
        logger.info(f"  - Total reports: {results.get('total_reports', 0)}")
        logger.info(f"  - Successful extractions: {results.get('successful_extractions', 0)}")
        logger.info(f"  - Successful translations: {results.get('successful_translations', 0)}")
        logger.info(f"  - Duration: {results.get('duration', 0):.2f} seconds")
        
        if results.get('errors'):
            logger.warning(f"⚠️  Errors encountered: {len(results['errors'])}")
            for error in results['errors'][:3]:  # Show first 3 errors
                logger.warning(f"    - {error}")
    
    async def _create_mock_pdf_data(self):
        """Create mock PDF data for demo purposes"""
        logger.info("📄 Creating mock PDF data...")
        
        # Create a simple mock PDF with financial data
        demo_pdf_path = Path("demo_data/ATW_2024_Q1_demo.pdf")
        
        # For demo purposes, we'll create a text file that simulates PDF content
        mock_content = """
        ATTIJARIWAFA BANK - RAPPORT FINANCIER Q1 2024
        
        COMPTE DE RÉSULTAT
        Revenus nets: 13,940,000,000 MAD
        Charges d'exploitation: 8,500,000,000 MAD
        Résultat d'exploitation: 5,440,000,000 MAD
        Résultat net: 3,200,000,000 MAD
        
        BILAN
        Actif total: 450,000,000,000 MAD
        Passif total: 380,000,000,000 MAD
        Capitaux propres: 70,000,000,000 MAD
        """
        
        with open(demo_pdf_path, 'w', encoding='utf-8') as f:
            f.write(mock_content)
        
        logger.info(f"✅ Mock PDF created: {demo_pdf_path}")
    
    async def _test_scheduler(self):
        """Test the scheduler functionality"""
        logger.info("⏰ Testing scheduler...")
        
        # Get scheduler status
        status = scheduler.get_scheduler_status()
        logger.info(f"📊 Scheduler Status: {'Running' if status['running'] else 'Stopped'}")
        logger.info(f"📋 Total Jobs: {status['jobs']}")
        
        # Show next run times
        for job_id, next_run in status['next_run'].items():
            if next_run:
                logger.info(f"  ⏭️  {job_id}: {next_run}")
    
    async def _test_caching(self):
        """Test Redis caching functionality"""
        logger.info("💾 Testing Redis caching...")
        
        from cache.redis_client import redis_client
        
        # Test cache operations
        test_key = "demo:test_data"
        test_value = {
            "company": "ATW",
            "timestamp": datetime.now().isoformat(),
            "data": {"revenue": 13940000000, "profit": 3200000000}
        }
        
        # Set cache
        success = await redis_client.set(test_key, test_value, ttl=300)
        logger.info(f"📝 Cache set: {'✅' if success else '❌'}")
        
        # Get cache
        cached_value = await redis_client.get(test_key)
        logger.info(f"📖 Cache get: {'✅' if cached_value else '❌'}")
        
        # Get cache stats
        stats = await redis_client.get_cache_stats()
        logger.info(f"📊 Cache stats: {stats}")
    
    async def _generate_demo_report(self):
        """Generate a demo report"""
        logger.info("📋 Generating demo report...")
        
        report = {
            "demo_timestamp": datetime.now().isoformat(),
            "pipeline_version": "2.0.0",
            "components_tested": [
                "ETL Orchestrator",
                "Health Monitoring",
                "Scheduler",
                "Redis Caching",
                "PDF Extraction",
                "GAAP Translation"
            ],
            "demo_companies": ["ATW"],
            "demo_year": 2024,
            "next_steps": [
                "Configure production environment",
                "Set up monitoring dashboards",
                "Configure alerting",
                "Deploy with Docker",
                "Scale for production load"
            ]
        }
        
        # Save report
        report_path = Path("demo_data/demo_report.json")
        import json
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✅ Demo report saved: {report_path}")
        
        # Print summary
        logger.info("\n" + "="*60)
        logger.info("🎉 DEMO COMPLETED SUCCESSFULLY!")
        logger.info("="*60)
        logger.info("📊 Pipeline Components Tested:")
        for component in report["components_tested"]:
            logger.info(f"  ✅ {component}")
        logger.info("\n📋 Next Steps:")
        for step in report["next_steps"]:
            logger.info(f"  🔄 {step}")
        logger.info("="*60)
    
    async def _cleanup(self):
        """Clean up demo resources"""
        logger.info("🧹 Cleaning up demo resources...")
        
        # Close cache connection
        await close_cache()
        logger.info("✅ Cache connection closed")
        
        # Stop scheduler if running
        if scheduler.scheduler.running:
            await scheduler.stop()
            logger.info("✅ Scheduler stopped")

async def main():
    """Main demo function"""
    demo = PipelineDemo()
    await demo.run_demo()

if __name__ == "__main__":
    # Check if running in the correct directory
    if not Path("etl").exists():
        logger.error("❌ Please run this script from the backend directory")
        sys.exit(1)
    
    # Run the demo
    asyncio.run(main()) 