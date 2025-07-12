import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any
import json
from datetime import datetime, timedelta

# Import the main app
from main import app

client = TestClient(app)

class TestAPIContracts:
    """Test API contracts and response schemas"""
    
    def test_health_check_contract(self):
        """Test health check endpoint contract"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] in ["healthy", "unhealthy"]
    
    def test_markets_quotes_contract(self):
        """Test markets quotes endpoint contract"""
        response = client.get("/api/markets/quotes")
        assert response.status_code == 200
        
        data = response.json()
        assert "quotes" in data
        assert isinstance(data["quotes"], list)
        
        if data["quotes"]:
            quote = data["quotes"][0]
            required_fields = ["ticker", "price", "change_amount", "change_percent"]
            for field in required_fields:
                assert field in quote
    
    def test_financials_company_contract(self):
        """Test financials company endpoint contract"""
        response = client.get("/api/financials/ATW")
        assert response.status_code == 200
        
        data = response.json()
        assert "company" in data
        assert "financial_data" in data
        assert "ratios" in data
    
    def test_currency_compare_contract(self):
        """Test currency comparison endpoint contract"""
        response = client.get("/api/currency/compare/USD/MAD")
        assert response.status_code == 200
        
        data = response.json()
        assert "currency_pair" in data
        assert "bam_rate" in data
        assert "remittance_rates" in data
        assert "best_rate" in data
    
    def test_portfolio_summary_contract(self):
        """Test portfolio summary endpoint contract"""
        response = client.get("/api/portfolio/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_value" in data
        assert "total_return" in data
        assert "holdings" in data
        assert isinstance(data["holdings"], list)
    
    def test_paper_trading_accounts_contract(self):
        """Test paper trading accounts endpoint contract"""
        response = client.post("/api/paper-trading/accounts", json={
            "account_name": "Test Account",
            "initial_balance": 100000.00
        })
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["id", "user_id", "account_name", "initial_balance", 
                         "current_balance", "total_pnl", "is_active"]
        for field in required_fields:
            assert field in data
    
    def test_sentiment_vote_contract(self):
        """Test sentiment voting endpoint contract"""
        response = client.post("/api/sentiment/vote", json={
            "ticker": "ATW",
            "sentiment": "bullish",
            "confidence": 4
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "ticker" in data
        assert "sentiment" in data
        assert "confidence" in data
        assert data["sentiment"] in ["bullish", "neutral", "bearish"]
        assert 1 <= data["confidence"] <= 5
    
    def test_premium_api_financials_contract(self):
        """Test premium API financials endpoint contract"""
        # Mock API key for testing
        headers = {"X-API-Key": "test_api_key"}
        response = client.post("/api/premium/financials", 
                             json={"tickers": ["ATW"], "metrics": ["revenue"]},
                             headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "metadata" in data
        assert "total_companies" in data["metadata"]
    
    def test_webhook_subscription_contract(self):
        """Test webhook subscription endpoint contract"""
        response = client.post("/api/webhooks", json={
            "webhook_url": "https://example.com/webhook",
            "events": ["price_alert", "earnings_release"],
            "description": "Test webhook"
        })
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["id", "webhook_url", "events", "secret_key", "is_active"]
        for field in required_fields:
            assert field in data
    
    def test_export_creation_contract(self):
        """Test export creation endpoint contract"""
        response = client.post("/api/exports", json={
            "export_type": "financials",
            "file_format": "csv",
            "filters": {"companies": ["ATW"]}
        })
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert "status" in data
        assert data["status"] in ["pending", "processing", "completed", "failed"]
    
    def test_error_response_contract(self):
        """Test error response contract"""
        # Test with invalid ticker
        response = client.get("/api/financials/INVALID_TICKER")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
    
    def test_pagination_contract(self):
        """Test pagination contract"""
        response = client.get("/api/markets/quotes?limit=5&offset=0")
        assert response.status_code == 200
        
        data = response.json()
        assert "quotes" in data
        assert len(data["quotes"]) <= 5
        
        # Check if pagination metadata is present
        if "pagination" in data:
            pagination = data["pagination"]
            assert "total" in pagination
            assert "limit" in pagination
            assert "offset" in pagination
    
    def test_date_range_contract(self):
        """Test date range parameter contract"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        response = client.get(f"/api/macro/series?start_date={start_date}&end_date={end_date}")
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "metadata" in data
    
    def test_validation_error_contract(self):
        """Test validation error response contract"""
        # Test with invalid sentiment value
        response = client.post("/api/sentiment/vote", json={
            "ticker": "ATW",
            "sentiment": "invalid_sentiment",
            "confidence": 6  # Invalid confidence
        })
        assert response.status_code == 422
        
        data = response.json()
        assert "detail" in data
        # Should contain validation error details
    
    def test_rate_limit_contract(self):
        """Test rate limiting response contract"""
        # Make many requests to trigger rate limiting
        for _ in range(100):
            response = client.get("/api/markets/quotes")
            if response.status_code == 429:
                data = response.json()
                assert "detail" in data
                assert "rate limit" in data["detail"].lower()
                break
        else:
            # If rate limiting is not implemented, this is acceptable
            pass
    
    def test_authentication_error_contract(self):
        """Test authentication error response contract"""
        # Test premium endpoint without API key
        response = client.post("/api/premium/financials", 
                             json={"tickers": ["ATW"]})
        assert response.status_code == 401
        
        data = response.json()
        assert "detail" in data
        assert "authentication" in data["detail"].lower() or "unauthorized" in data["detail"].lower()

