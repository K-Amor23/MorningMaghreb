#!/usr/bin/env python3

"""
Verify Sky Garden Supabase Setup

This script verifies that your Sky Garden Supabase project is properly configured
and has the necessary tables for the newsletter functionality.
"""

import os
import sys
import requests
import json
from pathlib import Path

# Sky Garden Supabase credentials
SUPABASE_URL = "https://gzsgehciddnrssuqxtsj.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6c2dlaGNpZGRucnNzdXF4dHNqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0MTk5OTEsImV4cCI6MjA2OTk5NTk5MX0.DiaqtEop6spZT7l1g0PIdljVcBAWfalFEemlZqgwdrk"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6c2dlaGNpZGRucnNzdXF4dHNqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQxOTk5MSwiZXhwIjoyMDY5OTk1OTkxfQ.RxCuA9XIdNriIEUBk90m9jEZNV11uHAVaQKH76lavX0"

def print_header():
    print("🔧 Verifying Sky Garden Supabase Setup")
    print("=" * 50)
    print()

def test_supabase_connection():
    """Test the Supabase connection"""
    print("🔍 Testing Supabase Connection...")
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test basic connection
        response = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
        
        if response.status_code == 200:
            print("✅ Supabase connection successful")
            return True
        else:
            print(f"❌ Supabase connection failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def check_newsletter_table():
    """Check if the newsletter_subscribers table exists"""
    print("\n📊 Checking Newsletter Table...")
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Try to query the newsletter_subscribers table
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/newsletter_subscribers?select=count",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ newsletter_subscribers table exists")
            return True
        elif response.status_code == 404:
            print("❌ newsletter_subscribers table not found")
            return False
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking table: {e}")
        return False

def create_newsletter_table():
    """Create the newsletter_subscribers table if it doesn't exist"""
    print("\n🔧 Creating Newsletter Table...")
    
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    # SQL to create the table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS newsletter_subscribers (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        email VARCHAR(255) UNIQUE NOT NULL,
        name VARCHAR(255),
        status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'unsubscribed', 'bounced')),
        preferences JSONB DEFAULT '{}',
        subscribed_at TIMESTAMPTZ DEFAULT NOW(),
        unsubscribed_at TIMESTAMPTZ
    );
    """
    
    try:
        # Execute the SQL
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
            headers=headers,
            json={'sql': create_table_sql}
        )
        
        if response.status_code in [200, 201]:
            print("✅ Newsletter table created successfully")
            return True
        else:
            print(f"❌ Failed to create table: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False

def test_newsletter_signup():
    """Test the newsletter signup functionality"""
    print("\n📝 Testing Newsletter Signup...")
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    test_email = "test@morningmaghreb.com"
    
    try:
        # Try to insert a test subscriber
        data = {
            'email': test_email,
            'name': 'Test User',
            'status': 'active',
            'preferences': {
                'language': 'en',
                'delivery_time': '08:00',
                'frequency': 'daily'
            }
        }
        
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/newsletter_subscribers",
            headers=headers,
            json=data
        )
        
        if response.status_code == 201:
            print("✅ Newsletter signup test successful")
            
            # Clean up - delete the test record
            delete_response = requests.delete(
                f"{SUPABASE_URL}/rest/v1/newsletter_subscribers?email=eq.{test_email}",
                headers=headers
            )
            
            if delete_response.status_code == 204:
                print("✅ Test record cleaned up")
            
            return True
        else:
            print(f"❌ Newsletter signup test failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing signup: {e}")
        return False

def main():
    print_header()
    
    # Test connection
    if not test_supabase_connection():
        print("\n❌ Cannot proceed - Supabase connection failed")
        return
    
    # Check if newsletter table exists
    table_exists = check_newsletter_table()
    
    if not table_exists:
        print("\n🔧 Newsletter table not found. Creating it...")
        if not create_newsletter_table():
            print("\n❌ Failed to create newsletter table")
            return
    
    # Test newsletter signup
    if test_newsletter_signup():
        print("\n🎉 Sky Garden Supabase setup is working correctly!")
        print("\n✅ Newsletter functionality should now work on your site")
        print("🌐 Test it at: https://morningmaghreb.com")
    else:
        print("\n❌ Newsletter signup test failed")
        print("Please check the error messages above")

if __name__ == "__main__":
    main() 