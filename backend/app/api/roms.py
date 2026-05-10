"""ROMs API endpoints."""
import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select, update

from app.database import get_db_context
from app.models import Rom
from app.schemas import ErrorResponse, RomListResponse, RomResponse, RomUpdate, StatsResponse
from app.utils.images import COVERS_DIR, SCREENSHOTS_DIR

router = APIRouter()


@router.get(
    "/roms",
    response_model=RomListResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def list_roms(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=50, ge=1, le=100, description="Items per page"),
    platform: Optional[str] = Query(default=None, description="Filter by platform slug"),
    region: Optional[str] = Query(default=None, description="Filter by region"),
    year: Optional[int] = Query(default=None, description="Filter by release year"),
    genre: Optional[str] = Query(default=None, description="Filter by genre"),
    search: Optional[str] = Query(default=None, description="Search in title"),
    sort_by: Optional[str] = Query(default="title", description="Sort field"),
    sort_dir: Optional[str] = Query(default="asc", description="Sort direction: asc | desc"),
) -> RomListResponse:
    """
    List ROMs with pagination and filtering.

    Args:
        page: Page number (1-indexed).
        page_size: Number of items per page.
        platform: Filter by platform slug.
        region: Filter by region.
        year: Filter by release year.
        genre: Filter by genre.
        search: Search query for title.

    Returns:
        Paginated list of ROMs.
    """
    async with get_db_context() as session:
        query = select(Rom)
        count_query = select(func.count(Rom.id))

        if platform:
            query = query.where(Rom.platform_slug == platform)
            count_query = count_query.where(Rom.platform_slug == platform)
        if region:
            query = query.where(Rom.region == region)
            count_query = count_query.where(Rom.region == region)
        if year:
            query = query.where(Rom.year == year)
            count_query = count_query.where(Rom.year == year)
        if genre:
            query = query.where(Rom.genre == genre)
            count_query = count_query.where(Rom.genre == genre)
        if search:
            search_filter = Rom.title.ilike(f"%{search}%")
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        _SORT_COLUMNS = {
            "title": Rom.title,
            "year": Rom.year,
            "rating": Rom.rating,
            "size": Rom.size,
            "scrape_status": Rom.scrape_status,
        }
        sort_col = _SORT_COLUMNS.get(sort_by or "title", Rom.title)
        if (sort_dir or "asc").lower() == "desc":
            query = query.order_by(sort_col.desc().nulls_last())
        else:
            query = query.order_by(sort_col.asc().nulls_last())

        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0

        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await session.execute(query)
        roms_list = result.scalars().all()

        pages = (total + page_size - 1) // page_size if total > 0 else 1

        return RomListResponse(
            items=[RomResponse.model_validate(rom) for rom in roms_list],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=pages,
        )


@router.get("/roms/stats", response_model=StatsResponse)
async def get_stats() -> StatsResponse:
    """
    Get ROM library statistics.

    Returns:
        Counts and totals for the ROM library.
    """
    async with get_db_context() as session:
        total_result = await session.execute(select(func.count(Rom.id)))
        total_roms = total_result.scalar() or 0

        platform_result = await session.execute(select(func.count(Rom.platform_slug.distinct())))
        total_platforms = platform_result.scalar() or 0

        size_result = await session.execute(select(func.sum(Rom.size)))
        total_size = size_result.scalar() or 0

        igdb_result = await session.execute(
            select(func.count(Rom.id)).where(Rom.igdb_id.isnot(None))
        )
        roms_with_igdb = igdb_result.scalar() or 0

        ss_result = await session.execute(
            select(func.count(Rom.id)).where(Rom.screenscraper_id.isnot(None))
        )
        roms_with_ss = ss_result.scalar() or 0

        return StatsResponse(
            total_roms=total_roms,
            total_platforms=total_platforms,
            total_size_bytes=total_size,
            roms_with_igdb=roms_with_igdb,
            roms_with_screenscraper=roms_with_ss,
            last_scan=None,
        )


@router.get("/roms/{rom_id}", response_model=RomResponse, responses={404: {"model": ErrorResponse}})
async def get_rom(rom_id: int) -> RomResponse:
    """
    Get a single ROM by ID.

    Args:
        rom_id: ROM ID.

    Returns:
        ROM details.

    Raises:
        HTTPException: If ROM not found.
    """
    async with get_db_context() as session:
        result = await session.execute(select(Rom).where(Rom.id == rom_id))
        rom = result.scalar_one_or_none()

        if rom is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ROM with id {rom_id} not found",
            )

        return RomResponse.model_validate(rom)


@router.patch("/roms/{rom_id}", response_model=RomResponse, responses={404: {"model": ErrorResponse}})
async def update_rom(rom_id: int, payload: RomUpdate) -> RomResponse:
    """Manually update ROM metadata."""
    async with get_db_context() as session:
        result = await session.execute(select(Rom).where(Rom.id == rom_id))
        rom = result.scalar_one_or_none()

        if rom is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ROM with id {rom_id} not found",
            )

        update_data = payload.model_dump(exclude_unset=True)
        if update_data:
            await session.execute(update(Rom).where(Rom.id == rom_id).values(**update_data))
            await session.commit()
            result = await session.execute(select(Rom).where(Rom.id == rom_id))
            rom = result.scalar_one()

        return RomResponse.model_validate(rom)


@router.delete("/roms/{rom_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rom(rom_id: int) -> None:
    """
    Delete a ROM by ID.

    Args:
        rom_id: ROM ID.

    Raises:
        HTTPException: If ROM not found.
    """
    async with get_db_context() as session:
        result = await session.execute(select(Rom).where(Rom.id == rom_id))
        rom = result.scalar_one_or_none()

        if rom is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ROM with id {rom_id} not found",
            )

        # Clean up local image files
        if rom.cover_url and rom.cover_url.startswith("/media/covers/"):
            (COVERS_DIR / Path(rom.cover_url).name).unlink(missing_ok=True)
        if rom.screenshots:
            try:
                for ss_path in json.loads(rom.screenshots):
                    if ss_path.startswith("/media/screenshots/"):
                        (SCREENSHOTS_DIR / Path(ss_path).name).unlink(missing_ok=True)
            except Exception:
                pass

        await session.delete(rom)
        await session.commit()
