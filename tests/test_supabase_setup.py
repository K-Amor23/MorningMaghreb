#!/usr/bin/env python3
"""
Test script for Supabase setup verification
"""

import os
import sys
from pathlib import Path

def test_environment():
    """Test environment setup"""
    print("🔍 Testing Environment Setup...")
    
    # Check Python version
    print(f"✅ Python version: {sys.version}")
    
    # Check if we're in virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
    else:
        print("⚠️  Not running in virtual environment")
    
    # Check if .env file exists
    if Path(".env").exists():
        print("✅ .env file found")
    else:
        print("❌ .env file not found")
    
    # Check Supabase credentials
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
    
    if supabase_url and supabase_url != 'your_supabase_url_here':
        print("✅ Supabase URL configured")
    else:
        print("❌ Supabase URL not configured (still using placeholder)")
    
    if supabase_key and supabase_key != 'your_supabase_anon_key_here':
        print("✅ Supabase key configured")
    else:
        print("❌ Supabase key not configured (still using placeholder)")
    
    return supabase_url and supabase_key and supabase_url != 'your_supabase_url_here'

def test_supabase_client():
    """Test Supabase client installation"""
    print("\n🔍 Testing Supabase Client...")
    
    try:
        from supabase import create_client
        print("✅ Supabase client imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Supabase client import failed: {e}")
        return False

def test_connection():
    """Test Supabase connection"""
    print("\n🔍 Testing Supabase Connection...")
    
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not configured")
        return False
    
    if supabase_url == 'your_supabase_url_here' or supabase_key == 'your_supabase_anon_key_here':
        print("❌ Supabase credentials still using placeholder values")
        return False
    
    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)
        
        # Try a simple query
        response = supabase.table('profiles').select('count').limit(1).execute()
        print("✅ Supabase connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

def test_files():
    """Test if required files exist"""
    print("\n🔍 Testing Required Files...")
    
    files_to_check = [
        "apps/backend/database/supabase_financial_schema.sql",
        "apps/backend/etl/initialize_supabase_cse.py",
        "apps/backend/etl/supabase_data_refresh.py",
        "SUPABASE_DATABASE_INTEGRATION_GUIDE.md",
        "setup_supabase_integration.sh"
    ]
    
    all_files_exist = True
    for file_path in files_to_check:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            all_files_exist = False
    
    return all_files_exist

def main():
    """Main test function"""
    print("🚀 Supabase Setup Verification")
    print("=" * 50)
    
    env_ok = test_environment()
    client_ok = test_supabase_client()
    files_ok = test_files()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Environment Setup: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"Supabase Client: {'✅ PASS' if client_ok else '❌ FAIL'}")
    print(f"Required Files: {'✅ PASS' if files_ok else '❌ FAIL'}")
    
    if env_ok and client_ok and files_ok:
        print("\n🎉 All tests passed! Ready to proceed with Supabase integration.")
        print("\n📋 Next Steps:")
        print("1. Configure your Supabase credentials in .env file")
        print("2. Add the database schema to your Supabase project")
        print("3. Run the initialization script")
        print("\n📖 For detailed instructions, see: SUPABASE_SETUP_COMPLETE_SUMMARY.md")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above before proceeding.")
        
        if not env_ok:
            print("\n🔧 To fix environment issues:")
            print("1. Edit .env file and add your Supabase credentials")
            print("2. Make sure you're running in the virtual environment")
        
        if not client_ok:
            print("\n🔧 To fix client issues:")
            print("1. Activate virtual environment: source venv/bin/activate")
            print("2. Install Supabase: pip install supabase")
        
        if not files_ok:
            print("\n🔧 To fix file issues:")
            print("1. Make sure all required files are present")
            print("2. Check file permissions")

if __name__ == "__main__":
    main()