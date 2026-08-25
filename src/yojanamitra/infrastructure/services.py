import asyncio
from dataclasses import dataclass

from yojanamitra.core.config import Settings
from yojanamitra.infrastructure.cache import Cache
from yojanamitra.infrastructure.database import Database
from yojanamitra.infrastructure.vector_store import VectorStore


@dataclass(slots=True)
class Services:
    database: Database
    cache: Cache
    vector_store: VectorStore

    @classmethod
    def from_settings(cls, settings: Settings) -> "Services":
        return cls(
            database=Database(settings.database_url),
            cache=Cache(settings.redis_url),
            vector_store=VectorStore(settings.qdrant_url),
        )

    async def close(self) -> None:
        await asyncio.gather(
            self.vector_store.close(),
            self.cache.close(),
            self.database.close(),
        )
