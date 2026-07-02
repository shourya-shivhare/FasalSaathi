import asyncio
import base64
import json
import logging
import zlib
from typing import Any, Callable, List, Optional, Union
from backend.app.core.redis import redis_manager

logger = logging.getLogger(__name__)

# Compression threshold (10 KB)
COMPRESSION_THRESHOLD = 10 * 1024


def serialize_payload(value: Any) -> str:
    """
    Serialize value to JSON and compress using zlib if it exceeds the threshold.
    Returns a JSON string containing metadata.
    """
    serialized = json.dumps(value)
    is_compressed = False

    if len(serialized) > COMPRESSION_THRESHOLD:
        try:
            compressed = zlib.compress(serialized.encode("utf-8"))
            serialized = base64.b64encode(compressed).decode("utf-8")
            is_compressed = True
            logger.info("📦 Compressed cache payload from %d to %d bytes", len(serialized), len(compressed))
        except Exception as e:
            logger.warning("⚠️ Compression failed: %s. Using raw JSON.", e)

    return json.dumps({"c": is_compressed, "v": serialized})


def deserialize_payload(raw: str) -> Any:
    """Decompress (if needed) and deserialize value from JSON."""
    wrapper = json.loads(raw)
    is_compressed = wrapper["c"]
    serialized = wrapper["v"]

    if is_compressed:
        compressed_bytes = base64.b64decode(serialized.encode("utf-8"))
        serialized = zlib.decompress(compressed_bytes).decode("utf-8")

    return json.loads(serialized)


