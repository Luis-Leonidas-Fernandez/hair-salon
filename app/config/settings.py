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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Build settings once per process from the configured environment."""

    return Settings()
