#!/usr/bin/env python3
"""
Simple Data Migration Script for Morning Maghreb
Migrates data from old database to new Supabase database
"""

import os
import sys
import json
from supabase import create_client, Client


def load_env():
    """Load environment variables"""
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


def migrate_data():
    """Migrate data from old to new database"""

    # Load environment
    load_env()

    # Database credentials
    old_supabase_url = "https://kszekypwdjqaycpuayda.supabase.co"
    old_supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtzZXlwd2RqYXljcHVheWRhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjE2ODE1NSwiZXhwIjoyMDY3NzQ0MTU1fQ.7iA4blj2cdFTQcBo4IVP1w71psgqdJAEc83ht_YVueY"

    new_supabase_url = "https://gzsgehciddnrssuqxtsj.supabase.co"
    new_supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6c2dlaGNpZGRucnNzdXF4dHNqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQxOTk5MSwiZXhwIjoyMDY5OTk1OTkxfQ.RxCuA9XIdNriIEUBk90m9jEZNV11uHAVaQKH76lavX0"

    # Initialize clients
    old_client = create_client(old_supabase_url, old_supabase_key)
    new_client = create_client(new_supabase_url, new_supabase_key)

    print("🚀 Starting data migration...")
    print("=" * 50)
    print(f"📤 Source: {old_supabase_url}")
    print(f"📥 Destination: {new_supabase_url}")
    print("=" * 50)

    # Tables to migrate (in order of dependencies)
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
    errors = []

    for table in tables_to_migrate:
        try:
            print(f"🔄 Migrating table: {table}")

            # Get data from old database
            old_data = old_client.table(table).select("*").execute()

            if old_data.data:
                # Insert into new database
                result = new_client.table(table).upsert(old_data.data).execute()

                migrated_count = len(old_data.data)
                total_migrated += migrated_count

                print(f"✅ Migrated {migrated_count} records from {table}")
            else:
                print(f"ℹ️ No data found in {table}")

        except Exception as e:
            error_msg = f"Error migrating {table}: {str(e)}"
            print(f"❌ {error_msg}")
            errors.append(error_msg)
            continue

    # Print summary
    print("\n" + "=" * 50)
    print("📊 MIGRATION SUMMARY")
    print("=" * 50)
    print(f"✅ Total records migrated: {total_migrated}")
    print(f"✅ Tables processed: {len(tables_to_migrate)}")

    if errors:
        print(f"❌ Errors encountered: {len(errors)}")
        for error in errors:
            print(f"   - {error}")
    else:
        print("✅ No errors encountered!")

    print("=" * 50)
    print("🎉 Data migration completed!")
    print("=" * 50)

    return len(errors) == 0


def verify_migration():
    """Verify that migration was successful"""
    print("\n🔍 Verifying migration...")

    new_supabase_url = "https://gzsgehciddnrssuqxtsj.supabase.co"
    new_supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6c2dlaGNpZGRucnNzdXF4dHNqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQxOTk5MSwiZXhwIjoyMDY5OTk1OTkxfQ.RxCuA9XIdNriIEUBk90m9jEZNV11uHAVaQKH76lavX0"

    new_client = create_client(new_supabase_url, new_supabase_key)

    # Check key tables
    key_tables = ["companies", "profiles", "watchlists"]

    for table in key_tables:
        try:
            result = new_client.table(table).select("count", count="exact").execute()
            count = result.count if hasattr(result, "count") else len(result.data)
            print(f"✅ {table}: {count} records")
        except Exception as e:
            print(f"❌ {table}: Error - {e}")

    print("✅ Migration verification completed!")


if __name__ == "__main__":
    success = migrate_data()

    if success:
        verify_migration()
        print("\n🎉 Data migration completed successfully!")
    else:
        print("\n❌ Data migration had errors. Check the output above.")
        sys.exit(1)
