"""Scraping API endpoints."""
import asyncio
from typing import Optional
import httpx

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from sqlalchemy import select, func

from app.database import get_db_context
from app.models import Rom
from app.scraper.batch import BatchScraper, BatchStatus
from app.scraper.screenscraper import ScreenScraperScraper
from app.scraper.igdb import IGDBScraper
from app.config import get_settings

router = APIRouter()

# Global batch scraper instance
_batch_scraper: Optional[BatchScraper] = None
scraper_lock = asyncio.Lock()

def get_batch_scraper() -> BatchScraper:
    """Get or create the global batch scraper."""
    global _batch_scraper
    if _batch_scraper is None:
        settings = get_settings()
        scraper = ScreenScraperScraper(
            username=settings.scraper.username,
            password=settings.scraper.password,
            rate_limit=settings.scraper.rate_limit,
        )
        _batch_scraper = BatchScraper(scraper=scraper)
    return _batch_scraper

@router.post("/scrape/start", status_code=status.HTTP_202_ACCEPTED)
async def start_batch_scrape(
    background_tasks: BackgroundTasks,
    platform: Optional[str] = None,
    only_missing: bool = True,
):
    """Start a batch scraping job."""
    async with scraper_lock:
        batch_scraper = get_batch_scraper()
        if batch_scraper.status == BatchStatus.RUNNING:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A scraping job is already running",
            )

        async with get_db_context() as session:
            query = select(Rom.id)
            if platform:
                query = query.where(Rom.platform_slug == platform)
            if only_missing:
                query = query.where(Rom.scrape_status != "done")
            
            result = await session.execute(query)
            rom_ids = [row[0] for row in result.all()]

        if not rom_ids:
            return {"message": "No ROMs to scrape"}

        # Start scraping in background
        background_tasks.add_task(batch_scraper.scrape_roms_by_ids, rom_ids)

        return {
            "status": "started",
            "message": f"Started scraping {len(rom_ids)} ROMs",
            "total": len(rom_ids)
        }


@router.post("/scrape/rom/{rom_id}", status_code=status.HTTP_202_ACCEPTED)
async def start_rom_rescrape(background_tasks: BackgroundTasks, rom_id: int):
    """Force metadata scraping for a single ROM."""
    async with scraper_lock:
        batch_scraper = get_batch_scraper()
        if batch_scraper.status == BatchStatus.RUNNING:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A scraping job is already running",
            )

        async with get_db_context() as session:
            result = await session.execute(select(Rom.id).where(Rom.id == rom_id))
            if result.scalar_one_or_none() is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"ROM with id {rom_id} not found",
                )

        background_tasks.add_task(batch_scraper.scrape_roms_by_ids, [rom_id])
        return {"status": "started", "message": f"Started scraping ROM {rom_id}", "total": 1}


@router.get("/scrape/status")
async def get_scrape_status():
    """Get the current scraping job status."""
    batch_scraper = get_batch_scraper()
    progress = batch_scraper.progress
    
    return {
        "status": batch_scraper.status.value,
        "total": progress.total,
        "done": progress.done,
        "success": progress.success,
        "failed": progress.failed,
        "skipped": progress.skipped,
        "current_file": progress.current,
        "percent": round(progress.percent, 2),
        "errors": progress.errors[-10:] if progress.errors else [], # last 10 errors
    }

@router.get("/scrape/test-auth")
async def test_scraper_auth():
    """Test authentication with all configured scrapers."""
    settings = get_settings()
    results = {}

    # 1. Test ScreenScraper
    ss = ScreenScraperScraper(
        username=settings.scraper.username,
        password=settings.scraper.password,
    )
    
    # We use a direct call to ssuserInfos to get detailed account status
    params = ss._get_auth_params()
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{ss.BASE_URL}/ssuserInfos.php",
                params=params
            )
            results["screenscraper"] = {
                "status": "success" if response.status_code == 200 else "failed",
                "http_code": response.status_code,
                "message": response.text if response.status_code != 200 else "Authenticated successfully",
                "user": settings.scraper.username,
                "details": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            results["screenscraper"] = {
                "status": "error",
                "message": str(e)
            }

    # 2. Test IGDB
    igdb = IGDBScraper(
        client_id=settings.scraper.igdb_client_id,
        client_secret=settings.scraper.igdb_client_secret,
    )
    try:
        success = await igdb.login()
        results["igdb"] = {
            "status": "success" if success else "failed",
            "message": "Authenticated successfully" if success else "Login failed (check logs for details)",
            "client_id": settings.scraper.igdb_client_id[:10] + "..." if settings.scraper.igdb_client_id else None
        }
    except Exception as e:
        results["igdb"] = {
            "status": "error",
            "message": str(e)
        }

    return results

@router.post("/scrape/stop")
async def stop_scrape():
    """Cancel the running scraping job."""
    batch_scraper = get_batch_scraper()
    batch_scraper.cancel()
    return {"message": "Scraping cancellation requested"}
