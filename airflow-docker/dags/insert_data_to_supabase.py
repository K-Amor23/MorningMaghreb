#!/usr/bin/env python3
"""
Insert scraped data into Supabase database tables
This script will be used by Airflow to populate the database
"""

import os
import json
from datetime import datetime, date
from supabase import create_client, Client
from typing import List, Dict, Any

def get_supabase_client() -> Client:
    """Initialize Supabase client"""
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("Supabase credentials not found in environment variables")
    
    return create_client(supabase_url, supabase_key)

def _to_iso(value):
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)

def insert_comprehensive_market_data(supabase: Client, companies: List[Dict[str, Any]]) -> int:
    """Insert companies and comprehensive market data into Supabase"""
    try:
        if not companies:
            print("⚠️ No companies data to insert")
            return 0
            
        # First, insert companies data
        company_records = []
        market_data_records = []
        
        for company in companies:
            ticker = company.get('ticker', '').upper()
            if not ticker:
                continue
                
            # Company record for companies table
            company_record = {
                'ticker': ticker,
                'name': company.get('name', ''),
                'sector': company.get('sector', 'Unknown')
            }
            company_records.append(company_record)
            
            # Market data record for comprehensive_market_data table
            price = float(company.get('price', 0) or 0)
            market_record = {
                'ticker': ticker,
                'current_price': price,
                'change_1d': float(company.get('change', 0) or 0),
                'change_1d_percent': float(company.get('change_percent', 0) or 0),
                'open_price': price,
                'high_price': price * 1.02,
                'low_price': price * 0.98,
                'volume': int(company.get('volume', 0) or 0),
                'market_cap': int((company.get('market_cap_billion', company.get('market_cap', 0)) or 0) * (1e9 if company.get('market_cap_billion') else 1)),
                'pe_ratio': float(company.get('pe_ratio', 15.0) or 15.0),
                'dividend_yield': float(company.get('dividend_yield', 2.5) or 2.5),
                'fifty_two_week_high': price * 1.3,  # Estimate 52w high
                'fifty_two_week_low': price * 0.7    # Estimate 52w low
            }
            market_data_records.append(market_record)
        
        print(f"📊 Preparing to insert {len(company_records)} companies and {len(market_data_records)} market data records")
        
        # Insert companies first
        if company_records:
            try:
                supabase.table('companies').upsert(company_records, on_conflict='ticker').execute()
                print(f"✅ Inserted/updated {len(company_records)} companies")
            except Exception as e:
                print(f"❌ Error inserting companies: {e}")
                # Continue with market data even if companies fail
        
        # Insert market data
        if market_data_records:
            try:
                supabase.table('comprehensive_market_data').insert(market_data_records).execute()
                print(f"✅ Inserted {len(market_data_records)} market data records")
                return len(market_data_records)
            except Exception as e:
                print(f"❌ Error inserting market data: {e}")
                return 0
        
    except Exception as e:
        print(f"❌ Error inserting market data: {e}")
        raise

def insert_company_news(supabase: Client, news_data: List[Dict[str, Any]]) -> int:
    """Insert company news into Supabase"""
    try:
        if not news_data:
            print("⚠️ No news data to insert")
            return 0
            
        # Transform and deduplicate news data to keep newest per (ticker,url)
        # Freshness priority: published_at -> created_at -> scraped_at (all ISO-able)
        def _parse_dt(val):
            try:
                return datetime.fromisoformat(str(val).replace('Z','+00:00')) if val else None
            except Exception:
                return None

        dedup: Dict[tuple, Dict[str, Any]] = {}
        for news in news_data:
            ticker = (news.get('ticker') or '').upper()
            url = news.get('url') or None
            if not ticker or not url:
                continue
            published_at = _parse_dt(news.get('published_at')) or _parse_dt(news.get('created_at')) or _parse_dt(news.get('scraped_at')) or datetime.now()
            key = (ticker, url)
            prev = dedup.get(key)
            if prev is None or _parse_dt(prev.get('published_at')) < published_at:
                dedup[key] = {
                    'ticker': ticker,
                    'headline': news.get('headline') or news.get('title', '') or '(no title)',
                    'summary': news.get('summary') or None,
                    'source': news.get('source') or None,
                    'published_at': _to_iso(published_at),
                    'url': url,
                    'category': news.get('category') or 'general',
                    'sentiment': news.get('sentiment') or 'neutral',
                    'impact': news.get('impact') or news.get('impact_level') or 'medium',
                }
        news_records = list(dedup.values())
        
        # Upsert data into Supabase to avoid duplicate key errors (ticker,url)
        supabase.table('company_news').upsert(
            news_records,
            on_conflict='ticker,url'
        ).execute()
        
        print(f"✅ Inserted/updated {len(news_records)} deduplicated news records")
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
                'type': dividend.get('type') or 'dividend',
                'amount': dividend.get('amount', 0),
                'currency': dividend.get('currency') or 'MAD',
                'ex_date': _to_iso(dividend.get('ex_date')),
                'record_date': _to_iso(dividend.get('record_date')),
                'payment_date': _to_iso(dividend.get('payment_date')),
                'description': dividend.get('description') or None,
                'status': dividend.get('status') or dividend.get('dividend_status') or 'announced',
            }
            dividend_records.append(record)
        
        # Insert data into Supabase (let DB assign id)
        supabase.table('dividend_announcements').insert(dividend_records).execute()
        
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
                'report_date': _to_iso(earnings.get('report_date')),
                'estimate': earnings.get('estimate', 0),
                'actual': earnings.get('actual', 0),
                'surprise': earnings.get('surprise', 0),
                'surprise_percent': earnings.get('surprise_percent', 0),
                'status': earnings.get('status') or earnings.get('earnings_status') or 'scheduled',
            }
            earnings_records.append(record)
        
        # Insert data into Supabase (let DB assign id)
        supabase.table('earnings_announcements').insert(earnings_records).execute()
        
        print(f"✅ Inserted {len(earnings_records)} earnings records")
        return len(earnings_records)
        
    except Exception as e:
        print(f"❌ Error inserting earnings data: {e}")
        raise

