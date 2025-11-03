"""Unit tests for AI client implementations."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.ai.anthropic_client import AnthropicClient
from src.ai.base_client import AIRequest, AIResponse, BaseAIClient, TaskComplexity
from src.ai.google_client import GoogleClient
from src.ai.ollama_client import OllamaClient
from src.ai.openai_client import OpenAIClient


class TestBaseClient:
    """Test base AI client functionality."""

    def test_ai_request_creation(self):
        """Test AI request object creation."""
        request = AIRequest(
            prompt="Test prompt", system_prompt="System prompt", temperature=0.7, max_tokens=1000
        )

        assert request.prompt == "Test prompt"
        assert request.system_prompt == "System prompt"
        assert request.temperature == 0.7
        assert request.max_tokens == 1000

    def test_ai_response_creation(self):
        """Test AI response object creation."""
        response = AIResponse(
            text="Response text",
            model="test-model",
            provider="test-provider",
            usage={"prompt_tokens": 100, "completion_tokens": 200},
        )

        assert response.text == "Response text"
        assert response.model == "test-model"
        assert response.provider == "test-provider"
        assert response.usage["prompt_tokens"] == 100

    def test_task_complexity_values(self):
        """Test task complexity enum values."""
        assert TaskComplexity.SIMPLE.value == "simple"
        assert TaskComplexity.MODERATE.value == "moderate"
        assert TaskComplexity.COMPLEX.value == "complex"


@pytest.mark.unit
class TestOllamaClient:
    """Test Ollama client implementation."""

    @pytest.fixture
    def client(self):
        """Create Ollama client for testing."""
        return OllamaClient(model_name="gemma:7b", base_url="http://localhost:11434")

    @pytest.mark.asyncio
    async def test_complete_success(self, client):
        """Test successful completion."""
        # Mock HTTP response
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "response": "Test response from Ollama",
            "model": "gemma:7b",
            "created_at": "2024-01-01T00:00:00Z",
            "done": True,
        }

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            result = await client.complete(prompt="Test prompt", system_prompt="System prompt")

        assert result.text == "Test response from Ollama"
        assert result.model == "gemma:7b"
        assert result.provider == "ollama"

    @pytest.mark.asyncio
    async def test_complete_error(self, client):
        """Test error handling during completion."""
        mock_response = AsyncMock()
        mock_response.raise_for_status.side_effect = Exception("Connection error")

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(Exception):
                await client.complete(prompt="Test prompt")

    def test_health_check(self, client):
        """Test health check functionality."""
        with patch("httpx.Client.get", return_value=Mock(status_code=200)):
            result = client.health_check()
            assert result is True

    def test_health_check_failure(self, client):
        """Test health check failure."""
        with patch("httpx.Client.get", side_effect=Exception("Connection refused")):
            result = client.health_check()
            assert result is False


@pytest.mark.unit
class TestAnthropicClient:
    """Test Anthropic Claude client implementation."""

    @pytest.fixture
    def client(self):
        """Create Anthropic client for testing."""
        return AnthropicClient(api_key="test-key")

    @pytest.mark.asyncio
    async def test_complete_success(self, client, mock_ai_response):
        """Test successful completion."""
        # Mock Anthropic client
        mock_claude = Mock()
        mock_claude.messages.create = AsyncMock(
            return_value=Mock(
                content=[Mock(text="Test Claude response")],
                usage=Mock(input_tokens=100, output_tokens=200),
            )
        )

        with patch("anthropic.Anthropic", return_value=mock_claude):
            result = await client.complete(prompt="Test prompt", system_prompt="System prompt")

        assert result.text == "Test Claude response"
        assert result.provider == "claude"

    @pytest.mark.asyncio
    async def test_complete_with_temperature(self, client):
        """Test completion with temperature parameter."""
        mock_claude = Mock()
        mock_claude.messages.create = AsyncMock(
            return_value=Mock(
                content=[Mock(text="Test response")],
                usage=Mock(input_tokens=100, output_tokens=200),
            )
        )

        with patch("anthropic.Anthropic", return_value=mock_claude):
            result = await client.complete(prompt="Test prompt", temperature=0.5)

        # Verify temperature was passed to the API
        mock_claude.messages.create.assert_called_once()
        call_args = mock_claude.messages.create.call_args
        assert call_args.kwargs.get("temperature") == 0.5

    def test_health_check(self, client):
        """Test health check functionality."""
        mock_claude = Mock()

        with patch("anthropic.Anthropic", return_value=mock_claude):
            result = client.health_check()
            assert result is True


@pytest.mark.unit
class TestOpenAIClient:
    """Test OpenAI client implementation."""

    @pytest.fixture
    def client(self):
        """Create OpenAI client for testing."""
        return OpenAIClient(api_key="test-key")

    @pytest.mark.asyncio
    async def test_complete_success(self, client):
        """Test successful completion."""
        mock_openai = Mock()
        mock_openai.chat.completions.create = AsyncMock(
            return_value=Mock(
                choices=[Mock(message=Mock(content="Test OpenAI response"))],
                usage=Mock(prompt_tokens=100, completion_tokens=200),
            )
        )

        with patch("openai.OpenAI", return_value=mock_openai):
            result = await client.complete(prompt="Test prompt", system_prompt="System prompt")

        assert result.text == "Test OpenAI response"
        assert result.provider == "openai"

    def test_health_check(self, client):
        """Test health check functionality."""
        mock_openai = Mock()

        with patch("openai.OpenAI", return_value=mock_openai):
            result = client.health_check()
            assert result is True


@pytest.mark.unit
class TestGoogleClient:
    """Test Google Gemini client implementation."""

    @pytest.fixture
    def client(self):
        """Create Google client for testing."""
        return GoogleClient(api_key="test-key")

    @pytest.mark.asyncio
    async def test_complete_success(self, client):
        """Test successful completion."""
        mock_model = Mock()
        mock_model.generate_content_async = AsyncMock(
            return_value=Mock(text="Test Gemini response")
        )

        with patch("google.generativeai.GenerativeModel", return_value=mock_model):
            result = await client.complete(prompt="Test prompt", system_prompt="System prompt")

        assert result.text == "Test Gemini response"
        assert result.provider == "gemini"

    def test_health_check(self, client):
        """Test health check functionality."""
        mock_model = Mock()

        with patch("google.generativeai.GenerativeModel", return_value=mock_model):
            result = client.health_check()
            assert result is True


@pytest.mark.unit
@pytest.mark.ai
class TestAIRouterIntegration:
    """Test AI router integration with multiple clients."""

    @pytest.fixture
    def mock_router(self, mock_ollama_client, mock_claude_client):
        """Create a router with mocked clients."""
        from src.ai.router import AIRouter

        router = AIRouter(ollama_client=mock_ollama_client, claude_client=mock_claude_client)
        return router

    @pytest.mark.asyncio
    async def test_simple_task_routing(self, mock_router):
        """Test routing of simple tasks to Ollama."""
        request = AIRequest(prompt="Patient summary request", task_type="patient_summary")

        result = await mock_router.route_and_complete(request)

        # Should route to Ollama for simple tasks
        mock_router.ollama_client.complete.assert_called_once()
        assert result.provider == "ollama"

    @pytest.mark.asyncio
    async def test_complex_task_routing(self, mock_router):
        """Test routing of complex tasks to Claude."""
        request = AIRequest(
            prompt="Complex differential diagnosis request", task_type="differential_diagnosis"
        )

        result = await mock_router.route_and_complete(request)

        # Should route to Claude for complex tasks
        mock_router.claude_client.complete.assert_called_once()
        assert result.provider == "claude"

    @pytest.mark.asyncio
    async def test_fallback_mechanism(self, mock_router):
        """Test fallback mechanism when primary provider fails."""
        # Make Ollama fail
        mock_router.ollama_client.complete.side_effect = Exception("Ollama unavailable")

        request = AIRequest(prompt="Test request", task_type="patient_summary")

        result = await mock_router.route_and_complete(request)

        # Should fallback to Claude
        mock_router.claude_client.complete.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_all(self, mock_router):
        """Test health check for all providers."""
        mock_router.ollama_client.health_check = AsyncMock(return_value=True)
        mock_router.claude_client.health_check = AsyncMock(return_value=True)

        results = await mock_router.health_check_all()

        assert results["ollama"] is True
        assert results["claude"] is True
        assert results["overall"] is True
