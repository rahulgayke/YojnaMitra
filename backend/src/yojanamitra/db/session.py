"""Construct database connections and yield short-lived request sessions."""

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from yojanamitra.core.config import get_settings


def create_database_engine(database_url: str) -> Engine:
    """Create one SQLAlchemy engine and enable SQLite foreign-key checks."""

    engine = create_engine(database_url, pool_pre_ping=True)
    if engine.dialect.name == "sqlite":

        @event.listens_for(engine, "connect")
        def enable_foreign_keys(connection: object, connection_record: object) -> None:
            """Enable SQLite referential integrity for every new connection."""

            # SQLite does not enforce FK constraints unless explicitly enabled.
            cursor = connection.cursor()  # type: ignore[attr-defined]
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


@lru_cache
def get_engine() -> Engine:
    """Reuse the configured engine instead of rebuilding its pool per request."""

    return create_database_engine(get_settings().database_url)


def get_db_session() -> Iterator[Session]:
    """Yield a request-scoped session and always release its connection."""

    session_factory = sessionmaker(bind=get_engine(), expire_on_commit=False)
    with session_factory() as session:
        yield session
