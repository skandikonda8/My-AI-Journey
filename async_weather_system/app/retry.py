
# app/retry.py

import asyncio
import logging
import random

from typing import Awaitable, Callable, TypeVar

from app.config import (
    MAX_RETRY_ATTEMPTS,
    RETRY_BASE_DELAY,
    RETRY_MAX_DELAY,
    RETRY_JITTER,
)


logger = logging.getLogger(__name__)

T = TypeVar("T")


async def retry_async(
    operation: Callable[[], Awaitable[T]],
    *,
    operation_name: str,
    should_retry: Callable[[Exception], bool],
    max_attempts: int = MAX_RETRY_ATTEMPTS,
    base_delay: float = RETRY_BASE_DELAY,
) -> T:

    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    for attempt in range(1, max_attempts + 1):

        try:
            logger.debug(
                "operation=%s event=attempt_started "
                "attempt=%s",
                operation_name,
                attempt,
            )

            result = await operation()

            if attempt > 1:
                logger.info(
                    "operation=%s event=retry_succeeded "
                    "attempt=%s",
                    operation_name,
                    attempt,
                )

            return result

        except Exception as error:

            retryable = should_retry(error)

            if not retryable:
                logger.error(
                    "operation=%s event=permanent_failure "
                    "error_type=%s",
                    operation_name,
                    type(error).__name__,
                )
                raise

            if attempt == max_attempts:
                logger.error(
                    "operation=%s event=retries_exhausted "
                    "attempts=%s error_type=%s",
                    operation_name,
                    attempt,
                    type(error).__name__,
                )
                raise

            exponential_delay = min(
                base_delay * (2 ** (attempt - 1)),
                RETRY_MAX_DELAY,
            )

            jitter = random.uniform(
                0,
                RETRY_JITTER,
            )

            wait_seconds = exponential_delay + jitter

            logger.warning(
                "operation=%s event=retry_scheduled "
                "attempt=%s wait_seconds=%.2f "
                "error_type=%s",
                operation_name,
                attempt,
                wait_seconds,
                type(error).__name__,
            )

            await asyncio.sleep(wait_seconds)

    raise RuntimeError("Unexpected retry loop exit")
