"""Application settings loaded from the environment."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Provide typed configuration without exposing environment reads to callers."""

    app_name: str = "After Look"
    app_version: str = "0.1.0"
    environment: str = "development"
    database_url: str

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        """Ensure connection string uses asyncpg driver required by SQLAlchemy."""
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v
    database_echo: bool = False
    database_pool_pre_ping: bool = True
    secret_key: str = "afterlook-default-secret-key-32-chars-long-secure!"
    seed_admin_name: str = "Sergio"
    seed_admin_email: str = "admin@afterlook.com"
    seed_hairdresser_1_name: str = "Peluquero 1"
    seed_hairdresser_1_email: str = "peluquero1@afterlook.com"
    seed_hairdresser_2_name: str = "Peluquero 2"
    seed_hairdresser_2_email: str = "peluquero2@afterlook.com"
    seed_hairdresser_3_name: str = "Peluquero 3"
    seed_hairdresser_3_email: str = "peluquero3@afterlook.com"
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str | None = None
    session_cookie_name: str = "afterlook_session"
    session_ttl_minutes: int = 480

    @property
    def google_oauth_enabled(self) -> bool:
        """Verify if Google OAuth has all required credentials configured."""
        return bool(
            self.google_client_id
            and self.google_client_secret
            and self.google_redirect_uri
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Build settings once per process from the configured environment."""

    return Settings()
