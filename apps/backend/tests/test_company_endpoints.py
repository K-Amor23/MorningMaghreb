import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date, timedelta
from decimal import Decimal
import json

# Import the FastAPI app
from main import app

# Test client
client = TestClient(app)

# ============================================
# TEST DATA
# ============================================

# Sample company data for testing
TEST_COMPANIES = {
    "IAM": {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "ticker": "IAM",
        "name": "Maroc Telecom",
        "sector": "Telecommunications",
        "industry": "Telecom Services",
        "market_cap_billion": Decimal("15.5"),
        "price": Decimal("125.50"),
        "change_1d_percent": Decimal("2.5"),
        "change_ytd_percent": Decimal("12.3"),
        "size_category": "Large Cap",
        "sector_group": "Technology",
        "exchange": "Casablanca Stock Exchange (BVC)",
        "country": "Morocco",
        "company_url": "https://www.iam.ma",
        "ir_url": "https://www.iam.ma/investors",
        "is_active": True,
        "updated_at": datetime.utcnow()
    },
    "ATW": {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "ticker": "ATW",
        "name": "Attijariwafa Bank",
        "sector": "Financial Services",
        "industry": "Banking",
        "market_cap_billion": Decimal("8.2"),
        "price": Decimal("89.75"),
        "change_1d_percent": Decimal("-1.2"),
        "change_ytd_percent": Decimal("5.8"),
        "size_category": "Large Cap",
        "sector_group": "Financials",
        "exchange": "Casablanca Stock Exchange (BVC)",
        "country": "Morocco",
        "company_url": "https://www.attijariwafabank.com",
        "ir_url": "https://www.attijariwafabank.com/investors",
        "is_active": True,
        "updated_at": datetime.utcnow()
    },
    "BCP": {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "ticker": "BCP",
        "name": "Banque Centrale Populaire",
        "sector": "Financial Services",
        "industry": "Banking",
        "market_cap_billion": Decimal("6.8"),
        "price": Decimal("67.25"),
        "change_1d_percent": Decimal("0.8"),
        "change_ytd_percent": Decimal("8.9"),
        "size_category": "Large Cap",
        "sector_group": "Financials",
        "exchange": "Casablanca Stock Exchange (BVC)",
        "country": "Morocco",
        "company_url": "https://www.banquecentrale.ma",
        "ir_url": "https://www.banquecentrale.ma/investors",
        "is_active": True,
        "updated_at": datetime.utcnow()
    }
}

# Sample price data
TEST_PRICES = {
    "IAM": [
        {
            "date": date.today(),
            "open": Decimal("123.00"),
            "high": Decimal("127.50"),
            "low": Decimal("122.50"),
            "close": Decimal("125.50"),
            "volume": 1500000,
            "adjusted_close": Decimal("125.50")
        },
        {
            "date": date.today() - timedelta(days=1),
            "open": Decimal("122.00"),
            "high": Decimal("124.00"),
            "low": Decimal("121.00"),
            "close": Decimal("122.50"),
            "volume": 1200000,
            "adjusted_close": Decimal("122.50")
        }
    ],
    "ATW": [
        {
            "date": date.today(),
            "open": Decimal("90.00"),
            "high": Decimal("91.00"),
            "low": Decimal("88.50"),
            "close": Decimal("89.75"),
            "volume": 800000,
            "adjusted_close": Decimal("89.75")
        },
        {
            "date": date.today() - timedelta(days=1),
            "open": Decimal("89.00"),
            "high": Decimal("91.50"),
            "low": Decimal("88.00"),
            "close": Decimal("90.85"),
            "volume": 750000,
            "adjusted_close": Decimal("90.85")
        }
    ],
    "BCP": [
        {
            "date": date.today(),
            "open": Decimal("66.50"),
            "high": Decimal("68.00"),
            "low": Decimal("66.00"),
            "close": Decimal("67.25"),
            "volume": 600000,
            "adjusted_close": Decimal("67.25")
        },
        {
            "date": date.today() - timedelta(days=1),
            "open": Decimal("67.00"),
            "high": Decimal("67.50"),
            "low": Decimal("66.25"),
            "close": Decimal("66.75"),
            "volume": 550000,
            "adjusted_close": Decimal("66.75")
        }
    ]
}

