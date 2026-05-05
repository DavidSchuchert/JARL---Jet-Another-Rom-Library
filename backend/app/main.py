"""FastAPI main application."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, platforms, roms, scan, scrape
from app.config import get_settings
from app.database import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown events."""
    await init_db()
    
    # Reset stuck scan jobs from previous runs
    from app.database import get_db_context
    from app.models import ScanJob
    from sqlalchemy import select, update
    
    async with get_db_context() as session:
        await session.execute(
            update(ScanJob)
            .where(ScanJob.status == "running")
            .values(status="failed", completed_at=None)
        )
        await session.commit()

    from app.scanner.filesystem import ensure_platforms_exist

    await ensure_platforms_exist()
    yield
    await close_db()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.name,
        version=settings.version,
        description="JARL - JetAnotherRomLibrary API",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api", tags=["Health"])
    app.include_router(roms.router, prefix="/api", tags=["ROMs"])
    app.include_router(scan.router, prefix="/api", tags=["Scan"])
    app.include_router(platforms.router, prefix="/api", tags=["Platforms"])
    app.include_router(scrape.router, prefix="/api", tags=["Scrape"])

    return app


app = create_app()


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint returning API info."""
    return {
        "name": get_settings().name,
        "version": get_settings().version,
        "docs": "/api/docs",
    }
