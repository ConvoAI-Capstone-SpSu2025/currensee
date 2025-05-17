from enum import StrEnum
from json import loads
from typing import Annotated, Any, Optional
import os

from dotenv import find_dotenv, load_dotenv
from pydantic import (
    BeforeValidator,
    Field,
    field_serializer,
    HttpUrl,
    SecretStr,
    TypeAdapter,
    computed_field,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

from currensee.schema.models import (
    AllModelEnum,
    FakeModelName,
    GoogleModelName,
    Provider
)

# Try to import the secrets module
# We use a try-except to allow the settings module to work even if the secrets module isn't available
try:
    from currensee.core.secrets import get_secret, get_secret_str
    HAS_SECRET_MANAGER = True
except ImportError:
    HAS_SECRET_MANAGER = False

# Load environment variables for fallback
load_dotenv()


class DatabaseType(StrEnum):
    SQLITE = "sqlite"
    POSTGRES = "postgres"


def check_str_is_http(x: str) -> str:
    http_url_adapter = TypeAdapter(HttpUrl)
    return str(http_url_adapter.validate_python(x))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
        validate_default=False,
    )
    MODE: str | None = None

    HOST: str = "0.0.0.0"
    PORT: int = 8080

    AUTH_SECRET: SecretStr | None = None

    GOOGLE_API_KEY: SecretStr | None = None
    USE_FAKE_MODEL: bool = False

    # If DEFAULT_MODEL is None, it will be set in model_post_init
    DEFAULT_MODEL: AllModelEnum | None = GoogleModelName.GEMINI_15_FLASH  # type: ignore[assignment]
    AVAILABLE_MODELS: set[AllModelEnum] = set()  # type: ignore[assignment]

    OPENWEATHERMAP_API_KEY: SecretStr | None = None
    
    # Serper API for search functionality
    SERPER_API_KEY: SecretStr | None = None

    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_PROJECT: str = "default"
    LANGCHAIN_ENDPOINT: Annotated[str, BeforeValidator(check_str_is_http)] = (
        "https://api.smith.langchain.com"
    )
    LANGCHAIN_API_KEY: SecretStr | None = None

    # Database Configuration
    DATABASE_TYPE: DatabaseType = (
        DatabaseType.SQLITE
    )  # Options: DatabaseType.SQLITE or DatabaseType.POSTGRES
    SQLITE_DB_PATH: str = "checkpoints.db"

    # PostgreSQL Configuration
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: SecretStr | None = None
    POSTGRES_HOST: str | None = None
    POSTGRES_PORT: int | None = None
    POSTGRES_DB: str | None = None
    POSTGRES_POOL_SIZE: int = Field(
        default=10, description="Maximum number of connections in the pool"
    )
    POSTGRES_MIN_SIZE: int = Field(
        default=3, description="Minimum number of connections in the pool"
    )
    POSTGRES_MAX_IDLE: int = Field(default=5, description="Maximum number of idle connections")

    @computed_field
    @property
    def POSTGRES_ENGINE_STR(self) -> str:
        return f'postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD.get_secret_value()}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}'

    def model_post_init(self, __context: Any) -> None:
        # Try to load SERPER_API_KEY from Secret Manager if available
        if HAS_SECRET_MANAGER:
            # Only set if not already provided through environment variables
            if self.SERPER_API_KEY is None:
                serper_key = get_secret_str('SERPER_API_KEY')
                if serper_key:
                    self.SERPER_API_KEY = serper_key
        
        # Continue with normal initialization
        api_keys = {
            Provider.GOOGLE: self.GOOGLE_API_KEY,
            Provider.FAKE: self.USE_FAKE_MODEL,
        }

        active_keys = [k for k, v in api_keys.items() if v]
        if not active_keys:
            raise ValueError("At least one LLM API key must be provided.")

        for provider in active_keys:
            if provider == Provider.GOOGLE:
                if self.DEFAULT_MODEL is None:
                    self.DEFAULT_MODEL = GoogleModelName.GEMINI_15_FLASH
                self.AVAILABLE_MODELS.update(set(GoogleModelName))
            elif provider == Provider.FAKE:
                if self.DEFAULT_MODEL is None:
                    self.DEFAULT_MODEL = FakeModelName.FAKE
                self.AVAILABLE_MODELS.update(set(FakeModelName))
            else:
                raise ValueError(f"Unknown provider: {provider}")

    @computed_field
    @property
    def BASE_URL(self) -> str:
        return f"http://{self.HOST}:{self.PORT}"



settings = Settings()