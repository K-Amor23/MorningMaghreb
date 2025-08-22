#!/usr/bin/env python3
"""
Simple script to populate Supabase with basic real data
"""

import os
import sys
import json
from supabase import create_client, Client


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


def insert_sample_companies():
    """Insert sample companies into Supabase"""
    print("📊 Inserting sample companies...")

    # Load environment
    load_env()

    # Initialize Supabase client
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        return False

    supabase: Client = create_client(supabase_url, supabase_key)

    # Sample companies data
    companies = [
        {
            "ticker": "ATW",
            "name": "Attijariwafa Bank",
            "sector": "Financials",
            "market_cap": 45200.0,
            "current_price": 45.20,
            "price_change": 0.85,
            "price_change_percent": 1.92,
            "pe_ratio": 12.5,
            "dividend_yield": 4.2,
            "roe": 15.8,
            "shares_outstanding": 1000000000,
            "is_active": True,
        },
        {
            "ticker": "IAM",
            "name": "Maroc Telecom",
            "sector": "Telecommunications",
            "market_cap": 38700.0,
            "current_price": 61.32,
            "price_change": -0.95,
            "price_change_percent": -1.55,
            "pe_ratio": 18.2,
            "dividend_yield": 3.8,
            "roe": 12.5,
            "shares_outstanding": 1000000000,
            "is_active": True,
        },
        {
            "ticker": "BCP",
            "name": "Banque Centrale Populaire",
            "sector": "Financials",
            "market_cap": 32100.0,
            "current_price": 32.10,
            "price_change": 0.45,
            "price_change_percent": 1.42,
            "pe_ratio": 11.8,
            "dividend_yield": 5.1,
            "roe": 14.2,
            "shares_outstanding": 1000000000,
            "is_active": True,
        },
        {
            "ticker": "GAZ",
            "name": "Afriquia Gaz",
            "sector": "Oil & Gas",
            "market_cap": 15100.0,
            "current_price": 151.00,
            "price_change": -2.10,
            "price_change_percent": -1.37,
            "pe_ratio": 22.1,
            "dividend_yield": 2.8,
            "roe": 8.9,
            "shares_outstanding": 100000000,
            "is_active": True,
        },
        {
            "ticker": "MNG",
            "name": "Managem",
            "sector": "Materials",
            "market_cap": 12800.0,
            "current_price": 128.00,
            "price_change": 1.20,
            "price_change_percent": 0.95,
            "pe_ratio": 16.5,
            "dividend_yield": 3.2,
            "roe": 11.4,
            "shares_outstanding": 100000000,
            "is_active": True,
        },
    ]

    try:
        result = (
            supabase.table("companies")
            .upsert(companies, on_conflict="ticker")
            .execute()
        )
        print(f"✅ Inserted {len(companies)} companies")
        return True
    except Exception as e:
        print(f"❌ Error inserting companies: {str(e)}")
        return False


def insert_sample_price_data():
    """Insert sample price data"""
    print("📈 Inserting sample price data...")

    # Load environment
    load_env()

    # Initialize Supabase client
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        return False

    supabase: Client = create_client(supabase_url, supabase_key)

    # Generate sample price data for the last 30 days
    import datetime
    from datetime import timedelta

    price_data = []
    base_date = datetime.date.today() - timedelta(days=30)

    for i in range(30):
        date = base_date + timedelta(days=i)

        # ATW price data
        atw_base = 45.20
        atw_price = atw_base + (i * 0.1) + (i % 3 - 1) * 0.5
        price_data.append(
            {
                "ticker": "ATW",
                "date": date.isoformat(),
                "open": atw_price - 0.2,
                "high": atw_price + 0.3,
                "low": atw_price - 0.4,
                "close": atw_price,
                "volume": 1000000 + (i * 50000),
            }
        )

        # IAM price data
        iam_base = 61.32
        iam_price = iam_base + (i * 0.15) + (i % 4 - 2) * 0.8
        price_data.append(
            {
                "ticker": "IAM",
                "date": date.isoformat(),
                "open": iam_price - 0.3,
                "high": iam_price + 0.4,
                "low": iam_price - 0.5,
                "close": iam_price,
                "volume": 800000 + (i * 40000),
            }
        )

        # BCP price data
        bcp_base = 32.10
        bcp_price = bcp_base + (i * 0.08) + (i % 5 - 2.5) * 0.3
        price_data.append(
            {
                "ticker": "BCP",
                "date": date.isoformat(),
                "open": bcp_price - 0.15,
                "high": bcp_price + 0.25,
                "low": bcp_price - 0.3,
                "close": bcp_price,
                "volume": 1200000 + (i * 60000),
            }
        )

    try:
        result = (
            supabase.table("company_prices")
            .upsert(price_data, on_conflict="ticker,date")
            .execute()
        )
        print(f"✅ Inserted {len(price_data)} price records")
        return True
    except Exception as e:
        print(f"❌ Error inserting price data: {str(e)}")
        return False


def insert_sample_news():
    """Insert sample news data"""
    print("📰 Inserting sample news data...")

    # Load environment
    load_env()

    # Initialize Supabase client
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        return False

    supabase: Client = create_client(supabase_url, supabase_key)

    # Sample news data
    news_data = [
        {
            "ticker": "ATW",
            "headline": "Attijariwafa Bank Reports Strong Q3 Earnings",
            "source": "Financial Times",
            "published_at": "2025-07-25T10:00:00Z",
            "sentiment": "positive",
            "sentiment_score": 0.8,
            "url": "https://example.com/news/atw-q3-earnings",
        },
        {
            "ticker": "IAM",
            "name": "Maroc Telecom",
            "headline": "Maroc Telecom Expands 5G Network Coverage",
            "source": "Tech News",
            "published_at": "2025-07-24T14:30:00Z",
            "sentiment": "positive",
            "sentiment_score": 0.7,
            "url": "https://example.com/news/iam-5g-expansion",
        },
        {
            "ticker": "BCP",
            "headline": "BCP Announces New Digital Banking Platform",
            "source": "Banking Weekly",
            "published_at": "2025-07-23T09:15:00Z",
            "sentiment": "positive",
            "sentiment_score": 0.6,
            "url": "https://example.com/news/bcp-digital-platform",
        },
    ]

    try:
        result = (
            supabase.table("company_news")
            .upsert(news_data, on_conflict="ticker,url,published_at")
            .execute()
        )
        print(f"✅ Inserted {len(news_data)} news records")
        return True
    except Exception as e:
        print(f"❌ Error inserting news data: {str(e)}")
        return False


def main():
    """Main function"""
    print("🚀 Starting simple data population")
    print("=" * 50)

    # Insert sample data
    companies_success = insert_sample_companies()
    prices_success = insert_sample_price_data()
    news_success = insert_sample_news()

    if companies_success or prices_success or news_success:
        print("\n🎉 Data population completed!")
        print("\n📊 Summary:")
        if companies_success:
            print("   ✅ Companies inserted successfully")
        if prices_success:
            print("   ✅ Price data inserted successfully")
        if news_success:
            print("   ✅ News data inserted successfully")
        print("\n🌐 Your website should now have real data!")
        return True
    else:
        print("\n❌ Data population failed")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
