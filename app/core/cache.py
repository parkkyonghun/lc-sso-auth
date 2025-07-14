import redis
from typing import Optional
from .config import settings

class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(
            settings.cache_url, 
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
    
    def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        try:
            return self.redis_client.get(key)
        except redis.RedisError:
            return None
    
    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set value in cache with optional expiration"""
        try:
            return self.redis_client.set(key, value, ex=ex)
        except redis.RedisError:
            return False
    
    def setex(self, key: str, time: int, value: str) -> bool:
        """Set value with expiration time"""
        try:
            return self.redis_client.setex(key, time, value)
        except redis.RedisError:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            return bool(self.redis_client.delete(key))
        except redis.RedisError:
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return bool(self.redis_client.exists(key))
        except redis.RedisError:
            return False
    
    def ping(self) -> bool:
        """Check if cache is available"""
        try:
            return self.redis_client.ping()
        except redis.RedisError:
            return False

# Global cache instance
cache = CacheManager()

def get_cache() -> CacheManager:
    """Dependency to get cache instance"""
    return cache