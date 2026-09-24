"""Read-only Stage 1 scheme endpoint backed by the registered domain model."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from yojanamitra.db.session import get_db_session
from yojanamitra.repositories.schemes import get_scheme_by_id
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
