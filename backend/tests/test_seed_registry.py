"""Safety and integrity tests for the Stage 2 curated source registry."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from datetime import date, timedelta
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session, sessionmaker

import yojanamitra.cli as cli
from yojanamitra.api.routes.schemes import get_db_session
from yojanamitra.core.config import Settings
from yojanamitra.db.base import Base
from yojanamitra.db.session import create_database_engine
from yojanamitra.models import Document, EligibilityRule, Scheme, Source
from yojanamitra.models.enums import SchemeStatus
from yojanamitra.services.seed_loader import SeedConflictError, seed_registry
from yojanamitra.services.seed_registry import DEFAULT_SEED_PATH, load_manifest, manifest_summary


@pytest.fixture
def seed_engine(tmp_path: Path) -> Iterator[Engine]:
    """Create and dispose of an isolated SQLite database for registry tests."""

    engine = create_database_engine(f"sqlite:///{tmp_path / 'official-registry.db'}")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


def _manifest_copy(tmp_path: Path, change: Callable[[list[dict[str, object]]], None]) -> Path:
    """Create a writable manifest copy and apply one deliberately invalid edit."""

    records = json.loads(DEFAULT_SEED_PATH.read_text(encoding="utf-8"))
    change(records)
    path = tmp_path / "changed.json"
    path.write_text(json.dumps(records), encoding="utf-8")
    return path


def test_seed_has_20_identified_schemes_with_source_review_scope() -> None:
    """Verify the dataset's declared coverage, not its unreviewed eligibility rules."""

    manifest = load_manifest()
    assert manifest_summary(manifest) == {
        "schemes": 20, "sources": 21, "primary_source_schemes": 20,
        "rules": 0, "publish_ready": 0,
    }
    assert all(entry.scheme.status == SchemeStatus.UNKNOWN for entry in manifest.entries)
    assert all(entry.scheme.last_verified_at is None for entry in manifest.entries)
    assert all(not entry.eligibility_rules for entry in manifest.entries)
    assert all(
        source.verification_scope == "government_source_identity_only"
        and source.content_review_status == "not_parsed"
        for entry in manifest.entries for source in entry.sources
    )


@pytest.mark.parametrize(
    "unsafe_url",
    [
        "https://pmkisan.gov.in.evil.example/test",
        "http://pmkisan.gov.in/",
        "https://some-shop.co.in/not-official",
        "https://myscheme.gov.in/",
        "https://user:secret@pmkisan.gov.in/",
    ],
)
def test_seed_rejects_unapproved_urls(tmp_path: Path, unsafe_url: str) -> None:
    """Prevent unauthorized, insecure and deceptive source addresses entering the corpus."""

    def change(records: list[dict[str, object]]) -> None:
        """Replace a curated URL with one unsafe value."""

        records[0]["sources"][0]["url"] = unsafe_url

    with pytest.raises(ValueError, match="Invalid seed manifest"):
        load_manifest(_manifest_copy(tmp_path, change))


def test_duplicate_scheme_and_source_urls_are_rejected(tmp_path: Path) -> None:
    """Detect repeated scheme IDs and source URLs before database import."""

    def duplicate_scheme(records: list[dict[str, object]]) -> None:
        """Make two entries claim the same public scheme ID."""

        records[1]["scheme"]["id"] = records[0]["scheme"]["id"]

    def duplicate_source(records: list[dict[str, object]]) -> None:
        """Make two separate sources point to the same URL."""

        records[1]["sources"][0]["url"] = records[0]["sources"][0]["url"]

    with pytest.raises(ValueError, match="Duplicate scheme ID"):
        load_manifest(_manifest_copy(tmp_path, duplicate_scheme))
    with pytest.raises(ValueError, match="Duplicate official source URL"):
        load_manifest(_manifest_copy(tmp_path, duplicate_source))


def test_future_review_or_unverified_active_claim_is_rejected(tmp_path: Path) -> None:
    """Disallow future timestamps and unsupported operational/publishing claims."""

    def future_date(records: list[dict[str, object]]) -> None:
        """Make registry review appear to occur tomorrow in India."""

        records[0]["sources"][0]["reviewed_on"] = (date.today() + timedelta(days=3)).isoformat()

    def active_status(records: list[dict[str, object]]) -> None:
        """Pretend that a registry-only identity check verified scheme operation."""

        records[0]["scheme"]["status"] = "active"

    def publishing(records: list[dict[str, object]]) -> None:
        """Pretend an unreviewed seed scheme is ready for public advice."""

        records[0]["scheme"]["metadata"]["publish_ready"] = True

    for change in (future_date, active_status, publishing):
        with pytest.raises(ValueError, match="Invalid seed manifest"):
            load_manifest(_manifest_copy(tmp_path, change))


