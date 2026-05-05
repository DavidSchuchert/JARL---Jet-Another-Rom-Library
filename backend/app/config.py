"""Application configuration using pydantic-settings."""
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration."""

    url: str = Field(default="sqlite+aiosqlite:///./jarl.db", description="Database URL")


class ScannerSettings(BaseSettings):
    """Scanner configuration."""

    roms_path: Path = Field(default=Path("/roms"), description="Path to ROMs directory")
    batch_size: int = Field(default=100, ge=1, description="Batch size for file processing")
    workers: int = Field(default=4, ge=1, description="Number of scanner workers")
    hash_size_limit_mb: int = Field(
        default=512,
        ge=0,
        description="Skip full-file hashes above this size in MiB. Use 0 to disable.",
    )
    file_timeout_seconds: int = Field(
        default=30,
        ge=1,
        description="Maximum time to spend processing one file before skipping it.",
    )


class ScraperSettings(BaseSettings):
    """Scraper configuration."""

    username: Optional[str] = Field(default=None, description="ScreenScraper username")
    password: Optional[str] = Field(default=None, description="ScreenScraper password")
    api_url: str = Field(
        default="https://www.screenscraper.fr/api2",
        description="ScreenScraper API URL",
    )
    rate_limit: float = Field(default=2.0, ge=0.1, description="Rate limit in seconds between requests")
    igdb_client_id: Optional[str] = Field(default=None, description="IGDB Client ID")
    igdb_client_secret: Optional[str] = Field(default=None, description="IGDB Client Secret")


class AuthSettings(BaseSettings):
    """Authentication configuration."""

    username: str = Field(default="admin", description="Admin username")
    password: str = Field(default="admin", description="Admin password")
    token_expire_minutes: int = Field(default=1440, description="Token expiration in minutes")


class AppSettings(BaseSettings):
...
    secret_key: str = Field(default="change-this-in-production", description="Secret key")

    auth: AuthSettings = Field(default_factory=AuthSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
...

    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:80"],
        description="Allowed CORS origins",
    )


@lru_cache
def get_settings() -> AppSettings:
    """Get cached application settings."""
    return AppSettings()
