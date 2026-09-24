"""Health endpoint used for local smoke tests and future runtime checks."""

from fastapi import APIRouter, Request

from yojanamitra.schemas.common import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse, summary="Check API health")
async def get_health(request: Request) -> HealthResponse:
    """Return a small deterministic response proving that the API is running."""

    settings = request.app.state.settings
    return HealthResponse(
        service="yojanamitra-api",
        environment=settings.environment,
        api_version=settings.api_version,
    )
