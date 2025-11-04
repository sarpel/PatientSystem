"""OpenAI GPT AI client implementation."""

import os
import time
from typing import List, Optional

from loguru import logger
from openai import APIError, APITimeoutError, AsyncOpenAI

from .base_client import AIProviderError, AIResponse, BaseAIClient


class OpenAIClient(BaseAIClient):
    """Client for OpenAI GPT models."""

    def __init__(
        self,
        model_name: str = "gpt-5",
        api_key: Optional[str] = None,
        timeout: int = 120,
        temperature: float = 0.5,
        max_tokens: int = 4096,
    ):
        """
        Initialize OpenAI client.

        Args:
            model_name: OpenAI model name (gpt-5, gpt-5-mini, gpt-4-turbo)
            api_key: OpenAI API key (or read from OPENAI_API_KEY env var)
            timeout: Request timeout in seconds
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        """
        super().__init__(model_name, timeout, temperature, max_tokens)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.client = AsyncOpenAI(api_key=self.api_key, timeout=timeout)

    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AIResponse:
        """Generate completion from GPT model."""
        start_time = time.time()

        try:
            # Build messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # Send request to OpenAI
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
            )

            latency_ms = (time.time() - start_time) * 1000

            # Extract content
            content = response.choices[0].message.content or ""

            logger.debug(
                f"GPT completion: {latency_ms:.0f}ms, "
                f"model={response.model}, "
                f"tokens={response.usage.total_tokens if response.usage else 0}"
            )

            return AIResponse(
                content=content,
                model=response.model,
                provider="openai",
                tokens_used=response.usage.total_tokens if response.usage else None,
                latency_ms=latency_ms,
                metadata={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else None,
                    "completion_tokens": (
                        response.usage.completion_tokens if response.usage else None
                    ),
                    "finish_reason": response.choices[0].finish_reason,
                    "id": response.id,
                },
            )

        except APITimeoutError as e:
            raise TimeoutError(f"OpenAI request timeout after {self.timeout}s") from e
        except APIError as e:
            raise AIProviderError(
                message=f"OpenAI API error: {str(e)}",
                provider="openai",
                status_code=getattr(e, "status_code", None),
                original_error=e,
            ) from e
        except Exception as e:
            if isinstance(e, (AIProviderError, TimeoutError)):
                raise
            raise AIProviderError(
                message=f"Unexpected OpenAI error: {str(e)}",
                provider="openai",
                original_error=e,
            ) from e

    async def health_check(self) -> bool:
        """Check if OpenAI API is available."""
        try:
            # Try listing models
            models = await self.client.models.list()
            return bool(models.data)
        except Exception as e:
            logger.warning(f"OpenAI health check failed: {e}")
            return False

    def list_models(self) -> List[str]:
        """List available OpenAI models (common ones)."""
        return [
            "gpt-5",
            "gpt-5-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
        ]

    def __repr__(self) -> str:
        """String representation."""
        return f"OpenAIClient(model={self.model_name})"
