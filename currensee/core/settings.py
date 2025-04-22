from enum import StrEnum
from json import loads
from typing import Annotated, Any

from dotenv import find_dotenv
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

    # Simplify access of confidential data
    @field_serializer(
        "postgres_password",
        when_used="json",
        check_fields=False,
    )
    def dump_secret(self, v):
        return v.get_secret_value()
    
    @property
    def postgres(self) -> dict[str, str | int]:
        return {
            "host": self.POSTGRES_HOST,
            "port": self.POSTGRES_PORT,
            "user": self.POSTGRES_USER,
            "password": self.POSTGRES_PASSWORD.get_secret_value(),
            "database": self.POSTGRES_DB,
            "perform_setup": False,
        }

    @property
    def sqlalchemy(self) -> URL:
        sqlalchemy_dict = {
            "drivername": "postgresql+psycopg",
            "username": self.POSTGRES_USER,
            "password": self.POSTGRES_PASSWORD.get_secret_value(),
            "host": self.POSTGRES_HOST,
            "database": self.POSTGRES_DB,
            "port": self.POSTGRES_PORT,
        }
        return URL.create(**sqlalchemy_dict)

    def model_post_init(self, __context: Any) -> None:
        api_keys = {
            Provider.GOOGLE: self.GOOGLE_API_KEY,
            Provider.FAKE: self.USE_FAKE_MODEL,
        }

        active_keys = [k for k, v in api_keys.items() if v]
        if not active_keys:
            raise ValueError("At least one LLM API key must be provided.")

        for provider in active_keys:
            match provider:
                case Provider.GOOGLE:
                    if self.DEFAULT_MODEL is None:
                        self.DEFAULT_MODEL = GoogleModelName.GEMINI_15_FLASH
                    self.AVAILABLE_MODELS.update(set(GoogleModelName))
                case Provider.FAKE:
                    if self.DEFAULT_MODEL is None:
                        self.DEFAULT_MODEL = FakeModelName.FAKE
                    self.AVAILABLE_MODELS.update(set(FakeModelName))
     
                case _:
                    raise ValueError(f"Unknown provider: {provider}")

    @computed_field
    @property
    def BASE_URL(self) -> str:
        return f"http://{self.HOST}:{self.PORT}"

    def is_dev(self) -> bool:
        return self.MODE == "dev"


settings = Settings()