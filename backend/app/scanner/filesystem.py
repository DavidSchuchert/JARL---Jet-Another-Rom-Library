"""Async filesystem scanner for ROM file discovery."""
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator

import aiofiles
from sqlalchemy import delete as sa_delete
from sqlalchemy import select

from app.config import get_settings
from app.database import get_db_context
from app.models import Platform, Rom, ScanJob
from app.scanner.dedup import check_duplicate_hash
from app.scanner.parser import parse_filename
from app.scanner.platforms import get_platform_by_extension, guess_platform_from_path
from app.scanner.progress import record_scan_event


BATCH_SIZE = 100
PROGRESS_UPDATE_INTERVAL = 10
SYSTEM_DIRS = ("__macosx", "system volume information", "$recycle.bin", "recycler")


def is_hidden_or_system(path: Path) -> bool:
    """Check if a path is hidden or a system directory."""
    name = path.name.lower()
    if name.startswith((".", "thumbs.db", "desktop.ini")):
        return True
    if name in SYSTEM_DIRS:
        return True
    return False


def is_rom_file(path: Path) -> bool:
    """Check if a file has a known ROM extension."""
    extension = path.suffix.lower().lstrip(".")
    return get_platform_by_extension(extension) is not None


async def compute_file_hashes(file_path: Path) -> tuple[str, str]:
    """Compute xxhash and sha1 for a file."""
    import hashlib
    import xxhash

    xx = xxhash.xxh64()
    sha = hashlib.sha1()

    async with aiofiles.open(file_path, "rb") as f:
        while chunk := await f.read(8192):
            xx.update(chunk)
            sha.update(chunk)

    return xx.hexdigest(), sha.hexdigest()


async def process_rom_file(file_path: Path, job_id: int, full_scan: bool = False) -> Rom | None:
    """Process a single ROM file and return a Rom object."""
    import logging
    logger = logging.getLogger(__name__)
    try:
        settings = get_settings()
        stat_info = await asyncio.to_thread(os.stat, file_path)
        size = stat_info.st_size
        mtime = stat_info.st_mtime

        # Quick check: does path + size + mtime exist?
        if not full_scan:
            async with get_db_context() as session:
                result = await session.execute(
                    select(Rom).where(
                        (Rom.path == str(file_path)) & 
                        (Rom.size == size) & 
                        (Rom.mtime == mtime)
                    )
                )
                if result.scalars().first():
                    return None  # Skip, already indexed and unchanged

        hash_limit_bytes = settings.scanner.hash_size_limit_mb * 1024 * 1024
        should_hash = hash_limit_bytes == 0 or size <= hash_limit_bytes

        if should_hash:
            xxhash_val, sha1_hash = await compute_file_hashes(file_path)
        else:
            xxhash_val = None
            sha1_hash = None
            if full_scan:
                logger.info(
                    "Skipping hash for large file over %s MiB: %s",
                    settings.scanner.hash_size_limit_mb,
                    file_path,
                )

        # Check for duplicates by hash if not a full scan
        if not full_scan and xxhash_val:
            is_dup = await check_duplicate_hash(xxhash_val)
            if is_dup:
                logger.debug(f"Skipping duplicate file: {file_path}")
                return None

        platform = guess_platform_from_path(str(file_path))
        if platform is None:
            ext = file_path.suffix.lower().lstrip(".")
            platform = get_platform_by_extension(ext)

        if platform is None:
            logger.warning(f"Could not determine platform for file: {file_path}")
            return None

        parsed = parse_filename(file_path.stem)

        langs = parsed.get("languages")
        return Rom(
            path=str(file_path),
            filename=file_path.name,
            platform_slug=platform.slug,
            title=parsed.get("title", file_path.stem),
            region=parsed.get("region"),
            languages=json.dumps(langs) if langs else None,
            version=parsed.get("version"),
            size=size,
            mtime=mtime,
            hash_sha1=sha1_hash,
            hash_xxhash=xxhash_val,
            scrape_status="pending",
        )
    except Exception as e:
        logger.exception(f"Error processing file {file_path}: {e}")
        return None