def test_seed_import_is_idempotent_and_keeps_unknowns(seed_engine: Engine) -> None:
    """Create 20/21 rows once without fabricating documents, rules or status."""

    manifest = load_manifest()
    with Session(seed_engine) as session, session.begin():
        first = seed_registry(session, manifest)
    with Session(seed_engine) as session, session.begin():
        second = seed_registry(session, manifest)
    assert first == {"schemes_created": 20, "sources_created": 21, "unchanged_schemes": 0}
    assert second == {"schemes_created": 0, "sources_created": 0, "unchanged_schemes": 20}
    with Session(seed_engine) as session:
        assert session.scalar(select(func.count()).select_from(Scheme)) == 20
        assert session.scalar(select(func.count()).select_from(Source)) == 21
        assert session.scalar(select(func.count()).select_from(Document)) == 0
        assert session.scalar(select(func.count()).select_from(EligibilityRule)) == 0
        assert set(session.scalars(select(Scheme.status)).all()) == {SchemeStatus.UNKNOWN}
        source = session.scalars(select(Source)).first()
        assert source is not None
        assert source.extra_metadata["verification_scope"] == "government_source_identity_only"
        assert source.extra_metadata["timestamp_precision"] == "calendar_day_ist"


def test_import_conflict_rolls_back_all_pending_rows(seed_engine: Engine) -> None:
    """Keep an existing conflicting record and prevent partial imports."""

    with Session(seed_engine) as session, session.begin():
        session.add(Scheme(id="pm-jay", name="Unrelated local record", category="test"))
    with Session(seed_engine) as session:
        with pytest.raises(SeedConflictError):
            with session.begin():
                seed_registry(session, load_manifest())
    with Session(seed_engine) as session:
        assert session.scalar(select(func.count()).select_from(Scheme)) == 1
        assert session.scalar(select(func.count()).select_from(Source)) == 0
        assert session.get(Scheme, "pm-jay").name == "Unrelated local record"


def test_source_review_conflict_is_rejected(seed_engine: Engine) -> None:
    """Never overwrite changed source permissions or provenance during a rerun."""

    manifest = load_manifest()
    with Session(seed_engine) as session, session.begin():
        seed_registry(session, manifest)
    with Session(seed_engine) as session, session.begin():
        source = session.scalars(select(Source)).first()
        assert source is not None
        source.extra_metadata = {**source.extra_metadata, "acquisition_policy": "altered"}
    with Session(seed_engine) as session:
        with pytest.raises(SeedConflictError, match="Existing source differs"):
            with session.begin():
                seed_registry(session, manifest)


def test_seed_cli_dry_run_never_opens_database(monkeypatch: pytest.MonkeyPatch) -> None:
    """Let citizens' source data be inspected without any database configuration."""

    def database_forbidden() -> None:
        """Fail if validation unexpectedly creates a database engine."""

        raise AssertionError("Dry run must not use database")

    monkeypatch.setattr(cli, "get_engine", database_forbidden)
    assert cli.validate_seed()["schemes"] == 20
    assert cli.seed_official(apply=False) is None


def test_seed_cli_rejects_production_import(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep an explicit write request from importing into a production setting."""

    def production_settings() -> Settings:
        """Return a nonlocal environment without connecting anywhere."""

        return Settings(environment="production", _env_file=None)

    monkeypatch.setattr(cli, "get_settings", production_settings)
    with pytest.raises(RuntimeError, match="disabled"):
        cli.seed_official(apply=True)


def test_read_only_api_lists_and_resolves_reviewed_sources(
    test_app: FastAPI, seed_engine: Engine
) -> None:
    """Exercise listing, filtering, source provenance and synthetic-record exclusion."""

    with Session(seed_engine) as session, session.begin():
        seed_registry(session, load_manifest())
        session.add(Scheme(id="stage1-demo-scheme", name="Synthetic", category="test_only"))
    session_factory = sessionmaker(seed_engine)

    def test_session() -> Iterator[Session]:
        """Supply the local seeded SQLite session for endpoint tests."""

        with session_factory() as session:
            yield session

    test_app.dependency_overrides[get_db_session] = test_session
    try:
        with TestClient(test_app) as client:
            listing = client.get("/api/v1/schemes")
            assert listing.status_code == 200
            assert len(listing.json()) == 20
            assert all(s["id"] != "stage1-demo-scheme" for s in listing.json())
            subset = client.get("/api/v1/schemes", params={"category": "education"})
            assert subset.status_code == 200
            assert {s["id"] for s in subset.json()} == {
                "nmmss", "pm-usp-csss", "pm-vidyalaxmi"
            }
            assert client.get("/api/v1/schemes", params={"status": "active"}).json() == []
            detail = client.get("/api/v1/schemes/pm-kisan")
            assert detail.status_code == 200
            assert detail.json()["status"] == "unknown"
            assert detail.json()["metadata"]["publish_ready"] is False
            source_id = detail.json()["sources"][0]["id"]
            source = client.get(f"/api/v1/sources/{source_id}")
            assert source.status_code == 200
            assert source.json()["metadata"]["content_review_status"] == "not_parsed"
            missing_source = "/api/v1/sources/00000000-0000-4000-8000-000000000099"
            assert client.get(missing_source).status_code == 404
            assert client.get("/api/v1/sources/not-uuid").status_code == 422
            assert client.get("/api/v1/schemes", params={"limit": 101}).status_code == 422
    finally:
        test_app.dependency_overrides.clear()