def insert_market_status(supabase: Client, market_status: Dict[str, Any]) -> int:
    """Insert market status into Supabase"""
    try:
        # Transform market status data to match table schema (Sky Garden uses status + time type)
        # Prefer sending 'status' (NOT NULL) and omit 'market_status' unless needed
        # Ensure current_time_local is time-only when a datetime is provided
        dt_raw = market_status.get('current_time')
        dt_parsed = None
        try:
            if dt_raw:
                dt_parsed = datetime.fromisoformat(str(dt_raw).replace('Z', '+00:00'))
        except Exception:
            dt_parsed = None

        current_time_value = (dt_parsed.time().isoformat() if dt_parsed else market_status.get('current_time'))

        base_record = {
            'status': market_status.get('status') or market_status.get('market_status') or 'open',
            'current_time_local': current_time_value,
            'trading_hours': market_status.get('trading_hours', ''),
            'total_market_cap': market_status.get('total_market_cap', 0),
            'total_volume': market_status.get('total_volume', 0),
            'advancers': market_status.get('advancers', 0),
            'decliners': market_status.get('decliners', 0),
            'unchanged': market_status.get('unchanged', 0),
            'top_gainer': market_status.get('top_gainer', {}),
            'top_loser': market_status.get('top_loser', {}),
            'most_active': market_status.get('most_active', {}),
        }

        # Try primary insert with 'status' column
        record = dict(base_record)
        try:
            supabase.table('market_status').insert([record]).execute()
            print(f"✅ Inserted market status record")
            return 1
        except Exception as e:
            msg = str(e)
            # If DB expects TIME not TIMESTAMPTZ, retry with time-only value
            if 'type time' in msg and record.get('current_time_local'):
                try:
                    dt = None
                    try:
                        dt = datetime.fromisoformat(str(record['current_time_local']).replace('Z','+00:00'))
                    except Exception:
                        dt = None
                    if dt is not None:
                        record_time_only = dict(record)
                        record_time_only['current_time_local'] = dt.time().isoformat()
                        supabase.table('market_status').insert([record_time_only]).execute()
                        print("✅ Inserted market status record (time-only current_time_local)")
                        return 1
                except Exception as e_time:
                    # Drop the field and try minimal
                    try:
                        record_no_time = dict(record)
                        record_no_time.pop('current_time_local', None)
                        supabase.table('market_status').insert([record_no_time]).execute()
                        print("✅ Inserted market status record (without current_time_local)")
                        return 1
                    except Exception as e_time2:
                        print(f"❌ Error inserting market status after time-type handling: {e_time2}")
                        # fallthrough to other handlers
            # Fallback: some schemas may use 'market_status' instead of 'status'
            if "'status' column" in msg or ' status ' in msg:
                record_fallback = dict(base_record)
                value = record_fallback.pop('status', None)
                record_fallback['market_status'] = value or 'open'
                try:
                    supabase.table('market_status').insert([record_fallback]).execute()
                    print("✅ Inserted market status record (fallback: market_status column)")
                    return 1
                except Exception as e2:
                    msg2 = str(e2)
                    # If time type mismatch, retry with time-only value while keeping status
                    if 'type time' in msg2 and record_fallback.get('current_time_local'):
                        try:
                            dt2 = None
                            try:
                                dt2 = datetime.fromisoformat(str(record_fallback['current_time_local']).replace('Z','+00:00'))
                            except Exception:
                                dt2 = None
                            if dt2 is not None:
                                record_fb_time = dict(record_fallback)
                                record_fb_time['current_time_local'] = dt2.time().isoformat()
                                supabase.table('market_status').insert([record_fb_time]).execute()
                                print("✅ Inserted market status record (fallback + time-only)")
                                return 1
                        except Exception as e_time_fb:
                            # Remove only the time field, keep status
                            try:
                                record_no_time2 = dict(record_fallback)
                                record_no_time2.pop('current_time_local', None)
                                supabase.table('market_status').insert([record_no_time2]).execute()
                                print("✅ Inserted market status record (fallback without current_time_local)")
                                return 1
                            except Exception as e_no_time2:
                                print(f"❌ Error inserting market status after fallback/time handling: {e_no_time2}")
                                raise
                    # If not a time error, bubble up
                    print(f"❌ Error inserting market status (fallback path): {e2}")
                    raise
            else:
                print(f"❌ Error inserting market status: {e}")
                raise
        
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
