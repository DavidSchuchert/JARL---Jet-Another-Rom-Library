"""Database connection and session management."""
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""

    pass


engine = create_async_engine(
    get_settings().database.url,
    echo=get_settings().debug,
    future=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides a database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for database sessions outside of request context."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


_NEW_COLUMNS: list[tuple[str, str, str]] = [
    ("roms", "screenshots", "TEXT"),
    ("roms", "rating", "REAL"),
    ("roms", "languages", "TEXT"),
    ("roms", "version", "VARCHAR(100)"),
    ("roms", "release_date", "VARCHAR(20)"),
    ("roms", "is_multi_disc", "INTEGER NOT NULL DEFAULT 0"),
    ("roms", "disc_count", "INTEGER"),
]


async def _migrate_new_columns(conn) -> None:
    for table, col, col_type in _NEW_COLUMNS:
        rows = await conn.execute(text(f"PRAGMA table_info({table})"))
        existing = [r[1] for r in rows.fetchall()]
        if col not in existing:
            await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))


async def init_db() -> None:
    """Initialize the database by creating all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("PRAGMA journal_mode=WAL"))
        await conn.execute(text("PRAGMA synchronous=NORMAL"))
        await _migrate_new_columns(conn)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
