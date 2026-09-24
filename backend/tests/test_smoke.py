"""Stage 0 smoke tests."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from yojanamitra.main import create_app


def test_application_factory_returns_fastapi_app() -> None:
    """Verify that importing and constructing the backend application succeeds."""

    application = create_app()

    assert isinstance(application, FastAPI)


def test_health_endpoint_returns_expected_contract(client: TestClient) -> None:
    """Verify the health endpoint response used as the Stage 0 acceptance gate."""

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "yojanamitra-api",
        "environment": "test",
        "api_version": "v1",
    }
