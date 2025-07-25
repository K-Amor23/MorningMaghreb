#!/usr/bin/env python3
"""
Pytest tests for FastAPI endpoints

Tests for:
- /api/companies/{id}/summary
- /api/companies/{id}/trading  
- /api/companies/{id}/reports
- /api/companies/{id}/news
"""

import pytest
import requests
import json
import os
from typing import Dict, List
import time

# Test configuration
BASE_URL = "http://localhost:3000"  # Next.js development server
TEST_COMPANIES = ["ATW", "IAM", "BCP", "GAZ", "MNG"]  # Top 5 companies

class TestAPIEndpoints:
    """Test suite for API endpoints"""
    
    def setup_method(self):
        """Setup before each test"""
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Casablanca-Insights-Test-Suite/1.0'
        })
    
    def test_health_check(self):
        """Test if the server is running"""
        try:
            response = self.session.get(f"{BASE_URL}/api/health", timeout=5)
            assert response.status_code == 200
        except requests.exceptions.RequestException:
            pytest.skip("Server not running")
    
    @pytest.mark.parametrize("ticker", TEST_COMPANIES)
    def test_company_summary_endpoint(self, ticker: str):
        """Test /api/companies/{id}/summary endpoint"""
        url = f"{BASE_URL}/api/companies/{ticker}/summary"
        
        response = self.session.get(url, timeout=10)
        
        # Should return 200 or 404 (if company not found)
        assert response.status_code in [200, 404], f"Unexpected status code: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            assert 'company' in data
            assert 'priceData' in data
            assert 'metadata' in data
            
            # Check company data
            company = data['company']
            assert company['ticker'] == ticker
            assert 'name' in company
            assert 'sector' in company
            assert 'currentPrice' in company
            
            # Check price data
            price_data = data['priceData']
            assert 'last90Days' in price_data
            assert 'currentPrice' in price_data
            assert 'priceChange' in price_data
            assert 'priceChangePercent' in price_data
            
            # Check metadata
            metadata = data['metadata']
            assert 'dataQuality' in metadata
            assert 'lastUpdated' in metadata
            assert 'sources' in metadata
            
            print(f"✅ {ticker}: Summary endpoint working")
        else:
            print(f"⚠️  {ticker}: Company not found in database")
    
    @pytest.mark.parametrize("ticker", TEST_COMPANIES)
    def test_company_trading_endpoint(self, ticker: str):
        """Test /api/companies/{id}/trading endpoint"""
        url = f"{BASE_URL}/api/companies/{ticker}/trading"
        
        response = self.session.get(url, timeout=10)
        
        # Should return 200 or 404 (if company not found)
        assert response.status_code in [200, 404], f"Unexpected status code: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            assert 'company' in data
            assert 'priceData' in data
            assert 'metadata' in data
            
            # Check company data
            company = data['company']
            assert company['ticker'] == ticker
            assert 'name' in company
            assert 'currentPrice' in company
            
            # Check price data
            price_data = data['priceData']
            assert 'last90Days' in price_data
            assert isinstance(price_data['last90Days'], list)
            
            # Check if we have real price data
            if len(price_data['last90Days']) > 0:
                first_price = price_data['last90Days'][0]
                assert 'date' in first_price
                assert 'open' in first_price
                assert 'high' in first_price
                assert 'low' in first_price
                assert 'close' in first_price
                assert 'volume' in first_price
            
            # Check sentiment data (optional)
            if 'sentiment' in data and data['sentiment']:
                sentiment = data['sentiment']
                assert 'bullishPercentage' in sentiment
                assert 'bearishPercentage' in sentiment
                assert 'neutralPercentage' in sentiment
            
            print(f"✅ {ticker}: Trading endpoint working")
        else:
            print(f"⚠️  {ticker}: Company not found in database")
    
    @pytest.mark.parametrize("ticker", TEST_COMPANIES)
    def test_company_reports_endpoint(self, ticker: str):
        """Test /api/companies/{id}/reports endpoint"""
        url = f"{BASE_URL}/api/companies/{ticker}/reports"
        
        response = self.session.get(url, timeout=10)
        
        # Should return 200 or 404 (if company not found)
        assert response.status_code in [200, 404], f"Unexpected status code: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            assert 'company' in data
            assert 'reports' in data
            assert 'metadata' in data
            
            # Check company data
            company = data['company']
            assert company['ticker'] == ticker
            assert 'name' in company
            
            # Check reports data
            reports = data['reports']
            assert 'all' in reports
            assert 'byType' in reports
            assert 'totalCount' in reports
            assert isinstance(reports['all'], list)
            assert isinstance(reports['byType'], dict)
            
            # Check report types
            by_type = reports['byType']
            expected_types = ['annual_reports', 'quarterly_reports', 'financial_statements', 'earnings', 'other']
            for report_type in expected_types:
                assert report_type in by_type
                assert isinstance(by_type[report_type], list)
            
            print(f"✅ {ticker}: Reports endpoint working")
        else:
            print(f"⚠️  {ticker}: Company not found in database")
    
    @pytest.mark.parametrize("ticker", TEST_COMPANIES)
    def test_company_news_endpoint(self, ticker: str):
        """Test /api/companies/{id}/news endpoint"""
        url = f"{BASE_URL}/api/companies/{ticker}/news"
        
        response = self.session.get(url, timeout=10)
        
        # Should return 200 or 404 (if company not found)
        assert response.status_code in [200, 404], f"Unexpected status code: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            assert 'company' in data
            assert 'news' in data
            assert 'metadata' in data
            
            # Check company data
            company = data['company']
            assert company['ticker'] == ticker
            assert 'name' in company
            
            # Check news data
            news = data['news']
            assert 'items' in news
            assert 'sentimentDistribution' in news
            assert 'totalCount' in news
            assert isinstance(news['items'], list)
            
            # Check sentiment distribution
            sentiment_dist = news['sentimentDistribution']
            assert 'positive' in sentiment_dist
            assert 'negative' in sentiment_dist
            assert 'neutral' in sentiment_dist
            assert 'total' in sentiment_dist
            
            # Check individual news items
            if len(news['items']) > 0:
                first_news = news['items'][0]
                assert 'headline' in first_news
                assert 'source' in first_news
                assert 'publishedAt' in first_news
                assert 'sentiment' in first_news
            
            print(f"✅ {ticker}: News endpoint working")
        else:
            print(f"⚠️  {ticker}: Company not found in database")
    
    @pytest.mark.parametrize("ticker", TEST_COMPANIES)
    def test_company_news_with_limit(self, ticker: str):
        """Test /api/companies/{id}/news endpoint with limit parameter"""
        url = f"{BASE_URL}/api/companies/{ticker}/news?limit=5"
        
        response = self.session.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            news = data['news']
            
            # Check that limit is respected
            assert len(news['items']) <= 5
            assert news['totalCount'] >= len(news['items'])
            
            print(f"✅ {ticker}: News endpoint with limit working")
    
    @pytest.mark.parametrize("ticker", TEST_COMPANIES)
    def test_company_news_with_sentiment_filter(self, ticker: str):
        """Test /api/companies/{id}/news endpoint with sentiment filter"""
        for sentiment in ['positive', 'negative', 'neutral']:
            url = f"{BASE_URL}/api/companies/{ticker}/news?sentiment={sentiment}"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                news = data['news']
                
                # Check that all returned news items have the correct sentiment
                for item in news['items']:
                    assert item['sentiment'] == sentiment
                
                print(f"✅ {ticker}: News endpoint with {sentiment} filter working")
    
    def test_invalid_company_ticker(self):
        """Test endpoints with invalid company ticker"""
        invalid_ticker = "INVALID123"
        
        endpoints = [
            f"/api/companies/{invalid_ticker}/summary",
            f"/api/companies/{invalid_ticker}/trading",
            f"/api/companies/{invalid_ticker}/reports",
            f"/api/companies/{invalid_ticker}/news"
        ]
        
        for endpoint in endpoints:
            url = f"{BASE_URL}{endpoint}"
            response = self.session.get(url, timeout=10)
            
            # Should return 404 for invalid ticker
            assert response.status_code == 404, f"Expected 404 for {endpoint}"
        
        print("✅ Invalid ticker handling working")
    
    def test_endpoint_performance(self):
        """Test endpoint response times"""
        ticker = "ATW"  # Use a company that should exist
        
        endpoints = [
            f"/api/companies/{ticker}/summary",
            f"/api/companies/{ticker}/trading",
            f"/api/companies/{ticker}/reports",
            f"/api/companies/{ticker}/news"
        ]
        
        for endpoint in endpoints:
            url = f"{BASE_URL}{endpoint}"
            
            start_time = time.time()
            response = self.session.get(url, timeout=10)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Should respond within 2 seconds
            assert response_time < 2.0, f"Slow response time for {endpoint}: {response_time:.2f}s"
            
            print(f"✅ {endpoint}: {response_time:.2f}s")
    
    def test_data_consistency(self):
        """Test data consistency across endpoints"""
        ticker = "ATW"  # Use a company that should exist
        
        # Get data from all endpoints
        endpoints = {
            'summary': f"/api/companies/{ticker}/summary",
            'trading': f"/api/companies/{ticker}/trading",
            'reports': f"/api/companies/{ticker}/reports",
            'news': f"/api/companies/{ticker}/news"
        }
        
        data = {}
        for name, endpoint in endpoints.items():
            url = f"{BASE_URL}{endpoint}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data[name] = response.json()
        
        # Check company consistency across endpoints
        if 'summary' in data and 'trading' in data:
            summary_company = data['summary']['company']
            trading_company = data['trading']['company']
            
            assert summary_company['ticker'] == trading_company['ticker']
            assert summary_company['name'] == trading_company['name']
            assert summary_company['sector'] == trading_company['sector']
        
        print("✅ Data consistency across endpoints verified")

def run_tests():
    """Run all tests"""
    print("🚀 Starting API endpoint tests...")
    print(f"📡 Testing against: {BASE_URL}")
    print(f"🏢 Test companies: {TEST_COMPANIES}")
    print("=" * 60)
    
    # Create test instance
    test_instance = TestAPIEndpoints()
    test_instance.setup_method()
    
    # Run tests
    test_methods = [
        test_instance.test_health_check,
        test_instance.test_company_summary_endpoint,
        test_instance.test_company_trading_endpoint,
        test_instance.test_company_reports_endpoint,
        test_instance.test_company_news_endpoint,
        test_instance.test_invalid_company_ticker,
        test_instance.test_endpoint_performance,
        test_instance.test_data_consistency
    ]
    
    passed = 0
    failed = 0
    
    for test_method in test_methods:
        try:
            test_method()
            passed += 1
        except Exception as e:
            print(f"❌ {test_method.__name__}: {str(e)}")
            failed += 1
    
    print("=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed")
        return False

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 