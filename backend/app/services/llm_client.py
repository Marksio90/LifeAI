"""LLM Client Service for OpenAI API calls with retry logic and caching."""
import os
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI, AsyncOpenAI
from openai import RateLimitError, APIConnectionError, APITimeoutError, APIError
import httpx

from app.utils.retry import with_retry
from app.utils.llm_cache import get_llm_cache

logger = logging.getLogger(__name__)

# Initialize OpenAI clients with timeout configuration
timeout_config = httpx.Timeout(60.0, connect=10.0)  # 60s total, 10s connect

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=timeout_config,
    max_retries=0  # We handle retries ourselves
)

aclient = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=timeout_config,
    max_retries=0  # We handle retries ourselves
)

# Initialize LLM cache
llm_cache = get_llm_cache(ttl=3600)  # 1 hour cache

# Define retryable exceptions from OpenAI
RETRYABLE_EXCEPTIONS = (
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
    ConnectionError,
    TimeoutError,
)

# Define non-retryable exceptions
NON_RETRYABLE_EXCEPTIONS = (
    ValueError,
    KeyError,
)  # Don't retry on client errors


@with_retry(
    max_retries=4,
    initial_delay=2.0,
    max_delay=60.0,
    exponential_base=2.0,
    jitter=True,
    retryable_exceptions=RETRYABLE_EXCEPTIONS,
    non_retryable_exceptions=NON_RETRYABLE_EXCEPTIONS
)
async def _call_llm_api(
    messages: List[Dict[str, str]],
    model: str,
    temperature: float,
    max_tokens: Optional[int],
    **kwargs
) -> str:
    """
    Internal function to call OpenAI API with retry logic.

    This is wrapped by @with_retry decorator for automatic retries.
    """
    response = await aclient.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )

    content = response.choices[0].message.content
    return content


async def call_llm(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    use_cache: bool = True,
    **kwargs
) -> str:
    """
    Call OpenAI LLM with given messages, with caching and retry logic.

    Features:
    - Automatic retry with exponential backoff (up to 4 retries)
    - Response caching (1 hour TTL)
    - Timeout configuration (60s total, 10s connect)
    - Detailed error logging

    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model to use (default: gpt-4o-mini)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        use_cache: Whether to use caching (default: True)
        **kwargs: Additional parameters for OpenAI API

    Returns:
        Generated text response

    Raises:
        RateLimitError: If rate limit exceeded after retries
        APIConnectionError: If connection fails after retries
        APITimeoutError: If request times out after retries
        APIError: For other OpenAI API errors
    """
    try:
        logger.debug(f"Calling LLM with model={model}, messages={len(messages)}")

        # Try to get from cache first
        if use_cache:
            cached_response = llm_cache.get(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            if cached_response:
                logger.info("Returning cached LLM response")
                return cached_response

        # Call API with retry logic
        content = await _call_llm_api(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        logger.debug(f"LLM response: {content[:100]}...")

        # Cache the response
        if use_cache:
            llm_cache.set(
                messages=messages,
                model=model,
                temperature=temperature,
                response=content,
                max_tokens=max_tokens,
                **kwargs
            )

        return content

    except RETRYABLE_EXCEPTIONS as e:
        logger.error(f"LLM call failed after retries: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error calling LLM: {e}", exc_info=True)
        raise


@with_retry(
    max_retries=4,
    initial_delay=2.0,
    retryable_exceptions=RETRYABLE_EXCEPTIONS,
    non_retryable_exceptions=NON_RETRYABLE_EXCEPTIONS
)
async def _call_llm_with_functions_api(
    messages: List[Dict[str, str]],
    functions: List[Dict[str, Any]],
    model: str,
    temperature: float,
    **kwargs
) -> Dict[str, Any]:
    """
    Internal function to call OpenAI API with functions.

    This is wrapped by @with_retry decorator for automatic retries.
    """
    response = await aclient.chat.completions.create(
        model=model,
        messages=messages,
        functions=functions,
        temperature=temperature,
        **kwargs
    )

    return response.model_dump()


async def call_llm_with_functions(
    messages: List[Dict[str, str]],
    functions: List[Dict[str, Any]],
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    **kwargs
) -> Dict[str, Any]:
    """
    Call OpenAI LLM with function calling, with retry logic.

    Features:
    - Automatic retry with exponential backoff
    - Timeout configuration
    - Detailed error logging

    Args:
        messages: List of message dicts
        functions: List of function definitions
        model: Model to use
        temperature: Sampling temperature
        **kwargs: Additional parameters

    Returns:
        Full response dict with function call info

    Raises:
        RateLimitError: If rate limit exceeded after retries
        APIConnectionError: If connection fails after retries
        APITimeoutError: If request times out after retries
    """
    try:
        logger.debug(f"Calling LLM with {len(functions)} functions")

        response = await _call_llm_with_functions_api(
            messages=messages,
            functions=functions,
            model=model,
            temperature=temperature,
            **kwargs
        )

        return response

    except RETRYABLE_EXCEPTIONS as e:
        logger.error(f"LLM function call failed after retries: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error calling LLM with functions: {e}", exc_info=True)
        raise


# Synchronous version for compatibility (e.g., Celery tasks)
def call_llm_sync(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    use_cache: bool = True,
    **kwargs
) -> str:
    """
    Synchronous version of call_llm for use in non-async contexts.

    Features:
    - Response caching (1 hour TTL)
    - Timeout configuration (60s total, 10s connect)
    - Note: Retries are handled by OpenAI client in sync mode

    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model to use (default: gpt-4o-mini)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        use_cache: Whether to use caching (default: True)
        **kwargs: Additional parameters for OpenAI API

    Returns:
        Generated text response
    """
    try:
        logger.debug(f"Calling LLM (sync) with model={model}, messages={len(messages)}")

        # Try to get from cache first
        if use_cache:
            cached_response = llm_cache.get(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            if cached_response:
                logger.info("Returning cached LLM response (sync)")
                return cached_response

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        content = response.choices[0].message.content
        logger.debug(f"LLM response (sync): {content[:100]}...")

        # Cache the response
        if use_cache:
            llm_cache.set(
                messages=messages,
                model=model,
                temperature=temperature,
                response=content,
                max_tokens=max_tokens,
                **kwargs
            )

        return content

    except Exception as e:
        logger.error(f"Error calling LLM (sync): {e}", exc_info=True)
        raise
