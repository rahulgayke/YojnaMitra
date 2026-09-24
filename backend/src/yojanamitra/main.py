"""FastAPI application factory and default application instance."""

from fastapi import FastAPI

from yojanamitra.api.router import api_router
from yojanamitra.core.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create a configured FastAPI application for runtime or tests."""

    resolved_settings = settings or get_settings()
    application = FastAPI(
        title=resolved_settings.app_name,
        version="0.0.1",
        debug=resolved_settings.debug,
    )
    application.state.settings = resolved_settings
    application.include_router(
        api_router,
        prefix=f"/api/{resolved_settings.api_version}",
    )
    return application


app = create_app()