# Sample reports data
TEST_REPORTS = {
    "IAM": [
        {
            "title": "Annual Report 2023",
            "report_type": "annual_report",
            "report_date": "2023-12-31",
            "report_year": "2023",
            "report_quarter": None,
            "url": "https://www.iam.ma/reports/annual-2023.pdf",
            "filename": "annual_report_2023.pdf",
            "scraped_at": datetime.utcnow() - timedelta(days=30)
        },
        {
            "title": "Q3 2023 Financial Results",
            "report_type": "quarterly_report",
            "report_date": "2023-09-30",
            "report_year": "2023",
            "report_quarter": "Q3",
            "url": "https://www.iam.ma/reports/q3-2023.pdf",
            "filename": "q3_2023_results.pdf",
            "scraped_at": datetime.utcnow() - timedelta(days=60)
        }
    ],
    "ATW": [
        {
            "title": "Annual Report 2023",
            "report_type": "annual_report",
            "report_date": "2023-12-31",
            "report_year": "2023",
            "report_quarter": None,
            "url": "https://www.attijariwafabank.com/reports/annual-2023.pdf",
            "filename": "annual_report_2023.pdf",
            "scraped_at": datetime.utcnow() - timedelta(days=25)
        }
    ],
    "BCP": [
        {
            "title": "Q4 2023 Financial Results",
            "report_type": "quarterly_report",
            "report_date": "2023-12-31",
            "report_year": "2023",
            "report_quarter": "Q4",
            "url": "https://www.banquecentrale.ma/reports/q4-2023.pdf",
            "filename": "q4_2023_results.pdf",
            "scraped_at": datetime.utcnow() - timedelta(days=15)
        }
    ]
}

# Sample news data
TEST_NEWS = {
    "IAM": [
        {
            "headline": "Maroc Telecom Reports Strong Q4 Results",
            "source": "Financial Times",
            "published_at": datetime.utcnow() - timedelta(days=5),
            "sentiment": "positive",
            "sentiment_score": Decimal("0.8"),
            "url": "https://www.ft.com/iam-q4-results",
            "content_preview": "Maroc Telecom announced strong fourth quarter results...",
            "scraped_at": datetime.utcnow() - timedelta(days=5)
        },
        {
            "headline": "IAM Expands 5G Network Coverage",
            "source": "Reuters",
            "published_at": datetime.utcnow() - timedelta(days=10),
            "sentiment": "positive",
            "sentiment_score": Decimal("0.6"),
            "url": "https://www.reuters.com/iam-5g-expansion",
            "content_preview": "Maroc Telecom expands its 5G network coverage...",
            "scraped_at": datetime.utcnow() - timedelta(days=10)
        }
    ],
    "ATW": [
        {
            "headline": "Attijariwafa Bank Announces Dividend Increase",
            "source": "Bloomberg",
            "published_at": datetime.utcnow() - timedelta(days=3),
            "sentiment": "positive",
            "sentiment_score": Decimal("0.7"),
            "url": "https://www.bloomberg.com/atw-dividend",
            "content_preview": "Attijariwafa Bank announced an increase in dividend...",
            "scraped_at": datetime.utcnow() - timedelta(days=3)
        }
    ],
    "BCP": [
        {
            "headline": "BCP Reports Lower Than Expected Q4 Earnings",
            "source": "Financial Times",
            "published_at": datetime.utcnow() - timedelta(days=7),
            "sentiment": "negative",
            "sentiment_score": Decimal("-0.4"),
            "url": "https://www.ft.com/bcp-q4-earnings",
            "content_preview": "Banque Centrale Populaire reported lower than expected...",
            "scraped_at": datetime.utcnow() - timedelta(days=7)
        }
    ]
}

# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def mock_db_session():
    """Mock database session"""
    with patch('routers.companies.get_db_session') as mock:
        session = AsyncMock()
        mock.return_value = session
        yield session

@pytest.fixture
def mock_analytics_service():
    """Mock analytics service"""
    with patch('routers.companies.get_analytics_service') as mock:
        service = AsyncMock()
        mock.return_value = service
        yield service

# ============================================
# TEST CASES
# ============================================

