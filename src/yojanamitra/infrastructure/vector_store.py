from qdrant_client import AsyncQdrantClient


class VectorStore:
    """Owns the Qdrant client and its health check."""

    def __init__(self, qdrant_url: str) -> None:
        self._client = AsyncQdrantClient(url=qdrant_url)

    @property
    def client(self) -> AsyncQdrantClient:
        return self._client

    async def ping(self) -> None:
        await self._client.get_collections()

    async def close(self) -> None:
        await self._client.close()
