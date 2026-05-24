"""
LLM factory – returns a configured ChatGoogleGenerativeAI instance.
Includes:
  - Global async rate limiter (10 RPM for Gemini 2.5 Flash free tier)
  - Retry logic with exponential backoff for 429 errors
  - Async-safe sleep (won't block the event loop)
"""
import asyncio
import time
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, AIMessage
from app.core.config import settings

logger = logging.getLogger(__name__)

# ── Rate Limit Configuration (Gemini 2.5 Flash Free Tier) ────────────────────
RPM_LIMIT = 10                # max requests per minute
MIN_INTERVAL = 60.0 / RPM_LIMIT  # 6 seconds between calls minimum

# Maximum retries for 429 RESOURCE_EXHAUSTED errors
MAX_RETRIES = 3
BASE_DELAY = 15  # seconds — generous to let quota window reset


# ── Global Rate Limiter (Token Bucket) ───────────────────────────────────────
class AsyncRateLimiter:
    """
    Simple token-bucket rate limiter.
    Ensures no more than `max_rpm` LLM calls are made per minute.
    Thread-safe via asyncio.Lock.
    """

    def __init__(self, max_rpm: int = RPM_LIMIT):
        self.max_rpm = max_rpm
        self.min_interval = 60.0 / max_rpm
        self._lock = asyncio.Lock()
        self._call_times: list[float] = []

    async def acquire(self):
        """Wait until we're allowed to make the next API call."""
        async with self._lock:
            now = time.monotonic()
            # Prune timestamps older than 60 seconds
            self._call_times = [t for t in self._call_times if now - t < 60.0]

            if len(self._call_times) >= self.max_rpm:
                # Wait until the oldest call is 60+ seconds old
                oldest = self._call_times[0]
                wait_time = 60.0 - (now - oldest) + 0.5  # +0.5s safety buffer
                if wait_time > 0:
                    logger.info(
                        "⏳ Rate limiter: %d/%d RPM used. Waiting %.1fs...",
                        len(self._call_times), self.max_rpm, wait_time
                    )
                    await asyncio.sleep(wait_time)

            # Enforce minimum interval between consecutive calls
            if self._call_times:
                last_call = self._call_times[-1]
                elapsed = time.monotonic() - last_call
                if elapsed < self.min_interval:
                    gap = self.min_interval - elapsed
                    await asyncio.sleep(gap)

            self._call_times.append(time.monotonic())


# Singleton rate limiter
_rate_limiter = AsyncRateLimiter(max_rpm=RPM_LIMIT)


def get_llm(temperature: float | None = None):
    return ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=temperature if temperature is not None else settings.LLM_TEMPERATURE,
        max_retries=0,          # We handle retries ourselves with proper backoff
        request_timeout=60,     # Increased timeout for free tier
    )


def _is_quota_error(err: Exception) -> bool:
    """Check if the error is a rate-limit / quota exhaustion error."""
    err_str = str(err).lower()
    return any(kw in err_str for kw in [
        "429", "resource_exhausted", "quota", "rate limit",
        "too many requests", "resourceexhausted"
    ])


async def safe_llm_invoke_async(
    llm,
    prompt,
    fallback: str = "I'm sorry, I'm temporarily unavailable. Please try again in a moment.",
) -> str:
    """
    Invoke LLM with:
      1. Global rate limiter (respects 10 RPM)
      2. Exponential backoff retry for 429 errors
      3. Async-safe (uses asyncio.sleep, not time.sleep)

    Returns the response content string, or fallback on persistent failure.
    """
    for attempt in range(MAX_RETRIES):
        try:
            # Wait for rate limiter clearance
            await _rate_limiter.acquire()

            # Run the synchronous LLM call in a thread to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, llm.invoke, prompt)

            content = response.content
            if isinstance(content, list):
                content = "".join(
                    str(block.get("text", "")) if isinstance(block, dict) else str(block)
                    for block in content
                )
            return str(content)

        except Exception as e:
            if _is_quota_error(e) and attempt < MAX_RETRIES - 1:
                delay = BASE_DELAY * (2 ** attempt)  # 15s, 30s
                logger.warning(
                    "⚠️ Quota hit (attempt %d/%d). Backing off %ds...",
                    attempt + 1, MAX_RETRIES, delay
                )
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
        # We're inside an async context (e.g., FastAPI) — use thread-safe approach
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(_sync_safe_invoke, llm, prompt, fallback)
            return future.result(timeout=120)
    else:
        # No event loop — safe to run synchronously
        return _sync_safe_invoke(llm, prompt, fallback)


def _sync_safe_invoke(llm, prompt, fallback: str) -> str:
    """
    Purely synchronous invoke with retry + inter-call delay.
    """
    for attempt in range(MAX_RETRIES):
        try:
            # Simple inter-call delay to respect RPM
            time.sleep(MIN_INTERVAL)

            response = llm.invoke(prompt)
            content = response.content
            if isinstance(content, list):
                content = "".join(
                    str(block.get("text", "")) if isinstance(block, dict) else str(block)
                    for block in content
                )
            return str(content)

        except Exception as e:
            if _is_quota_error(e) and attempt < MAX_RETRIES - 1:
                delay = BASE_DELAY * (2 ** attempt)
                logger.warning(
                    "⚠️ Quota hit (attempt %d/%d). Backing off %ds...",
                    attempt + 1, MAX_RETRIES, delay
                )
                time.sleep(delay)
                continue
            else:
                logger.error("LLM invoke failed: %s", e)
                return fallback

    return fallback
