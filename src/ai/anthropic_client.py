"""Anthropic Claude AI client implementation."""

import os
import time
from typing import Optional, List
from anthropic import AsyncAnthropic, APIError, APITimeoutError
from loguru import logger

from .base_client import BaseAIClient, AIResponse, AIProviderError


class AnthropicClient(BaseAIClient):
    """Client for Anthropic Claude AI models."""

    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None,
        timeout: int = 120,
        temperature: float = 0.5,
        max_tokens: int = 4096,
    ):
        """
        Initialize Anthropic Claude client.

        Args:
            model_name: Claude model name
            api_key: Anthropic API key (or read from ANTHROPIC_API_KEY env var)
            timeout: Request timeout in seconds
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        """
        super().__init__(model_name, timeout, temperature, max_tokens)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.client = AsyncAnthropic(api_key=self.api_key, timeout=timeout)

    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AIResponse:
        """Generate completion from Claude model."""
        start_time = time.time()

        try:
            # Build messages
            messages = [{"role": "user", "content": prompt}]

            # Create request parameters
            params = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens,
            }

            if system_prompt:
                params["system"] = system_prompt

            # Send request to Claude
            response = await self.client.messages.create(**params)

            latency_ms = (time.time() - start_time) * 1000

            # Extract text content
            content = ""
            for block in response.content:
                if hasattr(block, "text"):
                    content += block.text

            logger.debug(
                f"Claude completion: {latency_ms:.0f}ms, "
                f"model={response.model}, "
                f"tokens={response.usage.input_tokens + response.usage.output_tokens}"
            )

            return AIResponse(
                content=content,
                model=response.model,
                provider="anthropic",
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                latency_ms=latency_ms,
                metadata={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "stop_reason": response.stop_reason,
                    "id": response.id,
                },
            )

        except APITimeoutError as e:
            raise TimeoutError(
                f"Claude request timeout after {self.timeout}s"
            ) from e
        except APIError as e:
            raise AIProviderError(
                message=f"Claude API error: {str(e)}",
                provider="anthropic",
                status_code=getattr(e, "status_code", None),
                original_error=e,
            ) from e
        except Exception as e:
            if isinstance(e, (AIProviderError, TimeoutError)):
                raise
            raise AIProviderError(
                message=f"Unexpected Claude error: {str(e)}",
                provider="anthropic",
                original_error=e,
            ) from e

    async def health_check(self) -> bool:
        """Check if Claude API is available."""
        try:
            # Try a minimal completion request
            response = await self.client.messages.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10,
            )
            return bool(response.content)
        except Exception as e:
            logger.warning(f"Claude health check failed: {e}")
            return False

    def list_models(self) -> List[str]:
        """
        List available Claude models.

        Note: Anthropic doesn't provide a model listing API,
        so we return known models as of 2024.
        """
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]

    def __repr__(self) -> str:
        """String representation."""
        return f"AnthropicClient(model={self.model_name})"
