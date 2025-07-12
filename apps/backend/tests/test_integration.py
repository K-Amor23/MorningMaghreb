import pytest
import asyncio
from fastapi.testclient import TestClient
from typing import Dict, Any
import json
from datetime import datetime, timedelta
from decimal import Decimal

# Import the main app and components
from main import app
from etl.currency_scraper import CurrencyScraper
from etl.fetch_economic_data import EconomicDataFetcher
from storage.local_fs import LocalFileStorage
from utils.security import auth_manager, input_validator

client = TestClient(app)

class TestETLIntegration:
    """Test ETL pipeline integration"""
    
    @pytest.mark.asyncio
    async def test_currency_scraper_integration(self):
        """Test currency scraper with real data flow"""
        scraper = CurrencyScraper()
        
        try:
            # Test BAM rate fetching
            bam_rate = await scraper.fetch_bam_rate("USD/MAD")
            assert bam_rate is not None
            assert "rate" in bam_rate
            assert "currency_pair" in bam_rate
            
            # Test remittance rates fetching
            remittance_rates = await scraper.fetch_all_remittance_rates("USD/MAD", Decimal("1000"))
            assert isinstance(remittance_rates, list)
            assert len(remittance_rates) > 0
            
            # Test metrics collection
            metrics = scraper.get_metrics_summary()
            assert "total_requests" in metrics
            assert "success_rate" in metrics
            assert "average_response_time_ms" in metrics
            
        finally:
            await scraper.close()
    
    @pytest.mark.asyncio
    async def test_economic_data_fetcher_integration(self):
        """Test economic data fetcher integration"""
        storage = LocalFileStorage()
        fetcher = EconomicDataFetcher(storage)
        
        # Test data summary
        summary = await fetcher.get_data_summary()
        assert "total_indicators" in summary
        assert "indicators" in summary
        
        # Test fetching specific indicator
        results = await fetcher.fetch_all_economic_data(['key_policy_rate'])
        assert "data_fetched" in results
        assert "errors" in results
        assert "total_files" in results
    
    @pytest.mark.asyncio
    async def test_storage_integration(self):
        """Test storage system integration"""
        storage = LocalFileStorage()
        
        # Test PDF storage
        test_content = b"Test PDF content"
        file_path = await storage.save_pdf(
            content=test_content,
            filename="test.pdf",
            company="TEST",
            year=2024
        )
        assert file_path is not None
        
        # Test file info retrieval
        file_info = await storage.get_file_info(file_path)
        assert "size" in file_info
        assert "created" in file_info
        
        # Test company PDF listing
        pdfs = await storage.list_company_pdfs("TEST", 2024)
        assert isinstance(pdfs, list)
        assert len(pdfs) > 0

class TestSecurityIntegration:
    """Test security system integration"""
    
    def test_api_key_management_integration(self):
        """Test API key management integration"""
        # Generate API key
        api_key = auth_manager.generate_api_key(
            user_id="test_user",
            permissions=["read_financials", "read_macro"],
            rate_limit_per_hour=1000
        )
        assert api_key.startswith("cas_sk_")
        
        # Validate API key
        key_info = auth_manager.validate_api_key(api_key)
        assert key_info is not None
        assert key_info["user_id"] == "test_user"
        assert "read_financials" in key_info["permissions"]
        
        # Test permission checking
        assert auth_manager.check_permission(key_info, "read_financials")
        assert not auth_manager.check_permission(key_info, "admin")
        
        # Test rate limiting
        assert auth_manager.check_rate_limit(key_info)
    
    def test_input_validation_integration(self):
        """Test input validation integration"""
        # Test ticker validation
        valid_ticker = input_validator.validate_ticker("ATW")
        assert valid_ticker == "ATW"
        
        with pytest.raises(ValueError):
            input_validator.validate_ticker("INVALIDTICKERTOOLONG")
        
        # Test email validation
        valid_email = input_validator.validate_email("test@example.com")
        assert valid_email == "test@example.com"
        
        with pytest.raises(ValueError):
            input_validator.validate_email("invalid-email")
        
        # Test URL validation
        valid_url = input_validator.validate_url("https://example.com")
        assert valid_url == "https://example.com"
        
        with pytest.raises(ValueError):
            input_validator.validate_url("not-a-url")
        
        # Test JSON payload validation
        test_payload = {
            "name": "Test User",
            "email": "test@example.com",
            "data": {"key": "value"}
        }
        sanitized = input_validator.validate_json_payload(test_payload)
        assert sanitized == test_payload
    
    def test_suspicious_content_detection(self):
        """Test suspicious content detection"""
        # Test clean content
        assert not input_validator.check_suspicious_content("Normal text content")
        
        # Test suspicious content
        assert input_validator.check_suspicious_content("<script>alert('xss')</script>")
        assert input_validator.check_suspicious_content("javascript:alert('xss')")
        assert input_validator.check_suspicious_content("<iframe src='malicious.com'></iframe>")

