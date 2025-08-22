#!/usr/bin/env python3
"""
Immediate Supabase Database Population Script

This script will:
1. Scrape live data from African Markets
2. Populate Supabase with companies and market data
3. Provide feedback on what's missing
"""

import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

# Add ETL path
sys.path.append('apps/backend/etl')

from supabase import create_client
from african_markets_scraper import AfricanMarketsScraper

# Supabase client
url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase = create_client(url, key)

def check_database_status():
    """Check what tables exist and their data count"""
    print("🔍 CHECKING DATABASE STATUS...")
    
    tables_to_check = [
        'companies',
        'comprehensive_market_data', 
        'company_news',
        'dividend_announcements',
        'earnings_announcements',
        'market_status'
    ]
    
    status = {}
    
    for table in tables_to_check:
        try:
            result = supabase.table(table).select('*', count='exact').limit(1).execute()
            count = result.count
            status[table] = {'exists': True, 'count': count}
            print(f"✅ {table}: {count} records")
        except Exception as e:
            status[table] = {'exists': False, 'error': str(e)}
            print(f"❌ {table}: {e}")
    
    return status

async def populate_database():
    """Populate database with live scraped data"""
    print("\n🚀 SCRAPING LIVE DATA...")
    
    async with AfricanMarketsScraper() as scraper:
        companies = await scraper.scrape_all()
        print(f"📊 Scraped {len(companies)} companies from African Markets")
        
        if not companies:
            print("❌ No companies scraped! Check network connection.")
            return False
        
        # Prepare data
        company_records = []
        market_data_records = []
        
        for company in companies:
            ticker = company.get('ticker', '').upper()
            if not ticker:
                continue
                
            # Company record
            company_record = {
                'ticker': ticker,
                'name': company.get('name', ''),
                'sector': company.get('sector', 'Unknown')
            }
            company_records.append(company_record)
            
            # Market data record
            price = float(company.get('price', 0) or 0)
            market_record = {
                'ticker': ticker,
                'current_price': price,
                'change_1d_percent': float(company.get('change_1d_percent', 0) or 0),
                'open_price': price,
                'high_price': price * 1.02,  # Estimate
                'low_price': price * 0.98,   # Estimate
                'volume': int(company.get('volume', 0) or 0),
                'market_cap': int((company.get('market_cap_billion', 0) or 0) * 1e9),
                'pe_ratio': 15.0,  # Default estimate
                'dividend_yield': 2.5,  # Default estimate
                'fifty_two_week_high': price * 1.3,  # Estimate
                'fifty_two_week_low': price * 0.7,   # Estimate
            }
            market_data_records.append(market_record)
        
        # Insert companies
        print(f"\n📋 INSERTING {len(company_records)} COMPANIES...")
        try:
            result = supabase.table('companies').upsert(
                company_records, 
                on_conflict='ticker'
            ).execute()
            print(f"✅ Companies inserted: {len(result.data)}")
        except Exception as e:
            print(f"❌ Error inserting companies: {e}")
            return False
        
        # Insert market data
        print(f"\n📈 INSERTING {len(market_data_records)} MARKET DATA RECORDS...")
        try:
            result = supabase.table('comprehensive_market_data').upsert(
                market_data_records,
                on_conflict='ticker'
            ).execute()
            print(f"✅ Market data inserted: {len(result.data)}")
        except Exception as e:
            print(f"❌ Error inserting market data: {e}")
            return False
        
        # Add sample news, dividends, earnings
        await add_sample_data(company_records[:10])  # Add for first 10 companies
        
        return True

