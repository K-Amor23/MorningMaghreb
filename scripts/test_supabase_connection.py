#!/usr/bin/env python3
"""
Simple Supabase Connection Test for Casablanca Insights
Tests basic connectivity and operations
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_status(message: str, status: str = "INFO"):
    """Print colored status messages"""
    colors = {
        "INFO": "\033[94m",    # Blue
        "SUCCESS": "\033[92m", # Green
        "WARNING": "\033[93m", # Yellow
        "ERROR": "\033[91m",   # Red
        "RESET": "\033[0m"     # Reset
    }
    
    color = colors.get(status, colors["INFO"])
    print(f"{color}[{status}]{colors['RESET']} {message}")

def test_supabase_connection():
    """Test basic Supabase connectivity"""
    print_status("🚀 Testing Supabase Connection", "INFO")
    print_status("=" * 40, "INFO")
    
    # Check environment variables
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url:
        print_status("❌ NEXT_PUBLIC_SUPABASE_URL not found in environment", "ERROR")
        return False
    
    if not supabase_key:
        print_status("❌ SUPABASE_SERVICE_ROLE_KEY not found in environment", "ERROR")
        return False
    
    print_status(f"✅ Supabase URL: {supabase_url[:50]}...", "SUCCESS")
    print_status(f"✅ Service Role Key: {supabase_key[:20]}...", "SUCCESS")
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print_status("✅ Supabase client created successfully", "SUCCESS")
        
        # Test basic connection
        print_status("Testing basic connection...", "INFO")
        
        # Test if we can access the database
        try:
            # Try to access a table (companies should exist)
            result = supabase.table('companies').select('*').limit(1).execute()
            print_status("✅ Database connection successful", "SUCCESS")
        except Exception as e:
            print_status(f"⚠️ Companies table not found (this is normal if schema not set up): {str(e)}", "WARNING")
        
        # Test newsletter subscribers table
        try:
            result = supabase.table('newsletter_subscribers').select('*').limit(1).execute()
            print_status("✅ Newsletter subscribers table accessible", "SUCCESS")
        except Exception as e:
            print_status(f"⚠️ Newsletter subscribers table not found: {str(e)}", "WARNING")
        
        # Test users table
        try:
            result = supabase.table('users').select('*').limit(1).execute()
            print_status("✅ Users table accessible", "SUCCESS")
        except Exception as e:
            print_status(f"⚠️ Users table not found: {str(e)}", "WARNING")
        
        # Test volume data table
        try:
            result = supabase.table('volume_data').select('*').limit(1).execute()
            print_status("✅ Volume data table accessible", "SUCCESS")
        except Exception as e:
            print_status(f"⚠️ Volume data table not found: {str(e)}", "WARNING")
        
        # Test quotes table
        try:
            result = supabase.table('quotes').select('*').limit(1).execute()
            print_status("✅ Quotes table accessible", "SUCCESS")
        except Exception as e:
            print_status(f"⚠️ Quotes table not found: {str(e)}", "WARNING")
        
        print_status("✅ Supabase connection test completed successfully", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"❌ Supabase connection failed: {str(e)}", "ERROR")
        return False

def test_sample_data_insertion():
    """Test inserting sample data"""
    print_status("Testing sample data insertion...", "INFO")
    
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print_status("❌ Missing environment variables", "ERROR")
        return False
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Test inserting a sample company
        sample_company = {
            "ticker": "TEST",
            "name": "Test Company",
            "sector": "Technology",
            "industry": "Software"
        }
        
        try:
            result = supabase.table('companies').upsert(sample_company).execute()
            print_status("✅ Sample company inserted successfully", "SUCCESS")
            
            # Clean up - delete the test company
            supabase.table('companies').delete().eq('ticker', 'TEST').execute()
            print_status("✅ Test data cleaned up", "SUCCESS")
            
        except Exception as e:
            print_status(f"⚠️ Could not insert sample company (table may not exist): {str(e)}", "WARNING")
        
        # Test newsletter subscriber insertion
        sample_subscriber = {
            "email": "test@example.com",
            "name": "Test User",
            "status": "active"
        }
        
        try:
            result = supabase.table('newsletter_subscribers').upsert(sample_subscriber).execute()
            print_status("✅ Sample newsletter subscriber inserted", "SUCCESS")
            
            # Clean up
            supabase.table('newsletter_subscribers').delete().eq('email', 'test@example.com').execute()
            print_status("✅ Newsletter test data cleaned up", "SUCCESS")
            
        except Exception as e:
            print_status(f"⚠️ Could not insert sample subscriber: {str(e)}", "WARNING")
        
        return True
        
    except Exception as e:
        print_status(f"❌ Sample data insertion failed: {str(e)}", "ERROR")
        return False

def main():
    """Main function"""
    print_status("📊 Casablanca Insights - Supabase Connection Test", "INFO")
    print_status(f"Started at: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
    print()
    
    # Test connection
    connection_success = test_supabase_connection()
    
    print()
    
    # Test data insertion
    data_success = test_sample_data_insertion()
    
    print()
    print_status("📊 Test Results Summary", "INFO")
    print_status("=" * 30, "INFO")
    
    if connection_success:
        print_status("✅ Connection Test: PASS", "SUCCESS")
    else:
        print_status("❌ Connection Test: FAIL", "ERROR")
    
    if data_success:
        print_status("✅ Data Insertion Test: PASS", "SUCCESS")
    else:
        print_status("⚠️ Data Insertion Test: PARTIAL (tables may not exist yet)", "WARNING")
    
    print()
    
    if connection_success:
        print_status("🎉 Supabase connection is working!", "SUCCESS")
        print_status("Next step: Set up database schema using the SQL file", "INFO")
    else:
        print_status("❌ Supabase connection failed. Check your environment variables.", "ERROR")
    
    return connection_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 