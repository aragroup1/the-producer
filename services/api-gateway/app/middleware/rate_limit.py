"""Redis-backed rate limiting middleware."""

import time
from typing import Optional

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import redis
import structlog

logger = structlog.get_logger()

# Rate limit configuration
DEFAULT_RATE_LIMIT = 100  # requests per window
DEFAULT_RATE_WINDOW = 60  # seconds

# Endpoint-specific limits (stricter for expensive operations)
ENDPOINT_LIMITS = {
    '/api/v1/beats/generate': (5, 60),      # 5 beats per minute
    '/api/v1/beats/batch-generate': (2, 60), # 2 batches per minute
    '/api/v1/auth/login': (10, 60),          # 10 login attempts per minute
    '/api/v1/auth/register': (3, 60),        # 3 registrations per minute
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Redis-backed rate limiting with per-endpoint configuration."""
    
    def __init__(self, app, redis_url: Optional[str] = None):
        super().__init__(app)
        self.redis_url = redis_url or 'redis://localhost:6379/0'
        self._redis = None
    
    @property
    def redis_client(self):
        """Lazy initialization of Redis connection."""
        if self._redis is None:
            try:
                self._redis = redis.from_url(self.redis_url, decode_responses=True)
                self._redis.ping()
            except redis.ConnectionError:
                logger.error("redis_connection_failed", url=self.redis_url)
                # Fallback to in-memory (not production safe, but functional)
                self._redis = None
        return self._redis
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        
        # Get rate limit for this endpoint
        limit, window = ENDPOINT_LIMITS.get(path, (DEFAULT_RATE_LIMIT, DEFAULT_RATE_WINDOW))
        
        # Create rate limit key
        key = f"rate_limit:{client_ip}:{path}"
        
        if self.redis_client:
            # Redis-backed rate limiting
            current = self.redis_client.get(key)
            
            if current is None:
                # First request in window
                self.redis_client.setex(key, window, 1)
            elif int(current) >= limit:
                # Rate limit exceeded
                logger.warning(
                    "rate_limit_exceeded",
                    client_ip=client_ip,
                    path=path,
                    limit=limit,
                    window=window
                )
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded: {limit} requests per {window} seconds"
                )
            else:
                # Increment counter
                self.redis_client.incr(key)
        else:
            # Fallback: simple in-memory rate limiting (per-process only)
            # This is NOT production-safe for multi-instance deployments
            if not hasattr(self, '_request_counts'):
                self._request_counts = {}
            
            now = time.time()
            
            if key in self._request_counts:
                self._request_counts[key] = [
                    ts for ts in self._request_counts[key]
                    if now - ts < window
                ]
            else:
                self._request_counts[key] = []
            
            if len(self._request_counts[key]) >= limit:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded: {limit} requests per {window} seconds"
                )
            
            self._request_counts[key].append(now)
        
        return await call_next(request)
