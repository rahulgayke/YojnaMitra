from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from tests.conftest import FakeServices
from yojanamitra.main import create_app


async def test_readiness_returns_503_when_dependencies_fail() -> None:
    app = create_app()

    @asynccontextmanager
    async def failing_lifespan(test_app: FastAPI) -> AsyncIterator[None]:
        test_app.state.services = FakeServices(healthy=False)
        yield

    app.router.lifespan_context = failing_lifespan

    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/health/ready")

    assert response.status_code == 503
    detail = response.json()["detail"]
    assert detail["status"] == "degraded"
    assert set(detail["dependencies"].values()) == {"error"}
