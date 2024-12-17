from typing import Any, Optional
import logging
import json
import redis.asyncio as redis
from ..config import settings

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True,
            socket_timeout=settings.REDIS_TIMEOUT,
            retry_on_timeout=True
        )
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
            
        except Exception as e:
            logger.error(f"Error getting from cache: {str(e)}")
            return None
            
    async def set(self, 
                  key: str, 
                  value: Any, 
                  expire: Optional[int] = None) -> bool:
        """Set value in cache with optional expiration"""
        try:
            serialized = json.dumps(value)
            if expire:
                await self.redis.setex(key, expire, serialized)
            else:
                await self.redis.set(key, serialized)
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")
            return False
            
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            await self.redis.delete(key)
            return True
            
        except Exception as e:
            logger.error(f"Error deleting from cache: {str(e)}")
            return False
            
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return await self.redis.exists(key)
            
        except Exception as e:
            logger.error(f"Error checking cache existence: {str(e)}")
            return False
            
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment value in cache"""
        try:
            return await self.redis.incrby(key, amount)
            
        except Exception as e:
            logger.error(f"Error incrementing cache: {str(e)}")
            return None
            
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key"""
        try:
            return await self.redis.expire(key, seconds)
            
        except Exception as e:
            logger.error(f"Error setting cache expiration: {str(e)}")
            return False
            
    async def clear_pattern(self, pattern: str) -> bool:
        """Clear all keys matching pattern"""
        try:
            cursor = 0
            while True:
                cursor, keys = await self.redis.scan(
                    cursor=cursor,
                    match=pattern
                )
                if keys:
                    await self.redis.delete(*keys)
                if cursor == 0:
                    break
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache pattern: {str(e)}")
            return False
            
    async def health_check(self) -> bool:
        """Check if Redis connection is healthy"""
        try:
            return await self.redis.ping()
            
        except Exception as e:
            logger.error(f"Redis health check failed: {str(e)}")
            return False 