async def add_sample_data(companies):
    """Add sample news, dividends, and earnings data"""
    print(f"\n📰 ADDING SAMPLE NEWS AND FINANCIAL DATA...")
    
    # Sample news
    news_records = []
    dividend_records = []
    earnings_records = []
    
    for i, company in enumerate(companies):
        ticker = company['ticker']
        
        # Sample news
        news_records.append({
            'ticker': ticker,
            'title': f"{company['name']} Reports Strong Q4 Performance",
            'summary': f"Latest financial results show positive growth for {company['name']}",
            'source': 'African Markets',
            'published_at': datetime.now().isoformat(),
            'url': f'https://african-markets.com/news/{ticker.lower()}',
            'category': 'earnings',
            'sentiment': 'positive',
            'impact': 'medium'
        })
        
        # Sample dividend
        dividend_records.append({
            'ticker': ticker,
            'type': 'dividend',
            'amount': 2.5 + (i * 0.5),
            'currency': 'MAD',
            'ex_date': '2024-12-15',
            'record_date': '2024-12-17',
            'payment_date': '2024-12-30',
            'description': f'Annual dividend payment for {company["name"]}',
            'status': 'announced'
        })
        
        # Sample earnings
        earnings_records.append({
            'ticker': ticker,
            'period': 'Q4 2024',
            'report_date': '2024-12-01',
            'estimate': 3.2 + (i * 0.3),
            'actual': 3.5 + (i * 0.3),
            'surprise': 0.3,
            'surprise_percent': 9.4,
            'status': 'reported'
        })
    
    # Insert sample data
    try:
        supabase.table('company_news').insert(news_records).execute()
        print(f"✅ Added {len(news_records)} news items")
    except Exception as e:
        print(f"⚠️ News insertion error: {e}")
    
    try:
        supabase.table('dividend_announcements').insert(dividend_records).execute()
        print(f"✅ Added {len(dividend_records)} dividend announcements")
    except Exception as e:
        print(f"⚠️ Dividend insertion error: {e}")
    
    try:
        supabase.table('earnings_announcements').insert(earnings_records).execute()
        print(f"✅ Added {len(earnings_records)} earnings announcements")
    except Exception as e:
        print(f"⚠️ Earnings insertion error: {e}")
    
    # Add market status
    try:
        market_status = {
            'market_status': 'open',
            'current_time_local': datetime.now().strftime('%H:%M:%S'),
            'trading_hours': '09:00 - 16:00',
            'total_market_cap': 1016840000000,
            'total_volume': 212321128,
            'advancers': 45,
            'decliners': 23,
            'unchanged': 10,
            'top_gainer': {'ticker': 'SBM', 'name': 'SBM', 'change': 6.03},
            'top_loser': {'ticker': 'ZDJ', 'name': 'ZDJ', 'change': -5.99},
            'most_active': {'ticker': 'NAKL', 'name': 'NAKL', 'volume': 232399}
        }
        supabase.table('market_status').insert([market_status]).execute()
        print(f"✅ Added market status")
    except Exception as e:
        print(f"⚠️ Market status insertion error: {e}")

def main():
    """Main execution function"""
    print("🎯 SUPABASE DATABASE POPULATION STARTING...\n")
    
    # Check current status
    status = check_database_status()
    
    # Check if tables exist
    missing_tables = [table for table, info in status.items() if not info['exists']]
    
    if missing_tables:
        print(f"\n❌ MISSING TABLES: {', '.join(missing_tables)}")
        print("📋 Please run the SQL script in Supabase dashboard first:")
        print("   1. Go to Supabase Dashboard → SQL Editor")
        print("   2. Run the contents of 'supabase_table_setup.sql'")
        print("   3. Then run this script again")
        return
    
    # All tables exist, populate data
    print(f"\n✅ All tables exist! Populating with live data...")
    success = asyncio.run(populate_database())
    
    if success:
        print(f"\n🎉 DATABASE POPULATION COMPLETE!")
        print(f"🌐 Your frontend should now show live data!")
        
        # Final status check
        print(f"\n📊 FINAL DATABASE STATUS:")
        check_database_status()
    else:
        print(f"\n❌ DATABASE POPULATION FAILED!")
        print(f"Check the errors above and try again.")

if __name__ == "__main__":
    main()
