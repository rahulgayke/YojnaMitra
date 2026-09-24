"""Read-only official-source lookup with explicit provenance metadata."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from yojanamitra.db.session import get_db_session
from yojanamitra.models import Source
from yojanamitra.schemas.domain import SourceRead

router = APIRouter(prefix="/sources", tags=["sources"])
DatabaseSession = Annotated[Session, Depends(get_db_session)]


@router.get("/{source_id}", response_model=SourceRead, summary="Get registered official source")
def read_source(source_id: UUID, session: DatabaseSession) -> SourceRead:
    """Retrieve a source record or return an explicit HTTP 404."""

    source = session.get(Source, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return SourceRead.model_validate(source)
