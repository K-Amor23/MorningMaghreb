import redis.asyncio as redis
import json
import logging
from typing import Optional, Any, Dict, List
from datetime import timedelta
import os

logger = logging.getLogger(__name__)

class RedisClient:
    """Redis client for caching API responses"""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.client: Optional[redis.Redis] = None
        self.default_ttl = 3600  # 1 hour default
        
    async def connect(self):
        """Connect to Redis"""
        try:
            self.client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            await self.client.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Redis")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.client:
            return None
        
        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        if not self.client:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value, default=str)
            await self.client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.client:
            return False
        
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.client:
            return False
        
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking cache existence: {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration for key"""
        if not self.client:
            return False
        
        try:
            return await self.client.expire(key, ttl)
        except Exception as e:
            logger.error(f"Error setting expiration: {e}")
            return False
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache"""
        if not self.client:
            return {}
        
        try:
            values = await self.client.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value:
                    result[key] = json.loads(value)
            return result
        except Exception as e:
            logger.error(f"Error getting multiple from cache: {e}")
            return {}
    
    async def set_many(self, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple values in cache"""
        if not self.client:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            pipeline = self.client.pipeline()
            
            for key, value in data.items():
                serialized_value = json.dumps(value, default=str)
                pipeline.setex(key, ttl, serialized_value)
            
            await pipeline.execute()
            return True
        except Exception as e:
            logger.error(f"Error setting multiple in cache: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.client:
            return 0
        
        try:
            keys = await self.client.keys(pattern)
            if keys:
                await self.client.delete(*keys)
                return len(keys)
            return 0
        except Exception as e:
            logger.error(f"Error clearing pattern from cache: {e}")
            return 0
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.client:
            return {"connected": False}
        
        try:
            info = await self.client.info()
            return {
                "connected": True,
                "total_keys": info.get("db0", {}).get("keys", 0),
                "memory_usage": info.get("used_memory_human", "N/A"),
                "uptime": info.get("uptime_in_seconds", 0)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"connected": False, "error": str(e)}

# Global Redis client instance
redis_client = RedisClient()

# Cache decorator for API endpoints
def cache_response(ttl: int = 3600, key_prefix: str = "api"):
    """Decorator to cache API responses"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = await redis_client.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await redis_client.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {cache_key}")
            
            return result
        return wrapper
    return decorator

# Cache keys for different data types
class CacheKeys:
    """Standard cache keys for the application"""
    
    # Market data
    MARKET_OVERVIEW = "api:markets:overview"
    MARKET_QUOTES = "api:markets:quotes:{ticker}"
    MARKET_MOVERS = "api:markets:movers"
    
    # Financial data
    FINANCIAL_LATEST = "api:financials:latest:{company}"
    FINANCIAL_HISTORY = "api:financials:history:{company}:{year}"
    FINANCIAL_RATIOS = "api:financials:ratios:{company}"
    
    # Economic data
    ECONOMIC_INDICATORS = "api:economic:indicators"
    ECONOMIC_SERIES = "api:economic:series:{indicator}"
    
    # Portfolio data
    PORTFOLIO_SUMMARY = "api:portfolio:summary:{user_id}"
    PORTFOLIO_HOLDINGS = "api:portfolio:holdings:{user_id}"
    
    # Company data
    COMPANY_PROFILE = "api:company:profile:{ticker}"
    COMPANY_NEWS = "api:company:news:{ticker}"
    
    # ETL jobs
    ETL_JOBS = "api:etl:jobs"
    ETL_JOB_STATUS = "api:etl:job:{job_id}"

# Cache TTL constants
class CacheTTL:
    """Cache TTL values in seconds"""
    
    # Short-lived data (frequently changing)
    MARKET_QUOTES = 60  # 1 minute
    MARKET_MOVERS = 300  # 5 minutes
    
    # Medium-lived data
    FINANCIAL_LATEST = 3600  # 1 hour
    ECONOMIC_INDICATORS = 3600  # 1 hour
    PORTFOLIO_SUMMARY = 1800  # 30 minutes
    
    # Long-lived data (rarely changing)
    COMPANY_PROFILE = 86400  # 24 hours
    FINANCIAL_HISTORY = 86400  # 24 hours
    ETL_JOBS = 300  # 5 minutes

async def init_cache():
    """Initialize Redis cache connection"""
    await redis_client.connect()

async def close_cache():
    """Close Redis cache connection"""
    await redis_client.disconnect() 