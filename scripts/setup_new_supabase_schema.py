#!/usr/bin/env python3
"""
Setup script for new Supabase database schema
This script will apply the complete schema to your new Supabase instance
"""

import os
import sys
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_supabase_client() -> Client:
    """Initialize Supabase client"""
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        print("❌ Error: Missing Supabase credentials")
        print("Please set NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
        sys.exit(1)

    return create_client(url, key)


def read_schema_file(filepath: str) -> str:
    """Read the schema SQL file"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ Error: Schema file not found: {filepath}")
        sys.exit(1)


def execute_sql_script(supabase: Client, sql_script: str):
    """Execute SQL script using Supabase"""
    try:
        # Split the script into individual statements
        statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]

        print("🔄 Executing SQL statements...")

        for i, statement in enumerate(statements, 1):
            if statement and not statement.startswith("--"):
                try:
                    # Execute the statement
                    result = supabase.rpc("exec_sql", {"sql": statement}).execute()
                    print(f"✅ Statement {i}/{len(statements)} executed successfully")
                except Exception as e:
                    print(f"⚠️  Warning: Statement {i} failed: {str(e)}")
                    # Continue with other statements
                    continue

        print("✅ Schema setup completed!")

    except Exception as e:
        print(f"❌ Error executing SQL: {str(e)}")
        sys.exit(1)


def verify_tables(supabase: Client):
    """Verify that all tables were created successfully"""
    print("\n🔍 Verifying table creation...")

    expected_tables = [
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

    created_tables = []
    missing_tables = []

    for table in expected_tables:
        try:
            # Try to query the table
            result = supabase.table(table).select("*").limit(1).execute()
            created_tables.append(table)
            print(f"✅ Table '{table}' exists")
        except Exception as e:
            missing_tables.append(table)
            print(f"❌ Table '{table}' missing: {str(e)}")

    print(f"\n📊 Summary:")
    print(f"✅ Created: {len(created_tables)}/{len(expected_tables)} tables")
    print(f"❌ Missing: {len(missing_tables)} tables")

    if missing_tables:
        print(f"\nMissing tables: {', '.join(missing_tables)}")
        return False

    return True


def setup_row_level_security(supabase: Client):
    """Setup Row Level Security (RLS) policies"""
    print("\n🔒 Setting up Row Level Security...")

    # RLS policies for profiles table
    policies = [
        # Profiles - users can only access their own profile
        """
        CREATE POLICY "Users can view own profile" ON profiles
        FOR SELECT USING (auth.uid() = id);
        """,
        # Profiles - users can update their own profile
        """
        CREATE POLICY "Users can update own profile" ON profiles
        FOR UPDATE USING (auth.uid() = id);
        """,
        # Watchlists - users can only access their own watchlists
        """
        CREATE POLICY "Users can manage own watchlists" ON watchlists
        FOR ALL USING (auth.uid() = user_id);
        """,
        # Watchlist items - users can only access their own watchlist items
        """
        CREATE POLICY "Users can manage own watchlist items" ON watchlist_items
        FOR ALL USING (
            auth.uid() IN (
                SELECT user_id FROM watchlists WHERE id = watchlist_id
            )
        );
        """,
        # Price alerts - users can only access their own alerts
        """
        CREATE POLICY "Users can manage own price alerts" ON price_alerts
        FOR ALL USING (auth.uid() = user_id);
        """,
        # Sentiment votes - users can only access their own votes
        """
        CREATE POLICY "Users can manage own sentiment votes" ON sentiment_votes
        FOR ALL USING (auth.uid() = user_id);
        """,
        # Paper trading accounts - users can only access their own accounts
        """
        CREATE POLICY "Users can manage own paper trading accounts" ON paper_trading_accounts
        FOR ALL USING (auth.uid() = user_id);
        """,
        # Paper trading orders - users can only access their own orders
        """
        CREATE POLICY "Users can manage own paper trading orders" ON paper_trading_orders
        FOR ALL USING (auth.uid() IN (
            SELECT user_id FROM paper_trading_accounts WHERE id = account_id
        ));
        """,
        # Paper trading positions - users can only access their own positions
        """
        CREATE POLICY "Users can manage own paper trading positions" ON paper_trading_positions
        FOR ALL USING (auth.uid() IN (
            SELECT user_id FROM paper_trading_accounts WHERE id = account_id
        ));
        """,
        # Portfolios - users can only access their own portfolios
        """
        CREATE POLICY "Users can manage own portfolios" ON portfolios
        FOR ALL USING (auth.uid() = user_id);
        """,
        # Portfolio holdings - users can only access their own holdings
        """
        CREATE POLICY "Users can manage own portfolio holdings" ON portfolio_holdings
        FOR ALL USING (auth.uid() IN (
            SELECT user_id FROM portfolios WHERE id = portfolio_id
        ));
        """,
        # Chat queries - users can only access their own queries
        """
        CREATE POLICY "Users can manage own chat queries" ON chat_queries
        FOR ALL USING (auth.uid() = user_id);
        """,
        # Contest entries - users can only access their own entries
        """
        CREATE POLICY "Users can manage own contest entries" ON contest_entries
        FOR ALL USING (auth.uid() = user_id);
        """,
        # Contest notifications - users can only access their own notifications
        """
        CREATE POLICY "Users can manage own contest notifications" ON contest_notifications
        FOR ALL USING (auth.uid() = user_id);
        """,
    ]

    for i, policy in enumerate(policies, 1):
        try:
            supabase.rpc("exec_sql", {"sql": policy}).execute()
            print(f"✅ RLS Policy {i} created successfully")
        except Exception as e:
            print(f"⚠️  Warning: RLS Policy {i} failed: {str(e)}")
            continue


def main():
    """Main setup function"""
    print("🚀 Setting up new Supabase database schema...")
    print("=" * 50)

    # Initialize Supabase client
    supabase = get_supabase_client()
    print("✅ Supabase client initialized")

    # Read the schema file
    schema_file = "database/complete_supabase_schema.sql"
    sql_script = read_schema_file(schema_file)
    print(f"✅ Schema file loaded: {schema_file}")

    # Execute the schema
    execute_sql_script(supabase, sql_script)

    # Verify tables were created
    if verify_tables(supabase):
        print("✅ All tables verified successfully!")
    else:
        print("⚠️  Some tables may be missing. Please check the output above.")

    # Setup RLS policies
    setup_row_level_security(supabase)

    print("\n🎉 Database setup completed!")
    print("=" * 50)
    print("Next steps:")
    print("1. Test your application")
    print("2. Check that all features work correctly")
    print("3. Monitor the database for any issues")


if __name__ == "__main__":
    main()
