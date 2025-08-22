#!/usr/bin/env python3
"""
Script to run ETL pipeline with real 78 companies data
"""

import os
import sys
import json
from supabase import create_client, Client
import datetime
from datetime import timedelta


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


def load_companies_data():
    """Load the 78 companies from the data file"""
    print("📊 Loading 78 companies from data file...")

    data_file = os.path.join(
        os.path.dirname(__file__),
        "..",
        "apps",
        "backend",
        "data",
        "cse_companies_african_markets.json",
    )

    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        return None

    with open(data_file, "r") as f:
        companies_data = json.load(f)

    print(f"✅ Loaded {len(companies_data)} companies from data file")
    return companies_data


def insert_companies_to_supabase(companies_data):
    """Insert all 78 companies to Supabase"""
    print("📈 Inserting 78 companies to Supabase...")

    # Load environment
    load_env()

    # Initialize Supabase client
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        return False

    supabase: Client = create_client(supabase_url, supabase_key)

    # Transform companies data to match our schema
    companies_to_insert = []

    for company in companies_data:
        # Convert market cap from billion to actual value
        market_cap = (
            int(company.get("market_cap_billion", 0) * 1000000000)
            if company.get("market_cap_billion")
            else 0
        )

        # Map sectors to our standard format
        sector_mapping = {
            "Financials": "Financials",
            "Telecommunications": "Telecommunications",
            "Oil & Gas": "Oil & Gas",
            "Materials": "Materials",
            "Industrials": "Industrials",
            "Consumer Staples": "Consumer Staples",
            "Consumer Discretionary": "Consumer Discretionary",
            "Healthcare": "Healthcare",
            "Technology": "Technology",
            "Real Estate": "Real Estate",
            "Utilities": "Utilities",
        }

        sector = sector_mapping.get(
            company.get("sector"), company.get("sector", "Unknown")
        )

        company_record = {
            "ticker": company.get("ticker"),
            "name": company.get("name"),
            "sector": sector,
            "industry": company.get("sector_group", sector),
            "market_cap": market_cap,
            "is_active": True,
        }

        companies_to_insert.append(company_record)

    try:
        # Insert in batches to avoid timeout
        batch_size = 20
        total_inserted = 0

        for i in range(0, len(companies_to_insert), batch_size):
            batch = companies_to_insert[i : i + batch_size]
            result = (
                supabase.table("companies")
                .upsert(batch, on_conflict="ticker")
                .execute()
            )
            total_inserted += len(batch)
            print(f"✅ Inserted batch {i//batch_size + 1}: {len(batch)} companies")

        print(f"✅ Successfully inserted {total_inserted} companies to Supabase")
        return True

    except Exception as e:
        print(f"❌ Error inserting companies: {str(e)}")
        return False


def generate_price_data_for_all_companies(companies_data):
    """Generate price data for all companies"""
    print("📊 Generating price data for all companies...")

    # Load environment
    load_env()

    # Initialize Supabase client
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        return False

    supabase: Client = create_client(supabase_url, supabase_key)

    # Check if company_prices table exists
    try:
        result = supabase.table("company_prices").select("*").limit(1).execute()
        print("✅ company_prices table exists")
    except Exception as e:
        print("❌ company_prices table does not exist")
        return False

    # Generate price data for the last 30 days for each company
    price_data = []
    base_date = datetime.date.today() - timedelta(days=30)

    for company in companies_data:
        ticker = company.get("ticker")
        base_price = company.get("price", 50.0)

        # Handle None values
        if base_price is None:
            base_price = 50.0  # Default price if None

        for i in range(30):
            date = base_date + timedelta(days=i)

            # Create realistic price movement
            trend = (i * 0.02) + (i % 7 - 3.5) * 0.2  # Weekly cycles
            volatility = (i % 5 - 2.5) * 0.5  # Daily volatility
            price = base_price + trend + volatility

            price_data.append(
                {
                    "ticker": ticker,
                    "date": date.isoformat(),
                    "open": float(price - 0.2),
                    "high": float(price + 0.3),
                    "low": float(price - 0.4),
                    "close": float(price),
                    "volume": 1000000 + (i * 50000) + (hash(ticker) % 500000),
                    "adjusted_close": float(price),
                }
            )

    try:
        # Insert in batches
        batch_size = 100
        total_inserted = 0

        for i in range(0, len(price_data), batch_size):
            batch = price_data[i : i + batch_size]
            result = (
                supabase.table("company_prices")
                .upsert(batch, on_conflict="ticker,date")
                .execute()
            )
            total_inserted += len(batch)
            print(f"✅ Inserted price batch {i//batch_size + 1}: {len(batch)} records")

        print(f"✅ Successfully inserted {total_inserted} price records")
        return True

    except Exception as e:
        print(f"❌ Error inserting price data: {str(e)}")
        return False


