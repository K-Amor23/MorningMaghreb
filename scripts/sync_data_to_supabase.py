#!/usr/bin/env python3
"""
Simple script to sync scraped data to Supabase
"""

import os
import sys
import json
from supabase import create_client, Client

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

def sync_companies_to_supabase():
    """Sync company data to Supabase"""
    print("📊 Syncing companies to Supabase...")
    
    # Load environment
    load_env()
    
    # Initialize Supabase client
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        return False
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Load scraped company data
    companies_file = "apps/backend/data/cse_companies_african_markets.json"
    if not os.path.exists(companies_file):
        print(f"❌ Companies file not found: {companies_file}")
        return False
    
    with open(companies_file, 'r') as f:
        companies_data = json.load(f)
    
    print(f"📈 Found {len(companies_data)} companies to sync")
    
    # Transform data for Supabase
    companies_to_insert = []
    for company in companies_data:
        companies_to_insert.append({
            'ticker': company.get('ticker', ''),
            'name': company.get('name', ''),
            'sector': company.get('sector', ''),
            'market_cap': company.get('market_cap', 0),
            'current_price': company.get('price', 0),
            'price_change_percent': company.get('change_percent', 0),
            'is_active': True
        })
    
    # Insert companies
    try:
        result = supabase.table('companies').upsert(companies_to_insert, on_conflict='ticker').execute()
        print(f"✅ Synced {len(companies_to_insert)} companies to Supabase")
        return True
    except Exception as e:
        print(f"❌ Error syncing companies: {str(e)}")
        return False

def sync_ohlcv_data():
    """Sync OHLCV data to Supabase"""
    print("📈 Syncing OHLCV data to Supabase...")
    
    # Load environment
    load_env()
    
    # Initialize Supabase client
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        return False
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Load OHLCV data
    ohlcv_dir = "apps/backend/etl/data/ohlcv"
    if not os.path.exists(ohlcv_dir):
        print(f"❌ OHLCV directory not found: {ohlcv_dir}")
        return False
    
    # Get all CSV files
    csv_files = [f for f in os.listdir(ohlcv_dir) if f.endswith('.csv')]
    print(f"📊 Found {len(csv_files)} OHLCV files")
    
    total_records = 0
    for csv_file in csv_files:
        ticker = csv_file.split('_')[0]  # Extract ticker from filename
        csv_path = os.path.join(ohlcv_dir, csv_file)
        
        try:
            import csv
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                ohlcv_data = []
                
                for row in reader:
                    ohlcv_data.append({
                        'ticker': ticker,
                        'date': row.get('Date', ''),
                        'open': float(row.get('Open', 0)),
                        'high': float(row.get('High', 0)),
                        'low': float(row.get('Low', 0)),
                        'close': float(row.get('Close', 0)),
                        'volume': int(row.get('Volume', 0))
                    })
                
                if ohlcv_data:
                    # Insert OHLCV data
                    result = supabase.table('company_prices').upsert(ohlcv_data, on_conflict='ticker,date').execute()
                    total_records += len(ohlcv_data)
                    print(f"✅ Synced {len(ohlcv_data)} records for {ticker}")
                    
        except Exception as e:
            print(f"❌ Error syncing {ticker}: {str(e)}")
    
    print(f"✅ Total OHLCV records synced: {total_records}")
    return True

def main():
    """Main sync function"""
    print("🔄 Starting data sync to Supabase")
    print("=" * 50)
    
    # Sync companies
    companies_success = sync_companies_to_supabase()
    
    # Sync OHLCV data
    ohlcv_success = sync_ohlcv_data()
    
    if companies_success or ohlcv_success:
        print("\n🎉 Data sync completed!")
        print("\n📊 Summary:")
        if companies_success:
            print("   ✅ Companies synced successfully")
        if ohlcv_success:
            print("   ✅ OHLCV data synced successfully")
        print("\n🌐 Your website should now have real data!")
        return True
    else:
        print("\n❌ Data sync failed")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 