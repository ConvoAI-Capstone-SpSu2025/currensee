"""
Secret management for CurrenSee.

This module manages access to secrets stored in Google Secret Manager.
It provides a centralized interface for retrieving secrets with caching
and fallback to environment variables for local development.
"""

import os
import sys
import logging
import functools
from typing import Dict, Optional

from google.cloud import secretmanager
from google.auth import exceptions as auth_exceptions
from dotenv import load_dotenv
from pydantic import SecretStr

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Note: We deliberately DON'T load environment variables here
# We'll only load them as a fallback if the Google Secret Manager access fails


class SecretManager:
    """
    A centralized manager for accessing secrets from Google Secret Manager with
    environment variable fallback for local development.
    """

    def __init__(self):
        """Initialize the SecretManager."""
        # Try to load environment variables if PROJECT_ID is not set
        self._project_id = os.getenv("PROJECT_ID")
        if not self._project_id:
            logger.info("PROJECT_ID not found, attempting to load from .env file")
            # Try current directory
            if os.path.exists(".env"):
                load_dotenv('/home/jupyter/gf_currensee/currensee')
                logger.info("Loaded environment from ./.env")
                self._project_id = os.getenv("PROJECT_ID")
            # Then try project root
            elif os.path.exists(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")):
                env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
                load_dotenv(env_path)
                logger.info(f"Loaded environment from {env_path}")
                self._project_id = os.getenv("PROJECT_ID")
        
        # If still not found, raise error
        if not self._project_id:
            raise ValueError("PROJECT_ID environment variable must be set")
        
        logger.info(f"SecretManager initialized with project_id: {self._project_id}")
        
        self._client = None
        self._secret_cache: Dict[str, str] = {}
        self._google_auth_available = True  # Flag to track if Google Auth is available

    @property
    def client(self):
        """Lazy initialization of the Secret Manager client."""
        if self._client is None:
            try:
                logger.info("Initializing Secret Manager client...")
                self._client = secretmanager.SecretManagerServiceClient()
                logger.info("Secret Manager client initialized successfully")
            except auth_exceptions.DefaultCredentialsError as e:
                logger.error(f"Google authentication error: {e}")
                logger.error("Could not authenticate with Google Cloud. Make sure your credentials are properly set up.")
                self._google_auth_available = False
                return None
            except Exception as e:
                logger.error(f"Error initializing Secret Manager client: {e}")
                self._google_auth_available = False
                return None
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
            logger.debug(f"Returning cached value for {secret_id}")
            return self._secret_cache[cache_key]
        
        secret_value = None
        
        # Skip Google Secret Manager if authentication failed previously
        if self._google_auth_available and self.client is not None:
            # First try Google Secret Manager
            try:
                logger.info(f"Attempting to retrieve {secret_id} from Google Secret Manager")
                name = f"projects/{self._project_id}/secrets/{secret_id}/versions/{version_id}"
                response = self.client.access_secret_version(request={"name": name})
                secret_value = response.payload.data.decode("UTF-8")
                logger.info(f"Successfully retrieved {secret_id} from Google Secret Manager")
            except Exception as e:
                logger.warning(f"Error accessing secret {secret_id} from Secret Manager: {e}")
                # Mark Google Auth as unavailable for certain errors
                if "PERMISSION_DENIED" in str(e) or "UNAUTHENTICATED" in str(e):
                    logger.error("Authentication issue with Google Secret Manager. Disabling for this session.")
                    self._google_auth_available = False
        else:
            logger.warning(f"Skipping Google Secret Manager for {secret_id} due to previous auth failures")
            
        # Fall back to environment variables if Google Secret Manager failed
        if secret_value is None:
            logger.info(f"Falling back to environment variables for {secret_id}")
            
            # Only load environment variables if we need to fall back
            load_dotenv()
            
            secret_value = os.getenv(secret_id)
            if secret_value is not None:
                logger.info(f"Found {secret_id} in environment variables")
            else:
                logger.warning(f"Secret {secret_id} not found in environment variables")
                return None
        
        # Cache the result
        self._secret_cache[cache_key] = secret_value
        return secret_value
    
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
