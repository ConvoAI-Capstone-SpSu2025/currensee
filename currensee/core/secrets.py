"""
Secret management for CurrenSee.

This module manages access to secrets stored in Google Secret Manager.
It provides a centralized interface for retrieving secrets with caching
and fallback to environment variables for local development.
"""

import os
import functools
from typing import Dict, Optional

from google.cloud import secretmanager
from dotenv import load_dotenv
from pydantic import SecretStr

# Load environment variables for fallback
load_dotenv()


class SecretManager:
    """
    A centralized manager for accessing secrets from Google Secret Manager with
    environment variable fallback for local development.
    """

    def __init__(self):
        """Initialize the SecretManager."""
        self._project_id = os.getenv("PROJECT_ID")
        if not self._project_id:
            raise ValueError("PROJECT_ID environment variable must be set")
        
        self._client = None
        self._secret_cache: Dict[str, str] = {}

    @property
    def client(self):
        """Lazy initialization of the Secret Manager client."""
        if self._client is None:
            self._client = secretmanager.SecretManagerServiceClient()
        return self._client

    @functools.lru_cache(maxsize=128)
    def get_secret(self, secret_id: str, version_id: str = "latest") -> Optional[str]:
        """
        Retrieve a secret from Google Secret Manager.
        
        Args:
            secret_id: The ID of the secret to retrieve
            version_id: The version of the secret to retrieve (default: "latest")
            
        Returns:
            The secret value or None if not found
        """
        # Check cache first
        cache_key = f"{secret_id}:{version_id}"
        if cache_key in self._secret_cache:
            return self._secret_cache[cache_key]
        
        # Try to get from environment first (for local development)
        env_value = os.getenv(secret_id)
        
        # If not in environment, try Secret Manager
        if env_value is None:
            try:
                name = f"projects/{self._project_id}/secrets/{secret_id}/versions/{version_id}"
                response = self.client.access_secret_version(request={"name": name})
                env_value = response.payload.data.decode("UTF-8")
            except Exception as e:
                print(f"Error accessing secret {secret_id}: {e}")
                return None
        
        # Cache the result
        self._secret_cache[cache_key] = env_value
        return env_value
    
    def get_secret_str(self, secret_id: str, version_id: str = "latest") -> Optional[SecretStr]:
        """
        Retrieve a secret from Google Secret Manager as a SecretStr.
        
        Args:
            secret_id: The ID of the secret to retrieve
            version_id: The version of the secret to retrieve (default: "latest")
            
        Returns:
            The secret value as a SecretStr or None if not found
        """
        value = self.get_secret(secret_id, version_id)
        return SecretStr(value) if value is not None else None


# Singleton instance
secret_manager = SecretManager()


def get_secret(secret_id: str) -> Optional[str]:
    """
    Convenience function to retrieve a secret.
    
    Args:
        secret_id: The ID of the secret to retrieve
        
    Returns:
        The secret value or None if not found
    """
    return secret_manager.get_secret(secret_id)


def get_secret_str(secret_id: str) -> Optional[SecretStr]:
    """
    Convenience function to retrieve a secret as a SecretStr.
    
    Args:
        secret_id: The ID of the secret to retrieve
        
    Returns:
        The secret value as a SecretStr or None if not found
    """
    return secret_manager.get_secret_str(secret_id)
