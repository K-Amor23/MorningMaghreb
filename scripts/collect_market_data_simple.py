#!/usr/bin/env python3
"""
Morning Maghreb Market Data Collection Script (Simple Version)
Runs daily to collect and update market data
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from pathlib import Path

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

# Supabase configuration
SUPABASE_URL = "https://gzsgehciddnrssuqxtsj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6c2dlaGNpZGRucnNzdXF4dHNqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQxOTk5MSwiZXhwIjoyMDY5OTk1OTkxfQ.RxCuA9XIdNriIEUBk90m9jEZNV11uHAVaQKH76lavX0"

def collect_mock_market_data():
    """Collect mock market data for testing"""
    try:
        logger.info("Starting mock market data collection...")
        
        # Mock data for testing
        mock_data = {
            "companies": [
                {
                    "ticker": "ATW",
                    "name": "Attijariwafa Bank",
                    "sector": "Banking",
                    "price": 410.10,
                    "change_1d_percent": 0.31,
                    "change_ytd_percent": 5.25,
                    "market_cap_billion": 24.56,
                    "size_category": "Large Cap",
                    "sector_group": "Financial Services",
                    "updated_at": datetime.now().isoformat()
                },
                {
                    "ticker": "IAM",
                    "name": "Maroc Telecom",
                    "sector": "Telecommunications",
                    "price": 156.30,
                    "change_1d_percent": -1.33,
                    "change_ytd_percent": -2.15,
                    "market_cap_billion": 15.68,
                    "size_category": "Large Cap",
                    "sector_group": "Telecommunications",
                    "updated_at": datetime.now().isoformat()
                },
                {
                    "ticker": "BCP",
                    "name": "Banque Centrale Populaire",
                    "sector": "Banking",
                    "price": 245.80,
                    "change_1d_percent": 0.85,
                    "change_ytd_percent": 3.42,
                    "market_cap_billion": 18.92,
                    "size_category": "Large Cap",
                    "sector_group": "Financial Services",
                    "updated_at": datetime.now().isoformat()
                },
                {
                    "ticker": "BMCE",
                    "name": "BMCE Bank",
                    "sector": "Banking",
                    "price": 189.50,
                    "change_1d_percent": -0.52,
                    "change_ytd_percent": 1.87,
                    "market_cap_billion": 12.34,
                    "size_category": "Large Cap",
                    "sector_group": "Financial Services",
                    "updated_at": datetime.now().isoformat()
                }
            ],
            "market_summary": {
                "total_companies": 4,
                "total_market_cap": 71.5,
                "average_change_1d": -0.17,
                "average_change_ytd": 2.10,
                "updated_at": datetime.now().isoformat()
            }
        }
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"apps/backend/data/mock_market_data_{timestamp}.json"
        
        os.makedirs("apps/backend/data", exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(mock_data, f, indent=2)
        
        logger.info(f"✅ Mock market data collected: {len(mock_data['companies'])} companies")
        return mock_data
    except Exception as e:
        logger.error(f"❌ Error collecting mock market data: {e}")
        return None

def update_supabase_database(data):
    """Update Supabase database with collected data"""
    try:
        logger.info("Updating Supabase database...")
        
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        # Update companies table
        for company in data.get("companies", []):
            company_data = {
                "ticker": company["ticker"],
                "name": company["name"],
                "sector": company["sector"],
                "price": company["price"],
                "change_1d_percent": company["change_1d_percent"],
                "change_ytd_percent": company["change_ytd_percent"],
                "market_cap_billion": company["market_cap_billion"],
                "size_category": company["size_category"],
                "sector_group": company["sector_group"],
                "updated_at": company["updated_at"]
            }
            
            # Upsert company data
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/companies",
                headers=headers,
                json=company_data
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Updated {company['ticker']} in database")
            else:
                logger.warning(f"⚠️ Failed to update {company['ticker']}: {response.status_code}")
        
        # Update market summary
        summary_data = data.get("market_summary", {})
        if summary_data:
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/market_summary",
                headers=headers,
                json=summary_data
            )
            
            if response.status_code in [200, 201]:
                logger.info("✅ Updated market summary in database")
            else:
                logger.warning(f"⚠️ Failed to update market summary: {response.status_code}")
        
        logger.info("✅ Database update completed")
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
        
        logger.info(message)
        
        # You can add email/Slack notification here
        # For now, just log the message
        
    except Exception as e:
        logger.error(f"❌ Error sending notification: {e}")

def main():
    """Main data collection function"""
    logger.info("🚀 Starting Morning Maghreb daily data collection...")
    
    success = True
    
    try:
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Collect mock data (replace with real scrapers when available)
        data = collect_mock_market_data()
        
        if data:
            # Update database
            db_success = update_supabase_database(data)
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