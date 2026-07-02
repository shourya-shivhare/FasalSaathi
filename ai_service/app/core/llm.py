"""
LLM factory – returns a configured ChatGoogleGenerativeAI instance.
Includes:
  - Multi-key rotation pool (multiple free-tier Gemini API keys)
  - Global async rate limiter (10 RPM per key)
  - Retry logic with exponential backoff for 429 errors
  - Automatic key failover on rate limit
  - Async-safe sleep (won't block the event loop)

Key Rotation Strategy:
  When a key hits 429, it's placed on cooldown and the next key is tried.
  This effectively multiplies your free-tier capacity by the number of keys.
  Example: 3 keys × 10 RPM = ~30 RPM total throughput.
"""
import asyncio
import time
import logging
import threading
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, AIMessage
from ai_service.app.core.config import settings

logger = logging.getLogger(__name__)

# ── Rate Limit Configuration (Gemini Free Tier) ─────────────────────────────
RPM_LIMIT = 10                # max requests per minute per key
MIN_INTERVAL = 60.0 / RPM_LIMIT  # 6 seconds between calls per key

# Maximum retries for 429 RESOURCE_EXHAUSTED errors
MAX_RETRIES = 3
BASE_DELAY = 15  # seconds — generous to let quota window reset

# Cooldown duration for a key after it hits 429 (seconds)
KEY_COOLDOWN = 65  # slightly over 1 minute to let the quota window fully reset


# ── API Key Pool ─────────────────────────────────────────────────────────────

class APIKeyPool:
    """
    Round-robin pool of Gemini API keys with automatic cooldown.

    When a key gets rate-limited (429), it's placed on cooldown and the
    next available key is returned. This multiplies effective throughput.

    Thread-safe for use from asyncio executor threads.
    """

    def __init__(self):
        self._keys: list[str] = []
        self._cooldowns: dict[int, float] = {}  # key_index → cooldown_until timestamp
        self._current_index = 0
        self._lock = threading.Lock()
        self._last_call_per_key: dict[int, float] = {}
        self._load_keys()

    def _load_keys(self):
        """Load API keys from settings."""
        # Try GOOGLE_API_KEYS (comma-separated list) first
        keys_str = getattr(settings, 'GOOGLE_API_KEYS', '') or ''
        if keys_str:
            self._keys = [k.strip() for k in keys_str.split(',') if k.strip()]

        # If no multi-key config, fall back to single GOOGLE_API_KEY
        if not self._keys and settings.GOOGLE_API_KEY:
            self._keys = [settings.GOOGLE_API_KEY]

        if not self._keys:
            logger.error("❌ No Gemini API keys configured! Set GOOGLE_API_KEY or GOOGLE_API_KEYS in .env")
        else:
            logger.info("🔑 API Key Pool initialized with %d key(s)", len(self._keys))

    @property
    def key_count(self) -> int:
        return len(self._keys)

    @property
    def effective_rpm(self) -> int:
        """Total RPM across all non-cooldown keys."""
        return len(self._keys) * RPM_LIMIT

    def get_next_key(self) -> str | None:
        """
        Get the next available API key via round-robin.
        Skips keys that are on cooldown.
        Returns None if all keys are on cooldown.
        """
        if not self._keys:
            return None

        with self._lock:
            now = time.monotonic()
            tried = 0

            while tried < len(self._keys):
                idx = self._current_index % len(self._keys)
                self._current_index += 1

                # Check if this key is on cooldown
                cooldown_until = self._cooldowns.get(idx, 0)
                if now >= cooldown_until:
                    logger.debug("🔑 Using API key #%d/%d", idx + 1, len(self._keys))
                    return self._keys[idx]

                remaining = cooldown_until - now
                logger.debug(
                    "🔑 Key #%d on cooldown (%.0fs remaining), trying next...",
                    idx + 1, remaining
                )
                tried += 1

            # All keys on cooldown — return the one with the shortest remaining cooldown
            soonest_idx = min(self._cooldowns, key=self._cooldowns.get, default=0)
            wait = self._cooldowns.get(soonest_idx, 0) - now
            logger.warning(
                "⚠️ All %d keys on cooldown. Shortest wait: %.0fs (key #%d)",
                len(self._keys), max(0, wait), soonest_idx + 1
            )
            return self._keys[soonest_idx]

    def mark_rate_limited(self, api_key: str):
        """Place a key on cooldown after it hits 429."""
        with self._lock:
            try:
                idx = self._keys.index(api_key)
            except ValueError:
                return
            self._cooldowns[idx] = time.monotonic() + KEY_COOLDOWN
            logger.warning(
                "🔑 Key #%d rate-limited → cooldown for %ds. %d/%d keys available.",
                idx + 1, KEY_COOLDOWN,
                sum(1 for i in range(len(self._keys))
                    if time.monotonic() >= self._cooldowns.get(i, 0)),
                len(self._keys),
            )

    def get_key_status(self) -> list[dict]:
        """Get status of all keys (for debugging)."""
        now = time.monotonic()
        with self._lock:
            return [
                {
                    "key_index": i + 1,
                    "key_preview": f"{k[:8]}...{k[-4:]}",
                    "available": now >= self._cooldowns.get(i, 0),
                    "cooldown_remaining": max(0, self._cooldowns.get(i, 0) - now),
                }
                for i, k in enumerate(self._keys)
            ]


