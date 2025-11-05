"""Google Gemini AI client implementation."""

import os
import time
from typing import List, Optional

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from loguru import logger

from .base_client import AIProviderError, AIResponse, BaseAIClient


class GoogleClient(BaseAIClient):
    """Client for Google Gemini models."""

    def __init__(
        self,
        model_name: str = "gemini-2.5-pro",
        api_key: Optional[str] = None,
        timeout: int = 120,
        temperature: float = 0.5,
        max_tokens: int = 2048,
    ):
        """
        Initialize Google Gemini client.

        Args:
            model_name: Gemini model name (gemini-2.5-pro, gemini-pro-vision)
            api_key: Google API key (or read from GOOGLE_API_KEY env var)
            timeout: Request timeout in seconds
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        """
        super().__init__(model_name, timeout, temperature, max_tokens)
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Google API key required. Set GOOGLE_API_KEY environment variable "
                "or pass api_key parameter."
            )

        # Configure Google AI
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AIResponse:
        """Generate completion from Gemini model."""
        start_time = time.time()

        try:
            # Combine system prompt and user prompt if both provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature or self.temperature,
                max_output_tokens=max_tokens or self.max_tokens,
            )

            # Generate content (synchronous - Gemini doesn't have async API yet)
            response = self.model.generate_content(
                full_prompt, generation_config=generation_config
            )

            latency_ms = (time.time() - start_time) * 1000

            # Extract text content
            content = response.text if hasattr(response, "text") else ""

            # Get token counts if available
            tokens_used = None
            if hasattr(response, "usage_metadata"):
                tokens_used = (
                    response.usage_metadata.prompt_token_count
                    + response.usage_metadata.candidates_token_count
                )

            logger.debug(
                f"Gemini completion: {latency_ms:.0f}ms, "
                f"model={self.model_name}, "
                f"tokens={tokens_used or 'N/A'}"
            )

            return AIResponse(
                content=content,
                model=self.model_name,
                provider="google",
                tokens_used=tokens_used,
                latency_ms=latency_ms,
                metadata={
                    "prompt_token_count": (
                        getattr(response.usage_metadata, "prompt_token_count", None)
                        if hasattr(response, "usage_metadata")
                        else None
                    ),
                    "candidates_token_count": (
                        getattr(response.usage_metadata, "candidates_token_count", None)
                        if hasattr(response, "usage_metadata")
                        else None
                    ),
                    "finish_reason": (
                        response.candidates[0].finish_reason.name
                        if response.candidates
                        else None
                    ),
                },
            )

        except google_exceptions.DeadlineExceeded as e:
            raise TimeoutError(
                f"Google Gemini request timeout after {self.timeout}s"
            ) from e
        except google_exceptions.GoogleAPIError as e:
            raise AIProviderError(
                message=f"Google Gemini API error: {str(e)}",
                provider="google",
                status_code=getattr(e, "code", None),
                original_error=e,
            ) from e
        except Exception as e:
            if isinstance(e, (AIProviderError, TimeoutError)):
                raise
            raise AIProviderError(
                message=f"Unexpected Google Gemini error: {str(e)}",
                provider="google",
                original_error=e,
            ) from e

    async def health_check(self) -> bool:
        """Check if Google Gemini API is available."""
        try:
            # Try listing models
            models = genai.list_models()
            return any(models)
        except Exception as e:
            logger.warning(f"Google Gemini health check failed: {e}")
            return False

    def list_models(self) -> List[str]:
        """List available Gemini models."""
        try:
            models = genai.list_models()
            return [
                model.name
                for model in models
                if "generateContent" in model.supported_generation_methods
            ]
        except Exception as e:
            logger.error(f"Failed to list Google models: {e}")
            return ["gemini-2.5-pro", "gemini-pro-vision"]

    def __repr__(self) -> str:
        """String representation."""
        return f"GoogleClient(model={self.model_name})"