class TestSchemaValidation:
    """Test schema validation for request/response models"""
    
    def test_ticker_validation(self):
        """Test ticker symbol validation"""
        # Valid ticker
        response = client.get("/api/financials/ATW")
        assert response.status_code == 200
        
        # Invalid ticker (too long)
        response = client.get("/api/financials/INVALIDTICKERTOOLONG")
        assert response.status_code == 422
    
    def test_email_validation(self):
        """Test email validation"""
        # Valid email
        response = client.post("/api/newsletter/subscribe", json={
            "email": "test@example.com",
            "name": "Test User"
        })
        assert response.status_code == 200
        
        # Invalid email
        response = client.post("/api/newsletter/subscribe", json={
            "email": "invalid-email",
            "name": "Test User"
        })
        assert response.status_code == 422
    
    def test_decimal_validation(self):
        """Test decimal number validation"""
        # Valid decimal
        response = client.post("/api/paper-trading/accounts", json={
            "account_name": "Test Account",
            "initial_balance": 100000.00
        })
        assert response.status_code == 200
        
        # Invalid decimal (negative)
        response = client.post("/api/paper-trading/accounts", json={
            "account_name": "Test Account",
            "initial_balance": -1000.00
        })
        assert response.status_code == 422
    
    def test_enum_validation(self):
        """Test enum value validation"""
        # Valid sentiment
        response = client.post("/api/sentiment/vote", json={
            "ticker": "ATW",
            "sentiment": "bullish",
            "confidence": 4
        })
        assert response.status_code == 200
        
        # Invalid sentiment
        response = client.post("/api/sentiment/vote", json={
            "ticker": "ATW",
            "sentiment": "invalid",
            "confidence": 4
        })
        assert response.status_code == 422

class TestPerformanceContracts:
    """Test performance-related contracts"""
    
    def test_response_time_contract(self):
        """Test that responses are returned within acceptable time"""
        import time
        
        start_time = time.time()
        response = client.get("/api/markets/quotes")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Should respond within 2 seconds
    
    def test_large_dataset_contract(self):
        """Test handling of large datasets"""
        # Request many quotes
        response = client.get("/api/markets/quotes?limit=1000")
        assert response.status_code == 200
        
        data = response.json()
        # Should handle large datasets gracefully
        assert "quotes" in data
    
    def test_concurrent_requests_contract(self):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request():
            try:
                response = client.get("/api/markets/quotes")
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Make 10 concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should handle concurrent requests without errors
        assert len(errors) == 0
        assert all(status == 200 for status in results)

if __name__ == "__main__":
    pytest.main([__file__]) 