async def scan_directory(job_id: int, full_scan: bool = False) -> None:
    """Scan the ROMs directory and process files with optimized performance."""
    settings = get_settings()
    roms_path = settings.scanner.roms_path
    import logging
    logger = logging.getLogger(__name__)

    logger.info(f"Starting {'FULL ' if full_scan else ''}scan of {roms_path} for job {job_id}")

    # Pre-scan to get total count
    logger.info("Counting files...")
    def count_files():
        count = 0
        for root, dirs, files in os.walk(roms_path):
            dirs[:] = [d for d in dirs if not is_hidden_or_system(Path(root) / d)]
            for f in files:
                if is_rom_file(Path(f)):
                    count += 1
        return count

    total_count = await asyncio.to_thread(count_files)
    logger.info(f"Found {total_count} files to process")
    record_scan_event(
        job_id,
        f"Found {total_count} ROM files",
        event_type="info",
        scanned_files=0,
    )

    async with get_db_context() as session:
        result = await session.execute(select(ScanJob).where(ScanJob.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            return
        job.status = "running"
        job.total_files = total_count
        job.scanned_files = 0
        job.current_file = "Counting complete"
        await session.commit()

    processed = 0
    errors = 0
    rom_batch: list[Rom] = []
    # Use fewer workers for NAS to avoid network congestion
    semaphore = asyncio.Semaphore(min(settings.scanner.workers, 2))

    async def wrapped_process(file_path: Path) -> tuple[Path, Rom | None, bool]:
        async with semaphore:
            try:
                current_display = str(file_path.relative_to(roms_path))
            except ValueError:
                current_display = str(file_path)
            record_scan_event(
                job_id,
                f"Processing {current_display}",
                event_type="info",
                current_file=current_display,
            )
            try:
                rom = await asyncio.wait_for(
                    process_rom_file(file_path, job_id, full_scan),
                    timeout=settings.scanner.file_timeout_seconds,
                )
                return file_path, rom, False
            except TimeoutError:
                logger.warning(
                    "Skipping file after %s seconds: %s",
                    settings.scanner.file_timeout_seconds,
                    file_path,
                )
                record_scan_event(
                    job_id,
                    f"Timed out after {settings.scanner.file_timeout_seconds}s: {current_display}",
                    event_type="error",
                    current_file=current_display,
                )
                return file_path, None, True

    try:
        async for file_list in walk_directory(roms_path):
            # Create coroutines for this batch
            coroutines = [wrapped_process(f) for f in file_list]
            
            # Process as they complete for better UI responsiveness
            for task in asyncio.as_completed(coroutines):
                file_path, rom, timed_out = await task
                processed += 1
                if timed_out:
                    errors += 1

                try:
                    current_display = str(file_path.relative_to(roms_path))
                except ValueError:
                    current_display = str(file_path)

                if rom:
                    rom_batch.append(rom)
                    logger.info(f"Scanned: {current_display}")

                record_scan_event(
                    job_id,
                    current_display,
                    event_type="file",
                    current_file=current_display,
                    scanned_files=processed,
                )

                # Throttled DB update
                if processed % PROGRESS_UPDATE_INTERVAL == 0 or processed == total_count or timed_out:
                    async with get_db_context() as session:
                        result = await session.execute(select(ScanJob).where(ScanJob.id == job_id))
                        db_job = result.scalar_one_or_none()
                        if db_job:
                            db_job.current_file = current_display
                            db_job.scanned_files = processed
                            db_job.errors = errors
                            await session.commit()

                if len(rom_batch) >= BATCH_SIZE:
                    await save_batch(rom_batch, job_id)
                    rom_batch = []
            
    except Exception as e:
        logger.exception(f"Error during scan: {e}")
        raise

    if rom_batch:
        await save_batch(rom_batch, job_id)

    async with get_db_context() as session:
        result = await session.execute(select(ScanJob).where(ScanJob.id == job_id))
        job = result.scalar_one_or_none()
        if job:
            job.scanned_files = processed
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            job.current_file = None
            await session.commit()

    # Remove orphaned DB entries — ROMs whose file no longer exists on disk
    async with get_db_context() as session:
        result = await session.execute(select(Rom.id, Rom.path))
        all_roms = result.all()

    orphaned_ids = [rom_id for rom_id, rom_path in all_roms if not Path(rom_path).exists()]
    if orphaned_ids:
        async with get_db_context() as session:
            await session.execute(sa_delete(Rom).where(Rom.id.in_(orphaned_ids)))
            await session.commit()
        record_scan_event(
            job_id,
            f"Removed {len(orphaned_ids)} orphaned ROM(s) from library",
            event_type="info",
            scanned_files=processed,
        )
        logger.info(f"Removed {len(orphaned_ids)} orphaned ROMs from DB")

    record_scan_event(
        job_id,
        f"Scan complete. Processed {processed} files.",
        event_type="success",
        scanned_files=processed,
    )

    logger.info(f"Scan job {job_id} completed. Processed {processed} files.")


async def save_batch(roms: list[Rom], job_id: int) -> None:
    """Save a batch of ROMs to the database, updating existing paths in place."""
    async with get_db_context() as session:
        existing_by_path: dict[str, Rom] = {}
        if roms:
            result = await session.execute(select(Rom).where(Rom.path.in_([rom.path for rom in roms])))
            for existing in result.scalars().all():
                existing_by_path.setdefault(existing.path, existing)

        for rom in roms:
            existing = existing_by_path.get(rom.path)
            if existing:
                existing.filename = rom.filename
                existing.platform_slug = rom.platform_slug
                existing.title = rom.title
                existing.region = rom.region
                existing.languages = rom.languages
                existing.version = rom.version
                existing.size = rom.size
                existing.mtime = rom.mtime
                existing.hash_sha1 = rom.hash_sha1
                existing.hash_xxhash = rom.hash_xxhash
                if not existing.scrape_status:
                    existing.scrape_status = "pending"
            else:
                session.add(rom)
        await session.commit()


async def walk_directory(root_path: Path) -> AsyncGenerator[list[Path], None]:
    """Walk directory tree and yield batches of ROM files."""
    import logging
    logger = logging.getLogger(__name__)
    
    batch: list[Path] = []
    queue: asyncio.Queue[Path] = asyncio.Queue()
    await queue.put(Path(root_path))
    scanned_dirs = 0
    skipped_errors = 0

    logger.debug(f"Starting walk from {root_path}")

    while not queue.empty():
        current_dir = await queue.get()

        try:
            entries = await asyncio.to_thread(list_directory_entries, current_dir)
            scanned_dirs += 1
        except (asyncio.CancelledError, KeyboardInterrupt):
            logger.info("Directory walk cancelled")
            raise
        except (OSError, PermissionError) as exc:
            logger.warning(f"Skipping directory {current_dir} due to error: {exc}")
            skipped_errors += 1
            continue
        except Exception as exc:
            logger.exception(f"Unexpected error listing {current_dir}")
            skipped_errors += 1
            continue

        for entry_path, is_dir, is_symlink_dir in entries:

            if is_hidden_or_system(entry_path):
                continue

            if is_symlink_dir:
                logger.debug(f"Skipping symlink directory: {entry_path}")
                continue

            if is_dir:
                await queue.put(entry_path)
            elif is_rom_file(entry_path):
                batch.append(entry_path)
                if len(batch) >= BATCH_SIZE:
                    logger.debug(f"Yielding batch of {len(batch)} files")
                    yield batch
                    batch = []

    if batch:
        yield batch
    
    logger.info(f"Directory walk finished. Scanned {scanned_dirs} dirs, skipped {skipped_errors} errors.")


def list_directory_entries(directory: Path) -> list[tuple[Path, bool, bool]]:
    """List entries without following symlink directories."""
    entries: list[tuple[Path, bool, bool]] = []

    with os.scandir(directory) as iterator:
        for entry in iterator:
            entry_path = Path(entry.path)
            try:
                is_symlink = entry.is_symlink()
                is_dir = entry.is_dir(follow_symlinks=False)
                is_symlink_dir = is_symlink and entry.is_dir(follow_symlinks=True)
            except OSError:
                continue

            entries.append((entry_path, is_dir, is_symlink_dir))

    return entries


async def ensure_platforms_exist() -> None:
    """Ensure all known platforms exist in the database."""
    from app.scanner.platforms import get_all_platforms

    async with get_db_context() as session:
        for platform_info in get_all_platforms():
            result = await session.execute(
                select(Platform).where(Platform.slug == platform_info.slug)
            )
            if result.scalar_one_or_none() is None:
                platform = Platform(
                    slug=platform_info.slug,
                    name=platform_info.name,
                    family=platform_info.family,
                    icon=None,
                )
                session.add(platform)
        await session.commit()
