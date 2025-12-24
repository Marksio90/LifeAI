"""Input validation and sanitization for user messages.

Protects against:
- XSS attacks
- SQL injection
- Command injection
- Excessive input
"""

import re
import html
import logging
from typing import Optional
from pydantic import BaseModel, validator, Field

logger = logging.getLogger(__name__)


class MessageInput(BaseModel):
    """Validated message input schema."""

    content: str = Field(..., min_length=1, max_length=4000)
    modality: Optional[str] = Field(default="text")
    language: Optional[str] = Field(default="pl")

    @validator('content')
    def sanitize_content(cls, v: str) -> str:
        """
        Sanitize message content.

        Removes:
        - HTML tags (XSS prevention)
        - Excessive whitespace
        - Dangerous patterns (script tags, event handlers)

        Args:
            v: Raw content string

        Returns:
            Sanitized content

        Raises:
            ValueError: If dangerous content detected
        """
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")

        # Strip HTML tags (XSS prevention)
        v = re.sub(r'<[^>]+>', '', v)

        # HTML entity decode (then re-check for scripts)
        v = html.unescape(v)

        # Remove excessive whitespace
        v = ' '.join(v.split())

        # Check for dangerous patterns
        dangerous_patterns = [
            r'<script',
            r'javascript:',
            r'onerror\s*=',
            r'onclick\s*=',
            r'onload\s*=',
            r'eval\s*\(',
            r'exec\s*\(',
            r'<iframe',
            r'<object',
            r'<embed',
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected: {pattern}")
                raise ValueError(f"Invalid content detected: suspicious pattern")

        # Additional check for SQL injection patterns (defense in depth)
        sql_patterns = [
            r';\s*drop\s+table',
            r';\s*delete\s+from',
            r';\s*update\s+.+set',
            r'union\s+select',
            r'--\s*$',  # SQL comment at end
        ]

        for pattern in sql_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                logger.warning(f"SQL injection pattern detected: {pattern}")
                raise ValueError("Invalid content detected: suspicious SQL pattern")

        # Limit consecutive special characters (potential obfuscation)
        if re.search(r'[^\w\s]{10,}', v):
            logger.warning("Excessive special characters detected")
            raise ValueError("Invalid content: too many special characters")

        return v.strip()

    @validator('modality')
    def validate_modality(cls, v: Optional[str]) -> str:
        """
        Validate modality type.

        Args:
            v: Modality string

        Returns:
            Validated modality

        Raises:
            ValueError: If modality is invalid
        """
        if v is None:
            return "text"

        allowed_modalities = ['text', 'voice', 'image']
        v_lower = v.lower()

        if v_lower not in allowed_modalities:
            raise ValueError(
                f"Modality must be one of {allowed_modalities}, got: {v}"
            )

        return v_lower

    @validator('language')
    def validate_language(cls, v: Optional[str]) -> str:
        """
        Validate language code.

        Args:
            v: Language code (ISO 639-1)

        Returns:
            Validated language code

        Raises:
            ValueError: If language is invalid
        """
        if v is None:
            return "pl"

        # Common language codes
        allowed_languages = ['pl', 'en', 'de', 'fr', 'es', 'it', 'ru', 'uk']

        v_lower = v.lower()

        if v_lower not in allowed_languages:
            logger.warning(f"Unsupported language: {v}, defaulting to 'pl'")
            return "pl"

        return v_lower

    class Config:
        """Pydantic config."""
        str_strip_whitespace = True
        min_anystr_length = 1
        max_anystr_length = 4000


class FileUploadInput(BaseModel):
    """Validated file upload input."""

    filename: str = Field(..., min_length=1, max_length=255)
    content_type: str = Field(...)
    size_bytes: int = Field(..., gt=0, le=20_000_000)  # Max 20MB

    @validator('filename')
    def sanitize_filename(cls, v: str) -> str:
        """
        Sanitize filename.

        Removes path traversal attempts and dangerous characters.

        Args:
            v: Raw filename

        Returns:
            Sanitized filename

        Raises:
            ValueError: If filename is dangerous
        """
        # Remove path components (path traversal attack prevention)
        v = v.split('/')[-1].split('\\')[-1]

        # Check for path traversal patterns
        if '..' in v or v.startswith('.'):
            raise ValueError("Invalid filename: path traversal attempt")

        # Allow only safe characters
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', v):
            raise ValueError(
                "Invalid filename: only alphanumeric, dash, underscore, and dot allowed"
            )

        return v

    @validator('content_type')
    def validate_content_type(cls, v: str, values: dict) -> str:
        """
        Validate content type against filename extension.

        Args:
            v: Content type
            values: Other validated values

        Returns:
            Validated content type

        Raises:
            ValueError: If content type is invalid or mismatched
        """
        # Allowed image types
        allowed_image_types = [
            'image/jpeg',
            'image/jpg',
            'image/png',
            'image/gif',
            'image/webp'
        ]

        # Allowed audio types
        allowed_audio_types = [
            'audio/mpeg',
            'audio/mp3',
            'audio/wav',
            'audio/webm',
            'audio/ogg',
            'audio/m4a'
        ]

        allowed_types = allowed_image_types + allowed_audio_types

        if v not in allowed_types:
            raise ValueError(
                f"Invalid content type. Allowed: {', '.join(allowed_types)}"
            )

        # Verify extension matches content type
        filename = values.get('filename', '')
        ext = filename.split('.')[-1].lower() if '.' in filename else ''

        type_to_ext = {
            'image/jpeg': ['jpg', 'jpeg'],
            'image/png': ['png'],
            'image/gif': ['gif'],
            'image/webp': ['webp'],
            'audio/mpeg': ['mp3', 'mpeg'],
            'audio/wav': ['wav'],
            'audio/webm': ['webm'],
            'audio/ogg': ['ogg'],
            'audio/m4a': ['m4a']
        }

        expected_exts = type_to_ext.get(v, [])
        if ext not in expected_exts:
            logger.warning(
                f"Content type {v} doesn't match extension {ext}"
            )
            raise ValueError(
                f"Content type {v} doesn't match file extension .{ext}"
            )

        return v


# Convenience validation functions
def validate_message(content: str, modality: str = "text", language: str = "pl") -> MessageInput:
    """
    Validate and sanitize message input.

    Args:
        content: Message content
        modality: Message modality
        language: Language code

    Returns:
        Validated MessageInput

    Raises:
        ValueError: If validation fails
    """
    return MessageInput(
        content=content,
        modality=modality,
        language=language
    )


def validate_file_upload(filename: str, content_type: str, size_bytes: int) -> FileUploadInput:
    """
    Validate file upload.

    Args:
        filename: Original filename
        content_type: MIME type
        size_bytes: File size in bytes

    Returns:
        Validated FileUploadInput

    Raises:
        ValueError: If validation fails
    """
    return FileUploadInput(
        filename=filename,
        content_type=content_type,
        size_bytes=size_bytes
    )
