#!/usr/bin/env python3
"""
Morning Maghreb Market Data Collection Script
Runs daily to collect and update market data
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from apps.backend.etl.african_markets_scraper import AfricanMarketsScraper
from apps.backend.etl.casablanca_bourse_scraper import CasablancaBourseScraper
from apps.backend.etl.bank_al_maghrib_scraper import BankAlMaghribScraper
from apps.backend.services.data_service import DataService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def collect_african_markets_data():
    """Collect data from African Markets"""
    try:
        logger.info("Starting African Markets data collection...")
        scraper = AfricanMarketsScraper()
        data = scraper.scrape_all_companies()
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"apps/backend/data/african_markets_data_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"✅ African Markets data collected: {len(data)} companies")
        return data
    except Exception as e:
        logger.error(f"❌ Error collecting African Markets data: {e}")
        return None

def collect_casablanca_bourse_data():
    """Collect data from Casablanca Bourse"""
    try:
        logger.info("Starting Casablanca Bourse data collection...")
        scraper = CasablancaBourseScraper()
        data = scraper.scrape_market_data()
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"apps/backend/data/casablanca_bourse_data_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"✅ Casablanca Bourse data collected")
        return data
    except Exception as e:
        logger.error(f"❌ Error collecting Casablanca Bourse data: {e}")
        return None

def collect_bank_al_maghrib_data():
    """Collect data from Bank Al Maghrib"""
    try:
        logger.info("Starting Bank Al Maghrib data collection...")
        scraper = BankAlMaghribScraper()
        data = scraper.scrape_banking_data()
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"apps/backend/data/bank_al_maghrib_data_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"✅ Bank Al Maghrib data collected")
        return data
    except Exception as e:
        logger.error(f"❌ Error collecting Bank Al Maghrib data: {e}")
        return None

def update_database():
    """Update Supabase database with collected data"""
    try:
        logger.info("Updating database with collected data...")
        
        # Initialize data service with new database credentials
        data_service = DataService(
            supabase_url="https://gzsgehciddnrssuqxtsj.supabase.co",
            supabase_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6c2dlaGNpZGRucnNzdXF4dHNqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQxOTk5MSwiZXhwIjoyMDY5OTk1OTkxfQ.RxCuA9XIdNriIEUBk90m9jEZNV11uHAVaQKH76lavX0"
        )
        
        # Update companies data
        data_service.update_companies_data()
        
        # Update market data
        data_service.update_market_data()
        
        # Update banking data
        data_service.update_banking_data()
        
        logger.info("✅ Database updated successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error updating database: {e}")
        return False

def send_notification(success=True):
    """Send notification about data collection status"""
    try:
        if success:
            message = "✅ Morning Maghreb data collection completed successfully"
        else:
            message = "❌ Morning Maghreb data collection failed"
        
        # You can add email/Slack notification here
        logger.info(message)
        
    except Exception as e:
        logger.error(f"❌ Error sending notification: {e}")

def main():
    """Main data collection function"""
    logger.info("🚀 Starting Morning Maghreb daily data collection...")
    
    success = True
    
    try:
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Collect data from all sources
        african_data = collect_african_markets_data()
        bourse_data = collect_casablanca_bourse_data()
        banking_data = collect_bank_al_maghrib_data()
        
        # Update database
        if african_data or bourse_data or banking_data:
            db_success = update_database()
            if not db_success:
                success = False
        else:
            logger.warning("⚠️ No data collected, skipping database update")
            success = False
        
        # Send notification
        send_notification(success)
        
        if success:
            logger.info("🎉 Data collection completed successfully!")
        else:
            logger.error("❌ Data collection completed with errors")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Fatal error in data collection: {e}")
        send_notification(False)
        sys.exit(1)

if __name__ == "__main__":
    main()
