"""Tests for multimodal endpoints."""
import pytest
from fastapi import status
from unittest.mock import patch, AsyncMock, Mock
from io import BytesIO


class TestTranscription:
    """Test speech-to-text transcription."""

    @patch('app.api.multimodal.ASRService.transcribe')
    async def test_transcribe_success(self, mock_transcribe, client):
        """Test successful audio transcription."""
        # Mock transcription result
        mock_transcribe.return_value = {
            "text": "Hello, this is a test transcription.",
            "language": "en",
            "duration": 3.5
        }

        # Create mock audio file
        audio_data = b"fake audio content"
        files = {
            "file": ("test_audio.mp3", BytesIO(audio_data), "audio/mpeg")
        }

        response = client.post(
            "/multimodal/transcribe",
            files=files
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["text"] == "Hello, this is a test transcription."
        assert data["language"] == "en"
        assert data["duration"] == 3.5

    @patch('app.api.multimodal.ASRService.transcribe')
    async def test_transcribe_with_language(self, mock_transcribe, client):
        """Test transcription with specified language."""
        mock_transcribe.return_value = {
            "text": "Witaj, to jest test.",
            "language": "pl",
            "duration": 2.0
        }

        audio_data = b"fake audio content"
        files = {
            "file": ("audio.mp3", BytesIO(audio_data), "audio/mpeg")
        }

        response = client.post(
            "/multimodal/transcribe",
            files=files,
            data={"language": "pl"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["language"] == "pl"

    def test_transcribe_invalid_file_type(self, client):
        """Test transcription with invalid file type."""
        files = {
            "file": ("test.txt", BytesIO(b"text content"), "text/plain")
        }

        response = client.post(
            "/multimodal/transcribe",
            files=files
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Unsupported file type" in response.json()["detail"]

    @patch('app.api.multimodal.ASRService.transcribe')
    async def test_transcribe_service_error(self, mock_transcribe, client):
        """Test handling of transcription service errors."""
        mock_transcribe.side_effect = Exception("OpenAI API error")

        audio_data = b"fake audio content"
        files = {
            "file": ("audio.mp3", BytesIO(audio_data), "audio/mpeg")
        }

        response = client.post(
            "/multimodal/transcribe",
            files=files
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestTextToSpeech:
    """Test text-to-speech synthesis."""

    @patch('app.api.multimodal.TTSService.synthesize')
    async def test_synthesize_success(self, mock_synthesize, client):
        """Test successful speech synthesis."""
        # Mock audio output
        mock_audio = b"fake mp3 audio data"
        mock_synthesize.return_value = mock_audio

        response = client.post(
            "/multimodal/synthesize",
            json={
                "text": "Hello, world!",
                "voice": "nova",
                "high_quality": False,
                "speed": 1.0
            }
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "audio/mpeg"
        assert b"fake mp3 audio data" in response.content

    @patch('app.api.multimodal.TTSService.synthesize')
    async def test_synthesize_high_quality(self, mock_synthesize, client):
        """Test high-quality TTS."""
        mock_synthesize.return_value = b"high quality audio"

        response = client.post(
            "/multimodal/synthesize",
            json={
                "text": "Test message",
                "voice": "alloy",
                "high_quality": True,
                "speed": 1.0
            }
        )

        assert response.status_code == status.HTTP_200_OK
        # Verify tts-1-hd model was called
        mock_synthesize.assert_called_once()
        call_kwargs = mock_synthesize.call_args.kwargs
        assert call_kwargs["model"] == "tts-1-hd"

    @patch('app.api.multimodal.TTSService.synthesize')
    async def test_synthesize_different_voice(self, mock_synthesize, client):
        """Test different voice options."""
        mock_synthesize.return_value = b"audio data"

        for voice in ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]:
            response = client.post(
                "/multimodal/synthesize",
                json={
                    "text": "Test",
                    "voice": voice,
                    "high_quality": False,
                    "speed": 1.0
                }
            )

            assert response.status_code == status.HTTP_200_OK

    def test_synthesize_text_too_long(self, client):
        """Test TTS with text exceeding max length."""
        long_text = "a" * 5000  # Exceeds 4096 limit

        response = client.post(
            "/multimodal/synthesize",
            json={
                "text": long_text,
                "voice": "nova",
                "high_quality": False,
                "speed": 1.0
            }
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "too long" in response.json()["detail"].lower()

    @patch('app.api.multimodal.TTSService.synthesize')
    async def test_synthesize_custom_speed(self, mock_synthesize, client):
        """Test TTS with custom speed."""
        mock_synthesize.return_value = b"audio data"

        response = client.post(
            "/multimodal/synthesize",
            json={
                "text": "Fast speech",
                "voice": "nova",
                "high_quality": False,
                "speed": 1.5
            }
        )

        assert response.status_code == status.HTTP_200_OK
        call_kwargs = mock_synthesize.call_args.kwargs
        assert call_kwargs["speed"] == 1.5


class TestImageAnalysis:
    """Test image analysis with GPT-4 Vision."""

    @patch('app.api.multimodal.VisionService.analyze_image')
    async def test_analyze_image_general(self, mock_analyze, client):
        """Test general image analysis."""
        mock_analyze.return_value = {
            "analysis": "This image shows a beautiful sunset over the ocean.",
            "usage": {"total_tokens": 150}
        }

        image_data = b"fake image data"
        files = {
            "file": ("test.jpg", BytesIO(image_data), "image/jpeg")
        }
        data = {
            "prompt": "Describe this image",
            "analysis_type": "general"
        }

        response = client.post(
            "/multimodal/analyze-image",
            files=files,
            data=data
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert "sunset" in result["description"].lower()
        assert result["analysis_type"] == "general"
        assert result["tokens_used"] == 150

    @patch('app.api.multimodal.VisionService.analyze_food')
    async def test_analyze_food_image(self, mock_analyze_food, client):
        """Test food image analysis."""
        mock_analyze_food.return_value = {
            "analysis": "This appears to be a pizza with pepperoni and cheese.",
            "usage": {"total_tokens": 120}
        }

        image_data = b"fake food image"
        files = {
            "file": ("food.jpg", BytesIO(image_data), "image/jpeg")
        }
        data = {
            "prompt": "What food is this?",
            "analysis_type": "food"
        }

        response = client.post(
            "/multimodal/analyze-image",
            files=files,
            data=data
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["analysis_type"] == "food"
        mock_analyze_food.assert_called_once()

    @patch('app.api.multimodal.VisionService.analyze_document')
    async def test_analyze_document_image(self, mock_analyze_doc, client):
        """Test document image analysis."""
        mock_analyze_doc.return_value = {
            "analysis": "This document contains text about machine learning.",
            "usage": {"total_tokens": 200}
        }

        image_data = b"fake document image"
        files = {
            "file": ("doc.png", BytesIO(image_data), "image/png")
        }
        data = {
            "prompt": "What does this document say?",
            "analysis_type": "document"
        }

        response = client.post(
            "/multimodal/analyze-image",
            files=files,
            data=data
        )

        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["analysis_type"] == "document"
        mock_analyze_doc.assert_called_once()

    def test_analyze_image_invalid_type(self, client):
        """Test image analysis with invalid file type."""
        files = {
            "file": ("test.txt", BytesIO(b"text"), "text/plain")
        }
        data = {
            "prompt": "Describe this",
            "analysis_type": "general"
        }

        response = client.post(
            "/multimodal/analyze-image",
            files=files,
            data=data
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Unsupported image type" in response.json()["detail"]

    @patch('app.api.multimodal.VisionService.analyze_image')
    async def test_analyze_image_service_error(self, mock_analyze, client):
        """Test handling of vision service errors."""
        mock_analyze.side_effect = Exception("Vision API error")

        image_data = b"fake image"
        files = {
            "file": ("test.jpg", BytesIO(image_data), "image/jpeg")
        }
        data = {
            "prompt": "Describe this",
            "analysis_type": "general"
        }

        response = client.post(
            "/multimodal/analyze-image",
            files=files,
            data=data
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestOCR:
    """Test OCR text extraction."""

    @patch('app.api.multimodal.VisionService.extract_text')
    async def test_extract_text_success(self, mock_extract, client):
        """Test successful text extraction."""
        mock_extract.return_value = "This is extracted text from the image."

        image_data = b"fake image with text"
        files = {
            "file": ("document.png", BytesIO(image_data), "image/png")
        }

        response = client.post(
            "/multimodal/ocr",
            files=files
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["text"] == "This is extracted text from the image."

    @patch('app.api.multimodal.VisionService.extract_text')
    async def test_extract_text_from_jpeg(self, mock_extract, client):
        """Test OCR on JPEG image."""
        mock_extract.return_value = "JPEG text content"

        files = {
            "file": ("scan.jpg", BytesIO(b"jpeg data"), "image/jpeg")
        }

        response = client.post(
            "/multimodal/ocr",
            files=files
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["text"] == "JPEG text content"

    def test_ocr_invalid_file_type(self, client):
        """Test OCR with invalid file type."""
        files = {
            "file": ("file.pdf", BytesIO(b"pdf"), "application/pdf")
        }

        response = client.post(
            "/multimodal/ocr",
            files=files
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Unsupported image type" in response.json()["detail"]

    @patch('app.api.multimodal.VisionService.extract_text')
    async def test_ocr_service_error(self, mock_extract, client):
        """Test OCR error handling."""
        mock_extract.side_effect = Exception("OCR failed")

        files = {
            "file": ("text.png", BytesIO(b"image"), "image/png")
        }

        response = client.post(
            "/multimodal/ocr",
            files=files
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestVoiceList:
    """Test available voices endpoint."""

    def test_get_available_voices(self, client):
        """Test getting list of available TTS voices."""
        response = client.get("/multimodal/voices")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "voices" in data
        voices = data["voices"]
        assert len(voices) == 6

        # Check all expected voices are present
        voice_names = [v["name"] for v in voices]
        assert "alloy" in voice_names
        assert "echo" in voice_names
        assert "fable" in voice_names
        assert "onyx" in voice_names
        assert "nova" in voice_names
        assert "shimmer" in voice_names

        # Verify each voice has description
        for voice in voices:
            assert "name" in voice
            assert "description" in voice
            assert len(voice["description"]) > 0
