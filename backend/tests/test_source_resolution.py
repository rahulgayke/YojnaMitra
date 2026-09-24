"""Ensure tests import the current Stage 0 checkout, not an older project."""

from pathlib import Path

import yojanamitra
from yojanamitra.core.config import Settings
from yojanamitra.main import create_app


def test_imports_resolve_to_this_checkout() -> None:
    """Detect accidental imports from a prior editable install of YojanaMitra."""

    expected_package = Path(__file__).resolve().parents[1] / "src" / "yojanamitra"
    actual_package = Path(yojanamitra.__file__).resolve().parent

    assert actual_package == expected_package.resolve(), (
        f"Imported YojanaMitra from {actual_package}, "
        f"but expected the current checkout at {expected_package}. "
        "Run tests with 'python -m pytest' from the repository root or backend directory."
    )


def test_factory_uses_explicit_settings() -> None:
    """Confirm a test-specific settings instance reaches the application factory."""

    settings = Settings(environment="test", api_version="v1", _env_file=None)
    application = create_app(settings)

    assert application.state.settings is settings
