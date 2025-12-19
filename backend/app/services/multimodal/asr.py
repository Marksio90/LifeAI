import os
from typing import Optional, BinaryIO
from openai import OpenAI
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ASRService:
    """
    Automatic Speech Recognition service using OpenAI Whisper.

    Whisper is a state-of-the-art speech recognition model that:
    - Supports 100+ languages
    - Works well with noise and accents
    - Provides high accuracy transcription
    """

    MODEL = "whisper-1"  # OpenAI's Whisper model

    @staticmethod
    async def transcribe(
        audio_file: BinaryIO,
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> dict:
        """
        Transcribe audio to text.

        Args:
            audio_file: Audio file (mp3, mp4, mpeg, mpga, m4a, wav, webm)
            language: Optional language code (e.g., 'en', 'pl', 'de')
            prompt: Optional context to guide transcription

        Returns:
            dict with 'text' and optionally 'language'
        """
        try:
            # Call Whisper API
            transcript = client.audio.transcriptions.create(
                model=ASRService.MODEL,
                file=audio_file,
                language=language,
                prompt=prompt,
                response_format="verbose_json"  # Get detailed response
            )

            result = {
                "text": transcript.text,
                "language": transcript.language if hasattr(transcript, 'language') else language,
                "duration": transcript.duration if hasattr(transcript, 'duration') else None
            }

            logger.info(f"Transcribed audio: {len(transcript.text)} characters")
            return result

        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise

    @staticmethod
    async def transcribe_file_path(
        file_path: str,
        language: Optional[str] = None
    ) -> dict:
        """
        Transcribe audio from file path.

        Args:
            file_path: Path to audio file
            language: Optional language code

        Returns:
            Transcription result
        """
        try:
            with open(file_path, 'rb') as audio_file:
                return await ASRService.transcribe(audio_file, language)

        except Exception as e:
            logger.error(f"Error transcribing file {file_path}: {e}")
            raise


# Convenience function
async def transcribe_audio(
    audio_file: BinaryIO,
    language: Optional[str] = None
) -> str:
    """
    Transcribe audio and return text.

    Args:
        audio_file: Audio file
        language: Optional language code

    Returns:
        Transcribed text
    """
    result = await ASRService.transcribe(audio_file, language)
    return result["text"]
