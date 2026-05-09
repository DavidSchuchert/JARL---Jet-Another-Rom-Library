"""ScreenScraper.fr API v2 implementation."""
import asyncio
import logging
from typing import Optional

import httpx

from app.scraper.base import BaseScraper, ScraperResult

logger = logging.getLogger(__name__)

# ScreenScraper API base URL (must be api.screenscraper.fr, NOT www)
API_BASE = "https://api.screenscraper.fr/api2"


class ScreenScraperScraper(BaseScraper):
    """
    ScreenScraper.fr API v2 scraper.

    Free tier: 1 request/2sec (60 req/min).
    Requires free account: https://www.screenscraper.fr/

    Dev credentials: obtain via ScreenScraper forum.
    Fallback dev credentials from RomM (may be rate-limited/shared).
    """

    BASE_URL = API_BASE

    # Region priority (most common first)
    REGION_PRIORITY = ["wor", "usa", "eur", "jap", "fra", "ger", "esp", "ita", "bra", "fra", "wor"]

    # Language priority
    LANG_PRIORITY = ["en", "fr", "de", "es", "it", "pt", "ja", "zh"]

    # Default dev credentials (shared dev account from RomM)
    # Users should obtain their own via ScreenScraper forum
    DEFAULT_DEV_ID = "zurdi15"
    DEFAULT_DEV_PASSWORD = "xTJwoOFjOQG"
    DEFAULT_SOFTNAME = "jarl"

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        rate_limit: float = 2.0,  # seconds between requests
    ):
        self.username = username
        self.password = password
        self.rate_limit = rate_limit
        self._token: Optional[str] = None
        self._last_request_time: float = 0.0
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                headers={"User-Agent": "JARL/1.0 (self-hosted ROM manager)"},
            )
        return self._client

    async def _rate_limit(self) -> None:
        """Enforce rate limiting."""
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self.rate_limit:
            await asyncio.sleep(self.rate_limit - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()

    async def login(self) -> bool:
        """ScreenScraper credentials will be passed directly in request parameters."""
        return True

    async def is_authenticated(self) -> bool:
        return self.username is not None

    def _get_auth_params(self) -> dict[str, str]:
        """Get base parameters for authentication and developer ID."""
        params = {
            "output": "json",
            "devid": self.DEFAULT_DEV_ID,
            "devpassword": self.DEFAULT_DEV_PASSWORD,
            "softname": self.DEFAULT_SOFTNAME,
        }
        if self.username and self.password:
            params["ssid"] = self.username
            params["sspassword"] = self.password
        return params

    async def search(
        self,
        query: str,
        platform: Optional[str],
    ) -> list[ScraperResult]:
        """Search ScreenScraper for ROM by name using jeuRecherche.php."""
        await self._rate_limit()
        client = await self._get_client()

        params = self._get_auth_params()
        params["recherche"] = query

        system_id = PLATFORM_SYSTEM_IDS.get(platform) if platform else None
        if system_id:
            # NOTE: uses systemeid (french spelling), NOT systemid
            params["systemeid"] = str(system_id)

        try:
            logger.debug(f"ScreenScraper search: {query} (systemeid: {params.get('systemeid')})")
            response = await client.get(
                f"{self.BASE_URL}/jeuRecherche.php",
                params=params,
            )

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "60"))
                logger.warning(f"Rate limited, waiting {retry_after}s")
                await asyncio.sleep(retry_after)
                return await self.search(query, platform)

            if response.status_code == 404:
                logger.debug(f"ScreenScraper 404 for search: {query}")
                return []

            response.raise_for_status()
            data = response.json()

            if data.get("header", {}).get("error"):
                error = data["header"]["error"]
                if "NO RESULT" in str(error).upper():
                    return []
                logger.warning(f"ScreenScraper search error: {error}")
                return []

            games_data = data.get("response", {}).get("jeux", [])
            # If no roms are returned, "jeux" is a list with an empty dict
            if len(games_data) == 1 and not games_data[0]:
                games_data = []

            results = []
            for game in games_data:
                result = self._parse_game_response(game)
                if result:
                    results.append(result)
            return results

        except httpx.HTTPStatusError as e:
            logger.error(f"ScreenScraper HTTP error during search: {e.response.status_code} - {e.response.text}")
            return []
        except Exception as e:
            logger.exception(f"ScreenScraper search failed: {e}")
            return []

    async def scrape(self, rom_hash: str, platform: str) -> ScraperResult:
        """Scrape ROM metadata using SHA1 hash with jeuInfos.php."""
        await self._rate_limit()
        client = await self._get_client()

        params = self._get_auth_params()
        params["sha1"] = rom_hash

        system_id = PLATFORM_SYSTEM_IDS.get(platform)
        if system_id:
            # NOTE: uses systemeid (french spelling), NOT systemid
            params["systemeid"] = str(system_id)

        try:
            logger.debug(f"ScreenScraper hash lookup: {rom_hash} (systemeid: {params.get('systemeid')})")
            response = await client.get(
                f"{self.BASE_URL}/jeuInfos.php",
                params=params,
            )

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "60"))
                logger.warning(f"Rate limited, waiting {retry_after}s")
                await asyncio.sleep(retry_after)
                return await self.scrape(rom_hash, platform)

            if response.status_code == 404:
                return ScraperResult(success=False, error="Match not found (404)")

            response.raise_for_status()
            data = response.json()

            if data.get("header", {}).get("error"):
                error = data["header"]["error"]
                if "NO RESULT" in str(error).upper():
                    return ScraperResult(success=False, error="No match found")
                logger.warning(f"ScreenScraper scrape error: {error}")
                return ScraperResult(success=False, error=str(error))

            game_data = data.get("response", {}).get("jeu")
            if not game_data:
                return ScraperResult(success=False, error="No game found in response")

            # If it's a list, take the first one
            if isinstance(game_data, list):
                game_data = game_data[0]

            return self._parse_game_response(game_data)

        except httpx.HTTPStatusError as e:
            logger.error(f"ScreenScraper HTTP error during scrape: {e.response.status_code} - {e.response.text}")
            return ScraperResult(success=False, error=f"HTTP {e.response.status_code}")
        except Exception as e:
            logger.exception(f"ScreenScraper scrape failed: {e}")
            return ScraperResult(success=False, error=str(e))

    def _parse_game_response(self, game: dict) -> Optional[ScraperResult]:
        """Parse ScreenScraper game response into ScraperResult."""
        try:
            # Names — use 'noms' field (API v2 format), not 'names'
            noms = game.get("noms", {}) or {}
            title = self._pick_best_lang_noms(noms)

            # Description — synopsis is a list of {langue, text} dicts in v2
            synopsis_list = game.get("synopsis") or []
            description = self._pick_best_lang_synopsis(synopsis_list)

            # Regions
            regions = game.get("regions", []) or []
            region = regions[0] if regions else None

            # Year + full release date — try USA first, then EU, JP, worldwide
            dates = game.get("dates") or {}
            year = None
            release_date = None
            for region_key in ["us", "eu", "jp", "fr", "wor"]:
                date_str = dates.get(region_key) or dates.get(f"date_{region_key}")
                if date_str and str(date_str).strip():
                    date_str = str(date_str).strip()
                    try:
                        year = int(date_str[:4])
                        # Try to get full date (YYYY-MM-DD)
                        if len(date_str) >= 10 and date_str[4] in ("-", "/"):
                            release_date = date_str[:10].replace("/", "-")
                        else:
                            release_date = None
                        break
                    except ValueError:
                        continue

            # Players
            players = game.get("joueurs", "1")

            # Publisher / Developer — v2 uses 'editeur' and 'developpeur' (singular)
            publisher = game.get("editeur")
            developer = game.get("developpeur")

            # Genre
            genres_list = game.get("genres", []) or []
            genre = self._pick_best_genre(genres_list)

            # Rating — ScreenScraper uses 0-20 scale in "note.ss"
            rating = None
            note = game.get("note") or {}
            if isinstance(note, dict):
                ss_val = note.get("ss")
                if ss_val is not None:
                    try:
                        rating = round(float(str(ss_val)) * 5, 1)  # convert 0-20 → 0-100
                    except (ValueError, TypeError):
                        pass
            elif note:
                try:
                    rating = round(float(str(note)) * 5, 1)
                except (ValueError, TypeError):
                    pass

            # ScreenScraper game ID
            screenscraper_id = None
            try:
                screenscraper_id = int(game.get("id", 0)) or None
            except (TypeError, ValueError):
                pass

            # Media — cover and screenshots
            medias = game.get("medias", []) or []
            cover_url = None
            screenshot_urls = []

            for media in medias:
                media_type = media.get("type", "")
                url = media.get("url", "")
                if not url:
                    continue

                if media_type in ("boxart", "ssdb"):
                    cover_url = url
                elif media_type in ("screenshot", "ss"):
                    screenshot_urls.append(url)

            return ScraperResult(
                title=title or game.get("nom"),
                description=description,
                year=year,
                release_date=release_date,
                publisher=publisher,
                developer=developer,
                genre=genre,
                players=players,
                region=region,
                rating=rating,
                cover_url=cover_url,
                screenshot_urls=screenshot_urls,
                screenscraper_id=screenscraper_id,
                success=True,
            )

        except Exception as e:
            logger.warning(f"Failed to parse game response: {e}")
            return None

    def _pick_best_lang_noms(self, noms: dict) -> Optional[str]:
        """Pick best available language from noms {lang: text} dict (v2 format)."""
        if isinstance(noms, list):
            for lang in self.LANG_PRIORITY:
                for entry in noms:
                    if isinstance(entry, dict) and entry.get("langue") == lang and entry.get("text"):
                        return entry["text"]
            for entry in noms:
                if isinstance(entry, dict) and entry.get("text"):
                    return entry["text"]
            return None

        for lang in self.LANG_PRIORITY:
            key = lang
            if key in noms and noms[key]:
                return noms[key]
        # Fall back to any available
        for lang, value in noms.items():
            if value:
                return value
        return None

    def _pick_best_lang_synopsis(self, synopsis_list: list) -> Optional[str]:
        """Pick best available language from synopsis list of {langue, text} dicts."""
        if not synopsis_list:
            return None
        # First try to find a dict with langue key
        if isinstance(synopsis_list, list):
            for entry in synopsis_list:
                if isinstance(entry, dict):
                    langue = entry.get("langue", "")
                    text = entry.get("text", "")
                    if text and langue in self.LANG_PRIORITY:
                        return text
            # Fall back to any entry with text
            for entry in synopsis_list:
                if isinstance(entry, dict):
                    text = entry.get("text", "")
                    if text:
                        return text
        return None

    def _pick_best_genre(self, genres_list: list) -> Optional[str]:
        """Pick best genre from genres list with nested noms structure."""
        if not genres_list:
            return None
        for genre in genres_list:
            if isinstance(genre, dict):
                noms = genre.get("noms", []) or []
                for nom_entry in noms:
                    if isinstance(nom_entry, dict):
                        if nom_entry.get("langue") == "en":
                            return nom_entry.get("text")
        # Fall back to first genre, first nom entry
        if genres_list and isinstance(genres_list[0], dict):
            noms = genres_list[0].get("noms", [])
            if noms and isinstance(noms[0], dict):
                return noms[0].get("text")
        return None

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


