#!/usr/bin/env python3
"""
Simple ETL Pipeline Runner for Casablanca Insights
Runs the data pipeline without Airflow
"""

import os
import sys
import json
import csv
from datetime import datetime
from typing import Dict, List, Any

# Add the backend directory to the path
backend_path = os.path.join(os.path.dirname(__file__), "..", "apps", "backend")
sys.path.insert(0, backend_path)


def load_env():
    """Load environment variables from .env file"""
    env_file = os.path.join(os.path.dirname(__file__), "..", "apps", "web", ".env")
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value
        print(f"✅ Loaded environment from: {env_file}")
    else:
        print(f"❌ Environment file not found at: {env_file}")


def run_market_data_scraper():
    """Run the market data scraper"""
    print("📊 Running Market Data Scraper...")

    try:
        # Import the scraper
        from etl.african_markets_scraper import AfricanMarketsScraper
        import asyncio

        async def scrape():
            async with AfricanMarketsScraper() as scraper:
                return await scraper.scrape_all()

        data = asyncio.run(scrape())
        print(f"✅ Market data scraped: {len(data)} companies")
        return data

    except Exception as e:
        print(f"❌ Error running market scraper: {str(e)}")
        return None


def run_bank_al_maghrib_scraper():
    """Run the Bank Al Maghrib scraper"""
    print("🏦 Running Bank Al Maghrib Scraper...")

    try:
        # Import the scraper
        from etl.bank_al_maghrib_scraper import BankAlMaghribScraper
        import asyncio

        async def scrape():
            async with BankAlMaghribScraper() as scraper:
                return await scraper.scrape_all()

        data = asyncio.run(scrape())
        print(f"✅ Bank data scraped: {len(data)} records")
        return data

    except Exception as e:
        print(f"❌ Error running bank scraper: {str(e)}")
        return None


def sync_data_to_supabase():
    """Sync scraped data to Supabase"""
    print("🔄 Syncing data to Supabase...")

    try:
        # Import the deployment script
        from scripts.deployment.deploy_to_supabase_simple import SimpleSupabaseDeployer

        deployer = SimpleSupabaseDeployer()

        # Sync company data
        print("📊 Syncing company data...")
        deployer.sync_company_data()

        # Load OHLCV data
        print("📈 Loading OHLCV data...")
        deployer.load_ohlcv_data()

        print("✅ Data synced to Supabase successfully!")
        return True

    except Exception as e:
        print(f"❌ Error syncing to Supabase: {str(e)}")
        return False


def main():
    """Main ETL pipeline runner"""
    print("🚀 Starting Casablanca Insights ETL Pipeline")
    print("=" * 50)

    # Load environment variables
    load_env()

    # Check if Supabase is configured
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    if not supabase_url:
        print("❌ Supabase not configured. Please check your .env file.")
        return False

    print(f"✅ Supabase configured: {supabase_url}")

    # Run scrapers
    market_data = run_market_data_scraper()
    bank_data = run_bank_al_maghrib_scraper()

    # Sync to Supabase
    if market_data or bank_data:
        success = sync_data_to_supabase()
        if success:
            print("\n🎉 ETL Pipeline completed successfully!")
            print("\n📊 Data Summary:")
            if market_data:
                print(f"   • Market data: {len(market_data)} companies")
            if bank_data:
                print(f"   • Bank data: {len(bank_data)} records")
            print("\n🌐 Your website should now have real data!")
            return True
        else:
            print("\n❌ Failed to sync data to Supabase")
            return False
    else:
        print("\n❌ No data was scraped")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
