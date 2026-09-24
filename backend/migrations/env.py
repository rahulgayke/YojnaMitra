"""Run Alembic migrations against the configured Stage 1 database."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection, create_engine, pool

import yojanamitra.models  # noqa: F401  # Register tables before autogeneration.
from yojanamitra.core.config import get_settings
from yojanamitra.db.base import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Generate migrations without opening a database connection."""

    context.configure(
        url=get_settings().database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Apply migrations to a provided test connection or configured database."""

    connection = config.attributes.get("connection")
    if isinstance(connection, Connection):
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
        return

    engine = create_engine(get_settings().database_url, poolclass=pool.NullPool)
    with engine.connect() as live_connection:
        context.configure(connection=live_connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
