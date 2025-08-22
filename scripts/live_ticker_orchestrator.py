#!/usr/bin/env python3
"""
Morning Maghreb Live Ticker Orchestrator
Real-time data collection from multiple sources every few minutes
"""

import os
import sys
import json
import logging
import asyncio
import time
import schedule
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
from dataclasses import dataclass, asdict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import scrapers
from apps.backend.etl.african_markets_scraper import AfricanMarketsScraper
from apps.backend.etl.casablanca_bourse_scraper import CasablancaBourseScraper
from apps.backend.etl.wafabourse_scraper import WafaBourseScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/live_ticker_orchestrator.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = "https://gzsgehciddnrssuqxtsj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6c2dlaGNpZGRucnNzdXF4dHNqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQxOTk5MSwiZXhwIjoyMDY5OTk1OTkxfQ.RxCuA9XIdNriIEUBk90m9jEZNV11uHAVaQKH76lavX0"


@dataclass
class LiveTickerData:
    """Live ticker data structure"""

    ticker: str
    name: str
    price: float
    change_1d_percent: Optional[float]
    change_ytd_percent: Optional[float]
    volume: Optional[int]
    market_cap_billion: Optional[float]
    high_24h: Optional[float]
    low_24h: Optional[float]
    open_price: Optional[float]
    previous_close: Optional[float]
    source: str
    timestamp: str
    exchange: str = "Casablanca Stock Exchange"
    country: str = "Morocco"


