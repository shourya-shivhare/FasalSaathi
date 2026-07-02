import logging
from typing import Optional
import redis
import redis.asyncio as aioredis
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class RedisManager:
    """
    Manages connection pools and client instances for both asynchronous
    and synchronous Redis operations. Handles graceful fallback when Redis is down.
    """

    def __init__(self) -> None:
        self.async_client: Optional[aioredis.Redis] = None
        self.sync_client: Optional[redis.Redis] = None
        self._async_pool: Optional[aioredis.ConnectionPool] = None
        self._sync_pool: Optional[redis.ConnectionPool] = None
        self.is_connected = False

    def init_redis(self) -> None:
        """Initialize sync and async redis connection pools and clients."""
        try:
            url = settings.REDIS_URL
            max_conn = settings.REDIS_MAX_CONNECTIONS
            timeout = settings.REDIS_TIMEOUT

            logger.info(
                "🔌 Initializing Redis clients at %s (max_connections=%d, timeout=%.1f)",
                url,
                max_conn,
                timeout,
            )

            # Async connection pool & client setup
            self._async_pool = aioredis.ConnectionPool.from_url(
                url,
                max_connections=max_conn,
                socket_timeout=timeout,
                socket_connect_timeout=timeout,
                decode_responses=True,
            )
            self.async_client = aioredis.Redis(connection_pool=self._async_pool)

            # Sync connection pool & client setup
            self._sync_pool = redis.ConnectionPool.from_url(
                url,
                max_connections=max_conn,
                socket_timeout=timeout,
                socket_connect_timeout=timeout,
                decode_responses=True,
            )
            self.sync_client = redis.Redis(connection_pool=self._sync_pool)

            # Eagerly ping to verify connection
            self.is_connected = self.ping_sync()
            if self.is_connected:
                logger.info("✅ Redis connected successfully and health checked.")
            else:
                logger.warning("⚠️ Redis initialization completed but connection ping failed. Will run in fallback mode.")
        except Exception as e:
            logger.error("❌ Failed to initialize Redis connection: %s. Cache will run in fallback mode.", e)
            self.is_connected = False

    async def close_redis(self) -> None:
        """Close both connection pools gracefully."""
        logger.info("🔌 Closing Redis connection pools...")
        try:
            if self.async_client:
                await self.async_client.aclose()
            if self._async_pool:
                await self._async_pool.disconnect()
            if self.sync_client:
                self.sync_client.close()
            if self._sync_pool:
                self._sync_pool.disconnect()
            logger.info("🔌 Redis connection pools closed gracefully.")
        except Exception as e:
            logger.error("❌ Error while closing Redis connection pools: %s", e)
        finally:
            self.is_connected = False

    async def ping(self) -> bool:
        """Check the health of the async Redis connection."""
        if not self.async_client:
            return False
        try:
            return await self.async_client.ping()
        except Exception as e:
            logger.warning("⚠️ Redis async health check failed: %s", e)
            return False

    def ping_sync(self) -> bool:
        """Check the health of the sync Redis connection."""
        if not self.sync_client:
            return False
        try:
            return bool(self.sync_client.ping())
        except Exception as e:
            logger.warning("⚠️ Redis sync health check failed: %s", e)
            return False


# Singleton manager instance
redis_manager = RedisManager()
