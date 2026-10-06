"""Application settings loaded from the environment."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Provide typed configuration without exposing environment reads to callers."""

    app_name: str = "After Look"
    app_version: str = "0.1.0"
    environment: str = "development"
    database_url: str
    database_echo: bool = False
    database_pool_pre_ping: bool = True
    secret_key: str
    seed_admin_name: str
    seed_admin_email: str
    seed_hairdresser_1_name: str
    seed_hairdresser_1_email: str
    seed_hairdresser_2_name: str
    seed_hairdresser_2_email: str
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
