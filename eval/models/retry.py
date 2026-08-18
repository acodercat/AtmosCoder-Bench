"""Synchronous retry with exponential backoff + jitter (mirrors axon.models.retry).

The runner is a thread pool of single-shot calls, so this is the blocking
counterpart of axon's async ``with_retry`` — same backoff sequence and the same
"only retry what the provider says is retryable" contract.
"""

import time
import random
import logging
from collections.abc import Callable
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

MAX_RETRIES = 5
BASE_DELAY = 0.5   # seconds
MAX_DELAY = 32.0   # seconds
RETRYABLE_HTTP_STATUS = {408, 409, 429, 500, 502, 503, 504}


def exponential_backoff(attempt: int) -> float:
    """Delay for a 0-indexed attempt: 0.5, 1, 2, 4, 8, 16, 32s (capped) + 0-25% jitter."""
    base = min(BASE_DELAY * (2 ** attempt), MAX_DELAY)
    return base + random.uniform(0, 0.25 * base)


def with_retry(
    operation: Callable[[], T],
    *,
    is_retryable: Callable[[Exception], bool],
    get_delay: Callable[[int, Exception], float] | None = None,
    max_retries: int = MAX_RETRIES,
) -> T:
    """Run ``operation`` up to ``max_retries + 1`` times, retrying only errors
    ``is_retryable`` accepts. ``get_delay`` defaults to exponential backoff."""
    delay_fn = get_delay or (lambda attempt, _error: exponential_backoff(attempt))
    for attempt in range(max_retries + 1):
        try:
            return operation()
        except Exception as error:
            if attempt == max_retries or not is_retryable(error):
                raise
            delay = delay_fn(attempt, error)
            logger.warning("model call failed (attempt %d/%d), retrying in %.1fs: %s",
                           attempt + 1, max_retries + 1, delay, error)
            time.sleep(delay)
    raise AssertionError("unreachable")  # pragma: no cover
