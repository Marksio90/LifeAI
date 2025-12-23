from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Literal
import io
import logging

from app.services.multimodal import (
    transcribe_audio,
    synthesize_speech,
    analyze_image,
    ASRService,
    TTSService,
    VisionService
)
from app.middleware.rate_limit import multimodal_limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/multimodal", tags=["multimodal"])

# File size limits (in bytes)
MAX_AUDIO_SIZE = 25 * 1024 * 1024  # 25 MB (OpenAI Whisper limit)
MAX_IMAGE_SIZE = 20 * 1024 * 1024  # 20 MB (GPT-4 Vision limit)


class TranscriptionResponse(BaseModel):
    """Response from speech-to-text"""
    text: str
    language: Optional[str] = None
    duration: Optional[float] = None


class TTSRequest(BaseModel):
    """Request for text-to-speech"""
    text: str
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "nova"
    high_quality: bool = False
    speed: float = 1.0


class ImageAnalysisResponse(BaseModel):
    """Response from image analysis"""
    description: str
    analysis_type: str = "general"
    tokens_used: Optional[int] = None


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_speech(
    file: UploadFile = File(...),
    language: Optional[str] = None,
    _: None = Depends(multimodal_limiter)
):
    """
    Transcribe speech to text using OpenAI Whisper.

    Supports: mp3, mp4, mpeg, mpga, m4a, wav, webm

    Args:
        file: Audio file
        language: Optional language code (en, pl, de, etc.)

    Returns:
        Transcription result with text and metadata
    """
    try:
        # Validate file type
        allowed_types = ['audio/mpeg', 'audio/mp4', 'audio/wav', 'audio/webm', 'audio/m4a']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {allowed_types}"
            )

        # Read file
        audio_bytes = await file.read()

        # Validate file size
        if len(audio_bytes) > MAX_AUDIO_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Audio file too large. Maximum size: {MAX_AUDIO_SIZE / 1024 / 1024:.0f}MB"
            )
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = file.filename or "audio.mp3"

        # Transcribe
        result = await ASRService.transcribe(audio_file, language)

        logger.info(f"Transcribed audio file: {file.filename}")

        return TranscriptionResponse(
            text=result["text"],
            language=result.get("language"),
            duration=result.get("duration")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to transcribe audio")


@router.post("/synthesize")
async def synthesize_text_to_speech(
    request: TTSRequest,
    _: None = Depends(multimodal_limiter)
):
    """
    Synthesize speech from text using OpenAI TTS.

    Returns MP3 audio stream.

    Args:
        request: TTS configuration (text, voice, quality, speed)

    Returns:
        Audio stream (MP3)
    """
    try:
        if len(request.text) > 4096:
            raise HTTPException(
                status_code=400,
                detail="Text too long. Maximum 4096 characters."
            )

        # Generate speech
        model = "tts-1-hd" if request.high_quality else "tts-1"
        audio_bytes = await TTSService.synthesize(
            text=request.text,
            voice=request.voice,
            model=model,
            speed=request.speed
        )

        logger.info(f"Synthesized speech: {len(request.text)} chars")

        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error synthesizing speech: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to synthesize speech")


@router.post("/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_image_endpoint(
    file: UploadFile = File(...),
    prompt: str = Form("Describe this image in detail."),
    _limiter: None = Depends(multimodal_limiter),
    analysis_type: str = Form("general")
):
    """
    Analyze an image using GPT-4 Vision.

    Supports: jpg, jpeg, png, webp

    Args:
        file: Image file
        prompt: Question or instruction about the image
        analysis_type: Type of analysis (general, food, document)

    Returns:
        Image analysis result
    """
    try:
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image type. Allowed: {allowed_types}"
            )

        # Read image
        image_bytes = await file.read()

        # Validate file size
        if len(image_bytes) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Image file too large. Maximum size: {MAX_IMAGE_SIZE / 1024 / 1024:.0f}MB"
            )

        # Analyze based on type
        if analysis_type == "food":
            result = await VisionService.analyze_food(image_bytes)
        elif analysis_type == "document":
            result = await VisionService.analyze_document(image_bytes)
        else:
            result = await VisionService.analyze_image(image_bytes, prompt)

        logger.info(f"Analyzed image: {file.filename} (type: {analysis_type})")

        return ImageAnalysisResponse(
            description=result.get("analysis", result.get("description")),
            analysis_type=analysis_type,
            tokens_used=result.get("usage", {}).get("total_tokens")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to analyze image")


@router.post("/ocr")
async def extract_text_from_image(
    file: UploadFile = File(...),
    _: None = Depends(multimodal_limiter)
):
    """
    Extract text from image (OCR).

    Args:
        file: Image file

    Returns:
        Extracted text
    """
    try:
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image type. Allowed: {allowed_types}"
            )

        # Read image
        image_bytes = await file.read()

        # Validate file size
        if len(image_bytes) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Image file too large. Maximum size: {MAX_IMAGE_SIZE / 1024 / 1024:.0f}MB"
            )

        # Extract text
        text = await VisionService.extract_text(image_bytes)

        logger.info(f"Extracted text from image: {file.filename}")

        return {"text": text}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting text: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to extract text")


@router.get("/voices")
async def get_available_voices():
    """
    Get list of available TTS voices.

    Returns:
        List of voices with descriptions
    """
    voices = [
        {"name": "alloy", "description": "Balanced, neutral voice"},
        {"name": "echo", "description": "Deep, resonant voice"},
        {"name": "fable", "description": "Upbeat, dynamic voice"},
        {"name": "onyx", "description": "Confident, professional voice"},
        {"name": "nova", "description": "Warm, friendly voice"},
        {"name": "shimmer", "description": "Soft, soothing voice"}
    ]

    return {"voices": voices}
