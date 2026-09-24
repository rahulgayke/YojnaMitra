"""Read/write primitives for scheme records; no eligibility or RAG logic."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from yojanamitra.models import Scheme, Source


def get_scheme_by_id(session: Session, scheme_id: str) -> Scheme | None:
    """Fetch a scheme and its registered sources without issuing N+1 queries."""

    statement = select(Scheme).options(selectinload(Scheme.sources)).where(Scheme.id == scheme_id)
    return session.scalar(statement)


def add_scheme(session: Session, scheme: Scheme) -> Scheme:
    """Persist a validated scheme within the caller's transaction."""

    session.add(scheme)
    session.flush()
    return scheme


def add_source(session: Session, source: Source) -> Source:
    """Persist a source linked to an existing scheme in the same transaction."""

    session.add(source)
    session.flush()
    return source
