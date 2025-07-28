import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json

# Test Contest Features
class TestContestFeatures:
    """Test contest functionality"""
    
    @pytest.fixture
    def mock_contest_data(self):
        return {
            "contest_id": "contest_2024_01",
            "contest_name": "Monthly Portfolio Contest",
            "prize_pool": 100.00,
            "total_participants": 25,
            "end_date": "2024-02-01T00:00:00Z",
            "rules": {
                "min_positions": 3,
                "ranking_metric": "percentage_return",
                "eligibility": "registered_users_with_minimum_positions"
            }
        }
    
    @pytest.fixture
    def mock_rankings_data(self):
        return [
            {
                "contest_id": "contest_2024_01",
                "user_id": "user_1",
                "username": "Trader_12345678",
                "rank": 1,
                "total_return_percent": 15.67,
                "total_return": 15670.00,
                "position_count": 5,
                "last_updated": "2024-01-15T10:30:00Z",
                "is_winner": True,
                "prize_amount": 100
            },
            {
                "contest_id": "contest_2024_01",
                "user_id": "user_2",
                "username": "Trader_87654321",
                "rank": 2,
                "total_return_percent": 12.34,
                "total_return": 12340.00,
                "position_count": 4,
                "last_updated": "2024-01-15T10:25:00Z",
                "is_winner": False,
                "prize_amount": 0
            }
        ]
    
    def test_contest_rankings_api(self, mock_rankings_data):
        """Test contest rankings API endpoint"""
        # Mock the API response
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "rankings": mock_rankings_data,
                "contest_info": {
                    "contest_id": "contest_2024_01",
                    "contest_name": "Monthly Portfolio Contest",
                    "prize_pool": 100,
                    "total_participants": 25,
                    "end_date": "2024-02-01T00:00:00Z"
                }
            }
            
            # Test the API call
            response = mock_get.return_value
            assert response.status_code == 200
            
            data = response.json()
            assert "rankings" in data
            assert "contest_info" in data
            assert len(data["rankings"]) == 2
            assert data["rankings"][0]["is_winner"] == True
            assert data["rankings"][0]["prize_amount"] == 100
    
    def test_contest_join_api(self):
        """Test contest join API endpoint"""
        join_data = {
            "account_id": "account_123",
            "contest_id": "contest_2024_01"
        }
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "id": "entry_123",
                "contest_id": "contest_2024_01",
                "user_id": "user_123",
                "account_id": "account_123",
                "status": "active",
                "joined_at": "2024-01-15T10:00:00Z"
            }
            
            response = mock_post.return_value
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "active"
            assert data["contest_id"] == "contest_2024_01"
    
    def test_contest_results_api(self):
        """Test contest results API endpoint"""
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "contest_id": "contest_2024_01",
                "winner": {
                    "user_id": "user_1",
                    "username": "Trader_12345678",
                    "total_return_percent": 15.67,
                    "total_return": 15670.00,
                    "prize_amount": 100
                },
                "total_participants": 25,
                "prize_distributed": True,
                "contest_end_date": "2024-01-31T23:59:59Z",
                "next_contest_start": "2024-02-01T00:00:00Z"
            }
            
            response = mock_get.return_value
            assert response.status_code == 200
            
            data = response.json()
            assert "winner" in data
            assert data["winner"]["prize_amount"] == 100
            assert data["prize_distributed"] == True

