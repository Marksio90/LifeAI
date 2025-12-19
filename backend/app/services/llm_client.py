"""LLM Client Service for OpenAI API calls."""
import os
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def call_llm(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    **kwargs
) -> str:
    """
    Call OpenAI LLM with given messages.

    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model to use (default: gpt-4o-mini)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        **kwargs: Additional parameters for OpenAI API

    Returns:
        Generated text response
    """
    try:
        logger.debug(f"Calling LLM with model={model}, messages={len(messages)}")

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        content = response.choices[0].message.content
        logger.debug(f"LLM response: {content[:100]}...")

        return content

    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        raise


async def call_llm_with_functions(
    messages: List[Dict[str, str]],
    functions: List[Dict[str, Any]],
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    **kwargs
) -> Dict[str, Any]:
    """
    Call OpenAI LLM with function calling.

    Args:
        messages: List of message dicts
        functions: List of function definitions
        model: Model to use
        temperature: Sampling temperature
        **kwargs: Additional parameters

    Returns:
        Full response dict with function call info
    """
    try:
        logger.debug(f"Calling LLM with {len(functions)} functions")

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            functions=functions,
            temperature=temperature,
            **kwargs
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"Error calling LLM with functions: {e}")
        raise
