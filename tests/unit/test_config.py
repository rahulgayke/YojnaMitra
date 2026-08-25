from yojanamitra.core.config import Settings


def test_database_url_is_assembled_from_components() -> None:
    settings = Settings(
        postgres_user="user",
        postgres_password="pass",
        postgres_host="db",
        postgres_port=5432,
        postgres_db="app",
    )

    assert settings.database_url == "postgresql+asyncpg://user:pass@db:5432/app"