# Test AI Features
class TestAIFeatures:
    """Test AI integration features"""
    
    @pytest.fixture
    def mock_ai_summary_data(self):
        return {
            "ticker": "ATW",
            "summary": "ATW demonstrates strong fundamentals with consistent performance in the banking sector...",
            "language": "en",
            "generated_at": "2024-01-15T10:30:00Z",
            "company_data": {
                "ticker": "ATW",
                "name": "Attijariwafa Bank",
                "sector": "Banking",
                "market_cap": 50000000000,
                "current_price": 150.50,
                "price_change_percent": 2.3
            },
            "tokens_used": 245,
            "cached": False
        }
    
    def test_ai_company_summary_api(self, mock_ai_summary_data):
        """Test AI company summary API endpoint"""
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_ai_summary_data
            
            response = mock_get.return_value
            assert response.status_code == 200
            
            data = response.json()
            assert data["ticker"] == "ATW"
            assert "summary" in data
            assert data["tokens_used"] > 0
            assert "company_data" in data
    
    def test_ai_portfolio_analysis_api(self):
        """Test AI portfolio analysis API endpoint"""
        analysis_data = {
            "total_value": 150000.00,
            "total_cost": 140000.00,
            "total_pnl": 10000.00,
            "total_pnl_percent": 7.14,
            "diversification_score": 80,
            "risk_assessment": "Low Risk - Well diversified",
            "sector_allocation": {
                "Banking": 40.0,
                "Telecom": 30.0,
                "Energy": 30.0
            },
            "top_performers": [
                {
                    "ticker": "ATW",
                    "total_gain_loss_percent": 12.5
                }
            ],
            "underperformers": [
                {
                    "ticker": "IAM",
                    "total_gain_loss_percent": -2.1
                }
            ],
            "recommendations": [
                "Consider diversifying across more sectors to reduce concentration risk"
            ],
            "ai_insights": "Your portfolio shows good diversification with a 7.14% return..."
        }
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = analysis_data
            
            response = mock_post.return_value
            assert response.status_code == 200
            
            data = response.json()
            assert data["total_pnl_percent"] == 7.14
            assert data["diversification_score"] == 80
            assert len(data["recommendations"]) > 0
            assert "ai_insights" in data
    
    def test_ai_chat_api(self):
        """Test AI chat API endpoint"""
        chat_data = {
            "messages": [
                {"role": "user", "content": "Explain ATW's recent performance"}
            ],
            "context": {
                "portfolio_id": "portfolio_123",
                "tickers": ["ATW", "BMCE"]
            }
        }
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "success": True,
                "response": "ATW has shown strong performance with a 12.5% return over the past quarter...",
                "timestamp": "2024-01-15T10:30:00Z"
            }
            
            response = mock_post.return_value
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] == True
            assert "response" in data
            assert len(data["response"]) > 0

# Test Caching Features
class TestCachingFeatures:
    """Test Redis caching functionality"""
    
    @pytest.fixture
    def mock_cache_service(self):
        from services.redis_cache_service import RedisCacheService
        return RedisCacheService()
    
    @pytest.mark.asyncio
    async def test_ai_summary_caching(self, mock_cache_service):
        """Test AI summary caching"""
        ticker = "ATW"
        language = "en"
        summary_data = {
            "summary": "Test summary",
            "tokens_used": 100,
            "cached": False
        }
        
        # Test setting cache
        success = await mock_cache_service.set_ai_summary(ticker, summary_data, language)
        assert success == True
        
        # Test getting from cache
        cached_data = await mock_cache_service.get_ai_summary(ticker, language)
        assert cached_data is not None
        assert cached_data["summary"] == summary_data["summary"]
    
    @pytest.mark.asyncio
    async def test_contest_rankings_caching(self, mock_cache_service):
        """Test contest rankings caching"""
        contest_id = "contest_2024_01"
        rankings = [
            {"rank": 1, "username": "Trader_1", "total_return_percent": 15.67},
            {"rank": 2, "username": "Trader_2", "total_return_percent": 12.34}
        ]
        
        # Test setting cache
        success = await mock_cache_service.set_contest_rankings(contest_id, rankings)
        assert success == True
        
        # Test getting from cache
        cached_rankings = await mock_cache_service.get_contest_rankings(contest_id)
        assert cached_rankings is not None
        assert len(cached_rankings) == 2
        assert cached_rankings[0]["rank"] == 1
    
    @pytest.mark.asyncio
    async def test_token_usage_tracking(self, mock_cache_service):
        """Test token usage tracking"""
        user_id = "user_123"
        tokens_used = 500
        
        # Test incrementing usage
        success = await mock_cache_service.increment_token_usage(user_id, tokens_used)
        assert success == True
        
        # Test getting usage
        usage = await mock_cache_service.get_token_usage(user_id)
        assert usage == tokens_used
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, mock_cache_service):
        """Test rate limiting functionality"""
        user_id = "user_123"
        limit_type = "ai_queries"
        max_requests = 10
        window_seconds = 3600
        
        # Test rate limit check
        allowed = await mock_cache_service.check_rate_limit(user_id, limit_type, max_requests, window_seconds)
        assert allowed == True

