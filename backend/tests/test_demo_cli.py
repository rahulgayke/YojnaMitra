"""Local fixture CLI regression checks for safe, repeatable manual testing."""

from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

import yojanamitra.cli as cli
from yojanamitra.core.config import Settings
from yojanamitra.db.base import Base
from yojanamitra.db.session import create_database_engine
from yojanamitra.models import Scheme, Source


def test_demo_seed_is_idempotent_and_unofficial(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Create only the synthetic fixture once and keep its source unverified."""

    database_url = f"sqlite:///{tmp_path / 'demo.db'}"
    engine = create_database_engine(database_url)
    Base.metadata.create_all(engine)

    def test_settings() -> Settings:
        """Return an isolated local configuration for the demo CLI."""

        return Settings(environment="local", database_url=database_url, _env_file=None)

    def test_engine():
        """Point the seed function to the temporary test database."""

        return engine

    monkeypatch.setattr(cli, "get_settings", test_settings)
    monkeypatch.setattr(cli, "get_engine", test_engine)
    cli.seed_demo()
    cli.seed_demo()

    with Session(engine) as session:
        schemes = session.scalars(select(Scheme)).all()
        sources = session.scalars(select(Source)).all()
        assert len(schemes) == len(sources) == 1
        assert schemes[0].extra_metadata["demo_only"] is True
        assert sources[0].is_official is False
    engine.dispose()


def test_demo_seed_rejects_nonlocal_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prevent synthetic government-like fixtures from entering production settings."""

    def unsafe_settings() -> Settings:
        """Provide nonlocal settings without connecting to a production database."""

        return Settings(environment="production", _env_file=None)

    monkeypatch.setattr(cli, "get_settings", unsafe_settings)
    with pytest.raises(RuntimeError, match="local SQLite"):
        cli.seed_demo()
