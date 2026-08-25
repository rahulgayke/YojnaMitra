from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from yojanamitra.api.routes.health import router as health_router
from yojanamitra.core.config import get_settings
from yojanamitra.core.logging import configure_logging
from yojanamitra.infrastructure.services import Services

settings = get_settings()
configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    services = Services.from_settings(settings)
    app.state.services = services
    try:
        yield
    finally:
        await services.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        debug=settings.app_debug,
        lifespan=lifespan,
    )
    app.include_router(health_router, prefix=settings.api_v1_prefix)

    @app.get("/", tags=["root"])
    async def root() -> dict[str, str]:
        return {"name": settings.app_name, "stage": "1", "status": "running"}

    return app


app = create_app()
