#!/usr/bin/env python3
"""
Morning Maghreb Comprehensive Market Data Collection Script
Collects data for all 78 companies, bonds, ETFs, and market data
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import scrapers
from apps.backend.etl.african_markets_scraper import AfricanMarketsScraper
from apps.backend.etl.etf_bond_scraper import MoroccanETFBondScraper
from apps.backend.etl.casablanca_bourse_scraper import CasablancaBourseScraper
from apps.backend.etl.bank_al_maghrib_scraper import BankAlMaghribScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/comprehensive_data_collection.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = "https://gzsgehciddnrssuqxtsj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6c2dlaGNpZGRucnNzdXF4dHNqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQxOTk5MSwiZXhwIjoyMDY5OTk1OTkxfQ.RxCuA9XIdNriIEUBk90m9jEZNV11uHAVaQKH76lavX0"


class ComprehensiveDataCollector:
    """Comprehensive data collector for Morning Maghreb"""

    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path("apps/backend/data")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize scrapers
        self.african_markets_scraper = None
        self.etf_bond_scraper = MoroccanETFBondScraper()
        self.casablanca_bourse_scraper = CasablancaBourseScraper()
        self.bank_al_maghrib_scraper = BankAlMaghribScraper()

        # Collection results
        self.results = {
            "companies": [],
            "bonds": [],
            "etfs": [],
            "market_data": {},
            "banking_data": {},
            "metadata": {
                "collection_timestamp": datetime.now().isoformat(),
                "total_companies": 0,
                "total_bonds": 0,
                "total_etfs": 0,
                "success": True,
                "errors": [],
            },
        }

    async def collect_african_markets_data(self):
        """Collect data for all 78 companies from African Markets"""
        try:
            logger.info(
                "🔍 Collecting data for all 78 companies from African Markets..."
            )

            async with AfricanMarketsScraper() as scraper:
                companies = await scraper.scrape_all()

                if companies:
                    self.results["companies"] = companies
                    self.results["metadata"]["total_companies"] = len(companies)
                    logger.info(
                        f"✅ Collected data for {len(companies)} companies from African Markets"
                    )

                    # Save to file
                    output_file = (
                        self.output_dir / f"african_markets_data_{self.timestamp}.json"
                    )
                    with open(output_file, "w") as f:
                        json.dump(companies, f, indent=2)
                    logger.info(f"💾 Saved to: {output_file}")

                    # Show breakdown
                    sectors = {}
                    for company in companies:
                        sector = company.get("sector", "Unknown")
                        sectors[sector] = sectors.get(sector, 0) + 1

                    logger.info("📊 Companies by sector:")
                    for sector, count in sorted(sectors.items()):
                        logger.info(f"  - {sector}: {count}")
                else:
                    logger.warning("⚠️ No companies found from African Markets")
                    self.results["metadata"]["errors"].append(
                        "No companies found from African Markets"
                    )

        except Exception as e:
            logger.error(f"❌ Error collecting African Markets data: {e}")
            self.results["metadata"]["errors"].append(
                f"African Markets error: {str(e)}"
            )

    def collect_etf_bond_data(self):
        """Collect ETF and bond data"""
        try:
            logger.info("📈 Collecting ETF and bond data...")

            # Collect ETF data
            etfs = self.etf_bond_scraper.scrape_all_etfs()
            if etfs:
                self.results["etfs"] = [etf.__dict__ for etf in etfs]
                self.results["metadata"]["total_etfs"] = len(etfs)
                logger.info(f"✅ Collected data for {len(etfs)} ETFs")

                # Save to file
                output_file = self.output_dir / f"moroccan_etfs_{self.timestamp}.json"
                with open(output_file, "w") as f:
                    json.dump([etf.__dict__ for etf in etfs], f, indent=2)
                logger.info(f"💾 Saved to: {output_file}")
            else:
                logger.warning("⚠️ No ETFs found")
                self.results["metadata"]["errors"].append("No ETFs found")

            # Collect bond data
            bonds = self.etf_bond_scraper.scrape_all_bonds()
            if bonds:
                self.results["bonds"] = [bond.__dict__ for bond in bonds]
                self.results["metadata"]["total_bonds"] = len(bonds)
                logger.info(f"✅ Collected data for {len(bonds)} bonds")

                # Save to file
                output_file = self.output_dir / f"moroccan_bonds_{self.timestamp}.json"
                with open(output_file, "w") as f:
                    json.dump([bond.__dict__ for bond in bonds], f, indent=2)
                logger.info(f"💾 Saved to: {output_file}")
            else:
                logger.warning("⚠️ No bonds found")
                self.results["metadata"]["errors"].append("No bonds found")

        except Exception as e:
            logger.error(f"❌ Error collecting ETF/bond data: {e}")
            self.results["metadata"]["errors"].append(f"ETF/Bond error: {str(e)}")

    def collect_casablanca_bourse_data(self):
        """Collect Casablanca Bourse market data"""
        try:
            logger.info("🏛️ Collecting Casablanca Bourse market data...")

            # Collect market data
            market_data = self.casablanca_bourse_scraper.scrape_market_data()
            if market_data:
                self.results["market_data"] = market_data
                logger.info("✅ Collected Casablanca Bourse market data")

                # Save to file
                output_file = (
                    self.output_dir / f"casablanca_bourse_data_{self.timestamp}.json"
                )
                with open(output_file, "w") as f:
                    json.dump(market_data, f, indent=2)
                logger.info(f"💾 Saved to: {output_file}")
            else:
                logger.warning("⚠️ No Casablanca Bourse data found")
                self.results["metadata"]["errors"].append(
                    "No Casablanca Bourse data found"
                )

        except Exception as e:
            logger.error(f"❌ Error collecting Casablanca Bourse data: {e}")
            self.results["metadata"]["errors"].append(
                f"Casablanca Bourse error: {str(e)}"
            )

    def collect_bank_al_maghrib_data(self):
        """Collect Bank Al Maghrib banking data"""
        try:
            logger.info("🏦 Collecting Bank Al Maghrib banking data...")

            # Collect banking data
            banking_data = self.bank_al_maghrib_scraper.scrape_banking_data()
            if banking_data:
                self.results["banking_data"] = banking_data
                logger.info("✅ Collected Bank Al Maghrib banking data")

                # Save to file
                output_file = (
                    self.output_dir / f"bank_al_maghrib_data_{self.timestamp}.json"
                )
                with open(output_file, "w") as f:
                    json.dump(banking_data, f, indent=2)
                logger.info(f"💾 Saved to: {output_file}")
            else:
                logger.warning("⚠️ No Bank Al Maghrib data found")
                self.results["metadata"]["errors"].append(
                    "No Bank Al Maghrib data found"
                )

        except Exception as e:
            logger.error(f"❌ Error collecting Bank Al Maghrib data: {e}")
            self.results["metadata"]["errors"].append(
                f"Bank Al Maghrib error: {str(e)}"
            )

    def update_supabase_database(self):
        """Update Supabase database with collected data"""
        try:
            logger.info("🗄️ Updating Supabase database...")

            import requests

            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            }

            # Update companies
            for company in self.results.get("companies", []):
                try:
                    response = requests.post(
                        f"{SUPABASE_URL}/rest/v1/companies",
                        headers=headers,
                        json=company,
                    )
                    if response.status_code in [200, 201]:
                        logger.info(
                            f"✅ Updated {company.get('ticker', 'Unknown')} in database"
                        )
                    else:
                        logger.warning(
                            f"⚠️ Failed to update {company.get('ticker', 'Unknown')}: {response.status_code}"
                        )
                except Exception as e:
                    logger.error(
                        f"❌ Error updating company {company.get('ticker', 'Unknown')}: {e}"
                    )

            # Update bonds
            for bond in self.results.get("bonds", []):
                try:
                    response = requests.post(
                        f"{SUPABASE_URL}/rest/v1/bonds", headers=headers, json=bond
                    )
                    if response.status_code in [200, 201]:
                        logger.info(
                            f"✅ Updated bond {bond.get('ticker', 'Unknown')} in database"
                        )
                    else:
                        logger.warning(
                            f"⚠️ Failed to update bond {bond.get('ticker', 'Unknown')}: {response.status_code}"
                        )
                except Exception as e:
                    logger.error(
                        f"❌ Error updating bond {bond.get('ticker', 'Unknown')}: {e}"
                    )

            # Update ETFs
            for etf in self.results.get("etfs", []):
                try:
                    response = requests.post(
                        f"{SUPABASE_URL}/rest/v1/etfs", headers=headers, json=etf
                    )
                    if response.status_code in [200, 201]:
                        logger.info(
                            f"✅ Updated ETF {etf.get('ticker', 'Unknown')} in database"
                        )
                    else:
                        logger.warning(
                            f"⚠️ Failed to update ETF {etf.get('ticker', 'Unknown')}: {response.status_code}"
                        )
                except Exception as e:
                    logger.error(
                        f"❌ Error updating ETF {etf.get('ticker', 'Unknown')}: {e}"
                    )

            logger.info("✅ Database update completed")
            return True

        except Exception as e:
            logger.error(f"❌ Error updating database: {e}")
            self.results["metadata"]["errors"].append(f"Database error: {str(e)}")
            return False

    def save_comprehensive_results(self):
        """Save comprehensive results to file"""
        try:
            output_file = (
                self.output_dir / f"comprehensive_market_data_{self.timestamp}.json"
            )
            with open(output_file, "w") as f:
                json.dump(self.results, f, indent=2)
            logger.info(f"💾 Saved comprehensive results to: {output_file}")
        except Exception as e:
            logger.error(f"❌ Error saving comprehensive results: {e}")

    def print_summary(self):
        """Print collection summary"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 COMPREHENSIVE DATA COLLECTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"📈 Companies: {self.results['metadata']['total_companies']}")
        logger.info(f"📊 Bonds: {self.results['metadata']['total_bonds']}")
        logger.info(f"📈 ETFs: {self.results['metadata']['total_etfs']}")
        logger.info(f"🏛️ Market Data: {'✅' if self.results['market_data'] else '❌'}")
        logger.info(
            f"🏦 Banking Data: {'✅' if self.results['banking_data'] else '❌'}"
        )

        if self.results["metadata"]["errors"]:
            logger.info(f"\n❌ Errors: {len(self.results['metadata']['errors'])}")
            for error in self.results["metadata"]["errors"]:
                logger.info(f"  - {error}")

        logger.info("=" * 60)

    async def run_comprehensive_collection(self):
        """Run comprehensive data collection"""
        logger.info("🚀 Starting Morning Maghreb comprehensive data collection...")
        logger.info("=" * 60)

        try:
            # Collect all data sources
            await self.collect_african_markets_data()
            self.collect_etf_bond_data()
            self.collect_casablanca_bourse_data()
            self.collect_bank_al_maghrib_data()

            # Update database
            db_success = self.update_supabase_database()

            # Save comprehensive results
            self.save_comprehensive_results()

            # Print summary
            self.print_summary()

            if self.results["metadata"]["errors"]:
                self.results["metadata"]["success"] = False
                logger.warning("⚠️ Collection completed with errors")
            else:
                logger.info("🎉 Comprehensive data collection completed successfully!")

        except Exception as e:
            logger.error(f"❌ Fatal error in comprehensive collection: {e}")
            self.results["metadata"]["success"] = False
            self.results["metadata"]["errors"].append(f"Fatal error: {str(e)}")


async def main():
    """Main function"""
    collector = ComprehensiveDataCollector()
    await collector.run_comprehensive_collection()


if __name__ == "__main__":
    asyncio.run(main())
