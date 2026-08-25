import asyncio
import sys
import time

from yojanamitra.core.config import Settings
from yojanamitra.infrastructure.services import Services


async def main(timeout_seconds: int = 60) -> int:
    settings = Settings(postgres_host="localhost")
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        services = Services.from_settings(settings)
        try:
            await services.database.ping()
            await services.cache.ping()
            await services.vector_store.ping()
        except Exception:  # noqa: BLE001 - this is a generic service wait loop
            await services.close()
            await asyncio.sleep(2)
            continue
        await services.close()
        print("PostgreSQL, Redis and Qdrant are ready.")
        return 0

    print("Timed out waiting for infrastructure services.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
