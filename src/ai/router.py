"""AI routing system for intelligent model selection based on task complexity."""

from typing import Any, Dict, List, Optional

from loguru import logger
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ..utils.error_handler import error_context, handle_errors
from ..utils.exceptions import AIServiceError, ErrorSeverity, ErrorCategory
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


class AIRouter:
    """
    Smart AI routing system that selects appropriate models based on task complexity.

    Routing Strategy:
    - Simple tasks → Ollama (local, fast, free)
    - Moderate tasks → Ollama → GPT-4o-mini (if Ollama fails)
    - Complex tasks → Claude 3.5 Sonnet → GPT-4o → Gemini Pro → Ollama (fallback chain)
    """

    # Task complexity classification
    TASK_COMPLEXITY_MAP: Dict[str, TaskComplexity] = {
        # Simple tasks - basic summaries and stats
        "patient_summary": TaskComplexity.SIMPLE,
        "basic_stats": TaskComplexity.SIMPLE,
        "recent_visits": TaskComplexity.SIMPLE,
        # Moderate tasks - analysis but not critical decisions
        "lab_trend_analysis": TaskComplexity.MODERATE,
        "medication_adherence": TaskComplexity.MODERATE,
        "visit_patterns": TaskComplexity.MODERATE,
        # Complex tasks - critical clinical decisions
        "differential_diagnosis": TaskComplexity.COMPLEX,
        "treatment_planning": TaskComplexity.COMPLEX,
        "drug_interactions": TaskComplexity.COMPLEX,
        "risk_stratification": TaskComplexity.COMPLEX,
    }

    # Model priority by complexity
    MODEL_PRIORITY: Dict[TaskComplexity, List[str]] = {
        TaskComplexity.SIMPLE: ["ollama"],
        TaskComplexity.MODERATE: ["ollama", "gpt-5-mini"],
        TaskComplexity.COMPLEX: ["claude", "gpt-5", "gemini", "ollama"],
    }

    def __init__(
        self,
        ollama_client: Optional[OllamaClient] = None,
        claude_client: Optional[AnthropicClient] = None,
        openai_client: Optional[OpenAIClient] = None,
        google_client: Optional[GoogleClient] = None,
        strategy: str = "smart",
        enable_fallback: bool = True,
        max_retries: int = 3,
    ):
        """
        Initialize AI router.

        Args:
            ollama_client: Ollama client instance
            claude_client: Anthropic Claude client instance
            openai_client: OpenAI GPT client instance
            google_client: Google Gemini client instance
            strategy: Routing strategy ("smart", "manual", "round_robin")
            enable_fallback: Enable automatic fallback on failures
            max_retries: Maximum retry attempts per provider
        """
        self.clients: Dict[str, Optional[BaseAIClient]] = {
            "ollama": ollama_client,
            "claude": claude_client,
            "gpt-5": openai_client,
            "gpt-5-mini": openai_client,  # Same client, different model
            "gemini": google_client,
        }

        self.strategy = strategy
        self.enable_fallback = enable_fallback
        self.max_retries = max_retries

        logger.info(
            f"AIRouter initialized: strategy={strategy}, "
            f"providers={[k for k, v in self.clients.items() if v is not None]}"
        )

    def classify_task(self, task_type: str) -> TaskComplexity:
        """
        Classify task complexity.

        Args:
            task_type: Task identifier string

        Returns:
            TaskComplexity enum value
        """
        return self.TASK_COMPLEXITY_MAP.get(task_type, TaskComplexity.MODERATE)

    def get_provider_chain(
        self, complexity: TaskComplexity, preferred_provider: Optional[str] = None
    ) -> List[str]:
        """
        Get provider fallback chain for given complexity.

        Args:
            complexity: Task complexity level
            preferred_provider: Optional preferred provider to try first

        Returns:
            List of provider names in priority order
        """
        if preferred_provider and preferred_provider in self.clients:
            # Manual override - try preferred provider first
            chain = [preferred_provider]
            # Add standard chain excluding preferred
            standard_chain = self.MODEL_PRIORITY.get(complexity, ["ollama"])
            chain.extend([p for p in standard_chain if p != preferred_provider])
            return chain

        # Standard smart routing
        return self.MODEL_PRIORITY.get(complexity, ["ollama"])

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((AIProviderError, TimeoutError)),
        reraise=True,
    )
    async def _try_provider(
        self,
        provider_name: str,
        request: AIRequest,
    ) -> AIResponse:
        """
        Attempt completion with specific provider (with retries).

        Args:
            provider_name: Name of provider to use
            request: AI request

        Returns:
            AIResponse from provider

        Raises:
            AIProviderError: If provider fails
            TimeoutError: If request times out
        """
        with error_context(
            operation=f"AI provider request: {provider_name}",
            category=ErrorCategory.AI_SERVICE,
            severity=ErrorSeverity.MEDIUM,
            context={
                "provider": provider_name,
                "task_complexity": request.task_complexity.value,
            },
        ):
            client = self.clients.get(provider_name)

            if not client:
                raise AIServiceError(
                    message=f"Provider '{provider_name}' not configured",
                    provider=provider_name,
                    severity=ErrorSeverity.HIGH,
                )

            logger.debug(
                f"Trying provider: {provider_name} for task complexity: {request.task_complexity.value}"
            )

            # Handle model-specific routing for OpenAI
            if provider_name == "gpt-5-mini" and isinstance(client, OpenAIClient):
                original_model = client.model_name
                client.model_name = "gpt-5-mini"
                try:
                    response = await client.complete(
                        prompt=request.prompt,
                        system_prompt=request.system_prompt,
                        temperature=request.temperature,
                        max_tokens=request.max_tokens,
                    )
                finally:
                    client.model_name = original_model
                return response

            return await client.complete(
                prompt=request.prompt,
                system_prompt=request.system_prompt,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )

    async def route(
        self,
        request: AIRequest,
        task_type: Optional[str] = None,
        preferred_provider: Optional[str] = None,
    ) -> AIResponse:
        """
        Route AI request to appropriate provider with fallback.

        Args:
            request: AI request to process
            task_type: Optional task type for complexity classification
            preferred_provider: Optional provider to try first (manual override)

        Returns:
            AIResponse from successful provider

        Raises:
            AIProviderError: If all providers fail
        """
        # Determine task complexity
        if task_type:
            complexity = self.classify_task(task_type)
            request.task_complexity = complexity
        else:
            complexity = request.task_complexity

        # Get provider chain
        provider_chain = self.get_provider_chain(complexity, preferred_provider)

        logger.info(
            f"Routing request: complexity={complexity.value}, "
            f"chain={provider_chain}, "
            f"fallback={'enabled' if self.enable_fallback else 'disabled'}"
        )

        # Try providers in order
        errors = []
        for provider_name in provider_chain:
            try:
                response = await self._try_provider(provider_name, request)
                logger.info(
                    f"Success: {provider_name} completed in {response.latency_ms:.0f}ms "
                    f"({response.tokens_used or 'N/A'} tokens)"
                )
                return response

            except (AIProviderError, TimeoutError) as e:
                error_msg = f"{provider_name}: {str(e)}"
                errors.append(error_msg)
                logger.warning(f"Provider failed: {error_msg}")

                if not self.enable_fallback:
                    # Fallback disabled - fail immediately
                    raise

                # Continue to next provider in chain
                continue

        # All providers failed
        error_summary = "; ".join(errors)
        raise AIProviderError(
            message=f"All providers failed. Errors: {error_summary}",
            provider="router",
        )

    async def health_check_all(self) -> Dict[str, bool]:
        """
        Check health of all configured providers.

        Returns:
            Dictionary mapping provider names to health status
        """
        results = {}
        for name, client in self.clients.items():
            if client:
                try:
                    results[name] = await client.health_check()
                except Exception as e:
                    logger.error(f"Health check failed for {name}: {e}")
                    results[name] = False
            else:
                results[name] = False

        logger.info(f"Health check results: {results}")
        return results

    def get_available_providers(self) -> List[str]:
        """Get list of configured and available providers."""
        return [name for name, client in self.clients.items() if client is not None]

    def __repr__(self) -> str:
        """String representation."""
        available = self.get_available_providers()
        return f"AIRouter(strategy={self.strategy}, providers={available})"
