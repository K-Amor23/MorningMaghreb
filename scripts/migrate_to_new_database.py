#!/usr/bin/env python3
"""
Database Migration Script for Morning Maghreb
Migrates from old database to new Supabase database
"""

import os
import sys
import json
import asyncio
import logging
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from supabase import create_client, Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("migration.log"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """Handles database migration from old to new Supabase"""

    def __init__(self):
        self.old_supabase_url = "https://kszekypwdjqaycpuayda.supabase.co"
        self.old_supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtzZXlwd2RqYXljcHVheWRhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjE2ODE1NSwiZXhwIjoyMDY3NzQ0MTU1fQ.7iA4blj2cdFTQcBo4IVP1w71psgqdJAEc83ht_YVueY"

        self.new_supabase_url = "https://gzsgehciddnrssuqxtsj.supabase.co"
        self.new_supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6c2dlaGNpZGRucnNzdXF4dHNqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQxOTk5MSwiZXhwIjoyMDY5OTk1OTkxfQ.RxCuA9XIdNriIEUBk90m9jEZNV11uHAVaQKH76lavX0"

        self.old_client = create_client(self.old_supabase_url, self.old_supabase_key)
        self.new_client = create_client(self.new_supabase_url, self.new_supabase_key)

        self.migration_stats = {
            "tables_created": 0,
            "records_migrated": 0,
            "errors": [],
        }

    async def migrate_database(self) -> bool:
        """Main migration process"""
        logger.info("🚀 Starting database migration...")

        try:
            # 1. Create schema in new database
            if not await self._create_schema():
                return False

            # 2. Migrate data from old to new database
            if not await self._migrate_data():
                return False

            # 3. Verify migration
            if not await self._verify_migration():
                return False

            logger.info("✅ Database migration completed successfully!")
            self._print_migration_summary()
            return True

        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False

    async def _create_schema(self) -> bool:
        """Create complete schema in new database"""
        logger.info("📋 Creating database schema...")

        try:
            # Read the complete schema file
            schema_file = Path("database/complete_supabase_schema.sql")
            if not schema_file.exists():
                logger.error(f"❌ Schema file not found: {schema_file}")
                return False

            with open(schema_file, "r") as f:
                schema_sql = f.read()

            # Execute schema creation
            result = self.new_client.rpc("exec_sql", {"sql": schema_sql}).execute()

            logger.info("✅ Schema created successfully")
            self.migration_stats["tables_created"] = 1
            return True

        except Exception as e:
            logger.error(f"❌ Error creating schema: {e}")
            self.migration_stats["errors"].append(f"Schema creation: {e}")
            return False

    async def _migrate_data(self) -> bool:
        """Migrate data from old to new database"""
        logger.info("📊 Migrating data...")

        # Define tables to migrate
        tables_to_migrate = [
            "companies",
            "company_prices",
            "company_reports",
            "company_news",
            "profiles",
            "watchlists",
            "watchlist_items",
            "price_alerts",
            "sentiment_votes",
            "sentiment_aggregates",
            "newsletter_subscribers",
            "newsletter_campaigns",
            "contests",
            "contest_entries",
            "contest_prizes",
            "contest_notifications",
            "paper_trading_accounts",
            "paper_trading_orders",
            "paper_trading_positions",
            "portfolios",
            "portfolio_holdings",
            "ai_summaries",
            "chat_queries",
            "user_profiles",
            "cse_companies",
            "market_data",
        ]

        total_migrated = 0

        for table in tables_to_migrate:
            try:
                logger.info(f"🔄 Migrating table: {table}")

                # Get data from old database
                old_data = self.old_client.table(table).select("*").execute()

                if old_data.data:
                    # Insert into new database
                    result = (
                        self.new_client.table(table).upsert(old_data.data).execute()
                    )

                    migrated_count = len(old_data.data)
                    total_migrated += migrated_count

                    logger.info(f"✅ Migrated {migrated_count} records from {table}")
                else:
                    logger.info(f"ℹ️ No data found in {table}")

            except Exception as e:
                logger.warning(f"⚠️ Error migrating {table}: {e}")
                self.migration_stats["errors"].append(f"{table}: {e}")
                continue

        self.migration_stats["records_migrated"] = total_migrated
        logger.info(
            f"✅ Data migration completed. Total records migrated: {total_migrated}"
        )
        return True

    async def _verify_migration(self) -> bool:
        """Verify that migration was successful"""
        logger.info("🔍 Verifying migration...")

        try:
            # Check key tables have data
            key_tables = ["companies", "profiles", "watchlists"]

            for table in key_tables:
                try:
                    result = (
                        self.new_client.table(table)
                        .select("count", count="exact")
                        .execute()
                    )
                    count = (
                        result.count if hasattr(result, "count") else len(result.data)
                    )
                    logger.info(f"✅ {table}: {count} records")
                except Exception as e:
                    logger.warning(f"⚠️ Could not verify {table}: {e}")

            # Test a simple query
            companies = (
                self.new_client.table("companies")
                .select("ticker, name")
                .limit(5)
                .execute()
            )
            if companies.data:
                logger.info("✅ Database is accessible and contains data")
                return True
            else:
                logger.warning("⚠️ Database accessible but no data found")
                return False

        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return False

    def _print_migration_summary(self):
        """Print migration summary"""
        print("\n" + "=" * 50)
        print("📊 MIGRATION SUMMARY")
        print("=" * 50)
        print(f"✅ Tables created: {self.migration_stats['tables_created']}")
        print(f"✅ Records migrated: {self.migration_stats['records_migrated']}")

        if self.migration_stats["errors"]:
            print(f"⚠️ Errors encountered: {len(self.migration_stats['errors'])}")
            for error in self.migration_stats["errors"]:
                print(f"   - {error}")

        print("=" * 50)
        print("🎉 Migration completed successfully!")
        print("=" * 50)


async def main():
    """Main migration function"""
    migrator = DatabaseMigrator()

    print("🚀 Morning Maghreb Database Migration")
    print("=" * 50)
    print(f"📤 Source: {migrator.old_supabase_url}")
    print(f"📥 Destination: {migrator.new_supabase_url}")
    print("=" * 50)

    success = await migrator.migrate_database()

    if success:
        print("\n🎉 Migration completed successfully!")
        print("Your new database is ready to use.")
    else:
        print("\n❌ Migration failed. Check the logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
