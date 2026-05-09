"""Image download and local storage utilities."""
import logging
import os
from pathlib import Path
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)

DATA_DIR = Path("/app/data")
COVERS_DIR = DATA_DIR / "covers"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"

MEDIA_PREFIX = "/media"


def ensure_media_dirs() -> None:
    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def _ext_from_url(url: str, default: str = ".jpg") -> str:
    path = urlparse(url).path
    suffix = Path(path).suffix.lower()
    return suffix if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif"} else default


async def download_cover(rom_id: int, url: str) -> str | None:
    """Download cover image and return the local serve path."""
    ensure_media_dirs()
    ext = _ext_from_url(url)
    filename = f"{rom_id}_cover{ext}"
    dest = COVERS_DIR / filename

    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                logger.warning(f"Cover download failed ({resp.status_code}) for ROM {rom_id}: {url}")
                return None
            dest.write_bytes(resp.content)
        return f"{MEDIA_PREFIX}/covers/{filename}"
    except Exception as e:
        logger.warning(f"Cover download error for ROM {rom_id}: {e}")
        return None


async def download_screenshots(rom_id: int, urls: list[str], max_count: int = 3) -> list[str]:
    """Download screenshot images and return local serve paths."""
    ensure_media_dirs()
    paths: list[str] = []

    for i, url in enumerate(urls[:max_count]):
        ext = _ext_from_url(url)
        filename = f"{rom_id}_ss_{i}{ext}"
        dest = SCREENSHOTS_DIR / filename
        try:
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    dest.write_bytes(resp.content)
                    paths.append(f"{MEDIA_PREFIX}/screenshots/{filename}")
        except Exception as e:
            logger.warning(f"Screenshot download error for ROM {rom_id} index {i}: {e}")

    return paths
