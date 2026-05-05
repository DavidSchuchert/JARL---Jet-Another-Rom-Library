"""Health check endpoint."""
from fastapi import APIRouter, status
from sqlalchemy import text

from app import start_time
from app.config import get_settings
from app.database import async_session_maker
from app.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check() -> HealthResponse:
    """
    Check the health status of the API.

    Returns:
        HealthResponse with status, version, database status, and uptime.
    """
    import time

    settings = get_settings()

    db_status = "healthy"
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    return HealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        version=settings.version,
        database=db_status,
        uptime=time.time() - start_time,
    )