# Singleton key pool
_key_pool = APIKeyPool()


def get_key_pool() -> APIKeyPool:
    """Access the global API key pool."""
    return _key_pool


# ── Global Rate Limiter (Token Bucket) ───────────────────────────────────────
class AsyncRateLimiter:
    """
    Simple token-bucket rate limiter.
    With multi-key support, the effective RPM is keys × RPM_LIMIT.
    """

    def __init__(self, max_rpm: int = RPM_LIMIT):
        self.max_rpm = max_rpm
        self.min_interval = 60.0 / max_rpm
        self._lock = asyncio.Lock()
        self._call_times: list[float] = []

    def update_rpm(self, new_rpm: int):
        """Update RPM when key count changes."""
        self.max_rpm = new_rpm
        self.min_interval = 60.0 / new_rpm

    async def acquire(self):
        """Wait until we're allowed to make the next API call."""
        async with self._lock:
            now = time.monotonic()
            self._call_times = [t for t in self._call_times if now - t < 60.0]

            effective_rpm = _key_pool.effective_rpm or RPM_LIMIT
            if len(self._call_times) >= effective_rpm:
                oldest = self._call_times[0]
                wait_time = 60.0 - (now - oldest) + 0.5
                if wait_time > 0:
                    logger.info(
                        "⏳ Rate limiter: %d/%d RPM used (%d keys). Waiting %.1fs...",
                        len(self._call_times), effective_rpm,
                        _key_pool.key_count, wait_time,
                    )
                    await asyncio.sleep(wait_time)

            # Enforce minimum interval between consecutive calls (per-key basis)
            per_key_interval = self.min_interval / max(1, _key_pool.key_count)
            if self._call_times:
                last_call = self._call_times[-1]
                elapsed = time.monotonic() - last_call
                if elapsed < per_key_interval:
                    gap = per_key_interval - elapsed
                    await asyncio.sleep(gap)

            self._call_times.append(time.monotonic())


# Singleton rate limiter
_rate_limiter = AsyncRateLimiter(max_rpm=RPM_LIMIT)


def get_llm(temperature: float | None = None):
    """Create an LLM instance using the next available API key."""
    api_key = _key_pool.get_next_key() or settings.GOOGLE_API_KEY
    return ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        google_api_key=api_key,
        temperature=temperature if temperature is not None else settings.LLM_TEMPERATURE,
        max_retries=0,          # We handle retries ourselves with key rotation
        request_timeout=60,
    )


def _is_quota_error(err: Exception) -> bool:
    """Check if the error is a rate-limit / quota exhaustion error."""
    err_str = str(err).lower()
    return any(kw in err_str for kw in [
        "429", "resource_exhausted", "quota", "rate limit",
        "too many requests", "resourceexhausted"
    ])


def _is_availability_error(err: Exception) -> bool:
    """Check if the error is a temporary availability issue (503)."""
    err_str = str(err).lower()
    return any(kw in err_str for kw in [
        "503", "unavailable", "service unavailable", "overloaded"
    ])


