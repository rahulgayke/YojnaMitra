from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "YojanaMitra API"
    app_env: str = "development"
    app_debug: bool = False
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"

    postgres_db: str = "yojanamitra"
    postgres_user: str = "yojanamitra"
    postgres_password: str = "yojanamitra_dev"
    postgres_host: str = "localhost"
    postgres_port: int = Field(default=5432, ge=1, le=65535)

    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"

    @property
    def database_url(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
