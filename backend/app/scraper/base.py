"""Base scraper interface for ROM metadata sources."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ScraperResult:
    """Result from a scraping operation."""
    title: Optional[str] = None
    description: Optional[str] = None
    year: Optional[int] = None
    release_date: Optional[str] = None  # YYYY-MM-DD
    publisher: Optional[str] = None
    developer: Optional[str] = None
    genre: Optional[str] = None
    players: Optional[str | int] = None
    region: Optional[str] = None
    languages: Optional[list[str]] = None
    rating: Optional[float] = None  # 0-100 scale
    cover_url: Optional[str] = None
    screenshot_urls: Optional[list[str]] = None
    igdb_id: Optional[int] = None
    screenscraper_id: Optional[int] = None
    success: bool = False
    error: Optional[str] = None


class BaseScraper(ABC):
    """Abstract base class for ROM metadata scrapers."""

    @abstractmethod
    async def search(self, query: str, platform: Optional[str] = None) -> list[ScraperResult]:
        """
        Search for ROM metadata.

        Args:
            query: Search query (usually ROM title).
            platform: Optional platform slug to narrow search.

        Returns:
            List of matching results.
        """
        pass

    @abstractmethod
    async def scrape(self, rom_hash: str, platform: str) -> ScraperResult:
        """
        Scrape metadata for a specific ROM by hash.

        Args:
            rom_hash: ROM file hash (usually SHA1).
            platform: Platform slug.

        Returns:
            Scraper result with metadata or error.
        """
        pass

    @abstractmethod
    async def login(self) -> bool:
        """
        Authenticate with the scraper service.

        Returns:
            True if login was successful.
        """
        pass

    @abstractmethod
    async def is_authenticated(self) -> bool:
        """
        Check if currently authenticated.

        Returns:
            True if authenticated.
        """
        pass
