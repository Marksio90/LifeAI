"""Text-to-Speech and DALL-E Image Generation.

Integrates:
- OpenAI TTS (text-to-speech)
- DALL-E 3 (image generation)
- Audio streaming
- Image variants
"""

import logging
import os
from typing import Optional, List
import openai

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =========================================================================
# Text-to-Speech
# =========================================================================

async def text_to_speech(
    text: str,
    voice: str = "alloy",  # alloy, echo, fable, onyx, nova, shimmer
    model: str = "tts-1-hd",  # tts-1 or tts-1-hd
    speed: float = 1.0
) -> bytes:
    """
    Convert text to speech using OpenAI TTS.

    Args:
        text: Text to convert
        voice: Voice to use
        model: TTS model (tts-1 or tts-1-hd)
        speed: Speed multiplier (0.25 to 4.0)

    Returns:
        Audio data as bytes (MP3 format)
    """
    try:
        logger.info(f"Generating TTS for text: '{text[:50]}...' with voice: {voice}")

        response = await client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            speed=speed,
            response_format="mp3"
        )

        # Get audio bytes
        audio_data = response.read()

        logger.info(f"TTS generated: {len(audio_data)} bytes")

        return audio_data

    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise


async def text_to_speech_streaming(
    text: str,
    voice: str = "alloy",
    model: str = "tts-1"
):
    """
    Stream text-to-speech audio.

    Args:
        text: Text to convert
        voice: Voice to use
        model: TTS model

    Yields:
        Audio chunks
    """
    try:
        logger.info(f"Streaming TTS for: '{text[:50]}...'")

        response = await client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            response_format="mp3"
        )

        # Stream in chunks
        chunk_size = 4096
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            yield chunk

    except Exception as e:
        logger.error(f"TTS streaming error: {e}")
        raise


# =========================================================================
# DALL-E Image Generation
# =========================================================================

async def generate_image(
    prompt: str,
    size: str = "1024x1024",  # 256x256, 512x512, 1024x1024, 1792x1024, 1024x1792
    quality: str = "standard",  # standard or hd
    style: str = "vivid",  # vivid or natural
    n: int = 1  # number of images (1-10)
) -> List[str]:
    """
    Generate image using DALL-E 3.

    Args:
        prompt: Image description
        size: Image size
        quality: Quality level
        style: Image style
        n: Number of images

    Returns:
        List of image URLs
    """
    try:
        logger.info(f"Generating image with DALL-E: '{prompt[:50]}...'")

        response = await client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            style=style,
            n=n
        )

        image_urls = [img.url for img in response.data]

        logger.info(f"Generated {len(image_urls)} images")

        return image_urls

    except Exception as e:
        logger.error(f"DALL-E error: {e}")
        raise


async def create_image_variation(
    image_path: str,
    n: int = 1,
    size: str = "1024x1024"
) -> List[str]:
    """
    Create variations of an existing image.

    Args:
        image_path: Path to source image
        n: Number of variations
        size: Output size

    Returns:
        List of variation URLs
    """
    try:
        logger.info(f"Creating image variations: {image_path}")

        with open(image_path, "rb") as image_file:
            response = await client.images.create_variation(
                image=image_file,
                n=n,
                size=size
            )

        variation_urls = [img.url for img in response.data]

        logger.info(f"Created {len(variation_urls)} variations")

        return variation_urls

    except Exception as e:
        logger.error(f"Image variation error: {e}")
        raise


# =========================================================================
# Combined Multi-modal Response
# =========================================================================

async def generate_multimodal_response(
    text: str,
    include_audio: bool = False,
    include_image: bool = False,
    image_prompt: Optional[str] = None
) -> dict:
    """
    Generate multi-modal response with text, audio, and images.

    Args:
        text: Text response
        include_audio: Whether to generate audio
        include_image: Whether to generate image
        image_prompt: Custom image prompt

    Returns:
        Dictionary with text, audio_url, image_urls
    """
    result = {"text": text}

    try:
        if include_audio:
            # Generate audio
            audio_data = await text_to_speech(text)
            # In production, upload to S3/CDN and get URL
            result["audio_data"] = audio_data
            result["audio_format"] = "mp3"

        if include_image and image_prompt:
            # Generate image
            image_urls = await generate_image(image_prompt, n=1)
            result["image_urls"] = image_urls

        return result

    except Exception as e:
        logger.error(f"Multimodal response error: {e}")
        # Return at least the text
        return result


# =========================================================================
# Voice Options
# =========================================================================

VOICE_OPTIONS = {
    "alloy": {"description": "Neutral and balanced", "gender": "neutral"},
    "echo": {"description": "Male, clear", "gender": "male"},
    "fable": {"description": "British accent", "gender": "neutral"},
    "onyx": {"description": "Deep male", "gender": "male"},
    "nova": {"description": "Female, energetic", "gender": "female"},
    "shimmer": {"description": "Female, soft", "gender": "female"}
}


def get_voice_for_agent(agent_type: str) -> str:
    """
    Get recommended voice for agent type.

    Args:
        agent_type: Agent type

    Returns:
        Voice name
    """
    voice_map = {
        "health": "nova",  # Energetic female
        "finance": "onyx",  # Professional male
        "relations": "shimmer",  # Soft female
        "personal_development": "echo",  # Clear male
        "task_management": "alloy",  # Neutral
        "general": "alloy"  # Neutral
    }

    return voice_map.get(agent_type, "alloy")


logger.info("TTS and DALL-E modules initialized")
