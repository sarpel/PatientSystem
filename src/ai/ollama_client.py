"""Ollama local AI client implementation."""

import time
from typing import Optional, List
import httpx
from loguru import logger

from .base_client import BaseAIClient, AIResponse, AIProviderError


class OllamaClient(BaseAIClient):
    """Client for Ollama local AI models."""

    def __init__(
        self,
        model_name: str = "gemma:7b",
        base_url: str = "http://localhost:11434",
        timeout: int = 60,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ):
        """
        Initialize Ollama client.

        Args:
            model_name: Ollama model name (e.g., gemma:7b, qwen2.5:7b)
            base_url: Ollama server base URL
            timeout: Request timeout in seconds
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        """
        super().__init__(model_name, timeout, temperature, max_tokens)
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=timeout)

    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AIResponse:
        """Generate completion from Ollama model."""
        start_time = time.time()

        try:
            # Build request payload
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature or self.temperature,
                    "num_predict": max_tokens or self.max_tokens,
                },
            }

            if system_prompt:
                payload["system"] = system_prompt

            # Send request to Ollama
            response = await self.client.post(
                f"{self.base_url}/api/generate", json=payload
            )

            if response.status_code != 200:
                raise AIProviderError(
                    message=f"Ollama request failed: {response.text}",
                    provider="ollama",
                    status_code=response.status_code,
                )

            result = response.json()
            latency_ms = (time.time() - start_time) * 1000

            logger.debug(
                f"Ollama completion: {latency_ms:.0f}ms, "
                f"model={self.model_name}, "
                f"tokens={result.get('eval_count', 0)}"
            )

            return AIResponse(
                content=result["response"],
                model=self.model_name,
                provider="ollama",
                tokens_used=result.get("eval_count"),
                latency_ms=latency_ms,
                metadata={
                    "prompt_eval_count": result.get("prompt_eval_count"),
                    "eval_count": result.get("eval_count"),
                    "total_duration": result.get("total_duration"),
                },
            )

        except httpx.TimeoutException as e:
            raise TimeoutError(
                f"Ollama request timeout after {self.timeout}s"
            ) from e
        except httpx.RequestError as e:
            raise AIProviderError(
                message=f"Ollama connection error: {str(e)}",
                provider="ollama",
                original_error=e,
            ) from e
        except Exception as e:
            if isinstance(e, (AIProviderError, TimeoutError)):
                raise
            raise AIProviderError(
                message=f"Unexpected Ollama error: {str(e)}",
                provider="ollama",
                original_error=e,
            ) from e

    async def health_check(self) -> bool:
        """Check if Ollama server is available."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False

    def list_models(self) -> List[str]:
        """List available Ollama models (synchronous)."""
        try:
            import httpx

            with httpx.Client(timeout=10) as client:
                response = client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    models_data = response.json()
                    return [model["name"] for model in models_data.get("models", [])]
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []

        return []

    async def close(self):
        """Close HTTP client connection."""
        await self.client.aclose()

    def __repr__(self) -> str:
        """String representation."""
        return f"OllamaClient(model={self.model_name}, url={self.base_url})"
