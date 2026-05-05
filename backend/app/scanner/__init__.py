"""Scanner module for ROM file discovery and processing."""
from app.scanner.filesystem import scan_directory
from app.scanner.parser import parse_filename
from app.scanner.dedup import check_duplicate_hash
from app.scanner.platforms import get_platform_by_extension, get_all_platforms

__all__ = [
    "scan_directory",
    "parse_filename",
    "check_duplicate_hash",
    "get_platform_by_extension",
    "get_all_platforms",
]
