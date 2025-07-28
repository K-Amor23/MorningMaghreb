#!/usr/bin/env python3
"""
Script to check the actual database schema
"""

import os
import sys
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

def check_schema():
    """Check what tables and columns exist"""
    print("🔍 Checking database schema...")
    
    # Load environment
    load_env()
    
    # Initialize Supabase client
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        return False
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    tables_to_check = ['companies', 'company_prices', 'company_news']
    
    for table in tables_to_check:
        try:
            # Try to select from the table
            result = supabase.table(table).select('*').limit(1).execute()
            print(f"✅ Table '{table}' exists")
            
            # Try to get column info by selecting specific columns
            if table == 'companies':
                # Try different column combinations
                try:
                    result = supabase.table(table).select('ticker,name,sector,industry,market_cap,current_price,price_change,price_change_percent,pe_ratio,dividend_yield,roe,shares_outstanding,size_category,sector_group,exchange,country,company_url,ir_url,is_active').limit(1).execute()
                    print(f"   ✅ Companies table has standard columns")
                except Exception as e:
                    print(f"   ❌ Companies table schema error: {str(e)}")
                    
                    # Try minimal columns
                    try:
                        result = supabase.table(table).select('ticker,name,sector,industry,market_cap,is_active').limit(1).execute()
                        print(f"   ✅ Companies table has basic columns")
                    except Exception as e2:
                        print(f"   ❌ Companies table basic columns error: {str(e2)}")
            
        except Exception as e:
            print(f"❌ Table '{table}' does not exist: {str(e)}")
    
    return True

def test_insert():
    """Test inserting a simple company"""
    print("\n🧪 Testing simple insert...")
    
    # Load environment
    load_env()
    
    # Initialize Supabase client
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        return False
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Try minimal company data
    test_company = {
        'ticker': 'TEST',
        'name': 'Test Company',
        'sector': 'Technology',
        'industry': 'Software',
        'market_cap': 1000000000.00,
        'is_active': True
    }
    
    try:
        result = supabase.table('companies').upsert(test_company, on_conflict='ticker').execute()
        print(f"✅ Test insert successful")
        return True
    except Exception as e:
        print(f"❌ Test insert failed: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 Checking database schema")
    print("=" * 40)
    
    check_schema()
    test_insert()

if __name__ == "__main__":
    main() 