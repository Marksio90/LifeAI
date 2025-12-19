"""
Configuration Settings for LifeAI Platform
Manages all environment variables and application settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Keys
    openai_api_key: str
    anthropic_api_key: Optional[str] = None
    assemblyai_api_key: Optional[str] = None
    elevenlabs_api_key: Optional[str] = None

    # Database Configuration
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "lifeai"
    postgres_user: str = "lifeai_user"
    postgres_password: str

    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None

    # Neo4j Configuration
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str

    # Vector Database
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # Security
    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Application Settings
    environment: str = "development"
    log_level: str = "INFO"
    max_context_tokens: int = 100000
    default_llm_model: str = "gpt-4-turbo-preview"

    # Agent Configuration
    max_agents_per_request: int = 5
    agent_timeout_seconds: int = 30
    confidence_threshold: float = 0.7

    @property
    def database_url(self) -> str:
        """Construct PostgreSQL connection URL"""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def redis_url(self) -> str:
        """Construct Redis connection URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/0"
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Singleton settings instance
settings = Settings()
