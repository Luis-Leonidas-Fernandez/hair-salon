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


def test_settings_calendar_configuration() -> None:
    """Verify salon metadata and calendar feed settings defaults."""
    settings = Settings(
        database_url="postgresql+asyncpg://test:test@localhost:5432/afterlook_test",
    )
    assert settings.salon_name == "After Look"
    assert settings.salon_address == "Avenida Vélez Sarsfield 854"
    assert settings.salon_timezone == "America/Argentina/Buenos_Aires"
    assert settings.calendar_feed_ttl_minutes == 60


def test_settings_calendar_configuration_overrides(monkeypatch) -> None:
    """Verify salon metadata can be customized from environment variables."""
    monkeypatch.setenv("SALON_NAME", "After Look Nueva Córdoba")
    monkeypatch.setenv("SALON_ADDRESS", "Bv. Chacabuco 123")
    monkeypatch.setenv("SALON_TIMEZONE", "America/Argentina/Cordoba")
    monkeypatch.setenv("CALENDAR_FEED_TTL_MINUTES", "30")

    settings = Settings(
        database_url="postgresql+asyncpg://test:test@localhost:5432/afterlook_test",
    )
    assert settings.salon_name == "After Look Nueva Córdoba"
    assert settings.salon_address == "Bv. Chacabuco 123"
    assert settings.salon_timezone == "America/Argentina/Cordoba"
    assert settings.calendar_feed_ttl_minutes == 30