class TestCompanySummaryEndpoint:
    """Test cases for /companies/{ticker}/summary endpoint"""
    
    @pytest.mark.parametrize("ticker", ["IAM", "ATW", "BCP"])
    def test_get_company_summary_success(self, ticker, mock_db_session):
        """Test successful company summary retrieval"""
        # Mock database response
        company_data = TEST_COMPANIES[ticker]
        prices_data = TEST_PRICES[ticker]
        reports_data = TEST_REPORTS[ticker]
        news_data = TEST_NEWS[ticker]
        
        # Mock database queries
        mock_db_session.execute.return_value.fetchone.side_effect = [
            MagicMock(_mapping=company_data),  # Company data
            MagicMock(fetchall=lambda: [MagicMock(_mapping=p) for p in prices_data]),  # Prices
            MagicMock(fetchall=lambda: [MagicMock(_mapping=r) for r in reports_data]),  # Reports
            MagicMock(fetchall=lambda: [MagicMock(_mapping=n) for n in news_data])  # News
        ]
        
        # Make request
        response = client.get(f"/api/companies/{ticker}/summary")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        
        assert data["company"]["ticker"] == ticker
        assert data["company"]["name"] == company_data["name"]
        assert data["company"]["sector"] == company_data["sector"]
        assert "current_price" in data
        assert "data_quality" in data
        assert data["data_quality"] in ["Partial", "Complete"]
    
    def test_get_company_summary_not_found(self, mock_db_session):
        """Test company summary for non-existent company"""
        # Mock database to return no results
        mock_db_session.execute.return_value.fetchone.return_value = None
        
        response = client.get("/api/companies/INVALID/summary")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["error"].lower()
    
    def test_get_company_summary_invalid_ticker(self):
        """Test company summary with invalid ticker format"""
        response = client.get("/api/companies/invalid/summary")
        
        assert response.status_code == 400
        data = response.json()
        assert "uppercase letters" in data["error"].lower()

class TestCompanyTradingEndpoint:
    """Test cases for /companies/{ticker}/trading endpoint"""
    
    @pytest.mark.parametrize("ticker", ["IAM", "ATW", "BCP"])
    def test_get_company_trading_success(self, ticker, mock_db_session, mock_analytics_service):
        """Test successful trading data retrieval"""
        # Mock database response
        company_data = TEST_COMPANIES[ticker]
        prices_data = TEST_PRICES[ticker]
        
        # Mock database queries
        mock_db_session.execute.return_value.fetchone.side_effect = [
            MagicMock(_mapping=company_data),  # Company data
            MagicMock(fetchall=lambda: [MagicMock(_mapping=p) for p in prices_data])  # Prices
        ]
        
        # Mock analytics service
        mock_analytics_service.generate_signals.return_value = []
        
        # Make request
        response = client.get(f"/api/companies/{ticker}/trading?days=90&include_signals=true")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        
        assert data["ticker"] == ticker
        assert "prices" in data
        assert len(data["prices"]) > 0
        assert "current_price" in data
        assert "signals" in data
        assert "data_quality" in data
    
    def test_get_company_trading_no_price_data(self, mock_db_session):
        """Test trading data when no price data exists"""
        # Mock company exists but no price data
        company_data = TEST_COMPANIES["IAM"]
        mock_db_session.execute.return_value.fetchone.side_effect = [
            MagicMock(_mapping=company_data),  # Company data
            MagicMock(fetchall=lambda: [])  # No prices
        ]
        
        response = client.get("/api/companies/IAM/trading")
        
        assert response.status_code == 404
        data = response.json()
        assert "no price data" in data["error"].lower()
    
    def test_get_company_trading_with_signals(self, mock_db_session, mock_analytics_service):
        """Test trading data with technical signals"""
        # Mock database response
        company_data = TEST_COMPANIES["IAM"]
        prices_data = TEST_PRICES["IAM"]
        
        # Mock database queries
        mock_db_session.execute.return_value.fetchone.side_effect = [
            MagicMock(_mapping=company_data),  # Company data
            MagicMock(fetchall=lambda: [MagicMock(_mapping=p) for p in prices_data])  # Prices
        ]
        
        # Mock analytics service with signals
        mock_signals = [
            {
                "signal_date": date.today(),
                "signal_type": "buy",
                "indicator": "rsi",
                "value": Decimal("30.5"),
                "threshold": Decimal("30.0"),
                "confidence": Decimal("0.8"),
                "description": "RSI indicates oversold condition"
            }
        ]
        mock_analytics_service.generate_signals.return_value = mock_signals
        
        response = client.get("/api/companies/IAM/trading?include_signals=true")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["signals"]) > 0
        assert data["signals"][0]["signal_type"] == "buy"

