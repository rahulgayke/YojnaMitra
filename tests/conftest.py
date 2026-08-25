from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from yojanamitra.main import create_app


class HealthyDependency:
    async def ping(self) -> None:
        return None


class FailingDependency:
    async def ping(self) -> None:
        raise ConnectionError("unavailable")


class FakeServices:
    def __init__(self, *, healthy: bool = True) -> None:
        dependency: Any = HealthyDependency() if healthy else FailingDependency()
        self.database = dependency
        self.cache = dependency
        self.vector_store = dependency

    async def close(self) -> None:
        return None


@pytest.fixture
def app() -> FastAPI:
    application = create_app()

    @asynccontextmanager
    async def test_lifespan(test_app: FastAPI) -> AsyncIterator[None]:
        test_app.state.services = FakeServices(healthy=True)
        yield

    application.router.lifespan_context = test_lifespan
    return application


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as async_client:
            yield async_client
