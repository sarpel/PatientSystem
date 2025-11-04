"""
Application settings management using Pydantic Settings.
Loads configuration from environment variables and .env file.
"""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration settings.

    All settings can be overridden via environment variables.
    Loads from .env file if present.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Database Configuration
    db_server: str = Field(
        default="localhost", description="SQL Server instance name (e.g., Sarpel-PC\\HIZIR)"
    )
    db_name: str = Field(default="TestDB", description="Database name")
    db_driver: str = Field(default="ODBC Driver 18 for SQL Server", description="ODBC driver name")
    db_trust_certificate: str = Field(
        default="yes", description="Trust server certificate (yes/no)"
    )
    db_timeout: int = Field(default=30, description="Connection timeout in seconds")

    # AI API Keys
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic Claude API key")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    google_api_key: Optional[str] = Field(default=None, description="Google Gemini API key")

    # Ollama Configuration
    ollama_base_url: str = Field(
        default="http://localhost:11434", description="Ollama server base URL"
    )
    ollama_model: str = Field(default="gemma:7b", description="Default Ollama model")

    # AI Model Configuration
    claude_model: str = Field(default="claude-3-5-sonnet-20241022", description="Claude model name")
    openai_model: str = Field(default="gpt-4o", description="OpenAI model name")
    gemini_model: str = Field(default="gemini-pro", description="Google Gemini model name")

    # AI Routing Strategy
    ai_routing_strategy: str = Field(
        default="smart", description="AI routing strategy (smart, manual, round_robin)"
    )
    ai_enable_fallback: bool = Field(
        default=True, description="Enable automatic fallback to alternative AI providers"
    )
    ai_max_retries: int = Field(default=3, description="Maximum retry attempts per AI provider")
    ai_timeout: int = Field(default=120, description="AI request timeout in seconds")
    ai_temperature: float = Field(default=0.5, description="AI sampling temperature (0.0-1.0)")
    ai_max_tokens: int = Field(default=4096, description="Maximum tokens in AI response")

    # Application Settings
    log_level: str = Field(
        default="DEBUG", description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    environment: str = Field(
        default="development", description="Environment (development, production)"
    )

    # API Server
    api_host: str = Field(default="localhost", description="API server host")
    api_port: int = Field(default=8080, description="API server port")

    # Security (disabled for personal use)
    enable_auth: bool = Field(
        default=False, description="Enable authentication (disabled for personal use)"
    )
    enable_encryption: bool = Field(
        default=False, description="Enable encryption (disabled for personal use)"
    )

    # Clinical Thresholds and Constants
    crp_severe_threshold: float = Field(
        default=50.0, description="CRP threshold for severe inflammation (mg/L)"
    )
    hba1c_diabetes_threshold: float = Field(
        default=6.5, description="HbA1c threshold for diabetes diagnosis (%)"
    )
    fever_temperature_threshold: float = Field(
        default=38.0, description="Temperature threshold for fever (°C)"
    )
    hypertension_systolic_threshold: int = Field(
        default=140, description="Systolic BP threshold for hypertension (mmHg)"
    )
    hypertension_diastolic_threshold: int = Field(
        default=90, description="Diastolic BP threshold for hypertension (mmHg)"
    )
    tachycardia_threshold: int = Field(
        default=100, description="Heart rate threshold for tachycardia (bpm)"
    )
    obesity_bmi_threshold: float = Field(default=30.0, description="BMI threshold for obesity")
    overweight_bmi_threshold: float = Field(
        default=25.0, description="BMI threshold for overweight"
    )
    underweight_bmi_threshold: float = Field(
        default=18.5, description="BMI threshold for underweight"
    )

    # AI Model Limits
    ai_max_retry_attempts: int = Field(
        default=3, description="Maximum retry attempts for AI providers"
    )
    ai_retry_delay_multiplier: float = Field(
        default=1.0, description="Base multiplier for retry delay (seconds)"
    )
    ai_retry_delay_min: float = Field(default=1.0, description="Minimum retry delay (seconds)")
    ai_retry_delay_max: float = Field(default=10.0, description="Maximum retry delay (seconds)")

    # Performance Thresholds
    api_response_timeout: int = Field(default=30, description="API response timeout (seconds)")
    database_query_timeout: int = Field(default=30, description="Database query timeout (seconds)")
    ai_request_timeout: int = Field(default=120, description="AI request timeout (seconds)")

    @property
    def database_url(self) -> str:
        """
        Constructs SQLAlchemy database URL for SQL Server with Windows Authentication.

        Returns:
            Connection string for SQLAlchemy with pyodbc
        """
        # URL encode the server name for special characters like backslash
        import urllib.parse

        server_encoded = urllib.parse.quote_plus(self.db_server)
        driver_encoded = urllib.parse.quote_plus(self.db_driver)

        # Windows Authentication connection string
        connection_string = (
            f"DRIVER={{{self.db_driver}}};"
            f"SERVER={self.db_server};"
            f"DATABASE={self.db_name};"
            f"Trusted_Connection=yes;"
            f"TrustServerCertificate={self.db_trust_certificate};"
        )

        connection_string_encoded = urllib.parse.quote_plus(connection_string)

        return f"mssql+pyodbc:///?odbc_connect={connection_string_encoded}"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def has_ai_keys(self) -> bool:
        """Check if any AI API keys are configured."""
        return any([self.anthropic_api_key, self.openai_api_key, self.google_api_key])


# Global settings instance
settings = Settings()
