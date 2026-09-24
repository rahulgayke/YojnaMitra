"""Tests for environment-driven backend configuration."""

from yojanamitra.core.config import Settings


def test_settings_have_safe_local_defaults() -> None:
    """Verify that Stage 0 starts locally without requiring a committed env file."""

    settings = Settings(_env_file=None)

    assert settings.app_name == "YojanaMitra API"
    assert settings.environment == "local"
    assert settings.api_version == "v1"
    assert settings.debug is False
