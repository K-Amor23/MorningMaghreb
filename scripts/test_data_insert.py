#!/usr/bin/env python3
"""
Test script to insert data directly into Supabase
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

def test_supabase_connection():
    """Test Supabase connection and insert test data"""
    print("🔗 Testing Supabase connection...")
    
    # Load environment
    load_env()
    
    # Initialize Supabase client
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        return False
    
    print(f"✅ Supabase URL: {supabase_url}")
    print(f"✅ Service Key: {supabase_key[:20]}...")
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Test with minimal columns first
    test_company_minimal = {
        'ticker': 'TEST',
        'name': 'Test Company',
        'sector': 'Technology',
        'is_active': True
    }
    
    try:
        print("📊 Inserting test company (minimal columns)...")
        result = supabase.table('companies').insert(test_company_minimal).execute()
        print(f"✅ Test company inserted: {result.data}")
        return True
    except Exception as e:
        print(f"❌ Error inserting test company (minimal): {str(e)}")
        
        # Try with even fewer columns
        test_company_basic = {
            'ticker': 'TEST2',
            'name': 'Test Company 2'
        }
        
        try:
            print("📊 Inserting test company (basic columns)...")
            result = supabase.table('companies').insert(test_company_basic).execute()
            print(f"✅ Test company inserted: {result.data}")
            return True
        except Exception as e2:
            print(f"❌ Error inserting test company (basic): {str(e2)}")
            return False

def main():
    """Main function"""
    print("🧪 Testing Supabase data insertion")
    print("=" * 50)
    
    success = test_supabase_connection()
    
    if success:
        print("\n🎉 Supabase connection and insertion successful!")
        print("🌐 Your database is ready for real data!")
        return True
    else:
        print("\n❌ Supabase test failed")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 