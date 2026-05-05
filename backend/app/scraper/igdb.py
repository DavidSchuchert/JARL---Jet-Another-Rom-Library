"""IGDB API v4 implementation."""
import asyncio
import logging
import time
from typing import Optional

import httpx

from app.scraper.base import BaseScraper, ScraperResult

logger = logging.getLogger(__name__)


class IGDBScraper(BaseScraper):
    """
    IGDB (Twitch) API v4 scraper.
    
    Requires Client ID and Client Secret from Twitch Developer Portal.
    API docs: https://api-docs.igdb.com/
    """

    AUTH_URL = "https://id.twitch.tv/oauth2/token"
    BASE_URL = "https://api.igdb.com/v4"

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(30.0))
        return self._client

    async def login(self) -> bool:
        """Get OAuth2 access token from Twitch."""
        if not self.client_id or not self.client_secret:
            logger.warning("IGDB credentials missing")
            return False

        if self._access_token and time.time() < self._token_expires_at:
            return True

        client = await self._get_client()
        try:
            # Twitch requires these as POST body (form-data), not query params
            response = await client.post(
                self.AUTH_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials",
                },
            )
            if response.status_code != 200:
                logger.error(f"IGDB login failed with status {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            self._access_token = data["access_token"]
            self._token_expires_at = time.time() + data["expires_in"] - 60
            logger.info("IGDB authentication successful")
            return True
        except Exception as e:
            logger.error(f"IGDB login failed: {e}")
            return False

    async def is_authenticated(self) -> bool:
        return self._access_token is not None and time.time() < self._token_expires_at

    async def search(self, query: str, platform: Optional[str] = None) -> list[ScraperResult]:
        """Search for games by name."""
        if not await self.login():
            return []

        client = await self._get_client()
        
        # IGDB Query Language (Apex)
        body = f'search "{query}"; fields name, summary, first_release_date, cover.url, genres.name, involved_companies.company.name, involved_companies.publisher; limit 5;'
        
        # Add platform filter if possible (mapping needed, but let's try generic first)
        
        try:
            response = await client.post(
                f"{self.BASE_URL}/games",
                headers={
                    "Client-ID": self.client_id,
                    "Authorization": f"Bearer {self._access_token}",
                },
                content=body,
            )
            response.raise_for_status()
            games = response.json()
            
            results = []
            for game in games:
                results.append(self._parse_game(game))
            return results
        except Exception as e:
            logger.error(f"IGDB search failed: {e}")
            return []

    async def scrape(self, rom_hash: str, platform: str) -> ScraperResult:
        """IGDB doesn't support hash-based lookup directly for ROMs in the same way ScreenScraper does."""
        return ScraperResult(success=False, error="IGDB does not support hash lookup")

    def _parse_game(self, game: dict) -> ScraperResult:
        # Extract publisher and developer
        publisher = None
        developer = None
        if "involved_companies" in game:
            for ic in game["involved_companies"]:
                company_name = ic["company"]["name"]
                if ic.get("publisher"):
                    publisher = company_name
                if ic.get("developer"):
                    developer = company_name

        # Extract year
        year = None
        if "first_release_date" in game:
            # Unix timestamp
            ts = game["first_release_date"]
            year = time.gmtime(ts).tm_year

        # Cover URL
        cover_url = None
        if "cover" in game:
            url = game["cover"]["url"]
            if url.startswith("//"):
                url = "https:" + url
            # Change to big cover
            cover_url = url.replace("t_thumb", "t_cover_big")

        return ScraperResult(
            title=game.get("name"),
            description=game.get("summary"),
            year=year,
            publisher=publisher,
            developer=developer,
            genre=game.get("genres", [{}])[0].get("name") if game.get("genres") else None,
            cover_url=cover_url,
            success=True,
        )

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
