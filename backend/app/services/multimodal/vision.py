import os
import base64
from typing import Optional, Union, List
from openai import AsyncOpenAI
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class VisionService:
    """
    Vision analysis service using GPT-4 Vision.

    Capabilities:
    - Image understanding and description
    - Object detection and recognition
    - Text extraction (OCR)
    - Scene analysis
    - Food recognition (for nutrition tracking)
    - Document understanding
    """

    MODEL = "gpt-4o"  # GPT-4 Omni with vision capabilities

    @staticmethod
    async def analyze_image(
        image: Union[str, bytes],
        prompt: str = "What's in this image? Describe it in detail.",
        max_tokens: int = 300
    ) -> dict:
        """
        Analyze an image using GPT-4 Vision.

        Args:
            image: Either image URL (str) or image bytes
            prompt: Question or instruction about the image
            max_tokens: Maximum tokens in response

        Returns:
            dict with 'description' and 'metadata'
        """
        try:
            # Prepare image for API
            if isinstance(image, bytes):
                # Encode bytes to base64
                image_b64 = base64.b64encode(image).decode('utf-8')
                image_url = f"data:image/jpeg;base64,{image_b64}"
            else:
                # Assume it's a URL
                image_url = image

            # Call GPT-4 Vision API
            response = await client.chat.completions.create(
                model=VisionService.MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                max_tokens=max_tokens
            )

            result = {
                "description": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }

            logger.info(f"Analyzed image: {len(result['description'])} chars")
            return result

        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            raise

    @staticmethod
    async def analyze_image_file(
        file_path: str,
        prompt: str = "What's in this image?"
    ) -> dict:
        """
        Analyze an image from file path.

        Args:
            file_path: Path to image file
            prompt: Question about the image

        Returns:
            Analysis result
        """
        try:
            with open(file_path, 'rb') as f:
                image_bytes = f.read()

            return await VisionService.analyze_image(image_bytes, prompt)

        except Exception as e:
            logger.error(f"Error analyzing image file {file_path}: {e}")
            raise

    @staticmethod
    async def extract_text(image: Union[str, bytes]) -> str:
        """
        Extract text from image (OCR).

        Args:
            image: Image URL or bytes

        Returns:
            Extracted text
        """
        prompt = "Extract all text from this image. Return only the text, nothing else."
        result = await VisionService.analyze_image(image, prompt, max_tokens=500)
        return result["description"]

    @staticmethod
    async def analyze_food(image: Union[str, bytes]) -> dict:
        """
        Analyze food in image for nutrition tracking.

        Args:
            image: Image of food

        Returns:
            dict with food items, estimated portions, calories
        """
        prompt = """Analyze this food image. Identify:
1. Food items present
2. Estimated portion sizes
3. Approximate calorie count for each item
4. Nutritional highlights (protein, carbs, fats)

Format as a structured list."""

        result = await VisionService.analyze_image(image, prompt, max_tokens=400)

        return {
            "analysis": result["description"],
            "type": "food_analysis",
            "usage": result["usage"]
        }

    @staticmethod
    async def analyze_document(image: Union[str, bytes]) -> dict:
        """
        Analyze document image (receipts, forms, etc.).

        Args:
            image: Document image

        Returns:
            Document analysis
        """
        prompt = """Analyze this document. Extract:
1. Document type
2. Key information (amounts, dates, names, etc.)
3. Main content

Be precise and structured."""

        result = await VisionService.analyze_image(image, prompt, max_tokens=500)

        return {
            "analysis": result["description"],
            "type": "document_analysis",
            "usage": result["usage"]
        }

    @staticmethod
    async def compare_images(
        image1: Union[str, bytes],
        image2: Union[str, bytes],
        aspect: str = "general"
    ) -> dict:
        """
        Compare two images.

        Args:
            image1: First image
            image2: Second image
            aspect: What to compare (general, changes, differences)

        Returns:
            Comparison result
        """
        # Note: GPT-4V can only process one image at a time in current API
        # This would require two separate calls and then a comparison
        # For now, we'll analyze both separately

        logger.warning("Image comparison requires multiple API calls")

        result1 = await VisionService.analyze_image(image1, "Describe this image in detail.")
        result2 = await VisionService.analyze_image(image2, "Describe this image in detail.")

        # Use LLM to compare descriptions
        from app.services.llm_client import call_llm

        comparison_prompt = f"""Compare these two image descriptions:

Image 1: {result1['description']}

Image 2: {result2['description']}

Identify similarities, differences, and key changes."""

        comparison = await call_llm([{"role": "user", "content": comparison_prompt}])

        return {
            "comparison": comparison,
            "image1_description": result1["description"],
            "image2_description": result2["description"]
        }


# Convenience function
async def analyze_image(
    image: Union[str, bytes],
    prompt: Optional[str] = None
) -> str:
    """
    Analyze image and return description.

    Args:
        image: Image URL or bytes
        prompt: Optional custom prompt

    Returns:
        Image description
    """
    if prompt is None:
        prompt = "Describe this image in detail. What do you see?"

    result = await VisionService.analyze_image(image, prompt)
    return result["description"]