class LiveTickerOrchestrator:
    """Orchestrates real-time ticker data collection from multiple sources"""

    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path("apps/backend/data/live_tickers")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Priority companies for live tracking
        self.priority_tickers = [
            "ATW",
            "IAM",
            "BCP",
            "BMCE",
            "CIH",
            "WAA",
            "SAH",
            "ADH",
            "LBV",
            "MAR",
            "LES",
            "CEN",
            "HOL",
            "LAF",
            "MSA",
            "TMA",
        ]

        # Initialize scrapers
        self.african_markets_scraper = None
        self.casablanca_bourse_scraper = CasablancaBourseScraper()
        self.wafa_bourse_scraper = WafaBourseScraper()

        # Data cache
        self.live_data_cache = {}
        self.last_update = {}
        self.error_count = {}

        # Configuration
        self.update_interval_minutes = 5  # Update every 5 minutes
        self.max_retries = 3
        self.retry_delay_seconds = 30

        # Statistics
        self.stats = {
            "total_updates": 0,
            "successful_updates": 0,
            "failed_updates": 0,
            "last_run": None,
            "start_time": datetime.now().isoformat(),
        }

    async def scrape_african_markets_live(self) -> List[LiveTickerData]:
        """Scrape live data from African Markets"""
        try:
            logger.info("🔍 Scraping live data from African Markets...")

            async with AfricanMarketsScraper() as scraper:
                companies = await scraper.scrape_all()

                live_data = []
                for company in companies:
                    if company.get("ticker") in self.priority_tickers:
                        ticker_data = LiveTickerData(
                            ticker=company.get("ticker", ""),
                            name=company.get("name", ""),
                            price=company.get("price", 0.0),
                            change_1d_percent=company.get("change_1d_percent"),
                            change_ytd_percent=company.get("change_ytd_percent"),
                            volume=company.get("volume"),
                            market_cap_billion=company.get("market_cap_billion"),
                            high_24h=None,  # Not available from African Markets
                            low_24h=None,
                            open_price=None,
                            previous_close=None,
                            source="African Markets",
                            timestamp=datetime.now().isoformat(),
                        )
                        live_data.append(ticker_data)

                logger.info(
                    f"✅ Collected live data for {len(live_data)} priority companies from African Markets"
                )
                return live_data

        except Exception as e:
            logger.error(f"❌ Error scraping African Markets live data: {e}")
            return []

    def scrape_casablanca_bourse_live(self) -> List[LiveTickerData]:
        """Scrape live data from Casablanca Bourse"""
        try:
            logger.info("🏛️ Scraping live data from Casablanca Bourse...")

            # Get live market data
            market_data = self.casablanca_bourse_scraper.scrape_market_data()

            live_data = []
            if market_data and "companies" in market_data:
                for company in market_data["companies"]:
                    if company.get("ticker") in self.priority_tickers:
                        ticker_data = LiveTickerData(
                            ticker=company.get("ticker", ""),
                            name=company.get("name", ""),
                            price=company.get("price", 0.0),
                            change_1d_percent=company.get("change_1d_percent"),
                            change_ytd_percent=company.get("change_ytd_percent"),
                            volume=company.get("volume"),
                            market_cap_billion=company.get("market_cap_billion"),
                            high_24h=company.get("high_24h"),
                            low_24h=company.get("low_24h"),
                            open_price=company.get("open_price"),
                            previous_close=company.get("previous_close"),
                            source="Casablanca Bourse",
                            timestamp=datetime.now().isoformat(),
                        )
                        live_data.append(ticker_data)

            logger.info(
                f"✅ Collected live data for {len(live_data)} priority companies from Casablanca Bourse"
            )
            return live_data

        except Exception as e:
            logger.error(f"❌ Error scraping Casablanca Bourse live data: {e}")
            return []

    def scrape_wafa_bourse_live(self) -> List[LiveTickerData]:
        """Scrape live data from Wafa Bourse"""
        try:
            logger.info("📊 Scraping live data from Wafa Bourse...")

            # Get live market data
            market_data = self.wafa_bourse_scraper.scrape_live_data()

            live_data = []
            if market_data:
                for company in market_data:
                    if company.get("ticker") in self.priority_tickers:
                        ticker_data = LiveTickerData(
                            ticker=company.get("ticker", ""),
                            name=company.get("name", ""),
                            price=company.get("price", 0.0),
                            change_1d_percent=company.get("change_1d_percent"),
                            change_ytd_percent=company.get("change_ytd_percent"),
                            volume=company.get("volume"),
                            market_cap_billion=company.get("market_cap_billion"),
                            high_24h=company.get("high_24h"),
                            low_24h=company.get("low_24h"),
                            open_price=company.get("open_price"),
                            previous_close=company.get("previous_close"),
                            source="Wafa Bourse",
                            timestamp=datetime.now().isoformat(),
                        )
                        live_data.append(ticker_data)

            logger.info(
                f"✅ Collected live data for {len(live_data)} priority companies from Wafa Bourse"
            )
            return live_data

        except Exception as e:
            logger.error(f"❌ Error scraping Wafa Bourse live data: {e}")
            return []

    def merge_live_data(
        self, data_sources: List[List[LiveTickerData]]
    ) -> List[LiveTickerData]:
        """Merge data from multiple sources, prioritizing the most recent/reliable"""
        merged_data = {}

        for source_data in data_sources:
            for ticker_data in source_data:
                ticker = ticker_data.ticker

                # Keep the most recent data for each ticker
                if (
                    ticker not in merged_data
                    or ticker_data.timestamp > merged_data[ticker].timestamp
                ):
                    merged_data[ticker] = ticker_data

        return list(merged_data.values())

    def update_supabase_live_tickers(self, live_data: List[LiveTickerData]):
        """Update Supabase with live ticker data"""
        try:
            logger.info("🗄️ Updating Supabase with live ticker data...")

            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            }

            updated_count = 0
            for ticker_data in live_data:
                try:
                    # Convert dataclass to dict
                    data_dict = asdict(ticker_data)

                    response = requests.post(
                        f"{SUPABASE_URL}/rest/v1/live_tickers",
                        headers=headers,
                        json=data_dict,
                    )

                    if response.status_code in [200, 201]:
                        logger.info(
                            f"✅ Updated live ticker {ticker_data.ticker} in database"
                        )
                        updated_count += 1
                    else:
                        logger.warning(
                            f"⚠️ Failed to update {ticker_data.ticker}: {response.status_code}"
                        )

                except Exception as e:
                    logger.error(f"❌ Error updating {ticker_data.ticker}: {e}")

            logger.info(f"✅ Updated {updated_count} live tickers in database")
            return updated_count > 0

        except Exception as e:
            logger.error(f"❌ Error updating Supabase: {e}")
            return False

    def save_live_data_to_file(self, live_data: List[LiveTickerData]):
        """Save live data to JSON file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"live_tickers_{timestamp}.json"

            # Convert dataclasses to dicts
            data_dicts = [asdict(ticker_data) for ticker_data in live_data]

            with open(output_file, "w") as f:
                json.dump(
                    {
                        "metadata": {
                            "timestamp": timestamp,
                            "total_tickers": len(live_data),
                            "sources": list(set([d.source for d in live_data])),
                            "update_interval_minutes": self.update_interval_minutes,
                        },
                        "live_tickers": data_dicts,
                    },
                    f,
                    indent=2,
                )

            logger.info(f"💾 Saved live ticker data to: {output_file}")

        except Exception as e:
            logger.error(f"❌ Error saving live data: {e}")

    def print_live_summary(self, live_data: List[LiveTickerData]):
        """Print live ticker summary"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 LIVE TICKER DATA SUMMARY")
        logger.info("=" * 60)
        logger.info(f"📈 Total tickers: {len(live_data)}")
        logger.info(f"⏰ Update interval: {self.update_interval_minutes} minutes")
        logger.info(f"🕐 Last update: {datetime.now().strftime('%H:%M:%S')}")

        # Show top movers
        gainers = [
            d for d in live_data if d.change_1d_percent and d.change_1d_percent > 0
        ]
        losers = [
            d for d in live_data if d.change_1d_percent and d.change_1d_percent < 0
        ]

        if gainers:
            logger.info(f"\n📈 Top Gainers:")
            for ticker in sorted(
                gainers, key=lambda x: x.change_1d_percent or 0, reverse=True
            )[:5]:
                logger.info(
                    f"  {ticker.ticker}: {ticker.change_1d_percent:.2f}% (${ticker.price:.2f})"
                )

        if losers:
            logger.info(f"\n📉 Top Losers:")
            for ticker in sorted(losers, key=lambda x: x.change_1d_percent or 0)[:5]:
                logger.info(
                    f"  {ticker.ticker}: {ticker.change_1d_percent:.2f}% (${ticker.price:.2f})"
                )

        logger.info("=" * 60)

    async def run_live_update(self):
        """Run a single live update cycle"""
        try:
            logger.info(
                f"🚀 Starting live ticker update at {datetime.now().strftime('%H:%M:%S')}"
            )

            # Collect data from all sources
            african_data = await self.scrape_african_markets_live()
            casablanca_data = self.scrape_casablanca_bourse_live()
            wafa_data = self.scrape_wafa_bourse_live()

            # Merge data from all sources
            all_data = [african_data, casablanca_data, wafa_data]
            live_data = self.merge_live_data(all_data)

            if live_data:
                # Update database
                db_success = self.update_supabase_live_tickers(live_data)

                # Save to file
                self.save_live_data_to_file(live_data)

                # Print summary
                self.print_live_summary(live_data)

                # Update statistics
                self.stats["total_updates"] += 1
                if db_success:
                    self.stats["successful_updates"] += 1
                else:
                    self.stats["failed_updates"] += 1

                self.stats["last_run"] = datetime.now().isoformat()

                logger.info("✅ Live ticker update completed successfully!")
            else:
                logger.warning("⚠️ No live data collected")
                self.stats["failed_updates"] += 1

        except Exception as e:
            logger.error(f"❌ Error in live update: {e}")
            self.stats["failed_updates"] += 1

    def start_live_orchestrator(self):
        """Start the live ticker orchestrator"""
        logger.info("🚀 Starting Morning Maghreb Live Ticker Orchestrator...")
        logger.info(f"⏰ Update interval: {self.update_interval_minutes} minutes")
        logger.info(f"📈 Priority tickers: {', '.join(self.priority_tickers)}")
        logger.info("=" * 60)

        # Schedule the update job
        schedule.every(self.update_interval_minutes).minutes.do(
            lambda: asyncio.run(self.run_live_update())
        )

        # Run initial update
        asyncio.run(self.run_live_update())

        # Keep running
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                logger.info("🛑 Live ticker orchestrator stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in orchestrator loop: {e}")
                time.sleep(10)


async def main():
    """Main function for testing"""
    orchestrator = LiveTickerOrchestrator()
    await orchestrator.run_live_update()


def start_orchestrator():
    """Start the orchestrator"""
    orchestrator = LiveTickerOrchestrator()
    orchestrator.start_live_orchestrator()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run single test
        asyncio.run(main())
    else:
        # Start orchestrator
        start_orchestrator()
