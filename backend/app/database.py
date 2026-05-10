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


_SA_TYPE_TO_DDL = {
    "VARCHAR": lambda c: f"VARCHAR({c.type.length})" if hasattr(c.type, "length") and c.type.length else "VARCHAR",
    "TEXT": lambda _: "TEXT",
    "INTEGER": lambda c: "INTEGER NOT NULL DEFAULT 0" if not c.nullable and c.default is not None else "INTEGER",
    "FLOAT": lambda _: "REAL",
    "BOOLEAN": lambda c: "INTEGER NOT NULL DEFAULT 0" if not c.nullable else "INTEGER",
    "DATETIME": lambda _: "TIMESTAMP",
}


def _col_to_ddl(col) -> str:
    type_name = type(col.type).__name__.upper()
    if type_name in _SA_TYPE_TO_DDL:
        return _SA_TYPE_TO_DDL[type_name](col)
    return type_name


async def _migrate_new_columns(conn) -> None:
    for table in Base.metadata.sorted_tables:
        rows = await conn.execute(text(f"PRAGMA table_info({table.name})"))
        existing = {r[1] for r in rows.fetchall()}
        for col in table.columns:
            if col.name not in existing:
                ddl = _col_to_ddl(col)
                await conn.execute(
                    text(f"ALTER TABLE {table.name} ADD COLUMN {col.name} {ddl}")
                )


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
