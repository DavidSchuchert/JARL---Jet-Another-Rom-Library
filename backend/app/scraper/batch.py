"""Batch scraper with concurrency control, retry, and progress tracking."""
import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker
from app.models import Rom
from app.scraper.base import BaseScraper, ScraperResult
from app.scraper.screenscraper import ScreenScraperScraper
from app.scraper.igdb import IGDBScraper
from app.config import get_settings
from app.utils.images import download_cover, download_screenshots

logger = logging.getLogger(__name__)


class BatchStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BatchProgress:
    """Real-time batch scraping progress."""
    total: int = 0
    done: int = 0
    success: int = 0
    failed: int = 0
    skipped: int = 0
    current: Optional[str] = None
    current_title: Optional[str] = None
    current_cover: Optional[str] = None  # remote cover URL for live preview
    errors: list[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @property
    def percent(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.done / self.total) * 100


@dataclass
class BatchConfig:
    """Configuration for batch scraping."""
    concurrency: int = 8  # parallel scraper workers
    max_retries: int = 3
    retry_delay: float = 5.0  # seconds


class BatchScraper:
    """
    Batch scraper that processes ROMs with configurable concurrency,
    retry logic, rate limiting, and progress tracking.
    """

    def __init__(
        self,
        scraper: Optional[BaseScraper] = None,
        config: Optional[BatchConfig] = None,
    ):
        settings = get_settings()
        self.scraper = scraper or ScreenScraperScraper(
            username=settings.scraper.username,
            password=settings.scraper.password,
            rate_limit=settings.scraper.rate_limit,
            dev_id=settings.scraper.ss_dev_id,
            dev_password=settings.scraper.ss_dev_password,
            softname=settings.scraper.ss_softname,
        )
        self.fallback_scraper = IGDBScraper(
            client_id=settings.scraper.igdb_client_id,
            client_secret=settings.scraper.igdb_client_secret
        )
        self.config = config or BatchConfig()
        self._progress = BatchProgress()
        self._status = BatchStatus.IDLE
        self._cancel_event: Optional[asyncio.Event] = None
        self._pause_event: Optional[asyncio.Event] = None

    @property
    def status(self) -> BatchStatus:
        return self._status

    @property
    def progress(self) -> BatchProgress:
        return self._progress

    async def scrape_roms(
        self,
        rom_ids: list[int],
        session_arg: Optional[AsyncSession] = None, 
        job_id: Optional[int] = None,
    ) -> BatchProgress:
        """
        Scrape metadata for a list of ROMs.
        Uses fresh sessions for each ROM to avoid SQLite locks.
        """
        self._status = BatchStatus.RUNNING
        self._progress = BatchProgress(
            total=len(rom_ids),
            started_at=datetime.utcnow(),
        )
        self._cancel_event = asyncio.Event()
        self._pause_event = asyncio.Event()
        self._pause_event.set()  # not paused by default

        logger.info(f"Starting batch scrape of {len(rom_ids)} ROMs")

        # Login to scraper
        await self.scraper.login()

        # Process using a semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.config.concurrency)

        async def scrape_one(rom_id: int) -> None:
            async with semaphore:
                if self._cancel_event.is_set():
                    return
                await self._pause_event.wait()
                
                # Use a fresh session for EVERY individual ROM to prevent lock contention
                async with async_session_maker() as s:
                    try:
                        await self._scrape_single(rom_id, s)
                        await s.commit()
                    except Exception as e:
                        logger.error(f"Unexpected error scraping ROM {rom_id}: {e}")
                        self._progress.failed += 1
                        await s.rollback()
                    finally:
                        self._progress.done = self._progress.success + self._progress.failed + self._progress.skipped

        # Run tasks in parallel
        await asyncio.gather(*(scrape_one(rid) for rid in rom_ids), return_exceptions=True)

        self._progress.completed_at = datetime.utcnow()

        if self._cancel_event.is_set():
            self._status = BatchStatus.IDLE
            logger.info("Batch scrape cancelled")
        else:
            self._status = BatchStatus.COMPLETED
            logger.info(f"Batch scrape finished: {self._progress.success} success")

        return self._progress

    async def _scrape_single(self, rom_id: int, session: AsyncSession) -> None:
        """Scrape a single ROM with fallback logic."""
        result = await session.execute(select(Rom).where(Rom.id == rom_id))
        rom = result.scalar_one_or_none()

        if not rom or rom.scrape_status == "done":
            if not rom: self._progress.skipped += 1
            return

        self._progress.current = rom.filename
        self._progress.current_title = rom.title
        self._progress.current_cover = None
        platform = rom.platform_slug
        query = rom.title if rom.title else rom.filename
        
        result_obj: Optional[ScraperResult] = None
        import re
        clean_query = re.sub(r'\(.*?\)|\[.*?\]', '', query).strip()

        # 1. Try IGDB first (fast, no harsh rate limits)
        try:
            await self.fallback_scraper.login()
            igdb_results = await self._scrape_with_retry(self.fallback_scraper.search, clean_query, platform)
            if igdb_results:
                result_obj = igdb_results[0]
        except Exception:
            logger.debug(f"IGDB failed for {rom.filename}, trying ScreenScraper")

        # 2. Fallback: ScreenScraper hash lookup
        if not result_obj or not result_obj.success:
            if rom.hash_sha1:
                result_obj = await self._scrape_with_retry(self.scraper.scrape, rom.hash_sha1, platform)

        # 3. Fallback: ScreenScraper name search
        if not result_obj or not result_obj.success:
            search_results = await self._scrape_with_retry(self.scraper.search, clean_query, platform)
            if search_results:
                result_obj = search_results[0]

        # Save to DB
        if result_obj and result_obj.success:
            # Set live preview cover before downloading
            self._progress.current_cover = result_obj.cover_url
            self._progress.current_title = result_obj.title or rom.title

            # Download cover locally
            local_cover = None
            if result_obj.cover_url:
                local_cover = await download_cover(rom_id, result_obj.cover_url)

            # Download screenshots locally (up to 3)
            local_screenshots: list[str] = []
            if result_obj.screenshot_urls:
                local_screenshots = await download_screenshots(rom_id, result_obj.screenshot_urls)

            update_values = {
                "title": result_obj.title or rom.title,
                "description": result_obj.description,
                "year": result_obj.year,
                "release_date": result_obj.release_date,
                "publisher": result_obj.publisher,
                "developer": result_obj.developer,
                "genre": result_obj.genre,
                "players": str(result_obj.players) if result_obj.players else None,
                "region": result_obj.region,
                "rating": result_obj.rating,
                "languages": json.dumps(result_obj.languages) if result_obj.languages else None,
                "cover_url": local_cover or result_obj.cover_url,
                "screenshots": json.dumps(local_screenshots) if local_screenshots else None,
                "scrape_status": "done",
            }
            if result_obj.igdb_id:
                update_values["igdb_id"] = result_obj.igdb_id
            if result_obj.screenscraper_id:
                update_values["screenscraper_id"] = result_obj.screenscraper_id

            # Handle potential lock with a small retry
            for attempt in range(5):
                try:
                    await session.execute(update(Rom).where(Rom.id == rom_id).values(**update_values))
                    self._progress.success += 1
                    break
                except Exception as e:
                    if "locked" in str(e).lower() and attempt < 4:
                        await asyncio.sleep(0.5 * (attempt + 1))
                        continue
                    raise
        else:
            await session.execute(update(Rom).where(Rom.id == rom_id).values(scrape_status="failed"))
            self._progress.failed += 1
            err = result_obj.error if result_obj else "Not found"
            if len(self._progress.errors) < 100:
                self._progress.errors.append(f"{rom.filename}: {err}")

    async def _scrape_with_retry(self, func, *args, **kwargs):
        """Call a scraper function with retry logic."""
        for attempt in range(self.config.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
        return None

    def cancel(self) -> None:
        if self._cancel_event: self._cancel_event.set()
        self._status = BatchStatus.IDLE

    async def scrape_roms_by_ids(self, rom_ids: list[int]) -> BatchProgress:
        return await self.scrape_roms(rom_ids)