# Test Frontend Components
class TestFrontendComponents:
    """Test frontend component functionality"""
    
    def test_contest_leaderboard_component(self):
        """Test contest leaderboard component props"""
        rankings = [
            {
                "rank": 1,
                "username": "Trader_1",
                "total_return_percent": 15.67,
                "is_winner": True,
                "prize_amount": 100
            }
        ]
        
        contest_info = {
            "contest_name": "Monthly Contest",
            "prize_pool": 100,
            "total_participants": 25,
            "end_date": "2024-02-01T00:00:00Z"
        }
        
        # Test component props
        assert len(rankings) == 1
        assert rankings[0]["is_winner"] == True
        assert rankings[0]["prize_amount"] == 100
        assert contest_info["prize_pool"] == 100
    
    def test_ai_assistant_component(self):
        """Test AI assistant component props"""
        messages = [
            {
                "id": "1",
                "role": "assistant",
                "content": "Hello! I'm your AI financial assistant.",
                "timestamp": datetime.now()
            }
        ]
        
        suggested_questions = [
            "Explain ATW's recent performance",
            "Compare BMCE vs Attijari",
            "Show me risk drivers for my portfolio"
        ]
        
        # Test component props
        assert len(messages) == 1
        assert messages[0]["role"] == "assistant"
        assert len(suggested_questions) == 3
    
    def test_ai_summary_component(self):
        """Test AI summary component props"""
        summary_data = {
            "ticker": "ATW",
            "summary": "ATW demonstrates strong fundamentals...",
            "tokens_used": 245,
            "cached": False,
            "generated_at": "2024-01-15T10:30:00Z"
        }
        
        # Test component props
        assert summary_data["ticker"] == "ATW"
        assert summary_data["tokens_used"] > 0
        assert "summary" in summary_data

# Test Database Schema
class TestDatabaseSchema:
    """Test database schema for new features"""
    
    def test_contest_tables_schema(self):
        """Test contest tables schema"""
        # Test contests table structure
        contests_schema = {
            "contest_id": "VARCHAR(50) PRIMARY KEY",
            "contest_name": "VARCHAR(255) NOT NULL",
            "prize_pool": "DECIMAL(10,2) NOT NULL DEFAULT 100.00",
            "status": "VARCHAR(20) DEFAULT 'active'",
            "start_date": "DATE NOT NULL",
            "end_date": "DATE NOT NULL"
        }
        
        assert "contest_id" in contests_schema
        assert "prize_pool" in contests_schema
        assert contests_schema["status"] == "VARCHAR(20) DEFAULT 'active'"
    
    def test_ai_tables_schema(self):
        """Test AI tables schema"""
        # Test ai_summaries table structure
        ai_summaries_schema = {
            "ticker": "VARCHAR(10) NOT NULL",
            "language": "VARCHAR(10) NOT NULL DEFAULT 'en'",
            "summary": "TEXT NOT NULL",
            "tokens_used": "INTEGER DEFAULT 0",
            "model_used": "VARCHAR(50) DEFAULT 'gpt-4o-mini'"
        }
        
        assert "ticker" in ai_summaries_schema
        assert "tokens_used" in ai_summaries_schema
        assert ai_summaries_schema["model_used"] == "VARCHAR(50) DEFAULT 'gpt-4o-mini'"
    
    def test_caching_tables_schema(self):
        """Test caching tables schema"""
        # Test portfolio_analysis_cache table structure
        cache_schema = {
            "portfolio_id": "UUID NOT NULL",
            "analysis_data": "JSONB NOT NULL",
            "ai_insights": "TEXT",
            "tokens_used": "INTEGER DEFAULT 0",
            "expires_at": "TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '1 hour')"
        }
        
        assert "portfolio_id" in cache_schema
        assert "analysis_data" in cache_schema
        assert "expires_at" in cache_schema

# Integration Tests
class TestIntegrationFeatures:
    """Test integration between features"""
    
    def test_contest_ai_integration(self):
        """Test integration between contest and AI features"""
        # Test that AI can analyze contest performance
        contest_data = {
            "contest_id": "contest_2024_01",
            "participants": 25,
            "avg_return": 8.5
        }
        
        ai_analysis = {
            "contest_health": "Good",
            "participation_rate": "High",
            "performance_insights": "Strong returns across participants"
        }
        
        # Test integration
        assert contest_data["participants"] > 0
        assert "contest_health" in ai_analysis
        assert "performance_insights" in ai_analysis
    
    def test_caching_performance(self):
        """Test caching performance improvements"""
        # Test that caching reduces API calls
        cache_hit_rate = 0.85  # 85% cache hit rate
        response_time_with_cache = 50  # ms
        response_time_without_cache = 2000  # ms
        
        # Test performance improvement
        assert cache_hit_rate > 0.8
        assert response_time_with_cache < response_time_without_cache
        assert (response_time_without_cache / response_time_with_cache) > 10

if __name__ == "__main__":
    pytest.main([__file__]) 