class TestCompanyReportsEndpoint:
    """Test cases for /companies/{ticker}/reports endpoint"""
    
    @pytest.mark.parametrize("ticker", ["IAM", "ATW", "BCP"])
    def test_get_company_reports_success(self, ticker, mock_db_session):
        """Test successful reports data retrieval"""
        # Mock database response
        company_data = TEST_COMPANIES[ticker]
        reports_data = TEST_REPORTS[ticker]
        
        # Mock database queries
        mock_db_session.execute.return_value.fetchone.side_effect = [
            MagicMock(_mapping=company_data),  # Company data
            MagicMock(fetchall=lambda: [MagicMock(_mapping=r) for r in reports_data])  # Reports
        ]
        
        # Make request
        response = client.get(f"/api/companies/{ticker}/reports")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        
        assert data["ticker"] == ticker
        assert "reports" in data
        assert data["total_reports"] == len(reports_data)
        assert "latest_report" in data
        assert "report_types" in data
        assert "data_quality" in data
    
    def test_get_company_reports_with_filters(self, mock_db_session):
        """Test reports data with filters"""
        # Mock database response
        company_data = TEST_COMPANIES["IAM"]
        reports_data = [r for r in TEST_REPORTS["IAM"] if r["report_type"] == "annual_report"]
        
        # Mock database queries
        mock_db_session.execute.return_value.fetchone.side_effect = [
            MagicMock(_mapping=company_data),  # Company data
            MagicMock(fetchall=lambda: [MagicMock(_mapping=r) for r in reports_data])  # Reports
        ]
        
        response = client.get("/api/companies/IAM/reports?report_type=annual_report&year=2023")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_reports"] == len(reports_data)

class TestCompanyNewsEndpoint:
    """Test cases for /companies/{ticker}/news endpoint"""
    
    @pytest.mark.parametrize("ticker", ["IAM", "ATW", "BCP"])
    def test_get_company_news_success(self, ticker, mock_db_session):
        """Test successful news data retrieval"""
        # Mock database response
        company_data = TEST_COMPANIES[ticker]
        news_data = TEST_NEWS[ticker]
        
        # Mock database queries
        mock_db_session.execute.return_value.fetchone.side_effect = [
            MagicMock(_mapping=company_data),  # Company data
            MagicMock(fetchall=lambda: [MagicMock(_mapping=n) for n in news_data])  # News
        ]
        
        # Make request
        response = client.get(f"/api/companies/{ticker}/news")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        
        assert data["ticker"] == ticker
        assert "news" in data
        assert data["total_news"] == len(news_data)
        assert "sentiment_summary" in data
        assert "average_sentiment" in data
        assert "data_quality" in data
    
    def test_get_company_news_with_sentiment_filter(self, mock_db_session):
        """Test news data with sentiment filter"""
        # Mock database response
        company_data = TEST_COMPANIES["IAM"]
        news_data = [n for n in TEST_NEWS["IAM"] if n["sentiment"] == "positive"]
        
        # Mock database queries
        mock_db_session.execute.return_value.fetchone.side_effect = [
            MagicMock(_mapping=company_data),  # Company data
            MagicMock(fetchall=lambda: [MagicMock(_mapping=n) for n in news_data])  # News
        ]
        
        response = client.get("/api/companies/IAM/news?sentiment=positive&days=30")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_news"] == len(news_data)

# ============================================
# INTEGRATION TESTS
# ============================================

