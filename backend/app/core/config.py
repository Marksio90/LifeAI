"""Application configuration management."""
import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from app.core.secrets import get_secrets_manager


class Settings(BaseSettings):
    """Application settings loaded from environment variables and secrets."""

    # Environment
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    # API
    app_name: str = "LifeAI"
    app_version: str = "2.1.0"
    api_prefix: str = ""

    # Database
    database_url: str = ""

    # Redis
    redis_url: str = ""

    # Security
    secret_key: str = ""
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # OpenAI
    openai_api_key: str = ""

    # Vector Database
    vector_db_type: str = "in-memory"
    pinecone_api_key: str = ""
    pinecone_environment: str = "us-east-1"
    pinecone_index_name: str = "lifeai-embeddings"

    # CORS - Will be parsed manually from comma-separated string
    allowed_origins: List[str] = Field(default=["http://localhost:3000"])

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        # Exclude allowed_origins from automatic ENV parsing
        env_ignore=['allowed_origins']
    )

    @classmethod
    def load(cls) -> "Settings":
        """
        Load settings from environment and secrets manager.

        Returns:
            Settings instance with all configuration
        """
        secrets = get_secrets_manager()

        # Load from environment first
        settings = cls()

        # Override with secrets manager
        settings.database_url = secrets.get_database_url()
        settings.secret_key = secrets.get_secret_key()
        settings.openai_api_key = secrets.get_openai_api_key()

        # Optional secrets
        if redis_url := secrets.get_secret("REDIS_URL"):
            settings.redis_url = redis_url

        if pinecone_key := secrets.get_secret("PINECONE_API_KEY"):
            settings.pinecone_api_key = pinecone_key

        # Parse CORS origins
        origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
        settings.allowed_origins = [o.strip() for o in origins_str.split(",")]

        # Set debug mode based on environment
        settings.debug = settings.environment == "development"

        return settings


# Global settings instance
_settings = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings.load()
    return _settings