async def safe_llm_invoke_async(
    llm,
    prompt,
    fallback: str = "I'm sorry, I'm temporarily unavailable. Please try again in a moment.",
) -> str:
    """
    Invoke LLM with:
      1. Global rate limiter (respects RPM × key_count)
      2. Automatic key rotation on 429 errors
      3. Exponential backoff retry
      4. Async-safe (uses asyncio.sleep, not time.sleep)

    Returns the response content string, or fallback on persistent failure.
    """
    current_key = None

    for attempt in range(MAX_RETRIES):
        try:
            # Wait for rate limiter clearance
            await _rate_limiter.acquire()

            # Get the API key this LLM was configured with
            current_key = llm.google_api_key

            # Run the synchronous LLM call in a thread to avoid blocking
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, llm.invoke, prompt)

            content = response.content
            if isinstance(content, list):
                content = "".join(
                    str(block.get("text", "")) if isinstance(block, dict) else str(block)
                    for block in content
                )
            return str(content)

        except Exception as e:
            if _is_quota_error(e):
                # Mark this key as rate-limited
                if current_key:
                    _key_pool.mark_rate_limited(current_key)

                if attempt < MAX_RETRIES - 1:
                    # Try to get a fresh key
                    next_key = _key_pool.get_next_key()
                    if next_key and next_key != current_key:
                        logger.info(
                            "🔄 Key #%s hit 429 → rotating to next key (attempt %d/%d)",
                            _key_preview(current_key), attempt + 1, MAX_RETRIES,
                        )
                        # Create a new LLM with the fresh key
                        llm = ChatGoogleGenerativeAI(
                            model=llm.model,
                            google_api_key=next_key,
                            temperature=llm.temperature,
                            max_retries=0,
                            request_timeout=60,
                        )
                        # Small delay before retry with new key
                        await asyncio.sleep(2)
                        continue
                    else:
                        # All keys exhausted — backoff
                        delay = BASE_DELAY * (2 ** attempt)
                        logger.warning(
                            "⚠️ All keys exhausted (attempt %d/%d). Backing off %ds...",
                            attempt + 1, MAX_RETRIES, delay,
                        )
                        await asyncio.sleep(delay)
                        # Try getting a key again after backoff
                        next_key = _key_pool.get_next_key()
                        if next_key:
                            llm = ChatGoogleGenerativeAI(
                                model=llm.model,
                                google_api_key=next_key,
                                temperature=llm.temperature,
                                max_retries=0,
                                request_timeout=60,
                            )
                        continue
                else:
                    logger.error("LLM invoke failed after %d retries: %s", MAX_RETRIES, e)
                    return fallback

            elif _is_availability_error(e) and attempt < MAX_RETRIES - 1:
                # 503 errors — try another key immediately
                next_key = _key_pool.get_next_key()
                if next_key and next_key != current_key:
                    logger.info("🔄 503 error → trying next key")
                    llm = ChatGoogleGenerativeAI(
                        model=llm.model,
                        google_api_key=next_key,
                        temperature=llm.temperature,
                        max_retries=0,
                        request_timeout=60,
                    )
                    await asyncio.sleep(1)
                    continue
                else:
                    delay = BASE_DELAY * (2 ** attempt)
                    logger.warning("⚠️ 503 + no fresh keys. Backing off %ds...", delay)
                    await asyncio.sleep(delay)
                    continue
            else:
                logger.error("LLM invoke failed: %s", e)
                return fallback

    return fallback


def safe_llm_invoke(
    llm,
    prompt,
    fallback: str = "I'm sorry, I'm temporarily unavailable. Please try again in a moment.",
) -> str:
    """
    Synchronous wrapper for safe_llm_invoke_async.
    Used by LangGraph nodes that run in sync context.
    Includes the same rate limiting and retry logic.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(_sync_safe_invoke, llm, prompt, fallback)
            return future.result(timeout=120)
    else:
        return _sync_safe_invoke(llm, prompt, fallback)


def _sync_safe_invoke(llm, prompt, fallback: str) -> str:
    """
    Purely synchronous invoke with retry + key rotation.
    """
    current_key = None

    for attempt in range(MAX_RETRIES):
        try:
            # Simple inter-call delay
            per_key_interval = MIN_INTERVAL / max(1, _key_pool.key_count)
            time.sleep(per_key_interval)

            current_key = llm.google_api_key
            response = llm.invoke(prompt)
            content = response.content
            if isinstance(content, list):
                content = "".join(
                    str(block.get("text", "")) if isinstance(block, dict) else str(block)
                    for block in content
                )
            return str(content)

        except Exception as e:
            if _is_quota_error(e):
                if current_key:
                    _key_pool.mark_rate_limited(current_key)

                if attempt < MAX_RETRIES - 1:
                    next_key = _key_pool.get_next_key()
                    if next_key and next_key != current_key:
                        logger.info("🔄 Sync: key rotation on 429")
                        llm = ChatGoogleGenerativeAI(
                            model=llm.model,
                            google_api_key=next_key,
                            temperature=llm.temperature,
                            max_retries=0,
                            request_timeout=60,
                        )
                        time.sleep(2)
                        continue
                    else:
                        delay = BASE_DELAY * (2 ** attempt)
                        logger.warning("⚠️ Sync: all keys exhausted. Backing off %ds...", delay)
                        time.sleep(delay)
                        next_key = _key_pool.get_next_key()
                        if next_key:
                            llm = ChatGoogleGenerativeAI(
                                model=llm.model,
                                google_api_key=next_key,
                                temperature=llm.temperature,
                                max_retries=0,
                                request_timeout=60,
                            )
                        continue
                else:
                    logger.error("LLM invoke failed: %s", e)
                    return fallback
            else:
                logger.error("LLM invoke failed: %s", e)
                return fallback

    return fallback


def _key_preview(key: str | None) -> str:
    """Safe preview of API key for logging."""
    if not key:
        return "???"
    return f"{key[:6]}...{key[-4:]}"
