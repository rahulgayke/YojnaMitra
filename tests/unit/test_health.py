from httpx import AsyncClient


async def test_liveness(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_readiness_when_dependencies_are_healthy(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "dependencies": {
            "postgres": "ok",
            "redis": "ok",
            "qdrant": "ok",
        },
    }
