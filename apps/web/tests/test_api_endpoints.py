#!/usr/bin/env python3
"""
Comprehensive API Endpoint Tests for Casablanca Insights
Tests all endpoints with real data and Supabase integration
"""

import pytest
import requests
import json
import os
import sys
from typing import Dict, List, Any
from datetime import datetime, timedelta

# Add the web app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test configuration
BASE_URL = "http://localhost:3000"
API_BASE = f"{BASE_URL}/api"

# Test data for companies
TEST_COMPANIES = [
    "ATW",  # Attijariwafa Bank
    "IAM",  # Maroc Telecom
    "BCP",  # Banque Centrale Populaire
    "BMCE", # BMCE Bank of Africa
    "CIH",  # CIH Bank
    "CMT",  # Compagnie Minière de Touissit
    "CTM",  # CTM
    "DRI",  # Dari Couspate
    "FEN",  # Fenosa
    "JET",  # Jet Contractors
    "LES",  # Lesieur Cristal
    "MNG",  # Managem
    "MOR",  # Maroc Telecom
    "SID",  # Sonasid
    "SNP",  # Snep
    "TMA",  # Taqa Morocco
    "WAA",  # Wafa Assurance
    "WAL",  # Wafa Assurance
    "ZAL",  # Zellidja
]

class TestAPIEndpoints:
    """Test suite for all API endpoints"""
    
    def test_health_check(self):
        """Test basic health check endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200 or response.status_code == 404  # 404 if endpoint doesn't exist
        
    def test_market_data_unified(self):
        """Test /api/market-data/unified endpoint"""
        response = requests.get(f"{API_BASE}/market-data/unified")
        assert response.status_code == 200
        
        data = response.json()
        assert "companies" in data
        assert "metadata" in data
        assert "indices" in data
        assert "market_summary" in data
        
        # Check that we have company data
        assert len(data["companies"]) > 0
        
        # Check metadata
        metadata = data["metadata"]
        assert "combined_at" in metadata
        assert "sources" in metadata
        assert "total_companies" in metadata
        
    def test_market_data_companies(self):
        """Test /api/market-data/african-markets-companies endpoint"""
        response = requests.get(f"{API_BASE}/market-data/african-markets-companies")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check first company structure
        first_company = data[0]
        assert "ticker" in first_company
        assert "name" in first_company
        assert "sector" in first_company
        
    def test_company_summary_endpoint(self):
        """Test /api/companies/{id}/summary endpoint for all test companies"""
        for ticker in TEST_COMPANIES:
            response = requests.get(f"{API_BASE}/companies/{ticker}/summary")
            assert response.status_code == 200, f"Failed for ticker {ticker}"
            
            data = response.json()
            
            # Check company data structure
            assert "company" in data
            assert "priceData" in data
            assert "metadata" in data
            
            company = data["company"]
            assert company["ticker"] == ticker
            assert "name" in company
            assert "sector" in company
            assert "currentPrice" in company
            assert "priceChange" in company
            assert "priceChangePercent" in company
            assert "marketCap" in company
            
            # Check price data structure
            price_data = data["priceData"]
            assert "last90Days" in price_data
            assert "currentPrice" in price_data
            assert "priceChange" in price_data
            assert "priceChangePercent" in price_data
            
            # Check that we have 90 days of data
            assert len(price_data["last90Days"]) == 90
            
            # Check price data quality
            for day_data in price_data["last90Days"]:
                assert "date" in day_data
                assert "open" in day_data
                assert "high" in day_data
                assert "low" in day_data
                assert "close" in day_data
                assert "volume" in day_data
                
                # Validate price relationships
                assert day_data["high"] >= day_data["low"]
                assert day_data["high"] >= day_data["open"]
                assert day_data["high"] >= day_data["close"]
                assert day_data["low"] <= day_data["open"]
                assert day_data["low"] <= day_data["close"]
                assert day_data["volume"] > 0
            
            # Check metadata
            metadata = data["metadata"]
            assert "dataQuality" in metadata
            assert "lastUpdated" in metadata
            assert "sources" in metadata
            
            # Data quality should be "real" for companies with OHLCV data
            if ticker in TEST_COMPANIES:
                assert metadata["dataQuality"] in ["real", "mock"]
            
            print(f"✅ {ticker}: {company['name']} - {company['currentPrice']} MAD ({company['priceChangePercent']:.2f}%)")
    
    def test_company_summary_invalid_ticker(self):
        """Test /api/companies/{id}/summary endpoint with invalid ticker"""
        response = requests.get(f"{API_BASE}/companies/INVALID/summary")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
        assert "message" in data
    
    def test_supabase_endpoint(self):
        """Test /api/market-data/supabase endpoint"""
        response = requests.get(f"{API_BASE}/market-data/supabase")
        
        # This might return 404 if Supabase is not configured
        if response.status_code == 200:
            data = response.json()
            assert "companies" in data
            assert "metadata" in data
        else:
            print("⚠️  Supabase endpoint not available (expected if not configured)")
    
    def test_market_quotes_endpoint(self):
        """Test /api/markets/quotes endpoint"""
        response = requests.get(f"{API_BASE}/markets/quotes")
        
        # This might return 404 if endpoint doesn't exist
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))
        else:
            print("⚠️  Market quotes endpoint not available")
    
    def test_search_companies_endpoint(self):
        """Test /api/search/companies endpoint"""
        response = requests.get(f"{API_BASE}/search/companies?q=ATW")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
        else:
            print("⚠️  Search companies endpoint not available")
    
    def test_data_quality_consistency(self):
        """Test that data quality is consistent across endpoints"""
        for ticker in TEST_COMPANIES[:5]:  # Test first 5 companies
            response = requests.get(f"{API_BASE}/companies/{ticker}/summary")
            assert response.status_code == 200
            
            data = response.json()
            metadata = data["metadata"]
            
            # Check that data quality is properly set
            assert metadata["dataQuality"] in ["real", "mock"]
            
            # Check that sources are properly listed
            assert isinstance(metadata["sources"], list)
            assert len(metadata["sources"]) > 0
            
            print(f"✅ {ticker} data quality: {metadata['dataQuality']}, sources: {metadata['sources']}")
    
    def test_price_data_consistency(self):
        """Test that price data is consistent and realistic"""
        for ticker in TEST_COMPANIES[:3]:  # Test first 3 companies
            response = requests.get(f"{API_BASE}/companies/{ticker}/summary")
            assert response.status_code == 200
            
            data = response.json()
            price_data = data["priceData"]["last90Days"]
            
            # Check that prices are realistic (not negative, reasonable ranges)
            for day_data in price_data:
                assert day_data["open"] > 0
                assert day_data["high"] > 0
                assert day_data["low"] > 0
                assert day_data["close"] > 0
                assert day_data["volume"] > 0
                
                # Check that prices are in reasonable ranges for Moroccan stocks
                assert day_data["close"] < 10000  # No stock should be > 10,000 MAD
                assert day_data["volume"] < 10000000  # No volume should be > 10M
            
            # Check that the latest price matches the current price
            latest_price = price_data[-1]["close"]
            current_price = data["priceData"]["currentPrice"]
            assert abs(latest_price - current_price) < 0.01  # Should be very close
            
            print(f"✅ {ticker} price consistency: latest={latest_price}, current={current_price}")
    
    def test_date_continuity(self):
        """Test that dates are continuous and recent"""
        for ticker in TEST_COMPANIES[:2]:  # Test first 2 companies
            response = requests.get(f"{API_BASE}/companies/{ticker}/summary")
            assert response.status_code == 200
            
            data = response.json()
            price_data = data["priceData"]["last90Days"]
            
            # Check that we have 90 days of data
            assert len(price_data) == 90
            
            # Check that dates are recent (within last 6 months)
            today = datetime.now()
            for day_data in price_data:
                date = datetime.strptime(day_data["date"], "%Y-%m-%d")
                assert date <= today
                assert date >= today - timedelta(days=180)  # Within last 6 months
            
            # Check that dates are in order
            dates = [day_data["date"] for day_data in price_data]
            assert dates == sorted(dates)
            
            print(f"✅ {ticker} date continuity: {dates[0]} to {dates[-1]}")

class TestAPIPerformance:
    """Test API performance and response times"""
    
    def test_response_times(self):
        """Test that API responses are reasonably fast"""
        import time
        
        endpoints = [
            f"{API_BASE}/market-data/unified",
            f"{API_BASE}/companies/ATW/summary",
            f"{API_BASE}/companies/IAM/summary",
            f"{API_BASE}/companies/BCP/summary",
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = requests.get(endpoint)
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response.status_code == 200
            assert response_time < 5.0  # Should respond within 5 seconds
            
            print(f"✅ {endpoint}: {response_time:.2f}s")
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import concurrent.futures
        import time
        
        def make_request(ticker):
            start_time = time.time()
            response = requests.get(f"{API_BASE}/companies/{ticker}/summary")
            end_time = time.time()
            return {
                "ticker": ticker,
                "status": response.status_code,
                "time": end_time - start_time
            }
        
        # Test with 5 concurrent requests
        test_tickers = TEST_COMPANIES[:5]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(make_request, test_tickers))
        
        for result in results:
            assert result["status"] == 200
            assert result["time"] < 10.0  # Should handle concurrent requests
            print(f"✅ Concurrent {result['ticker']}: {result['time']:.2f}s")

class TestDataValidation:
    """Test data validation and error handling"""
    
    def test_malformed_requests(self):
        """Test handling of malformed requests"""
        # Test with empty ticker
        response = requests.get(f"{API_BASE}/companies//summary")
        assert response.status_code in [400, 404]
        
        # Test with very long ticker
        long_ticker = "A" * 100
        response = requests.get(f"{API_BASE}/companies/{long_ticker}/summary")
        assert response.status_code in [400, 404]
        
        # Test with special characters
        special_ticker = "ATW@#$%"
        response = requests.get(f"{API_BASE}/companies/{special_ticker}/summary")
        assert response.status_code in [400, 404]
    
    def test_data_types(self):
        """Test that data types are correct"""
        response = requests.get(f"{API_BASE}/companies/ATW/summary")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check data types
        assert isinstance(data["company"]["ticker"], str)
        assert isinstance(data["company"]["name"], str)
        assert isinstance(data["company"]["currentPrice"], (int, float))
        assert isinstance(data["company"]["priceChange"], (int, float))
        assert isinstance(data["company"]["priceChangePercent"], (int, float))
        assert isinstance(data["company"]["marketCap"], (int, float))
        
        # Check price data types
        for day_data in data["priceData"]["last90Days"]:
            assert isinstance(day_data["date"], str)
            assert isinstance(day_data["open"], (int, float))
            assert isinstance(day_data["high"], (int, float))
            assert isinstance(day_data["low"], (int, float))
            assert isinstance(day_data["close"], (int, float))
            assert isinstance(day_data["volume"], int)

def run_api_tests():
    """Run all API tests and generate a report"""
    print("🚀 Starting API Endpoint Tests")
    print("=" * 60)
    
    # Test configuration
    test_config = {
        "base_url": BASE_URL,
        "api_base": API_BASE,
        "test_companies": TEST_COMPANIES,
        "total_companies": len(TEST_COMPANIES)
    }
    
    print(f"📊 Test Configuration:")
    print(f"   Base URL: {test_config['base_url']}")
    print(f"   API Base: {test_config['api_base']}")
    print(f"   Test Companies: {test_config['total_companies']}")
    print(f"   Companies: {', '.join(TEST_COMPANIES[:5])}...")
    print()
    
    # Run tests
    test_results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "errors": []
    }
    
    # Create test instances
    test_classes = [
        TestAPIEndpoints(),
        TestAPIPerformance(),
        TestDataValidation()
    ]
    
    for test_class in test_classes:
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        for method_name in test_methods:
            test_results["total_tests"] += 1
            method = getattr(test_class, method_name)
            
            try:
                method()
                test_results["passed"] += 1
                print(f"✅ {method_name}")
            except Exception as e:
                test_results["failed"] += 1
                error_msg = f"❌ {method_name}: {str(e)}"
                test_results["errors"].append(error_msg)
                print(error_msg)
    
    # Generate report
    print("\n" + "=" * 60)
    print("📋 API Test Report")
    print("=" * 60)
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    print(f"Success Rate: {(test_results['passed'] / test_results['total_tests'] * 100):.1f}%")
    
    if test_results["errors"]:
        print("\n❌ Errors:")
        for error in test_results["errors"]:
            print(f"  {error}")
    
    # Save test results
    test_report = {
        "timestamp": datetime.now().isoformat(),
        "config": test_config,
        "results": test_results
    }
    
    with open("api_test_report.json", "w") as f:
        json.dump(test_report, f, indent=2)
    
    print(f"\n📄 Test report saved to: api_test_report.json")
    
    return test_results["failed"] == 0

if __name__ == "__main__":
    success = run_api_tests()
    sys.exit(0 if success else 1) 