# ScreenScraper system IDs for major platforms
# Source: https://api.screenscraper.fr/api2/systemesListe.php
PLATFORM_SYSTEM_IDS: dict[str, int] = {
    "n64": 15,
    "n64dd": 91,
    "gamecube": 14,
    "wii": 17,
    "wiiu": 123,
    "switch": 130,
    "nes": 1,
    "snes": 3,
    "nds": 8,
    "3ds": 103,
    "gameboy": 2,
    "gameboycolor": 41,
    "gameboyadvance": 5,
    "virtualboy": 91,
    "psx": 11,
    "ps2": 87,
    "ps3": 95,
    "ps4": 124,
    "psp": 13,
    "vita": 106,
    "mastersystem": 7,
    "megadrive": 16,
    "segacd": 20,
    "saturn": 12,
    "dreamcast": 19,
    "gamegear": 21,
    "sg1000": 111,
    "sega32x": 26,
    "atari2600": 22,
    "atari7800": 23,
    "atarilynx": 25,
    "atarijaguar": 24,
    "neogeo": 142,
    "neogeocd": 142,
    "arcade": 75,
    "mame": 75,
    "fbneo": 142,
    "amiga500": 66,
    "amiga1200": 67,
    "c64": 54,
    "apple2": 40,
    "msx": 28,
    "scummvm": 135,
    "xbox": 117,
    "xbox360": 118,
    "zx81": 56,
    "zxspectrum": 57,
}
