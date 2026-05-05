"""Platforms API endpoints."""
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select

from app.database import get_db_context
from app.models import Platform, Rom
from app.schemas import ErrorResponse, PlatformResponse, RomListResponse, RomResponse

router = APIRouter()


@router.get("/platforms", response_model=list[PlatformResponse])
async def list_platforms() -> list[PlatformResponse]:
    """
    List all platforms.

    Returns:
        List of all platforms.
    """
    async with get_db_context() as session:
        result = await session.execute(
            select(Platform, func.count(Rom.id).label("rom_count"))
            .outerjoin(Rom, Rom.platform_slug == Platform.slug)
            .group_by(Platform.id)
            .having(func.count(Rom.id) > 0)
            .order_by(Platform.name)
        )
        return [
            PlatformResponse(
                id=platform.id,
                slug=platform.slug,
                name=platform.name,
                family=platform.family,
                icon=platform.icon,
                rom_count=rom_count,
            )
            for platform, rom_count in result.all()
        ]


@router.get(
    "/platforms/{slug}",
    response_model=PlatformResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_platform(slug: str) -> PlatformResponse:
    """
    Get a single platform by slug.

    Args:
        slug: Platform slug.

    Returns:
        Platform details with ROM count.

    Raises:
        HTTPException: If platform not found.
    """
    async with get_db_context() as session:
        result = await session.execute(
            select(Platform, func.count(Rom.id).label("rom_count"))
            .outerjoin(Rom, Rom.platform_slug == Platform.slug)
            .where(Platform.slug == slug)
            .group_by(Platform.id)
        )
        row = result.one_or_none()

        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Platform with slug '{slug}' not found",
            )

        platform, rom_count = row
        return PlatformResponse(
            id=platform.id,
            slug=platform.slug,
            name=platform.name,
            family=platform.family,
            icon=platform.icon,
            rom_count=rom_count,
        )


@router.get(
    "/platforms/{slug}/roms",
    response_model=RomListResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_platform_roms(slug: str, page: int = 1, page_size: int = 50) -> RomListResponse:
    """
    Get ROMs for a specific platform.

    Args:
        slug: Platform slug.
        page: Page number.
        page_size: Items per page.

    Returns:
        Paginated list of ROMs for the platform.

    Raises:
        HTTPException: If platform not found.
    """
    async with get_db_context() as session:
        platform_result = await session.execute(select(Platform).where(Platform.slug == slug))
        platform = platform_result.scalar_one_or_none()

        if platform is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Platform with slug '{slug}' not found",
            )

        count_result = await session.execute(
            select(func.count(Rom.id)).where(Rom.platform_slug == slug)
        )
        total = count_result.scalar() or 0

        result = await session.execute(
            select(Rom)
            .where(Rom.platform_slug == slug)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        roms_list = result.scalars().all()

        pages = (total + page_size - 1) // page_size if total > 0 else 1

        return RomListResponse(
            items=[RomResponse.model_validate(rom) for rom in roms_list],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=pages,
        )