class CacheService:
    """
    High-level caching service providing Cache-Aside capabilities.
    Methods exist in both Async and Sync versions to support all application contexts.
    All operations catch Redis errors and fallback gracefully.
    """

    # ── Asynchronous Cache Operations ──

    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """Retrieve key from Redis and deserialize."""
        client = redis_manager.async_client
        if not client:
            return None
        try:
            raw = await client.get(key)
            if raw:
                logger.info("⚡ Cache HIT (async) for key: %s", key)
                return deserialize_payload(raw)
            logger.info("⚡ Cache MISS (async) for key: %s", key)
            return None
        except Exception as e:
            logger.warning("⚠️ Redis get failed for key %s: %s. Falling back.", key, e)
            return None

    @staticmethod
    async def set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value in Redis with optional TTL (seconds)."""
        client = redis_manager.async_client
        if not client:
            return False
        try:
            payload = serialize_payload(value)
            await client.set(key, payload, ex=ttl)
            logger.info("⚡ Cache SET (async) for key: %s (TTL: %s)", key, ttl)
            return True
        except Exception as e:
            logger.warning("⚠️ Redis set failed for key %s: %s. Falling back.", key, e)
            return False

    @staticmethod
    async def delete(key: str) -> bool:
        """Delete key from Redis."""
        client = redis_manager.async_client
        if not client:
            return False
        try:
            res = await client.delete(key)
            logger.info("⚡ Cache DELETE (async) for key: %s", key)
            return bool(res)
        except Exception as e:
            logger.warning("⚠️ Redis delete failed for key %s: %s.", key, e)
            return False

    @staticmethod
    async def exists(key: str) -> bool:
        """Check if key exists in Redis."""
        client = redis_manager.async_client
        if not client:
            return False
        try:
            return bool(await client.exists(key))
        except Exception as e:
            logger.warning("⚠️ Redis exists failed for key %s: %s.", key, e)
            return False

    @staticmethod
    async def expire(key: str, ttl: int) -> bool:
        """Set a Time-To-Live on a Redis key."""
        client = redis_manager.async_client
        if not client:
            return False
        try:
            return bool(await client.expire(key, ttl))
        except Exception as e:
            logger.warning("⚠️ Redis expire failed for key %s: %s.", key, e)
            return False

    @staticmethod
    async def delete_many(keys: List[str]) -> bool:
        """Delete multiple keys from Redis."""
        if not keys:
            return True
        client = redis_manager.async_client
        if not client:
            return False
        try:
            await client.delete(*keys)
            logger.info("⚡ Cache DELETE_MANY (async) for keys: %s", keys)
            return True
        except Exception as e:
            logger.warning("⚠️ Redis delete_many failed for keys %s: %s.", keys, e)
            return False

    @staticmethod
    async def invalidate_pattern(pattern: str) -> bool:
        """Find keys matching a pattern and delete them."""
        client = redis_manager.async_client
        if not client:
            return False
        try:
            keys = await client.keys(pattern)
            if keys:
                await client.delete(*keys)
                logger.info("⚡ Cache INVALIDATE (async) pattern: %s (deleted %d keys)", pattern, len(keys))
            return True
        except Exception as e:
            logger.warning("⚠️ Redis invalidate_pattern failed for pattern %s: %s.", pattern, e)
            return False

    @staticmethod
    async def get_or_set(key: str, default_fn: Callable[[], Any], ttl: Optional[int] = None) -> Any:
        """Retrieve cached value. On miss, invoke callable, cache the result, and return it."""
        cached = await CacheService.get(key)
        if cached is not None:
            return cached

        # Invoke callable (handles both synchronous and asynchronous callables)
        val = default_fn()
        if asyncio.iscoroutine(val) or hasattr(val, "__await__"):
            val = await val

        await CacheService.set(key, val, ttl)
        return val

    # ── Synchronous Cache Operations ──

    @staticmethod
    def get_sync(key: str) -> Optional[Any]:
        """Retrieve key from Redis and deserialize (sync)."""
        client = redis_manager.sync_client
        if not client:
            return None
        try:
            raw = client.get(key)
            if raw:
                logger.info("⚡ Cache HIT (sync) for key: %s", key)
                return deserialize_payload(raw)
            logger.info("⚡ Cache MISS (sync) for key: %s", key)
            return None
        except Exception as e:
            logger.warning("⚠️ Redis get_sync failed for key %s: %s. Falling back.", key, e)
            return None

    @staticmethod
    def set_sync(key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value in Redis with optional TTL (sync)."""
        client = redis_manager.sync_client
        if not client:
            return False
        try:
            payload = serialize_payload(value)
            client.set(key, payload, ex=ttl)
            logger.info("⚡ Cache SET (sync) for key: %s (TTL: %s)", key, ttl)
            return True
        except Exception as e:
            logger.warning("⚠️ Redis set_sync failed for key %s: %s. Falling back.", key, e)
            return False

    @staticmethod
    def delete_sync(key: str) -> bool:
        """Delete key from Redis (sync)."""
        client = redis_manager.sync_client
        if not client:
            return False
        try:
            res = client.delete(key)
            logger.info("⚡ Cache DELETE (sync) for key: %s", key)
            return bool(res)
        except Exception as e:
            logger.warning("⚠️ Redis delete_sync failed for key %s: %s.", key, e)
            return False

    @staticmethod
    def exists_sync(key: str) -> bool:
        """Check if key exists in Redis (sync)."""
        client = redis_manager.sync_client
        if not client:
            return False
        try:
            return bool(client.exists(key))
        except Exception as e:
            logger.warning("⚠️ Redis exists_sync failed for key %s: %s.", key, e)
            return False

    @staticmethod
    def expire_sync(key: str, ttl: int) -> bool:
        """Set a Time-To-Live on a Redis key (sync)."""
        client = redis_manager.sync_client
        if not client:
            return False
        try:
            return bool(client.expire(key, ttl))
        except Exception as e:
            logger.warning("⚠️ Redis expire_sync failed for key %s: %s.", key, e)
            return False

    @staticmethod
    def delete_many_sync(keys: List[str]) -> bool:
        """Delete multiple keys from Redis (sync)."""
        if not keys:
            return True
        client = redis_manager.sync_client
        if not client:
            return False
        try:
            client.delete(*keys)
            logger.info("⚡ Cache DELETE_MANY (sync) for keys: %s", keys)
            return True
        except Exception as e:
            logger.warning("⚠️ Redis delete_many_sync failed for keys %s: %s.", keys, e)
            return False

    @staticmethod
    def invalidate_pattern_sync(pattern: str) -> bool:
        """Find keys matching a pattern and delete them (sync)."""
        client = redis_manager.sync_client
        if not client:
            return False
        try:
            keys = client.keys(pattern)
            if keys:
                client.delete(*keys)
                logger.info("⚡ Cache INVALIDATE (sync) pattern: %s (deleted %d keys)", pattern, len(keys))
            return True
        except Exception as e:
            logger.warning("⚠️ Redis invalidate_pattern_sync failed for pattern %s: %s.", pattern, e)
            return False

    @staticmethod
    def get_or_set_sync(key: str, default_fn: Callable[[], Any], ttl: Optional[int] = None) -> Any:
        """Retrieve cached value. On miss, invoke callable, cache sync, and return result."""
        cached = CacheService.get_sync(key)
        if cached is not None:
            return cached

        val = default_fn()
        CacheService.set_sync(key, val, ttl)
        return val
