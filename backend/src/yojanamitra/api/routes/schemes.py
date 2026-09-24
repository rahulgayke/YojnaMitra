"""Read-only Stage 1 scheme endpoint backed by the registered domain model."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from yojanamitra.db.session import get_db_session
from yojanamitra.models.enums import SchemeStatus
from yojanamitra.repositories.schemes import get_scheme_by_id, list_official_schemes
from yojanamitra.schemas.domain import SchemeRead, Slug

router = APIRouter(prefix="/schemes", tags=["schemes"])
DatabaseSession = Annotated[Session, Depends(get_db_session)]


@router.get("/{scheme_id}", response_model=SchemeRead, summary="Get structured scheme metadata")
def read_scheme(scheme_id: Slug, session: DatabaseSession) -> SchemeRead:
    """Return a stored scheme and registered source metadata, or an HTTP 404."""

    scheme = get_scheme_by_id(session, scheme_id)
    if scheme is None:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return SchemeRead.model_validate(scheme)


@router.get("", response_model=list[SchemeRead], summary="List registered Central schemes")
def read_schemes(
    session: DatabaseSession,
    category: Annotated[str | None, Query(min_length=2, max_length=80)] = None,
    status: SchemeStatus | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[SchemeRead]:
    """Return paginated registry metadata without inferring operational scheme status."""

    schemes = list_official_schemes(
        session, category=category, status=status, limit=limit, offset=offset
    )
    return [SchemeRead.model_validate(scheme) for scheme in schemes]
