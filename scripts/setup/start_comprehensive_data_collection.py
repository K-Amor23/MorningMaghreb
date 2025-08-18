#!/usr/bin/env python3
"""
Start Comprehensive Data Collection for Company Profiles

This script initiates the comprehensive data collection process to build
real company profiles with market data, news, dividends, and earnings.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the backend ETL directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent / 'apps' / 'backend' / 'etl'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def start_comprehensive_data_collection():
    """Start the comprehensive data collection process"""
    try:
        logger.info("🚀 Starting comprehensive data collection for company profiles...")
        
        # Import the comprehensive scraper
        from comprehensive_market_scraper import ComprehensiveMarketScraper
        
        # Initialize the scraper
        async with ComprehensiveMarketScraper() as scraper:
            logger.info("✅ Comprehensive market scraper initialized")
            
            # Start scraping all comprehensive data
            logger.info("📊 Starting comprehensive market data scraping...")
            comprehensive_data = await scraper.scrape_all_comprehensive_data()
            
            # Log what we collected
            logger.info("📈 Data collection completed successfully!")
            logger.info(f"  - Market data: {len(comprehensive_data.get('market_data', []))} companies")
            logger.info(f"  - News: {len(comprehensive_data.get('news', []))} items")
            logger.info(f"  - Dividends: {len(comprehensive_data.get('dividends', []))} announcements")
            logger.info(f"  - Earnings: {len(comprehensive_data.get('earnings', []))} announcements")
            logger.info(f"  - ETFs: {len(comprehensive_data.get('etfs', []))} ETFs")
            logger.info(f"  - Corporate actions: {len(comprehensive_data.get('corporate_actions', []))} actions")
            logger.info(f"  - Market sentiment: {len(comprehensive_data.get('sentiment', []))} sentiment scores")
            
            # Export data to files for review
            output_dir = Path("comprehensive_data_export")
            output_dir.mkdir(exist_ok=True)
            
            json_file, csv_file = await scraper.export_comprehensive_data(comprehensive_data, output_dir)
            
            logger.info(f"📁 Data exported to:")
            logger.info(f"  - JSON: {json_file}")
            logger.info(f"  - CSV: {csv_file}")
            
            # Now let's populate the database
            logger.info("🗄️ Starting database population...")
            
            # Populate market status
            if comprehensive_data.get('market_status'):
                await scraper.populate_market_status(comprehensive_data['market_status'])
                logger.info("✅ Market status populated")
            
            # Populate comprehensive market data
            if comprehensive_data.get('market_data'):
                await scraper.populate_comprehensive_market_data(comprehensive_data['market_data'])
                logger.info(f"✅ Market data for {len(comprehensive_data['market_data'])} companies populated")
            
            # Populate company news
            if comprehensive_data.get('news'):
                await scraper.populate_company_news(comprehensive_data['news'])
                logger.info(f"✅ Company news populated")
            
            # Populate dividend announcements
            if comprehensive_data.get('dividends'):
                await scraper.populate_dividend_announcements(comprehensive_data['dividends'])
                logger.info(f"✅ Dividend announcements populated")
            
            # Populate earnings announcements
            if comprehensive_data.get('earnings'):
                await scraper.populate_earnings_announcements(comprehensive_data['earnings'])
                logger.info(f"✅ Earnings announcements populated")
            
            # Populate ETF data
            if comprehensive_data.get('etfs'):
                await scraper.populate_etf_data(comprehensive_data['etfs'])
                logger.info(f"✅ ETF data populated")
            
            # Populate corporate actions
            if comprehensive_data.get('corporate_actions'):
                await scraper.populate_corporate_actions(comprehensive_data['corporate_actions'])
                logger.info(f"✅ Corporate actions populated")
            
            # Populate market sentiment
            if comprehensive_data.get('sentiment'):
                await scraper.populate_market_sentiment(comprehensive_data['sentiment'])
                logger.info(f"✅ Market sentiment populated")
            
            logger.info("🎉 Comprehensive data collection and database population completed!")
            logger.info("🌐 Your enhanced frontend now has access to real company profiles!")
            
            return comprehensive_data
            
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Make sure you're running this from the correct directory")
        return None
    except Exception as e:
        logger.error(f"❌ Error during data collection: {e}")
        return None

async def test_database_connection():
    """Test the database connection to Sky Garden"""
    try:
        logger.info("🔍 Testing database connection to Sky Garden...")
        
        # Import the scraper to test connection
        from comprehensive_market_scraper import ComprehensiveMarketScraper
        
        async with ComprehensiveMarketScraper() as scraper:
            # Test a simple query
            test_data = await scraper.test_connection()
            if test_data:
                logger.info("✅ Database connection successful!")
                return True
            else:
                logger.error("❌ Database connection failed")
                return False
                
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False

async def main():
    """Main function"""
    logger.info("🔧 Comprehensive Data Collection Setup")
    logger.info("=" * 50)
    
    # Test database connection first
    if not await test_database_connection():
        logger.error("❌ Cannot proceed without database connection")
        return
    
    # Start comprehensive data collection
    result = await start_comprehensive_data_collection()
    
    if result:
        logger.info("\n🎯 Next Steps:")
        logger.info("1. Check the exported data files in 'comprehensive_data_export/'")
        logger.info("2. Visit your enhanced frontend to see the new data")
        logger.info("3. Set up automated scheduling with Airflow")
        logger.info("4. Monitor data quality and refresh rates")
        
        logger.info("\n🚀 Your enhanced Casablanca Insights platform is now populated with real data!")
    else:
        logger.error("❌ Data collection failed. Check logs for details.")

if __name__ == "__main__":
    asyncio.run(main())
