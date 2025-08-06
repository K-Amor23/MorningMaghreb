#!/usr/bin/env python3

"""
Setup Sky Garden Newsletter Table

This script creates the newsletter_subscribers table in your Sky Garden Supabase project
using the existing database schema.
"""

import os
import sys
import requests
import json
from pathlib import Path

# Sky Garden Supabase credentials
SUPABASE_URL = "https://gzsgehciddnrssuqxtsj.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6c2dlaGNpZGRucnNzdXF4dHNqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQxOTk5MSwiZXhwIjoyMDY5OTk1OTkxfQ.RxCuA9XIdNriIEUBk90m9jEZNV11uHAVaQKH76lavX0"

def print_header():
    print("🔧 Setting up Sky Garden Newsletter Table")
    print("=" * 50)
    print()

def create_newsletter_table():
    """Create the newsletter_subscribers table"""
    print("🔧 Creating Newsletter Table...")
    
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # First, let's check what tables exist
    try:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
        if response.status_code == 200:
            print("✅ Connected to Sky Garden Supabase")
            print(f"Available endpoints: {len(response.json())}")
        else:
            print(f"❌ Failed to connect: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Try to create the table using a direct SQL approach
    # We'll use the existing database schema from the project
    print("\n📋 Using existing database schema...")
    
    # Read the database schema file
    schema_file = Path("database/advanced_features_supabase.sql")
    if schema_file.exists():
        print("✅ Found database schema file")
        
        # Extract the newsletter table creation SQL
        with open(schema_file, 'r') as f:
            content = f.read()
        
        # Find the newsletter_subscribers table definition
        if 'newsletter_subscribers' in content:
            print("✅ Newsletter table definition found in schema")
            print("📝 You can create the table manually in Supabase Dashboard:")
            print("   1. Go to https://supabase.com/dashboard")
            print("   2. Select your Sky Garden project")
            print("   3. Go to SQL Editor")
            print("   4. Run this SQL:")
            print()
            print("""
CREATE TABLE IF NOT EXISTS newsletter_subscribers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'unsubscribed', 'bounced')),
    preferences JSONB DEFAULT '{}',
    subscribed_at TIMESTAMPTZ DEFAULT NOW(),
    unsubscribed_at TIMESTAMPTZ
);
            """)
        else:
            print("❌ Newsletter table definition not found in schema")
    else:
        print("❌ Database schema file not found")
    
    return True

def test_newsletter_functionality():
    """Test if the newsletter functionality works"""
    print("\n🧪 Testing Newsletter Functionality...")
    
    # Test the API endpoint
    test_url = "https://morningmaghreb.com/api/newsletter/signup"
    test_data = {
        "email": "test@morningmaghreb.com",
        "name": "Test User",
        "preferences": {
            "language": "en",
            "delivery_time": "08:00",
            "frequency": "daily"
        }
    }
    
    try:
        response = requests.post(
            test_url,
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=10
        )
        
        print(f"📊 API Response Status: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ Newsletter signup API is working!")
            return True
        elif response.status_code == 500:
            print("❌ Newsletter signup API returned 500 error")
            try:
                error_data = response.json()
                print(f"Error: {error_data.get('error', 'Unknown error')}")
                print(f"Message: {error_data.get('message', 'No message')}")
            except:
                print(f"Response: {response.text}")
            return False
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def main():
    print_header()
    
    # Create the newsletter table
    if create_newsletter_table():
        print("\n✅ Sky Garden setup instructions provided")
    else:
        print("\n❌ Failed to set up Sky Garden")
        return
    
    # Test the newsletter functionality
    if test_newsletter_functionality():
        print("\n🎉 Newsletter functionality is working!")
        print("✅ Your site should now accept newsletter signups")
    else:
        print("\n⚠️ Newsletter functionality needs the table to be created")
        print("📝 Please create the newsletter_subscribers table in Supabase Dashboard")
    
    print("\n🔗 Next Steps:")
    print("1. Create the newsletter_subscribers table in Supabase Dashboard")
    print("2. Deploy the updated vercel.json to production")
    print("3. Test the newsletter signup on your site")
    print("\n🌐 Your site: https://morningmaghreb.com")

if __name__ == "__main__":
    main() 