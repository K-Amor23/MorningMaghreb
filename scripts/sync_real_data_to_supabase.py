#!/usr/bin/env python3
"""
Script to sync real market data to Supabase

This script takes our real data from the data integration service and syncs it to Supabase,
ensuring the database is always up-to-date with the latest market information.
"""

import os
import sys
import json
from pathlib import Path

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent.parent / "apps" / "backend" / "services"))

from supabase_data_sync import SupabaseDataSync

def main():
    """Main function to sync data to Supabase"""
    print("🔄 Starting Real Data Sync to Supabase")
    print("=" * 60)
    
    try:
        # Check environment variables
        if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_ANON_KEY'):
            print("❌ Error: SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
            print("Please set these in your .env file or environment")
            return False
        
        # Initialize sync service
        print("📡 Initializing Supabase sync service...")
        sync_service = SupabaseDataSync()
        
        # Sync all data
        print("🔄 Syncing all data to Supabase...")
        results = sync_service.sync_all_data()
        
        # Display results
        print("\n📊 Sync Results:")
        print("-" * 40)
        
        for key, result in results.items():
            if isinstance(result, dict):
                if result.get('success'):
                    print(f"✅ {key}: Success")
                    if 'companies_synced' in result:
                        print(f"   📈 Companies synced: {result['companies_synced']}")
                    if 'market_data_synced' in result:
                        print(f"   📊 Market data records: {result['market_data_synced']}")
                else:
                    print(f"❌ {key}: Failed")
                    if 'error' in result:
                        print(f"   Error: {result['error']}")
            else:
                print(f"📅 {key}: {result}")
        
        # Check overall success
        if results.get('overall_success'):
            print("\n🎉 All data successfully synced to Supabase!")
            
            # Verify data in Supabase
            print("\n🔍 Verifying data in Supabase...")
            companies = sync_service.get_companies_from_supabase()
            print(f"✅ Companies in Supabase: {len(companies)}")
            
            if companies:
                print(f"📋 Sample company: {companies[0].get('ticker')} - {companies[0].get('name')}")
            
            return True
        else:
            print("\n⚠️ Some sync operations failed. Check the errors above.")
            return False
            
    except Exception as e:
        print(f"❌ Error during sync: {e}")
        return False

def test_supabase_connection():
    """Test Supabase connection"""
    print("🧪 Testing Supabase Connection")
    print("=" * 40)
    
    try:
        sync_service = SupabaseDataSync()
        
        # Test basic connection
        companies = sync_service.get_companies_from_supabase()
        print(f"✅ Connection successful")
        print(f"📊 Companies in database: {len(companies)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def show_data_summary():
    """Show summary of data in Supabase"""
    print("📊 Supabase Data Summary")
    print("=" * 40)
    
    try:
        sync_service = SupabaseDataSync()
        
        # Get companies
        companies = sync_service.get_companies_from_supabase()
        print(f"📈 Companies: {len(companies)}")
        
        # Get market data
        market_data = sync_service.get_market_data_from_supabase()
        print(f"📊 Market data records: {len(market_data)}")
        
        if companies:
            # Show sample data
            sample_company = companies[0]
            print(f"\n📋 Sample Company:")
            print(f"   Ticker: {sample_company.get('ticker')}")
            print(f"   Name: {sample_company.get('name')}")
            print(f"   Sector: {sample_company.get('sector')}")
            print(f"   ISIN: {sample_company.get('isin')}")
            
            # Show metadata if available
            if sample_company.get('metadata'):
                metadata = sample_company['metadata']
                print(f"   Data Sources: {metadata.get('data_sources', [])}")
                print(f"   Completeness Score: {metadata.get('completeness_score', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error getting summary: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Sync real data to Supabase')
    parser.add_argument('--test', action='store_true', help='Test Supabase connection')
    parser.add_argument('--summary', action='store_true', help='Show data summary')
    parser.add_argument('--sync', action='store_true', help='Sync data to Supabase')
    
    args = parser.parse_args()
    
    if args.test:
        success = test_supabase_connection()
    elif args.summary:
        success = show_data_summary()
    elif args.sync:
        success = main()
    else:
        # Default: run sync
        success = main()
    
    sys.exit(0 if success else 1) 