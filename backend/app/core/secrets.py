"""Secrets management utilities for production."""
import os
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class SecretsManager:
    """Manages secrets from various sources (env vars, AWS, GCP, etc.)."""

    def __init__(self, environment: str = "development"):
        """
        Initialize secrets manager.

        Args:
            environment: Current environment (development, staging, production)
        """
        self.environment = environment
        self.secrets_cache: Dict[str, str] = {}

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a secret value from the configured source.

        Priority:
        1. Environment variable
        2. AWS Secrets Manager (if configured)
        3. Docker secrets (if available)
        4. Default value

        Args:
            key: Secret key
            default: Default value if secret not found

        Returns:
            Secret value or default
        """
        # Check cache first
        if key in self.secrets_cache:
            return self.secrets_cache[key]

        # Try environment variable
        value = os.getenv(key)
        if value:
            self.secrets_cache[key] = value
            return value

        # Try Docker secrets
        value = self._get_docker_secret(key)
        if value:
            self.secrets_cache[key] = value
            return value

        # Try AWS Secrets Manager (production only)
        if self.environment == "production":
            value = self._get_aws_secret(key)
            if value:
                self.secrets_cache[key] = value
                return value

        # Return default
        logger.warning(f"Secret '{key}' not found, using default")
        return default

    def _get_docker_secret(self, key: str) -> Optional[str]:
        """
        Get secret from Docker secrets.

        Docker secrets are mounted at /run/secrets/<secret_name>
        """
        try:
            secret_path = f"/run/secrets/{key.lower()}"
            if os.path.exists(secret_path):
                with open(secret_path, 'r') as f:
                    return f.read().strip()
        except Exception as e:
            logger.debug(f"Docker secret not found for {key}: {e}")

        return None

    def _get_aws_secret(self, key: str) -> Optional[str]:
        """
        Get secret from AWS Secrets Manager.

        Requires: boto3, AWS credentials configured
        """
        try:
            import boto3
            from botocore.exceptions import ClientError

            # Get AWS region from environment
            region = os.getenv("AWS_REGION", "us-east-1")

            # Create Secrets Manager client
            client = boto3.client(
                service_name='secretsmanager',
                region_name=region
            )

            # Get the secret
            response = client.get_secret_value(SecretId=key)

            # Parse secret
            if 'SecretString' in response:
                secret = response['SecretString']
                try:
                    # Try to parse as JSON
                    secret_dict = json.loads(secret)
                    return secret_dict.get(key)
                except json.JSONDecodeError:
                    # Return as plain string
                    return secret

        except ImportError:
            logger.debug("boto3 not installed, skipping AWS Secrets Manager")
        except ClientError as e:
            logger.error(f"Error getting AWS secret {key}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting AWS secret {key}: {e}")

        return None

    def get_database_url(self) -> str:
        """Get database URL with fallback to individual components."""
        # Try full DATABASE_URL first
        db_url = self.get_secret("DATABASE_URL")
        if db_url:
            return db_url

        # Build from components
        user = self.get_secret("POSTGRES_USER", "lifeai")
        password = self.get_secret("POSTGRES_PASSWORD", "")
        host = self.get_secret("POSTGRES_HOST", "localhost")
        port = self.get_secret("POSTGRES_PORT", "5432")
        database = self.get_secret("POSTGRES_DB", "lifeai")

        return f"postgresql://{user}:{password}@{host}:{port}/{database}"

    def get_openai_api_key(self) -> str:
        """Get OpenAI API key."""
        api_key = self.get_secret("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required but not found")
        return api_key

    def get_secret_key(self) -> str:
        """Get JWT secret key."""
        secret_key = self.get_secret("SECRET_KEY")
        if not secret_key:
            logger.warning("SECRET_KEY not found, generating random key (NOT FOR PRODUCTION)")
            import secrets
            secret_key = secrets.token_urlsafe(32)
        return secret_key


# Global secrets manager instance
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """Get or create the global secrets manager instance."""
    global _secrets_manager
    if _secrets_manager is None:
        environment = os.getenv("ENVIRONMENT", "development")
        _secrets_manager = SecretsManager(environment=environment)
    return _secrets_manager
