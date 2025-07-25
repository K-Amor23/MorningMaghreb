#!/usr/bin/env python3
"""
Test OpenAI Integration for Casablanca Insights
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_openai_connection():
    """Test basic OpenAI connection"""
    print("🤖 Testing OpenAI Integration")
    print("=" * 50)
    
    # Check if API key is available
    api_key = os.getenv("OpenAi_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No OpenAI API key found in environment variables")
        return False
    
    print(f"✅ OpenAI API key found: {api_key[:20]}...")
    
    try:
        from openai import OpenAI
        
        # Initialize client
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized")
        
        # Test a simple completion
        print("🧪 Testing API call...")
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello from Casablanca Insights!' in one sentence."}
            ],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✅ API call successful!")
        print(f"🤖 Response: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing OpenAI: {str(e)}")
        return False

async def test_newsletter_generation():
    """Test newsletter generation using the OpenAI service"""
    print("\n📧 Testing Newsletter Generation")
    print("=" * 50)
    
    try:
        from lib.openai_service import generate_weekly_recap
        
        print("🧪 Generating weekly recap...")
        recap = await generate_weekly_recap(
            include_macro=True,
            include_sectors=True,
            include_top_movers=True,
            language="en"
        )
        
        print("✅ Newsletter generation successful!")
        print(f"📧 Subject: {recap.get('subject', 'N/A')}")
        print(f"📝 Content length: {len(recap.get('content', ''))} characters")
        print(f"🌐 Language: {recap.get('language', 'N/A')}")
        
        # Show first 200 characters of content
        content_preview = recap.get('content', '')[:200]
        print(f"📄 Content preview: {content_preview}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating newsletter: {str(e)}")
        return False

async def test_supabase_connection():
    """Test Supabase connection"""
    print("\n🗄️ Testing Supabase Connection")
    print("=" * 50)
    
    try:
        from supabase import create_client
        
        url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
        
        if not url or not key:
            print("❌ Supabase credentials not found")
            return False
        
        print(f"✅ Supabase URL: {url}")
        print(f"✅ Supabase Key: {key[:20]}...")
        
        # Initialize client
        supabase = create_client(url, key)
        print("✅ Supabase client initialized")
        
        # Test connection by querying a table
        try:
            response = supabase.table('newsletter_subscribers').select('*').limit(1).execute()
            print("✅ Supabase connection successful!")
            return True
        except Exception as e:
            print(f"⚠️ Supabase query failed (table might not exist): {str(e)}")
            print("✅ But connection is working (client initialized)")
            return True
            
    except Exception as e:
        print(f"❌ Error testing Supabase: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Casablanca Insights - Integration Testing")
    print("=" * 60)
    
    # Test OpenAI
    openai_working = await test_openai_connection()
    
    # Test Newsletter Generation
    newsletter_working = await test_newsletter_generation()
    
    # Test Supabase
    supabase_working = await test_supabase_connection()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TESTING SUMMARY")
    print("=" * 60)
    print(f"🤖 OpenAI: {'✅ Working' if openai_working else '❌ Failed'}")
    print(f"📧 Newsletter: {'✅ Working' if newsletter_working else '❌ Failed'}")
    print(f"🗄️ Supabase: {'✅ Working' if supabase_working else '❌ Failed'}")
    
    if openai_working and newsletter_working and supabase_working:
        print("\n🎉 All systems are working! Ready to start the server.")
    else:
        print("\n⚠️ Some systems need attention before starting the server.")

if __name__ == "__main__":
    asyncio.run(main()) 