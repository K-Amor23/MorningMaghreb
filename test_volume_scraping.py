#!/usr/bin/env python3
"""
Test Volume Scraping for Casablanca Stock Exchange

This script tests the volume scraping functionality to ensure it's working correctly.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent / "apps" / "backend" / "etl"))

from volume_scraper import VolumeScraper
from african_markets_scraper import AfricanMarketsScraper

async def test_volume_scraping():
    """Test the volume scraping functionality"""
    print("🧪 Testing Volume Scraping for CSE")
    print("=" * 50)
    
    # Test 1: Volume Scraper
    print("\n📊 Test 1: Volume Scraper")
    print("-" * 30)
    
    try:
        async with VolumeScraper() as scraper:
            volume_data = await scraper.scrape_all_volume_data()
            
            print(f"✅ Volume scraper test: {len(volume_data)} records found")
            
            if volume_data:
                print(f"📋 Sample volume data:")
                for i, data in enumerate(volume_data[:5]):
                    print(f"  {i+1}. {data.ticker}: {data.volume:,} ({data.source})")
            else:
                print("⚠️  No volume data found")
                
    except Exception as e:
        print(f"❌ Volume scraper test failed: {e}")
    
    # Test 2: African Markets Scraper with Volume
    print("\n🏢 Test 2: African Markets Scraper with Volume")
    print("-" * 45)
    
    try:
        async with AfricanMarketsScraper() as scraper:
            companies = await scraper.scrape_all()
            
            # Filter companies with volume data
            companies_with_volume = [
                company for company in companies 
                if company.get('volume') is not None
            ]
            
            print(f"✅ African Markets test: {len(companies_with_volume)} companies with volume")
            
            if companies_with_volume:
                print(f"📋 Sample companies with volume:")
                for i, company in enumerate(companies_with_volume[:5]):
                    volume = company.get('volume', 0)
                    print(f"  {i+1}. {company['ticker']}: {volume:,} shares")
            else:
                print("⚠️  No companies with volume data found")
                
    except Exception as e:
        print(f"❌ African Markets test failed: {e}")
    
    # Test 3: Volume Data Integration
    print("\n🔄 Test 3: Volume Data Integration")
    print("-" * 35)
    
    try:
        # Import the integration module
        from volume_data_integration import VolumeDataIntegration
        
        # Check if Supabase credentials are available
        supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
        supabase_key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
        
        if supabase_url and supabase_key:
            print("✅ Supabase credentials found")
            
            # Initialize integration (but don't run full integration for test)
            integration = VolumeDataIntegration(supabase_url, supabase_key)
            print("✅ Volume data integration initialized")
            
        else:
            print("⚠️  Supabase credentials not found - skipping database tests")
            print("   Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY")
            
    except Exception as e:
        print(f"❌ Volume data integration test failed: {e}")
    
    print("\n🎉 Volume scraping tests completed!")

async def test_volume_cleaning():
    """Test volume value cleaning functionality"""
    print("\n🧹 Test 4: Volume Value Cleaning")
    print("-" * 35)
    
    try:
        async with VolumeScraper() as scraper:
            # Test various volume formats
            test_values = [
                "1,234,567",
                "2.5M",
                "1.2B",
                "500K",
                "1000000",
                "1,000K",
                "2.5 M",
                "1.2 B",
                "-",
                "",
                "N/A"
            ]
            
            print("📋 Testing volume value cleaning:")
            for value in test_values:
                cleaned = scraper.clean_volume_value(value)
                print(f"  '{value}' -> {cleaned}")
                
    except Exception as e:
        print(f"❌ Volume cleaning test failed: {e}")

async def main():
    """Main test function"""
    print("🚀 Starting Volume Scraping Tests")
    print("=" * 60)
    
    # Run tests
    await test_volume_scraping()
    await test_volume_cleaning()
    
    print("\n" + "=" * 60)
    print("✅ All volume scraping tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 