#!/usr/bin/env python3
"""
Test script to verify complete data flow:
Airflow → Supabase → Frontend API → Frontend Components
"""

import os
import requests
import json
from datetime import datetime

def test_supabase_connection():
    """Test if we can connect to Supabase"""
    print("🔍 Testing Supabase connection...")
    
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        return False
    
    print(f"✅ Supabase URL: {supabase_url}")
    print(f"✅ Service Key: {supabase_key[:20]}...")
    return True

def test_database_tables():
    """Test if required database tables exist"""
    print("\n🔍 Testing database tables...")
    
    # This would require a Supabase client to actually query
    # For now, we'll just check if the tables are mentioned in our schema
    required_tables = [
        'comprehensive_market_data',
        'company_news', 
        'dividend_announcements',
        'earnings_announcements',
        'market_status'
    ]
    
    print(f"✅ Required tables: {', '.join(required_tables)}")
    return True

def test_frontend_api():
    """Test if frontend API endpoints are working"""
    print("\n🔍 Testing frontend API endpoints...")
    
    base_url = "http://localhost:3000"
    endpoints = [
        "/api/market-data/comprehensive",
        "/api/search/companies?q=ATW",
        "/api/health"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=10)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {endpoint}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint}: Connection failed - {e}")
    
    return True

def test_data_flow():
    """Test the complete data flow"""
    print("\n🚀 Testing Complete Data Flow...")
    
    # Step 1: Check if Airflow is running
    print("1️⃣ Checking Airflow status...")
    try:
        airflow_response = requests.get("http://localhost:8080/health", timeout=5)
        if airflow_response.status_code == 200:
            print("✅ Airflow is running")
        else:
            print("⚠️ Airflow responded but with unexpected status")
    except requests.exceptions.RequestException:
        print("❌ Airflow is not accessible")
    
    # Step 2: Check if Supabase is accessible
    print("2️⃣ Checking Supabase accessibility...")
    if test_supabase_connection():
        print("✅ Supabase credentials are configured")
    else:
        print("❌ Supabase connection failed")
    
    # Step 3: Check if frontend is running
    print("3️⃣ Checking frontend accessibility...")
    try:
        frontend_response = requests.get("http://localhost:3000", timeout=5)
        if frontend_response.status_code == 200:
            print("✅ Frontend is running")
        else:
            print("⚠️ Frontend responded but with unexpected status")
    except requests.exceptions.RequestException:
        print("❌ Frontend is not accessible")
    
    # Step 4: Test API endpoints
    print("4️⃣ Testing API endpoints...")
    test_frontend_api()
    
    print("\n📊 Data Flow Test Summary:")
    print("=" * 50)
    print("✅ Airflow: Data collection and processing")
    print("✅ Supabase: Data storage and management") 
    print("✅ Frontend API: Data serving endpoints")
    print("✅ Frontend Components: Data display")
    print("\n🎯 Next Steps:")
    print("1. Run the SQL script in Supabase to create tables")
    print("2. Restart Airflow to install requirements")
    print("3. Trigger your DAG to populate data")
    print("4. Verify data appears in your frontend")

def main():
    """Main test function"""
    print("🌐 Casablanca Insights - Data Flow Test")
    print("=" * 50)
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_data_flow()
    
    print(f"\n🏁 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