class TestCompanyEndpointsIntegration:
    """Integration tests for company endpoints"""
    
    def test_full_company_workflow(self, mock_db_session, mock_analytics_service):
        """Test complete workflow for a company"""
        ticker = "IAM"
        company_data = TEST_COMPANIES[ticker]
        prices_data = TEST_PRICES[ticker]
        reports_data = TEST_REPORTS[ticker]
        news_data = TEST_NEWS[ticker]
        
        # Mock all database responses
        mock_db_session.execute.return_value.fetchone.side_effect = [
            MagicMock(_mapping=company_data),  # Company data
            MagicMock(fetchall=lambda: [MagicMock(_mapping=p) for p in prices_data]),  # Prices
            MagicMock(fetchall=lambda: [MagicMock(_mapping=r) for r in reports_data]),  # Reports
            MagicMock(fetchall=lambda: [MagicMock(_mapping=n) for n in news_data]),  # News
            MagicMock(_mapping=company_data),  # Company data for trading
            MagicMock(fetchall=lambda: [MagicMock(_mapping=p) for p in prices_data]),  # Prices for trading
            MagicMock(_mapping=company_data),  # Company data for reports
            MagicMock(fetchall=lambda: [MagicMock(_mapping=r) for r in reports_data]),  # Reports
            MagicMock(_mapping=company_data),  # Company data for news
            MagicMock(fetchall=lambda: [MagicMock(_mapping=n) for n in news_data])  # News
        ]
        
        mock_analytics_service.generate_signals.return_value = []
        
        # Test all endpoints
        endpoints = [
            f"/api/companies/{ticker}/summary",
            f"/api/companies/{ticker}/trading",
            f"/api/companies/{ticker}/reports",
            f"/api/companies/{ticker}/news"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"Failed for endpoint: {endpoint}"
            data = response.json()
            assert "data_quality" in data, f"Missing data_quality for endpoint: {endpoint}"

# ============================================
# ERROR HANDLING TESTS
# ============================================

class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_database_connection_error(self, mock_db_session):
        """Test handling of database connection errors"""
        # Mock database to raise exception
        mock_db_session.execute.side_effect = Exception("Database connection failed")
        
        response = client.get("/api/companies/IAM/summary")
        
        assert response.status_code == 500
        data = response.json()
        assert "internal server error" in data["error"].lower()
    
    def test_invalid_query_parameters(self):
        """Test handling of invalid query parameters"""
        # Test invalid days parameter
        response = client.get("/api/companies/IAM/trading?days=1000")
        
        assert response.status_code == 422  # Validation error
        
        # Test invalid limit parameter
        response = client.get("/api/companies/IAM/reports?limit=200")
        
        assert response.status_code == 422  # Validation error

# ============================================
# PERFORMANCE TESTS
# ============================================

class TestPerformance:
    """Test performance characteristics"""
    
    def test_response_time(self, mock_db_session):
        """Test that responses are returned within reasonable time"""
        import time
        
        # Mock database response
        company_data = TEST_COMPANIES["IAM"]
        prices_data = TEST_PRICES["IAM"]
        
        mock_db_session.execute.return_value.fetchone.side_effect = [
            MagicMock(_mapping=company_data),
            MagicMock(fetchall=lambda: [MagicMock(_mapping=p) for p in prices_data])
        ]
        
        start_time = time.time()
        response = client.get("/api/companies/IAM/summary")
        end_time = time.time()
        
        assert response.status_code == 200
        assert end_time - start_time < 1.0  # Should respond within 1 second

# ============================================
# DATA QUALITY TESTS
# ============================================

class TestDataQuality:
    """Test data quality assessment"""
    
    def test_complete_data_quality(self, mock_db_session):
        """Test data quality assessment for complete data"""
        # Mock complete data
        company_data = TEST_COMPANIES["IAM"]
        prices_data = TEST_PRICES["IAM"] * 10  # More price data
        reports_data = TEST_REPORTS["IAM"] * 5  # More reports
        news_data = TEST_NEWS["IAM"] * 10  # More news
        
        mock_db_session.execute.return_value.fetchone.side_effect = [
            MagicMock(_mapping=company_data),
            MagicMock(fetchall=lambda: [MagicMock(_mapping=p) for p in prices_data]),
            MagicMock(fetchall=lambda: [MagicMock(_mapping=r) for r in reports_data]),
            MagicMock(fetchall=lambda: [MagicMock(_mapping=n) for n in news_data])
        ]
        
        response = client.get("/api/companies/IAM/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert data["data_quality"] == "Complete"
    
    def test_partial_data_quality(self, mock_db_session):
        """Test data quality assessment for partial data"""
        # Mock incomplete data
        company_data = TEST_COMPANIES["IAM"]
        prices_data = []  # No price data
        reports_data = []  # No reports
        news_data = []  # No news
        
        mock_db_session.execute.return_value.fetchone.side_effect = [
            MagicMock(_mapping=company_data),
            MagicMock(fetchall=lambda: [MagicMock(_mapping=p) for p in prices_data]),
            MagicMock(fetchall=lambda: [MagicMock(_mapping=r) for r in reports_data]),
            MagicMock(fetchall=lambda: [MagicMock(_mapping=n) for n in news_data])
        ]
        
        response = client.get("/api/companies/IAM/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert data["data_quality"] == "Partial" 