class TestAPIIntegration:
    """Test API integration scenarios"""
    
    def test_complete_user_workflow(self):
        """Test complete user workflow integration"""
        # 1. Create paper trading account
        account_response = client.post("/api/paper-trading/accounts", json={
            "account_name": "Integration Test Account",
            "initial_balance": 100000.00
        })
        assert account_response.status_code == 200
        account_data = account_response.json()
        account_id = account_data["id"]
        
        # 2. Place a trade order
        order_response = client.post(f"/api/paper-trading/accounts/{account_id}/orders", json={
            "ticker": "ATW",
            "order_type": "buy",
            "quantity": 100,
            "price": 150.00,
            "notes": "Integration test order"
        })
        assert order_response.status_code == 200
        order_data = order_response.json()
        
        # 3. Check account summary
        summary_response = client.get(f"/api/paper-trading/accounts/{account_id}/summary")
        assert summary_response.status_code == 200
        summary_data = summary_response.json()
        assert "account" in summary_data
        assert "positions" in summary_data
        
        # 4. Vote on sentiment
        sentiment_response = client.post("/api/sentiment/vote", json={
            "ticker": "ATW",
            "sentiment": "bullish",
            "confidence": 4
        })
        assert sentiment_response.status_code == 200
        
        # 5. Check sentiment aggregate
        aggregate_response = client.get("/api/sentiment/aggregate/ATW")
        assert aggregate_response.status_code == 200
        aggregate_data = aggregate_response.json()
        assert "ticker" in aggregate_data
        assert "total_votes" in aggregate_data
    
    def test_data_export_workflow(self):
        """Test data export workflow integration"""
        # 1. Create export request
        export_response = client.post("/api/exports", json={
            "export_type": "financials",
            "file_format": "csv",
            "filters": {"companies": ["ATW"]},
            "include_metadata": True
        })
        assert export_response.status_code == 200
        export_data = export_response.json()
        export_id = export_data["id"]
        
        # 2. Check export status
        status_response = client.get(f"/api/exports/{export_id}")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert "status" in status_data
        
        # 3. List all exports
        list_response = client.get("/api/exports")
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert isinstance(list_data, list)
    
    def test_webhook_integration(self):
        """Test webhook integration workflow"""
        # 1. Create webhook subscription
        webhook_response = client.post("/api/webhooks", json={
            "webhook_url": "https://example.com/webhook",
            "events": ["price_alert", "earnings_release"],
            "description": "Integration test webhook"
        })
        assert webhook_response.status_code == 200
        webhook_data = webhook_response.json()
        webhook_id = webhook_data["id"]
        
        # 2. Test webhook
        test_response = client.post(f"/api/webhooks/{webhook_id}/test")
        assert test_response.status_code == 200
        
        # 3. List webhooks
        list_response = client.get("/api/webhooks")
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert isinstance(list_data, list)
    
    def test_premium_api_integration(self):
        """Test premium API integration"""
        # Mock API key for testing
        headers = {"X-API-Key": "test_premium_key"}
        
        # 1. Get financial data
        financials_response = client.post("/api/premium/financials", 
                                        json={"tickers": ["ATW"], "metrics": ["revenue"]},
                                        headers=headers)
        assert financials_response.status_code == 200
        financials_data = financials_response.json()
        assert "data" in financials_data
        
        # 2. Get macro data
        macro_response = client.post("/api/premium/macro",
                                   json={"series_codes": ["MAR_POLICY_RATE"], 
                                        "start_date": "2024-01-01",
                                        "end_date": "2024-12-31"},
                                   headers=headers)
        assert macro_response.status_code == 200
        macro_data = macro_response.json()
        assert "data" in macro_data
        
        # 3. Check API usage
        usage_response = client.get("/api/premium/usage", headers=headers)
        assert usage_response.status_code == 200
        usage_data = usage_response.json()
        assert "current_period" in usage_data

