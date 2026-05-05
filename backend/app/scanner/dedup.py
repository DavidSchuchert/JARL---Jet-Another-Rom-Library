"""xxhash-based deduplication for ROM files."""
from sqlalchemy import select

from app.database import get_db_context
from app.models import Rom


async def check_duplicate_hash(xxhash: str) -> bool:
    """
    Check if a ROM with the given xxhash already exists in the database.

    Args:
        xxhash: The xxhash64 hash of the ROM file.

    Returns:
        True if a duplicate exists, False otherwise.
    """
    async with get_db_context() as session:
        result = await session.execute(
            select(Rom).where(Rom.hash_xxhash == xxhash)
        )
        return result.scalars().first() is not None


async def get_duplicate_roms(xxhash: str) -> list[Rom]:
    """
    Get all ROMs with the given xxhash.

    Args:
        xxhash: The xxhash64 hash of the ROM file.

    Returns:
        List of ROMs with matching hash.
    """
    async with get_db_context() as session:
        result = await session.execute(
            select(Rom).where(Rom.hash_xxhash == xxhash)
        )
        return list(result.scalars().all())


async def check_sha1_duplicate(sha1: str) -> bool:
    """
    Check if a ROM with the given SHA1 hash already exists.

    Args:
        sha1: The SHA1 hash of the ROM file.

    Returns:
        True if a duplicate exists, False otherwise.
    """
    async with get_db_context() as session:
        result = await session.execute(
            select(Rom).where(Rom.hash_sha1 == sha1)
        )
        return result.scalars().first() is not None


async def get_duplicate_by_any_hash(xxhash: str, sha1: str) -> list[Rom]:
    """
    Get all ROMs matching either xxhash or sha1.

    Args:
        xxhash: The xxhash64 hash.
        sha1: The SHA1 hash.

    Returns:
        List of matching ROMs.
    """
    async with get_db_context() as session:
        result = await session.execute(
            select(Rom).where(
                (Rom.hash_xxhash == xxhash) | (Rom.hash_sha1 == sha1)
            )
        )
        return list(result.scalars().all())
