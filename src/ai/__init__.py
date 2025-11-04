"""AI integration module for clinical decision support."""

from typing import Optional

from loguru import logger

from .anthropic_client import AnthropicClient
from .base_client import (
    AIProviderError,
    AIRequest,
    AIResponse,
    BaseAIClient,
    TaskComplexity,
)
from .google_client import GoogleClient
from .ollama_client import OllamaClient
from .openai_client import OpenAIClient
from .prompt_templates import TurkishMedicalPrompts
from .router import AIRouter


def create_ai_router(
    config: Optional[object] = None,
    enable_ollama: bool = True,
    enable_claude: bool = True,
    enable_openai: bool = True,
    enable_gemini: bool = True,
) -> AIRouter:
    """
    Factory function to create AIRouter with configured clients.

    Args:
        config: Settings object (defaults to global settings)
        enable_ollama: Enable Ollama client
        enable_claude: Enable Anthropic Claude client
        enable_openai: Enable OpenAI GPT client
        enable_gemini: Enable Google Gemini client

    Returns:
        Configured AIRouter instance
    """
    if config is None:
        from ..config.settings import settings as config

    clients = {}

    # Initialize Ollama client
    if enable_ollama:
        try:
            clients["ollama"] = OllamaClient(
                model_name=config.ollama_model,
                base_url=config.ollama_base_url,
                timeout=config.ai_timeout,
                temperature=config.ai_temperature,
                max_tokens=config.ai_max_tokens,
            )
            logger.info(f"Ollama client initialized: {config.ollama_model}")
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama client: {e}")

    # Initialize Anthropic Claude client
    if enable_claude and config.anthropic_api_key:
        try:
            clients["claude"] = AnthropicClient(
                model_name=config.claude_model,
                api_key=config.anthropic_api_key,
                timeout=config.ai_timeout,
                temperature=config.ai_temperature,
                max_tokens=config.ai_max_tokens,
            )
            logger.info(f"Claude client initialized: {config.claude_model}")
        except Exception as e:
            logger.warning(f"Failed to initialize Claude client: {e}")

    # Initialize OpenAI GPT client
    if enable_openai and config.openai_api_key:
        try:
            clients["gpt-5"] = OpenAIClient(
                model_name=config.openai_model,
                api_key=config.openai_api_key,
                timeout=config.ai_timeout,
                temperature=config.ai_temperature,
                max_tokens=config.ai_max_tokens,
            )
            logger.info(f"OpenAI client initialized: {config.openai_model}")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI client: {e}")

    # Initialize Google Gemini client
    if enable_gemini and config.google_api_key:
        try:
            clients["gemini"] = GoogleClient(
                model_name=config.gemini_model,
                api_key=config.google_api_key,
                timeout=config.ai_timeout,
                temperature=config.ai_temperature,
                max_tokens=2048,  # Gemini has lower token limit
            )
            logger.info(f"Gemini client initialized: {config.gemini_model}")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini client: {e}")

    if not clients:
        logger.error("No AI clients could be initialized!")
        raise RuntimeError(
            "Failed to initialize any AI providers. Check configuration and API keys."
        )

    # Create router
    router = AIRouter(
        ollama_client=clients.get("ollama"),
        claude_client=clients.get("claude"),
        openai_client=clients.get("gpt-5"),
        google_client=clients.get("gemini"),
        strategy=config.ai_routing_strategy,
        enable_fallback=config.ai_enable_fallback,
        max_retries=config.ai_max_retries,
    )

    logger.info(
        f"AIRouter created: {len(clients)} providers, "
        f"strategy={config.ai_routing_strategy}, "
        f"fallback={'enabled' if config.ai_enable_fallback else 'disabled'}"
    )

    return router


__all__ = [
    "BaseAIClient",
    "AIResponse",
    "AIRequest",
    "TaskComplexity",
    "AIProviderError",
    "OllamaClient",
    "AnthropicClient",
    "OpenAIClient",
    "GoogleClient",
    "AIRouter",
    "TurkishMedicalPrompts",
    "create_ai_router",
]
