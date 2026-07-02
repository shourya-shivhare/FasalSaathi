import logging
import time
from fastapi import HTTPException, status
from backend.app.core.redis import redis_manager
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class RedisRateLimiter:
    """
    Fixed-window rate limiter powered by Redis.
    Uses pipeline operations to increment counters and manage expirations atomically.
    Gracefully falls back to allowing requests if Redis is offline/unavailable.
    """

    @staticmethod
    def check_rate_limit(
        key: str,
        limit: int,
        window_seconds: int,
        error_detail: str = "Too many requests. Please try again later.",
    ) -> None:
        """
        Evaluate rate limit against Redis (synchronous version for sync contexts).
        Raises HTTPException with 429 if the limit is exceeded.
        """
        if not settings.ENABLE_RATE_LIMIT:
            return

        client = redis_manager.sync_client
        if not client:
            logger.warning("⚠️ Redis sync client is unavailable. Bypassing rate limit check for key: %s", key)
            return

        try:
            # Multi/pipeline to read-increment atomically
            pipe = client.pipeline()
            pipe.incr(key)
            pipe.ttl(key)
            current_count, current_ttl = pipe.execute()

            if current_count == 1:
                # Key is new, set expiration
                client.expire(key, window_seconds)
            elif current_ttl == -1:
                # Fallback if TTL is lost for some reason
                client.expire(key, window_seconds)

            if current_count > limit:
                logger.warning("🚫 Rate limit exceeded (sync) for key %s (%d/%d)", key, current_count, limit)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=error_detail,
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error("⚠️ Error enforcing rate limit in Redis (sync): %s. Bypassing.", e)
            return

    @staticmethod
    async def check_rate_limit_async(
        key: str,
        limit: int,
        window_seconds: int,
        error_detail: str = "Too many requests. Please try again later.",
    ) -> None:
        """
        Evaluate rate limit against Redis (asynchronous version).
        Raises HTTPException with 429 if the limit is exceeded.
        """
        if not settings.ENABLE_RATE_LIMIT:
            return

        client = redis_manager.async_client
        if not client:
            logger.warning("⚠️ Redis async client is unavailable. Bypassing rate limit check for key: %s", key)
            return

        try:
            # Multi/pipeline to read-increment atomically
            pipe = client.pipeline()
            pipe.incr(key)
            pipe.ttl(key)
            current_count, current_ttl = await pipe.execute()

            if current_count == 1:
                # Key is new, set expiration
                await client.expire(key, window_seconds)
            elif current_ttl == -1:
                # Fallback if TTL is lost
                await client.expire(key, window_seconds)

            if current_count > limit:
                logger.warning("🚫 Rate limit exceeded (async) for key %s (%d/%d)", key, current_count, limit)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=error_detail,
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error("⚠️ Error enforcing rate limit in Redis (async): %s. Bypassing.", e)
            return
