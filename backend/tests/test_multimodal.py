"""Tests for multimodal endpoints."""
import pytest
from fastapi import status
from io import BytesIO
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_audio_file():
    """Create a mock audio file."""
    audio_data = b"fake audio data"
    return BytesIO(audio_data)


@pytest.fixture
def mock_image_file():
    """Create a mock image file."""
    # Simple 1x1 red PNG
    image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x00\x00\x00\x00IEND\xaeB`\x82'
    return BytesIO(image_data)


@patch('app.services.multimodal.asr.ASRService.transcribe')
def test_transcribe_audio(mock_transcribe, authenticated_client, mock_audio_file):
    """Test audio transcription endpoint."""
    client, _ = authenticated_client

    # Mock ASR response
    mock_transcribe.return_value = {
        "text": "Hello, this is a test",
        "language": "en",
        "duration": 2.5
    }

    response = client.post(
        "/multimodal/transcribe",
        files={"file": ("audio.webm", mock_audio_file, "audio/webm")}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "text" in data
    assert data["text"] == "Hello, this is a test"


@patch('app.services.multimodal.tts.TTSService.synthesize')
def test_synthesize_speech(mock_synthesize, authenticated_client):
    """Test text-to-speech endpoint."""
    client, _ = authenticated_client

    # Mock TTS response
    mock_synthesize.return_value = b"fake audio bytes"

    response = client.post("/multimodal/synthesize", json={
        "text": "Hello, world!",
        "voice": "nova",
        "model": "tts-1"
    })

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "audio/mpeg"


@patch('app.services.multimodal.vision.VisionService.analyze_image')
def test_analyze_image(mock_analyze, authenticated_client, mock_image_file):
    """Test image analysis endpoint."""
    client, _ = authenticated_client

    # Mock Vision response
    mock_analyze.return_value = {
        "description": "A beautiful sunset over the ocean",
        "usage": {"prompt_tokens": 100, "completion_tokens": 50}
    }

    response = client.post(
        "/multimodal/vision",
        files={"file": ("image.png", mock_image_file, "image/png")}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "description" in data


@patch('app.services.multimodal.vision.VisionService.analyze_food')
def test_analyze_food_image(mock_analyze_food, authenticated_client, mock_image_file):
    """Test food image analysis endpoint."""
    client, _ = authenticated_client

    # Mock food analysis response
    mock_analyze_food.return_value = {
        "analysis": "Pizza with pepperoni, approximately 800 calories",
        "type": "food_analysis",
        "usage": {"prompt_tokens": 120, "completion_tokens": 60}
    }

    response = client.post(
        "/multimodal/vision/food",
        files={"file": ("food.png", mock_image_file, "image/png")}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "analysis" in data
    assert data["type"] == "food_analysis"
