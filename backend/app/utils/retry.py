"""Retry utilities with exponential backoff for external service calls."""
import asyncio
import logging
from typing import TypeVar, Callable, Any, Optional
from functools import wraps
import random

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryableError(Exception):
    """Base exception for retryable errors."""
    pass


class NonRetryableError(Exception):
    """Exception for non-retryable errors."""
    pass


async def retry_with_exponential_backoff(
    func: Callable[..., T],
    max_retries: int = 4,
    initial_delay: float = 2.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple = (Exception,),
    non_retryable_exceptions: tuple = (),
    *args,
    **kwargs
) -> T:
    """
    Retry an async function with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds (default: 2s)
        max_delay: Maximum delay in seconds (default: 60s)
        exponential_base: Base for exponential backoff (default: 2)
        jitter: Add random jitter to prevent thundering herd
        retryable_exceptions: Tuple of exceptions to retry on
        non_retryable_exceptions: Tuple of exceptions to never retry
        *args, **kwargs: Arguments to pass to the function

    Returns:
        Result from the function

    Raises:
        The last exception if all retries fail
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)

        except non_retryable_exceptions as e:
            logger.error(f"Non-retryable error in {func.__name__}: {e}")
            raise NonRetryableError(f"Non-retryable error: {e}") from e

        except retryable_exceptions as e:
            last_exception = e

            if attempt >= max_retries:
                logger.error(
                    f"Max retries ({max_retries}) exceeded for {func.__name__}: {e}"
                )
                break

            # Calculate delay with exponential backoff
            delay = min(initial_delay * (exponential_base ** attempt), max_delay)

            # Add jitter to prevent thundering herd
            if jitter:
                delay = delay * (0.5 + random.random())

            logger.warning(
                f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {e}. "
                f"Retrying in {delay:.2f}s..."
            )

            await asyncio.sleep(delay)

    # If we get here, all retries failed
    raise last_exception


def with_retry(
    max_retries: int = 4,
    initial_delay: float = 2.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple = (Exception,),
    non_retryable_exceptions: tuple = ()
):
    """
    Decorator to add retry logic with exponential backoff to async functions.

    Usage:
        @with_retry(max_retries=3, initial_delay=1.0)
        async def my_function():
            # Your code here
            pass

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Add random jitter to prevent thundering herd
        retryable_exceptions: Tuple of exceptions to retry on
        non_retryable_exceptions: Tuple of exceptions to never retry

    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_with_exponential_backoff(
                func,
                max_retries=max_retries,
                initial_delay=initial_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                jitter=jitter,
                retryable_exceptions=retryable_exceptions,
                non_retryable_exceptions=non_retryable_exceptions,
                *args,
                **kwargs
            )
        return wrapper
    return decorator


# Sync version for non-async functions
def retry_sync(
    func: Callable[..., T],
    max_retries: int = 4,
    initial_delay: float = 2.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple = (Exception,),
    non_retryable_exceptions: tuple = (),
    *args,
    **kwargs
) -> T:
    """
    Retry a synchronous function with exponential backoff.

    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Add random jitter
        retryable_exceptions: Tuple of exceptions to retry on
        non_retryable_exceptions: Tuple of exceptions to never retry
        *args, **kwargs: Arguments to pass to the function

    Returns:
        Result from the function

    Raises:
        The last exception if all retries fail
    """
    import time
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)

        except non_retryable_exceptions as e:
            logger.error(f"Non-retryable error in {func.__name__}: {e}")
            raise NonRetryableError(f"Non-retryable error: {e}") from e

        except retryable_exceptions as e:
            last_exception = e

            if attempt >= max_retries:
                logger.error(
                    f"Max retries ({max_retries}) exceeded for {func.__name__}: {e}"
                )
                break

            # Calculate delay with exponential backoff
            delay = min(initial_delay * (exponential_base ** attempt), max_delay)

            # Add jitter
            if jitter:
                delay = delay * (0.5 + random.random())

            logger.warning(
                f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {e}. "
                f"Retrying in {delay:.2f}s..."
            )

            time.sleep(delay)

    # If we get here, all retries failed
    raise last_exception
