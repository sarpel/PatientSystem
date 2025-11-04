"""Base AI client abstract class for unified AI provider interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskComplexity(Enum):
    """AI task complexity levels for routing decisions."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


@dataclass
class AIResponse:
    """Standardized AI response format across all providers."""

    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    latency_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "tokens_used": self.tokens_used,
            "latency_ms": self.latency_ms,
            "metadata": self.metadata or {},
        }


@dataclass
class AIRequest:
    """Standardized AI request format."""

    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.5
    max_tokens: int = 4096
    task_complexity: TaskComplexity = TaskComplexity.MODERATE
    metadata: Optional[Dict[str, Any]] = None


class BaseAIClient(ABC):
    """Abstract base class for AI service clients."""

    def __init__(
        self,
        model_name: str,
        timeout: int = 120,
        temperature: float = 0.5,
        max_tokens: int = 4096,
    ):
        """
        Initialize AI client.

        Args:
            model_name: Name of the AI model to use
            timeout: Request timeout in seconds
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
        """
        self.model_name = model_name
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.provider_name = self.__class__.__name__.replace("Client", "").lower()

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AIResponse:
        """
        Generate completion from AI model.

        Args:
            prompt: User prompt text
            system_prompt: Optional system instructions
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            AIResponse with generated content

        Raises:
            AIProviderError: If provider request fails
            TimeoutError: If request exceeds timeout
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if AI provider is available.

        Returns:
            True if provider is healthy, False otherwise
        """
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """
        List available models from provider.

        Returns:
            List of model names
        """
        pass

    def __repr__(self) -> str:
        """String representation of client."""
        return f"{self.__class__.__name__}(model={self.model_name})"


class AIProviderError(Exception):
    """Exception raised when AI provider encounters an error."""

    def __init__(
        self,
        message: str,
        provider: str,
        status_code: Optional[int] = None,
        original_error: Optional[Exception] = None,
    ):
        """
        Initialize AI provider error.

        Args:
            message: Error message
            provider: Name of the provider that failed
            status_code: HTTP status code if applicable
            original_error: Original exception that was caught
        """
        self.message = message
        self.provider = provider
        self.status_code = status_code
        self.original_error = original_error
        super().__init__(self.message)

    def __str__(self) -> str:
        """String representation of error."""
        parts = [f"{self.provider}: {self.message}"]
        if self.status_code:
            parts.append(f"(HTTP {self.status_code})")
        return " ".join(parts)
