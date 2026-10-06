"""Unit tests for centralized application configuration."""

from app.config.settings import Settings


def test_settings_exposes_runtime_configuration() -> None:
    """Application and database consumers receive explicit typed settings."""

    settings = Settings(
        app_name="Test After Look",
        app_version="9.9.9",
        database_url="postgresql+asyncpg://test:test@localhost:5432/afterlook_test",
        database_echo=True,
        database_pool_pre_ping=False,
        secret_key="test-secret",
        seed_admin_name="Admin",
        seed_admin_email="admin@example.com",
        seed_hairdresser_1_name="One",
        seed_hairdresser_1_email="one@example.com",
        seed_hairdresser_2_name="Two",
        seed_hairdresser_2_email="two@example.com",
    )

    assert settings.app_name == "Test After Look"
    assert settings.app_version == "9.9.9"
    assert settings.database_echo is True
    assert settings.database_pool_pre_ping is False


def test_settings_normalizes_postgres_url() -> None:
    """Normalize postgres:// to postgresql+asyncpg:// for cloud hosts."""
    settings = Settings(
        database_url="postgres://user:pass@render.com/db",
        secret_key="secret",
        seed_admin_name="A",
        seed_admin_email="a@a.com",
        seed_hairdresser_1_name="H1",
        seed_hairdresser_1_email="h1@a.com",
        seed_hairdresser_2_name="H2",
        seed_hairdresser_2_email="h2@a.com",
    )
    assert settings.database_url == "postgresql+asyncpg://user:pass@render.com/db"
