import os
from typing import Literal, Optional
from openai import OpenAI
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Type definitions for voice and model options
Voice = Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
TTSModel = Literal["tts-1", "tts-1-hd"]


class TTSService:
    """
    Text-to-Speech service using OpenAI TTS.

    Features:
    - Multiple voice options (alloy, echo, fable, onyx, nova, shimmer)
    - High-quality audio (tts-1-hd) or fast generation (tts-1)
    - Natural-sounding speech
    - Supports multiple languages
    """

    DEFAULT_MODEL: TTSModel = "tts-1"  # Standard quality, faster
    HD_MODEL: TTSModel = "tts-1-hd"     # High quality, slower
    DEFAULT_VOICE: Voice = "nova"       # Friendly, warm voice

    @staticmethod
    async def synthesize(
        text: str,
        voice: Voice = "nova",
        model: TTSModel = "tts-1",
        speed: float = 1.0
    ) -> bytes:
        """
        Synthesize speech from text.

        Args:
            text: Text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            model: TTS model (tts-1 or tts-1-hd)
            speed: Speed of speech (0.25 to 4.0, default 1.0)

        Returns:
            Audio bytes (MP3 format)
        """
        try:
            response = client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                speed=speed
            )

            audio_bytes = response.content

            logger.info(
                f"Synthesized speech: {len(text)} chars -> "
                f"{len(audio_bytes)} bytes (voice: {voice}, model: {model})"
            )

            return audio_bytes

        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            raise

    @staticmethod
    async def synthesize_to_file(
        text: str,
        output_path: str,
        voice: Voice = "nova",
        model: TTSModel = "tts-1",
        speed: float = 1.0
    ) -> str:
        """
        Synthesize speech and save to file.

        Args:
            text: Text to convert
            output_path: Path to save audio file
            voice: Voice to use
            model: TTS model
            speed: Speech speed

        Returns:
            Path to saved file
        """
        try:
            audio_bytes = await TTSService.synthesize(text, voice, model, speed)

            # Save to file
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'wb') as f:
                f.write(audio_bytes)

            logger.info(f"Saved audio to {output_path}")
            return str(output_file)

        except Exception as e:
            logger.error(f"Error saving speech to file: {e}")
            raise

    @staticmethod
    def get_voice_for_tone(tone: str) -> Voice:
        """
        Get recommended voice based on desired tone.

        Args:
            tone: Desired tone (friendly, professional, calm, energetic)

        Returns:
            Recommended voice
        """
        tone_map = {
            "friendly": "nova",      # Warm, approachable
            "professional": "onyx",  # Confident, clear
            "calm": "shimmer",       # Soft, soothing
            "energetic": "fable",    # Upbeat, dynamic
            "neutral": "alloy",      # Balanced
            "deep": "echo"           # Deep, resonant
        }

        return tone_map.get(tone.lower(), "nova")


# Convenience function
async def synthesize_speech(
    text: str,
    voice: Voice = "nova",
    high_quality: bool = False
) -> bytes:
    """
    Synthesize speech from text.

    Args:
        text: Text to convert
        voice: Voice to use
        high_quality: Use HD model for higher quality

    Returns:
        Audio bytes (MP3)
    """
    model: TTSModel = "tts-1-hd" if high_quality else "tts-1"
    return await TTSService.synthesize(text, voice, model)
