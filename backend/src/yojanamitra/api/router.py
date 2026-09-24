"""Top-level API router composition."""

from fastapi import APIRouter

from yojanamitra.api.routes.health import router as health_router
from yojanamitra.api.routes.schemes import router as schemes_router
from yojanamitra.api.routes.sources import router as sources_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(schemes_router)
api_router.include_router(sources_router)
