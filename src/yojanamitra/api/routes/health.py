import asyncio
from collections.abc import Awaitable
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from yojanamitra.api.dependencies import get_services
from yojanamitra.infrastructure.services import Services

router = APIRouter(prefix="/health", tags=["health"])


class LivenessResponse(BaseModel):
    status: Literal["ok"] = "ok"


class DependencyStatus(BaseModel):
    postgres: Literal["ok", "error"]
    redis: Literal["ok", "error"]
    qdrant: Literal["ok", "error"]


class ReadinessResponse(BaseModel):
    status: Literal["ok", "degraded"]
    dependencies: DependencyStatus


async def _check(coroutine: Awaitable[object]) -> bool:
    try:
        await asyncio.wait_for(coroutine, timeout=3.0)
    except Exception:  # noqa: BLE001 - health endpoint intentionally collapses dependency errors
        return False
    return True


@router.get("/live", response_model=LivenessResponse)
async def liveness() -> LivenessResponse:
    return LivenessResponse()


async def _readiness_payload(services: Services) -> ReadinessResponse:
    postgres_ok, redis_ok, qdrant_ok = await asyncio.gather(
        _check(services.database.ping()),
        _check(services.cache.ping()),
        _check(services.vector_store.ping()),
    )
    dependencies = DependencyStatus(
        postgres="ok" if postgres_ok else "error",
        redis="ok" if redis_ok else "error",
        qdrant="ok" if qdrant_ok else "error",
    )
    all_ok = postgres_ok and redis_ok and qdrant_ok
    return ReadinessResponse(status="ok" if all_ok else "degraded", dependencies=dependencies)


@router.get("/ready", response_model=ReadinessResponse)
async def readiness(services: Services = Depends(get_services)) -> ReadinessResponse:
    payload = await _readiness_payload(services)
    if payload.status != "ok":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=payload.model_dump(),
        )
    return payload


@router.get("", response_model=ReadinessResponse)
async def health(services: Services = Depends(get_services)) -> ReadinessResponse:
    return await readiness(services)
