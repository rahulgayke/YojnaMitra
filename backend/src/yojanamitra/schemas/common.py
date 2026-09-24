"""Shared API response and error schemas."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Describe the minimal service health information exposed by the API."""

    status: Literal["ok"] = "ok"
    service: str
    environment: str
    api_version: str


class ErrorDetail(BaseModel):
    """Describe one machine-readable API error."""

    code: str = Field(description="Stable application-level error code.")
    message: str = Field(description="Human-readable error message.")
    details: dict[str, Any] | None = Field(
        default=None,
        description="Optional structured context that is safe to return to the caller.",
    )


class ErrorResponse(BaseModel):
    """Provide a consistent top-level envelope for future API errors."""

    error: ErrorDetail
