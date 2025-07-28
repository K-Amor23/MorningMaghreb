#!/usr/bin/env python3
"""
Script to populate missing tables with data
"""

import os
import sys
import json
from supabase import create_client, Client
import datetime
from datetime import timedelta

def load_env():
    """Load environment variables from .env file"""
    env_file = os.path.join(os.path.dirname(__file__), '..', 'apps', 'web', '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print(f"✅ Loaded environment from: {env_file}")
    else:
        print(f"❌ Environment file not found at: {env_file}")

def insert_price_data():
    """Insert sample price data"""
    print("📈 Inserting price data...")
    
    # Load environment
    load_env()
    
    # Initialize Supabase client
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        return False
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Check if company_prices table exists
    try:
        result = supabase.table('company_prices').select('*').limit(1).execute()
        print("✅ company_prices table exists")
    except Exception as e:
        print("❌ company_prices table does not exist")
        print("   Please run the SQL in database/create_missing_tables.sql first")
        return False
    
    # Generate sample price data for the last 90 days
    price_data = []
    base_date = datetime.date.today() - timedelta(days=90)
    
    tickers = ['ATW', 'IAM', 'BCP', 'GAZ', 'MNG']
    
    for ticker in tickers:
        # Base prices for each ticker
        base_prices = {
            'ATW': 45.20,
            'IAM': 61.32,
            'BCP': 32.10,
            'GAZ': 28.75,
            'MNG': 245.80
        }
        
        base_price = base_prices.get(ticker, 50.0)
        
        for i in range(90):
            date = base_date + timedelta(days=i)
            
            # Create realistic price movement
            trend = (i * 0.05) + (i % 7 - 3.5) * 0.3  # Weekly cycles
            volatility = (i % 5 - 2.5) * 0.8  # Daily volatility
            price = base_price + trend + volatility
            
            price_data.append({
                'ticker': ticker,
                'date': date.isoformat(),
                'open': float(price - 0.2),
                'high': float(price + 0.3),
                'low': float(price - 0.4),
                'close': float(price),
                'volume': 1000000 + (i * 50000) + (hash(ticker) % 500000),
                'adjusted_close': float(price)
            })
    
    try:
        result = supabase.table('company_prices').upsert(price_data, on_conflict='ticker,date').execute()
        print(f"✅ Inserted {len(price_data)} price records")
        return True
    except Exception as e:
        print(f"❌ Error inserting price data: {str(e)}")
        return False

def insert_sentiment_data():
    """Insert sample sentiment data"""
    print("📊 Inserting sentiment data...")
    
    # Load environment
    load_env()
    
    # Initialize Supabase client
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        return False
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Check if sentiment_aggregates table exists
    try:
        result = supabase.table('sentiment_aggregates').select('*').limit(1).execute()
        print("✅ sentiment_aggregates table exists")
    except Exception as e:
        print("❌ sentiment_aggregates table does not exist")
        print("   Please run the SQL in database/create_missing_tables.sql first")
        return False
    
    # Sample sentiment data
    sentiment_data = [
        {
            'ticker': 'ATW',
            'bullish_percentage': 65,
            'bearish_percentage': 20,
            'neutral_percentage': 15,
            'total_votes': 150,
            'average_confidence': 3.8
        },
        {
            'ticker': 'IAM',
            'bullish_percentage': 70,
            'bearish_percentage': 15,
            'neutral_percentage': 15,
            'total_votes': 120,
            'average_confidence': 4.1
        },
        {
            'ticker': 'BCP',
            'bullish_percentage': 55,
            'bearish_percentage': 25,
            'neutral_percentage': 20,
            'total_votes': 95,
            'average_confidence': 3.5
        },
        {
            'ticker': 'GAZ',
            'bullish_percentage': 60,
            'bearish_percentage': 20,
            'neutral_percentage': 20,
            'total_votes': 80,
            'average_confidence': 3.9
        },
        {
            'ticker': 'MNG',
            'bullish_percentage': 75,
            'bearish_percentage': 10,
            'neutral_percentage': 15,
            'total_votes': 110,
            'average_confidence': 4.2
        }
    ]
    
    try:
        result = supabase.table('sentiment_aggregates').upsert(sentiment_data, on_conflict='ticker').execute()
        print(f"✅ Inserted {len(sentiment_data)} sentiment records")
        return True
    except Exception as e:
        print(f"❌ Error inserting sentiment data: {str(e)}")
        return False

def insert_news_data():
    """Insert sample news data"""
    print("📰 Inserting news data...")
    
    # Load environment
    load_env()
    
    # Initialize Supabase client
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        return False
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Check if company_news table exists
    try:
        result = supabase.table('company_news').select('*').limit(1).execute()
        print("✅ company_news table exists")
    except Exception as e:
        print("❌ company_news table does not exist")
        print("   Please run the SQL in database/create_missing_tables.sql first")
        return False
    
    # Sample news data
    news_data = [
        {
            'ticker': 'ATW',
            'headline': 'Attijariwafa Bank Reports Strong Q3 Earnings',
            'source': 'Financial Times',
            'published_at': '2025-07-25T10:00:00Z',
            'sentiment': 'positive',
            'sentiment_score': 0.8,
            'url': 'https://example.com/news/atw-q3-earnings',
            'content_preview': 'Attijariwafa Bank reported strong third-quarter earnings, exceeding analyst expectations...'
        },
        {
            'ticker': 'IAM',
            'headline': 'Maroc Telecom Expands 5G Network Coverage',
            'source': 'Tech News',
            'published_at': '2025-07-24T14:30:00Z',
            'sentiment': 'positive',
            'sentiment_score': 0.7,
            'url': 'https://example.com/news/iam-5g-expansion',
            'content_preview': 'Maroc Telecom announced expansion of its 5G network coverage across major cities...'
        },
        {
            'ticker': 'BCP',
            'headline': 'BCP Announces New Digital Banking Platform',
            'source': 'Banking Weekly',
            'published_at': '2025-07-23T09:15:00Z',
            'sentiment': 'positive',
            'sentiment_score': 0.6,
            'url': 'https://example.com/news/bcp-digital-platform',
            'content_preview': 'Banque Centrale Populaire launched its new digital banking platform...'
        },
        {
            'ticker': 'GAZ',
            'headline': 'Afriquia Gaz Reports Record Sales',
            'source': 'Energy Daily',
            'published_at': '2025-07-22T16:45:00Z',
            'sentiment': 'positive',
            'sentiment_score': 0.5,
            'url': 'https://example.com/news/gaz-record-sales',
            'content_preview': 'Afriquia Gaz reported record sales figures for the quarter...'
        },
        {
            'ticker': 'MNG',
            'headline': 'Managem Expands Mining Operations',
            'source': 'Mining Journal',
            'published_at': '2025-07-21T11:20:00Z',
            'sentiment': 'positive',
            'sentiment_score': 0.9,
            'url': 'https://example.com/news/mng-mining-expansion',
            'content_preview': 'Managem announced expansion of its mining operations in Morocco...'
        }
    ]
    
    try:
        result = supabase.table('company_news').upsert(news_data, on_conflict='ticker,url,published_at').execute()
        print(f"✅ Inserted {len(news_data)} news records")
        return True
    except Exception as e:
        print(f"❌ Error inserting news data: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 Starting missing data population")
    print("=" * 50)
    
    # Insert missing data
    prices_success = insert_price_data()
    sentiment_success = insert_sentiment_data()
    news_success = insert_news_data()
    
    if prices_success or sentiment_success or news_success:
        print("\n🎉 Data population completed!")
        print("\n📊 Summary:")
        if prices_success:
            print("   ✅ Price data inserted successfully")
        if sentiment_success:
            print("   ✅ Sentiment data inserted successfully")
        if news_success:
            print("   ✅ News data inserted successfully")
        print("\n🌐 Your website should now have real data!")
        return True
    else:
        print("\n❌ Data population failed")
        print("   Please make sure to run the SQL in database/create_missing_tables.sql first")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 