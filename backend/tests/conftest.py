"""Shared test fixtures for the Stage 0 backend."""

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from yojanamitra.core.config import Settings
from yojanamitra.main import create_app


@pytest.fixture
def test_app() -> FastAPI:
    """Create an application configured explicitly for deterministic tests."""

    return create_app(
        Settings(
            environment="test",
            api_version="v1",
            debug=False,
        )
    )


@pytest.fixture
def client(test_app: FastAPI) -> Iterator[TestClient]:
    """Yield a synchronous HTTP client for exercising the FastAPI application."""

    with TestClient(test_app) as test_client:
        yield test_client