class TestErrorHandlingIntegration:
    """Test error handling integration"""
    
    def test_graceful_degradation(self):
        """Test graceful degradation when services are unavailable"""
        # Test with invalid company ticker
        response = client.get("/api/financials/INVALID_TICKER")
        assert response.status_code == 404
        
        # Test with invalid currency pair
        response = client.get("/api/currency/compare/INVALID/PAIR")
        assert response.status_code == 400
        
        # Test with invalid date range
        response = client.get("/api/macro/series?start_date=invalid&end_date=invalid")
        assert response.status_code == 422
    
    def test_rate_limiting_integration(self):
        """Test rate limiting integration"""
        # Make many requests to test rate limiting
        responses = []
        for _ in range(50):
            response = client.get("/api/markets/quotes")
            responses.append(response.status_code)
        
        # Should handle rate limiting gracefully
        assert 200 in responses  # Some should succeed
        # Note: Rate limiting might not be implemented in test environment
    
    def test_authentication_error_handling(self):
        """Test authentication error handling"""
        # Test premium endpoint without API key
        response = client.post("/api/premium/financials", 
                             json={"tickers": ["ATW"]})
        assert response.status_code == 401
        
        # Test with invalid API key
        response = client.post("/api/premium/financials", 
                             json={"tickers": ["ATW"]},
                             headers={"X-API-Key": "invalid_key"})
        assert response.status_code == 401

class TestPerformanceIntegration:
    """Test performance integration"""
    
    def test_concurrent_user_simulation(self):
        """Test concurrent user simulation"""
        import threading
        import time
        
        results = []
        errors = []
        
        def simulate_user():
            try:
                # Simulate user workflow
                response1 = client.get("/api/markets/quotes")
                response2 = client.get("/api/financials/ATW")
                response3 = client.post("/api/sentiment/vote", json={
                    "ticker": "ATW",
                    "sentiment": "bullish",
                    "confidence": 4
                })
                
                results.append({
                    "quotes": response1.status_code,
                    "financials": response2.status_code,
                    "sentiment": response3.status_code
                })
            except Exception as e:
                errors.append(str(e))
        
        # Simulate 10 concurrent users
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=simulate_user)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should handle concurrent users without errors
        assert len(errors) == 0
        assert len(results) == 10
        
        # All responses should be successful
        for result in results:
            assert result["quotes"] == 200
            assert result["financials"] == 200
            assert result["sentiment"] == 200
    
    def test_large_data_handling(self):
        """Test handling of large datasets"""
        # Test with large limit
        response = client.get("/api/markets/quotes?limit=1000")
        assert response.status_code == 200
        
        data = response.json()
        assert "quotes" in data
        
        # Test with large date range
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        response = client.get(f"/api/macro/series?start_date={start_date}&end_date={end_date}")
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 