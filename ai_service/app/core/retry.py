"""
Retry policies with exponential backoff for external service calls.
Only transient failures are retried — validation errors fail immediately.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Callable, Any, Tuple, Type

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    """Custom error for API rate limit responses."""
    pass


class RetryPolicy:
    """Configurable retry with exponential backoff."""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        backoff_factor: float = 2.0,
        retryable_exceptions: Tuple[Type[Exception], ...] = (TimeoutError, ConnectionError),
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.backoff_factor = backoff_factor
        self.retryable_exceptions = retryable_exceptions


# ── Pre-configured policies (RESTRICTED retryable exceptions) ────────────────
# Only transient errors are retried. ValidationError, malformed input, etc. fail immediately.

GEMINI_RETRY = RetryPolicy(
    max_attempts=3,
    base_delay=2.0,
    backoff_factor=2.0,
    retryable_exceptions=(TimeoutError, ConnectionError, RateLimitError),
)

AGMARKNET_RETRY = RetryPolicy(
    max_attempts=3,
    base_delay=1.0,
    backoff_factor=2.0,
    retryable_exceptions=(TimeoutError, ConnectionError, OSError),
)

OPENWEATHER_RETRY = RetryPolicy(
    max_attempts=3,
    base_delay=1.0,
    backoff_factor=2.0,
    retryable_exceptions=(TimeoutError, ConnectionError, OSError),
)

YOLO_RETRY = RetryPolicy(
    max_attempts=2,
    base_delay=0.5,
    backoff_factor=2.0,
    retryable_exceptions=(TimeoutError, RuntimeError),
)

MEMORY_RETRY = RetryPolicy(
    max_attempts=2,
    base_delay=0.5,
    backoff_factor=2.0,
    retryable_exceptions=(TimeoutError, OSError),
)


async def retry_async(
    func: Callable,
    policy: RetryPolicy,
    *args,
    operation_name: str = "operation",
    **kwargs,
) -> Any:
    """
    Execute async callable with retry + exponential backoff.

    Schedule:
      Attempt 1: immediate
      Attempt 2: base_delay seconds (default 1s)
      Attempt 3: base_delay * backoff_factor (default 2s)

    On exhaustion: raises last exception.
    Non-retryable exceptions propagate immediately.
    """
    last_exc = None

    for attempt in range(1, policy.max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except policy.retryable_exceptions as e:
            last_exc = e
            if attempt < policy.max_attempts:
                delay = policy.base_delay * (policy.backoff_factor ** (attempt - 1))
                logger.warning(
                    "⚠️ %s attempt %d/%d failed: %s. Retry in %.1fs",
                    operation_name, attempt, policy.max_attempts, e, delay,
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    "❌ %s failed after %d attempts: %s",
                    operation_name, policy.max_attempts, e,
                )

    raise last_exc  # type: ignore[misc]