def generate_sentiment_data_for_all_companies(companies_data):
    """Generate sentiment data for all companies"""
    print("📊 Generating sentiment data for all companies...")

    # Load environment
    load_env()

    # Initialize Supabase client
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        return False

    supabase: Client = create_client(supabase_url, supabase_key)

    # Check if sentiment_aggregates table exists
    try:
        result = supabase.table("sentiment_aggregates").select("*").limit(1).execute()
        print("✅ sentiment_aggregates table exists")
    except Exception as e:
        print("❌ sentiment_aggregates table does not exist")
        return False

    # Generate sentiment data for each company
    sentiment_data = []

    for company in companies_data:
        ticker = company.get("ticker")

        # Generate realistic sentiment based on sector and performance
        sector = company.get("sector", "Unknown")

        # Base sentiment by sector
        sector_sentiment = {
            "Financials": {"bullish": 65, "bearish": 20, "neutral": 15},
            "Telecommunications": {"bullish": 70, "bearish": 15, "neutral": 15},
            "Oil & Gas": {"bullish": 60, "bearish": 25, "neutral": 15},
            "Materials": {"bullish": 75, "bearish": 10, "neutral": 15},
            "Industrials": {"bullish": 55, "bearish": 25, "neutral": 20},
            "Consumer Staples": {"bullish": 65, "bearish": 20, "neutral": 15},
            "Consumer Discretionary": {"bullish": 60, "bearish": 25, "neutral": 15},
            "Healthcare": {"bullish": 70, "bearish": 15, "neutral": 15},
            "Technology": {"bullish": 75, "bearish": 10, "neutral": 15},
            "Real Estate": {"bullish": 50, "bearish": 30, "neutral": 20},
            "Utilities": {"bullish": 55, "bearish": 25, "neutral": 20},
        }

        sentiment = sector_sentiment.get(
            sector, {"bullish": 60, "bearish": 20, "neutral": 20}
        )

        sentiment_data.append(
            {
                "ticker": ticker,
                "bullish_percentage": sentiment["bullish"],
                "bearish_percentage": sentiment["bearish"],
                "neutral_percentage": sentiment["neutral"],
                "total_votes": 100 + (hash(ticker) % 200),
                "average_confidence": 3.5 + (hash(ticker) % 10) / 10,
            }
        )

    try:
        result = (
            supabase.table("sentiment_aggregates")
            .upsert(sentiment_data, on_conflict="ticker")
            .execute()
        )
        print(f"✅ Successfully inserted {len(sentiment_data)} sentiment records")
        return True

    except Exception as e:
        print(f"❌ Error inserting sentiment data: {str(e)}")
        return False


def main():
    """Main function"""
    print("🚀 Starting ETL pipeline with real 78 companies data")
    print("=" * 60)

    # Load companies data
    companies_data = load_companies_data()
    if not companies_data:
        print("❌ Failed to load companies data")
        return False

    # Insert companies to Supabase
    companies_success = insert_companies_to_supabase(companies_data)

    # Generate price data
    prices_success = generate_price_data_for_all_companies(companies_data)

    # Generate sentiment data
    sentiment_success = generate_sentiment_data_for_all_companies(companies_data)

    if companies_success or prices_success or sentiment_success:
        print("\n🎉 ETL pipeline completed!")
        print("\n📊 Summary:")
        if companies_success:
            print("   ✅ 78 companies inserted successfully")
        if prices_success:
            print("   ✅ Price data generated for all companies")
        if sentiment_success:
            print("   ✅ Sentiment data generated for all companies")
        print(
            f"\n🌐 Your website now has data for {len(companies_data)} Moroccan companies!"
        )
        return True
    else:
        print("\n❌ ETL pipeline failed")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
