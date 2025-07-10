#!/usr/bin/env python3
"""
Test script for Economic Data Fetcher
Demonstrates how to fetch and process Moroccan economic data from BAM
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent))

from etl.fetch_economic_data import EconomicDataFetcher
from storage.local_fs import LocalFileStorage
from models.economic_data import EconomicIndicatorType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_economic_data_fetcher():
    """Test the economic data fetcher functionality"""
    
    print("🚀 Testing Economic Data Fetcher")
    print("=" * 50)
    
    # Initialize storage and fetcher
    storage = LocalFileStorage()
    fetcher = EconomicDataFetcher(storage)
    
    # Test 1: Get data summary
    print("\n📊 Test 1: Getting data summary...")
    try:
        summary = await fetcher.get_data_summary()
        print(f"✅ Data summary retrieved successfully")
        print(f"   Total indicators: {summary['total_indicators']}")
        print(f"   Available indicators: {list(summary['indicators'].keys())}")
    except Exception as e:
        print(f"❌ Error getting data summary: {e}")
    
    # Test 2: Fetch specific indicator (Key Policy Rate)
    print("\n📈 Test 2: Fetching Key Policy Rate data...")
    try:
        results = await fetcher.fetch_all_economic_data(['key_policy_rate'])
        print(f"✅ Key Policy Rate fetch completed")
        print(f"   Total files: {results['total_files']}")
        print(f"   Errors: {len(results['errors'])}")
        
        for data_result in results['data_fetched']:
            print(f"   {data_result['data_type']}:")
            print(f"     Files downloaded: {data_result['files_downloaded']}")
            print(f"     Data points: {data_result['data_points']}")
            print(f"     Latest date: {data_result['latest_date']}")
            
    except Exception as e:
        print(f"❌ Error fetching Key Policy Rate: {e}")
    
    # Test 3: Fetch multiple indicators
    print("\n📊 Test 3: Fetching multiple indicators...")
    try:
        indicators = ['inflation_cpi', 'foreign_exchange_reserves']
        results = await fetcher.fetch_all_economic_data(indicators)
        print(f"✅ Multiple indicators fetch completed")
        print(f"   Indicators requested: {indicators}")
        print(f"   Total files: {results['total_files']}")
        print(f"   Errors: {len(results['errors'])}")
        
        for data_result in results['data_fetched']:
            print(f"   {data_result['data_type']}:")
            print(f"     Files downloaded: {data_result['files_downloaded']}")
            print(f"     Data points: {data_result['data_points']}")
            
    except Exception as e:
        print(f"❌ Error fetching multiple indicators: {e}")
    
    # Test 4: Get latest data for an indicator
    print("\n🕒 Test 4: Getting latest data...")
    try:
        latest_data = await fetcher.get_latest_data('key_policy_rate')
        if latest_data:
            print(f"✅ Latest data retrieved")
            print(f"   Value: {latest_data.get('value')}")
            print(f"   Date: {latest_data.get('latest_date')}")
            print(f"   Unit: {latest_data.get('unit')}")
        else:
            print("ℹ️  No latest data available")
            
    except Exception as e:
        print(f"❌ Error getting latest data: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Economic Data Fetcher tests completed!")

async def test_api_integration():
    """Test the API integration"""
    
    print("\n🌐 Testing API Integration")
    print("=" * 50)
    
    # This would test the FastAPI endpoints
    # For now, just show the expected API structure
    
    api_endpoints = [
        "GET /api/economic-data/",
        "GET /api/economic-data/indicators",
        "GET /api/economic-data/key_policy_rate",
        "GET /api/economic-data/key_policy_rate/latest",
        "POST /api/economic-data/fetch",
        "GET /api/economic-data/compare/key_policy_rate/inflation_cpi",
        "GET /api/economic-data/trends/key_policy_rate",
        "GET /api/economic-data/dashboard/overview"
    ]
    
    print("Available API endpoints:")
    for endpoint in api_endpoints:
        print(f"   {endpoint}")
    
    print("\nExample API usage:")
    print("""
    # Get all available indicators
    curl http://localhost:8000/api/economic-data/indicators
    
    # Get key policy rate data
    curl http://localhost:8000/api/economic-data/key_policy_rate
    
    # Get latest inflation data
    curl http://localhost:8000/api/economic-data/inflation_cpi/latest
    
    # Fetch new data from BAM
    curl -X POST http://localhost:8000/api/economic-data/fetch
    
    # Get economic dashboard
    curl http://localhost:8000/api/economic-data/dashboard/overview
    """)

def show_data_structure():
    """Show the data structure and models"""
    
    print("\n📋 Data Structure Overview")
    print("=" * 50)
    
    print("Economic Indicators:")
    for indicator in EconomicIndicatorType:
        print(f"   • {indicator.value}")
    
    print("\nData Models:")
    models = [
        "EconomicDataPoint - Individual data point",
        "EconomicDataSet - Collection of data points",
        "EconomicDataRaw - Raw downloaded data",
        "EconomicDataParsed - Processed data",
        "EconomicDataSummary - API response summary"
    ]
    
    for model in models:
        print(f"   • {model}")
    
    print("\nExample Data Point:")
    example_data = {
        "date": "2024-01-15",
        "value": 3.0,
        "unit": "percent",
        "indicator": "key_policy_rate",
        "source": "BAM",
        "confidence": 0.95
    }
    
    for key, value in example_data.items():
        print(f"   {key}: {value}")

async def main():
    """Main test function"""
    
    print("🏦 Casablanca Insight - Economic Data Fetcher")
    print("Testing Moroccan Economic Data from BAM")
    print("=" * 60)
    
    # Show data structure
    show_data_structure()
    
    # Test the fetcher
    await test_economic_data_fetcher()
    
    # Test API integration
    await test_api_integration()
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed!")
    print("\nNext steps:")
    print("1. Run the backend server: python main.py")
    print("2. Test API endpoints with curl or Postman")
    print("3. Integrate with frontend dashboard")
    print("4. Set up automated data fetching with cron jobs")

if __name__ == "__main__":
    asyncio.run(main()) 