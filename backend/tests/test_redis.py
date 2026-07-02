import pytest
import fnmatch
from fastapi import HTTPException
from backend.app.core.redis import redis_manager
from backend.app.core.config import settings
from backend.app.services.cache_service import CacheService
from backend.app.services.redis_rate_limiter import RedisRateLimiter


class MockRedis:
    def __init__(self):
        self.store = {}
        self.ttls = {}

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value, ex=None):
        self.store[key] = value
        self.ttls[key] = ex
        return True

    def delete(self, *keys):
        count = 0
        for k in keys:
            if k in self.store:
                del self.store[k]
                if k in self.ttls:
                    del self.ttls[k]
                count += 1
        return count

    def exists(self, key):
        return key in self.store

    def expire(self, key, ttl):
        if key in self.store:
            self.ttls[key] = ttl
            return True
        return False

    def keys(self, pattern):
        return [k for k in self.store.keys() if fnmatch.fnmatch(k, pattern)]

    def pipeline(self):
        return MockPipeline(self)


class MockPipeline:
    def __init__(self, mock_redis):
        self.mock_redis = mock_redis
        self.commands = []

    def incr(self, key):
        self.commands.append(("incr", key))
        return self

    def ttl(self, key):
        self.commands.append(("ttl", key))
        return self

    def execute(self):
        res = []
        for cmd, key in self.commands:
            if cmd == "incr":
                val = int(self.mock_redis.store.get(key, 0)) + 1
                self.mock_redis.store[key] = str(val)
                res.append(val)
            elif cmd == "ttl":
                res.append(self.mock_redis.ttls.get(key, -1) or -1)
        self.commands = []
        return res


class AsyncMockRedis(MockRedis):
    async def get(self, key):
        return super().get(key)

    async def set(self, key, value, ex=None):
        return super().set(key, value, ex)

    async def delete(self, *keys):
        return super().delete(*keys)

    async def exists(self, key):
        return super().exists(key)

    async def expire(self, key, ttl):
        return super().expire(key, ttl)

    async def keys(self, pattern):
        return super().keys(pattern)

    def pipeline(self):
        return AsyncMockPipeline(self)


class AsyncMockPipeline(MockPipeline):
    async def execute(self):
        return super().execute()


@pytest.fixture(autouse=True)
def setup_mock_redis(monkeypatch):
    """Fixture to mock Redis clients for all tests."""
    mock_sync = MockRedis()
    mock_async = AsyncMockRedis()

    monkeypatch.setattr(redis_manager, "sync_client", mock_sync)
    monkeypatch.setattr(redis_manager, "async_client", mock_async)
    monkeypatch.setattr(redis_manager, "is_connected", True)
    monkeypatch.setattr(settings, "ENABLE_RATE_LIMIT", True)

    yield mock_sync, mock_async


def test_cache_set_get_sync(setup_mock_redis):
    mock_sync, _ = setup_mock_redis

    key = "test_sync_key"
    val = {"hello": "world"}

    # Assert miss
    assert CacheService.get_sync(key) is None

    # Assert set and hit
    assert CacheService.set_sync(key, val, ttl=300) is True
    assert CacheService.get_sync(key) == val

    # Verify key properties in mock
    assert mock_sync.exists(key) is True
    assert mock_sync.ttls[key] == 300


@pytest.mark.asyncio
async def test_cache_set_get_async(setup_mock_redis):
    _, mock_async = setup_mock_redis

    key = "test_async_key"
    val = [1, 2, 3]

    # Assert miss
    assert await CacheService.get(key) is None

    # Assert set and hit
    assert await CacheService.set(key, val, ttl=60) is True
    assert await CacheService.get(key) == val

    assert await mock_async.exists(key) is True
    assert mock_async.ttls[key] == 60


def test_cache_delete_sync(setup_mock_redis):
    key = "delete_sync_key"
    CacheService.set_sync(key, "data")
    assert CacheService.get_sync(key) == "data"

    assert CacheService.delete_sync(key) is True
    assert CacheService.get_sync(key) is None


@pytest.mark.asyncio
async def test_cache_delete_async(setup_mock_redis):
    key = "delete_async_key"
    await CacheService.set(key, "data")
    assert await CacheService.get(key) == "data"

    assert await CacheService.delete(key) is True
    assert await CacheService.get(key) is None


def test_cache_compression(setup_mock_redis):
    key = "compressed_key"
    # Large data payload (> 10KB compression threshold)
    large_payload = "a" * 15000

    CacheService.set_sync(key, large_payload)
    retrieved = CacheService.get_sync(key)

    assert retrieved == large_payload

    # Inspecting serialized mock storage wrapper to verify it was compressed
    mock_sync, _ = setup_mock_redis
    raw_stored = mock_sync.get(key)
    import json
    parsed = json.loads(raw_stored)
    assert parsed["c"] is True  # c represents compression flag


def test_redis_fallback_when_offline(monkeypatch):
    """Verify that if Redis client is missing (offline), the cache service behaves gracefully."""
    monkeypatch.setattr(redis_manager, "sync_client", None)
    monkeypatch.setattr(redis_manager, "async_client", None)
    monkeypatch.setattr(redis_manager, "is_connected", False)

    # Operations must fail-safe without throwing Redis connection errors
    assert CacheService.get_sync("some_key") is None
    assert CacheService.set_sync("some_key", "value") is False
    assert CacheService.delete_sync("some_key") is False

    # get_or_set_sync should just execute default function
    res = CacheService.get_or_set_sync("some_key", lambda: "direct_fallback")
    assert res == "direct_fallback"


def test_rate_limiting_sync(setup_mock_redis):
    key = "rate_limit_test_key"
    limit = 3
    window = 10

    # Under limit
    for _ in range(limit):
        RedisRateLimiter.check_rate_limit(key, limit, window)

    # Exceed limit
    with pytest.raises(HTTPException) as exc_info:
        RedisRateLimiter.check_rate_limit(key, limit, window)

    assert exc_info.value.status_code == 429
    assert "Too many requests" in exc_info.value.detail


@pytest.mark.asyncio
async def test_rate_limiting_async(setup_mock_redis):
    key = "rate_limit_test_key_async"
    limit = 2
    window = 5

    # Under limit
    for _ in range(limit):
        await RedisRateLimiter.check_rate_limit_async(key, limit, window)

    # Exceed limit
    with pytest.raises(HTTPException) as exc_info:
        await RedisRateLimiter.check_rate_limit_async(key, limit, window)

    assert exc_info.value.status_code == 429
