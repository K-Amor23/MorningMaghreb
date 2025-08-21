#!/usr/bin/env python3
"""
Test Volume Integration for Airflow

This script tests the volume scraper integration in the Airflow environment.
"""

import sys
import os
from pathlib import Path

# Add ETL directory to path
etl_dir = Path(__file__).parent / "etl"
sys.path.append(str(etl_dir))

def test_volume_scraper_import():
    """Test if volume scraper can be imported"""
    try:
        from volume_scraper import VolumeScraper
        print("✅ VolumeScraper imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import VolumeScraper: {e}")
        return False

def test_volume_integration_import():
    """Test if volume integration can be imported"""
    try:
        from volume_data_integration import VolumeDataIntegration
        print("✅ VolumeDataIntegration imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import VolumeDataIntegration: {e}")
        return False

def test_african_markets_import():
    """Test if African Markets scraper can be imported"""
    try:
        from african_markets_scraper import AfricanMarketsScraper
        print("✅ AfricanMarketsScraper imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import AfricanMarketsScraper: {e}")
        return False

def test_environment_variables():
    """Test if required environment variables are set"""
    required_vars = [
        "NEXT_PUBLIC_SUPABASE_URL",
        "NEXT_PUBLIC_SUPABASE_ANON_KEY"
    ]
    
    all_set = True
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is not set")
            all_set = False
    
    return all_set

if __name__ == "__main__":
    print("🧪 Testing Volume Integration for Airflow")
    print("=" * 50)
    
    tests = [
        test_volume_scraper_import,
        test_volume_integration_import,
        test_african_markets_import,
        test_environment_variables
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Volume integration is ready for Airflow.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
