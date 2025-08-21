#!/usr/bin/env python3
"""
Insert scraped data into Supabase database tables
This script will be used by Airflow to populate the database
"""

import os
import json
from datetime import datetime
from supabase import create_client, Client
from typing import List, Dict, Any

def get_supabase_client() -> Client:
    """Initialize Supabase client"""
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("Supabase credentials not found in environment variables")
    
    return create_client(supabase_url, supabase_key)

def insert_comprehensive_market_data(supabase: Client, companies: List[Dict[str, Any]]) -> int:
    """Insert comprehensive market data into Supabase"""
    try:
        # Transform companies data to match table schema
        market_data_records = []
        for company in companies:
            record = {
                'ticker': company.get('ticker', '').upper(),
                'name': company.get('name', ''),
                'sector': company.get('sector', ''),
                'current_price': company.get('price', 0),
                'change': company.get('change', 0),
                'change_percent': company.get('change_percent', 0),
                'open': company.get('open', 0),
                'high': company.get('high', 0),
                'low': company.get('low', 0),
                'volume': company.get('volume', 0),
                'market_cap': company.get('market_cap', 0),
                'pe_ratio': company.get('pe_ratio', 0),
                'dividend_yield': company.get('dividend_yield', 0),
                'roe': company.get('roe', 0),
                'shares_outstanding': company.get('shares_outstanding', 0),
                'scraped_at': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            market_data_records.append(record)
        
        # Insert data into Supabase
        result = supabase.table('comprehensive_market_data').upsert(
            market_data_records,
            on_conflict='ticker'
        ).execute()
        
        print(f"✅ Inserted {len(market_data_records)} market data records")
        return len(market_data_records)
        
    except Exception as e:
        print(f"❌ Error inserting market data: {e}")
        raise

def insert_company_news(supabase: Client, news_data: List[Dict[str, Any]]) -> int:
    """Insert company news into Supabase"""
    try:
        # Transform news data to match table schema
        news_records = []
        for news in news_data:
            record = {
                'ticker': news.get('ticker', '').upper(),
                'title': news.get('title', ''),
                'summary': news.get('summary', ''),
                'source': news.get('source', ''),
                'published_at': news.get('published_at'),
                'url': news.get('url', ''),
                'sentiment': news.get('sentiment', 'neutral'),
                'impact_level': news.get('impact_level', 'medium'),
                'scraped_at': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            news_records.append(record)
        
        # Insert data into Supabase
        result = supabase.table('company_news').upsert(
            news_records,
            on_conflict='id'
        ).execute()
        
        print(f"✅ Inserted {len(news_records)} news records")
        return len(news_records)
        
    except Exception as e:
        print(f"❌ Error inserting news data: {e}")
        raise

def insert_dividend_announcements(supabase: Client, dividend_data: List[Dict[str, Any]]) -> int:
    """Insert dividend announcements into Supabase"""
    try:
        # Transform dividend data to match table schema
        dividend_records = []
        for dividend in dividend_data:
            record = {
                'ticker': dividend.get('ticker', '').upper(),
                'amount': dividend.get('amount', 0),
                'ex_date': dividend.get('ex_date'),
                'payment_date': dividend.get('payment_date'),
                'dividend_status': dividend.get('dividend_status', 'announced'),
                'scraped_at': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            dividend_records.append(record)
        
        # Insert data into Supabase
        result = supabase.table('dividend_announcements').upsert(
            dividend_records,
            on_conflict='id'
        ).execute()
        
        print(f"✅ Inserted {len(dividend_records)} dividend records")
        return len(dividend_records)
        
    except Exception as e:
        print(f"❌ Error inserting dividend data: {e}")
        raise

def insert_earnings_announcements(supabase: Client, earnings_data: List[Dict[str, Any]]) -> int:
    """Insert earnings announcements into Supabase"""
    try:
        # Transform earnings data to match table schema
        earnings_records = []
        for earnings in earnings_data:
            record = {
                'ticker': earnings.get('ticker', '').upper(),
                'period': earnings.get('period', ''),
                'estimate': earnings.get('estimate', 0),
                'actual': earnings.get('actual', 0),
                'surprise': earnings.get('surprise', 0),
                'surprise_percent': earnings.get('surprise_percent', 0),
                'earnings_status': earnings.get('earnings_status', 'scheduled'),
                'report_date': earnings.get('report_date'),
                'scraped_at': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            earnings_records.append(record)
        
        # Insert data into Supabase
        result = supabase.table('earnings_announcements').upsert(
            earnings_records,
            on_conflict='id'
        ).execute()
        
        print(f"✅ Inserted {len(earnings_records)} earnings records")
        return len(earnings_records)
        
    except Exception as e:
        print(f"❌ Error inserting earnings data: {e}")
        raise

def insert_market_status(supabase: Client, market_status: Dict[str, Any]) -> int:
    """Insert market status into Supabase"""
    try:
        # Transform market status data to match table schema
        record = {
            'market_status': market_status.get('market_status', 'open'),
            'current_time': market_status.get('current_time'),
            'trading_hours': market_status.get('trading_hours', ''),
            'total_market_cap': market_status.get('total_market_cap', 0),
            'total_volume': market_status.get('total_volume', 0),
            'advancers': market_status.get('advancers', 0),
            'decliners': market_status.get('decliners', 0),
            'unchanged': market_status.get('unchanged', 0),
            'top_gainer': market_status.get('top_gainer', {}),
            'top_loser': market_status.get('top_loser', {}),
            'most_active': market_status.get('most_active', {}),
            'scraped_at': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat()
        }
        
        # Insert data into Supabase
        result = supabase.table('market_status').upsert(
            [record],
            on_conflict='id'
        ).execute()
        
        print(f"✅ Inserted market status record")
        return 1
        
    except Exception as e:
        print(f"❌ Error inserting market status: {e}")
        raise

def main():
    """Main function to test database insertion"""
    try:
        print("🚀 Starting database insertion test...")
        
        # Initialize Supabase client
        supabase = get_supabase_client()
        print("✅ Supabase client initialized")
        
        # Test data insertion
        test_companies = [
            {
                'ticker': 'ATW',
                'name': 'Attijariwafa Bank',
                'sector': 'Banks',
                'price': 410.10,
                'change': 1.25,
                'change_percent': 0.31,
                'open': 408.85,
                'high': 412.50,
                'low': 407.20,
                'volume': 1500000,
                'market_cap': 50000000000,
                'pe_ratio': 15.2,
                'dividend_yield': 3.5,
                'roe': 12.8,
                'shares_outstanding': 121951220
            }
        ]
        
        # Insert test data
        insert_comprehensive_market_data(supabase, test_companies)
        
        print("✅ Database insertion test completed successfully!")
        
    except Exception as e:
        print(f"❌ Database insertion test failed: {e}")
        raise

if __name__ == "__main__":
    main()
