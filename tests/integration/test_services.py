import os

import pytest

from yojanamitra.core.config import Settings
from yojanamitra.infrastructure.services import Services

pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION") != "1",
    reason="set RUN_INTEGRATION=1 to run service integration tests",
)
async def test_postgres_redis_qdrant_are_reachable() -> None:
    settings = Settings(
        postgres_host=os.getenv("POSTGRES_HOST", "localhost"),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
    )
    services = Services.from_settings(settings)

    try:
        await services.database.ping()
        await services.cache.ping()
        await services.vector_store.ping()
    finally:
        await services.close()
