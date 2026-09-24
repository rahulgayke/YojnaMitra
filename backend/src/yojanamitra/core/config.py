"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Store runtime settings that may vary between local and hosted environments."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="YOJANAMITRA_",
        extra="ignore",
    )

    app_name: str = "YojanaMitra API"
    environment: Literal["local", "test", "development", "staging", "production"] = "local"
    api_version: str = "v1"
    debug: bool = False
    # Local SQLite keeps this stage testable without a database server.
    database_url: str = "sqlite:///./yojanamitra.db"


@lru_cache
def get_settings() -> Settings:
    """Return one cached settings object for the current process."""

    return Settings()
