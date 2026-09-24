"""HTTP contract tests for Stage 1's read-only scheme detail endpoint."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from yojanamitra.api.routes.schemes import get_db_session
from yojanamitra.db.base import Base
from yojanamitra.db.session import create_database_engine
from yojanamitra.models import Scheme, Source
from yojanamitra.models.enums import SourceTier, SourceType


@pytest.fixture
def scheme_client(test_app: FastAPI, tmp_path: Path) -> Iterator[TestClient]:
    """Serve HTTP tests with an isolated sample database, never real scheme data."""

    engine: Engine = create_database_engine(f"sqlite:///{tmp_path / 'api.db'}")
    Base.metadata.create_all(engine)
    with Session(engine) as session, session.begin():
        session.add(Scheme(id="stage1-demo-scheme", name="Synthetic Test Scheme", category="test"))
        session.add(Source(
            scheme_id="stage1-demo-scheme", title="Synthetic source",
            url="https://example.org/test",
            authority="Local tests", source_type=SourceType.OTHER, tier=SourceTier.CONTEXT_ONLY
        ))
    factory = sessionmaker(engine, expire_on_commit=False)

    def provide_test_session() -> Iterator[Session]:
        """Override production database access with the isolated test engine."""

        with factory() as session:
            yield session

    test_app.dependency_overrides[get_db_session] = provide_test_session
    try:
        with TestClient(test_app) as test_client:
            yield test_client
    finally:
        test_app.dependency_overrides.clear()
        engine.dispose()


def test_get_scheme_and_its_sources(scheme_client: TestClient) -> None:
    """Return only validated metadata; never invent eligibility or benefit data."""

    response = scheme_client.get("/api/v1/schemes/stage1-demo-scheme")
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "stage1-demo-scheme"
    assert payload["status"] == "unknown"
    assert payload["sources"][0]["is_official"] is False
    assert payload["sources"][0]["url"] == "https://example.org/test"
    assert "eligible" not in payload


def test_scheme_not_found(scheme_client: TestClient) -> None:
    """Return a stable 404 for IDs absent from the structured registry."""

    response = scheme_client.get("/api/v1/schemes/nonexistent")
    assert response.status_code == 404
    assert response.json() == {"detail": "Scheme not found"}


def test_scheme_id_validation(scheme_client: TestClient) -> None:
    """Reject malformed IDs without constructing raw database queries."""

    response = scheme_client.get("/api/v1/schemes/INVALID_ID")
    assert response.status_code == 422
