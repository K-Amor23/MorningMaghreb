import redis
import json
import logging
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class RedisCacheService:
    """Redis caching service for AI responses and contest data"""
    
    def __init__(self):
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.client = redis.from_url(self.redis_url, decode_responses=True)
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, expire_seconds: int = 3600) -> bool:
        """Set value in cache with expiration"""
        try:
            serialized_value = json.dumps(value)
            return self.client.setex(key, expire_seconds, serialized_value)
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Redis exists error for key {key}: {e}")
            return False
    
    # AI Summary Caching
    async def get_ai_summary(self, ticker: str, language: str = 'en') -> Optional[Dict]:
        """Get cached AI summary"""
        key = f"ai_summary:{ticker}:{language}"
        return await self.get(key)
    
    async def set_ai_summary(self, ticker: str, summary_data: Dict, language: str = 'en') -> bool:
        """Cache AI summary for 24 hours"""
        key = f"ai_summary:{ticker}:{language}"
        return await self.set(key, summary_data, 24 * 60 * 60)  # 24 hours
    
    # Contest Rankings Caching
    async def get_contest_rankings(self, contest_id: str, limit: int = 10) -> Optional[list]:
        """Get cached contest rankings"""
        key = f"contest_rankings:{contest_id}:{limit}"
        return await self.get(key)
    
    async def set_contest_rankings(self, contest_id: str, rankings: list, limit: int = 10) -> bool:
        """Cache contest rankings for 5 minutes"""
        key = f"contest_rankings:{contest_id}:{limit}"
        return await self.set(key, rankings, 5 * 60)  # 5 minutes
    
    async def invalidate_contest_rankings(self, contest_id: str) -> bool:
        """Invalidate all contest ranking caches for a contest"""
        try:
            pattern = f"contest_rankings:{contest_id}:*"
            keys = self.client.keys(pattern)
            if keys:
                return bool(self.client.delete(*keys))
            return True
        except Exception as e:
            logger.error(f"Redis invalidate contest rankings error: {e}")
            return False
    
    # Portfolio Analysis Caching
    async def get_portfolio_analysis(self, portfolio_id: str) -> Optional[Dict]:
        """Get cached portfolio analysis"""
        key = f"portfolio_analysis:{portfolio_id}"
        return await self.get(key)
    
    async def set_portfolio_analysis(self, portfolio_id: str, analysis_data: Dict) -> bool:
        """Cache portfolio analysis for 1 hour"""
        key = f"portfolio_analysis:{portfolio_id}"
        return await self.set(key, analysis_data, 60 * 60)  # 1 hour
    
    # AI Chat Response Caching
    async def get_chat_response(self, query_hash: str) -> Optional[str]:
        """Get cached chat response"""
        key = f"chat_response:{query_hash}"
        return await self.get(key)
    
    async def set_chat_response(self, query_hash: str, response: str) -> bool:
        """Cache chat response for 1 hour"""
        key = f"chat_response:{query_hash}"
        return await self.set(key, response, 60 * 60)  # 1 hour
    
    # Token Usage Tracking
    async def increment_token_usage(self, user_id: str, tokens_used: int) -> bool:
        """Track token usage for cost control"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            key = f"token_usage:{user_id}:{today}"
            
            # Increment daily token usage
            self.client.incrby(key, tokens_used)
            # Set expiration to 30 days
            self.client.expire(key, 30 * 24 * 60 * 60)
            
            return True
        except Exception as e:
            logger.error(f"Redis token usage tracking error: {e}")
            return False
    
    async def get_token_usage(self, user_id: str, date: str = None) -> int:
        """Get user's token usage for a specific date"""
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            key = f"token_usage:{user_id}:{date}"
            usage = self.client.get(key)
            return int(usage) if usage else 0
        except Exception as e:
            logger.error(f"Redis get token usage error: {e}")
            return 0
    
    # Cost Tracking
    async def increment_cost(self, user_id: str, cost_usd: float) -> bool:
        """Track cost for billing"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            key = f"cost_tracking:{user_id}:{today}"
            
            # Increment daily cost
            self.client.incrbyfloat(key, cost_usd)
            # Set expiration to 30 days
            self.client.expire(key, 30 * 24 * 60 * 60)
            
            return True
        except Exception as e:
            logger.error(f"Redis cost tracking error: {e}")
            return False
    
    async def get_daily_cost(self, user_id: str, date: str = None) -> float:
        """Get user's cost for a specific date"""
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            key = f"cost_tracking:{user_id}:{date}"
            cost = self.client.get(key)
            return float(cost) if cost else 0.0
        except Exception as e:
            logger.error(f"Redis get daily cost error: {e}")
            return 0.0
    
    # Rate Limiting
    async def check_rate_limit(self, user_id: str, limit_type: str, max_requests: int, window_seconds: int) -> bool:
        """Check if user has exceeded rate limit"""
        try:
            key = f"rate_limit:{user_id}:{limit_type}"
            current_requests = self.client.get(key)
            
            if current_requests is None:
                # First request in window
                self.client.setex(key, window_seconds, 1)
                return True
            elif int(current_requests) < max_requests:
                # Increment request count
                self.client.incr(key)
                return True
            else:
                # Rate limit exceeded
                return False
        except Exception as e:
            logger.error(f"Redis rate limit check error: {e}")
            return True  # Allow request if Redis fails
    
    # Cache Statistics
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            info = self.client.info()
            return {
                'total_connections_received': info.get('total_connections_received', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'connected_clients': info.get('connected_clients', 0)
            }
        except Exception as e:
            logger.error(f"Redis cache stats error: {e}")
            return {}
    
    # Health Check
    async def health_check(self) -> bool:
        """Check if Redis is healthy"""
        try:
            self.client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False

# Global cache service instance
cache_service = RedisCacheService() 