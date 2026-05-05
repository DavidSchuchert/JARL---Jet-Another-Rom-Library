"""In-memory progress events for active scan jobs."""
from collections import defaultdict, deque
from datetime import UTC, datetime
from threading import Lock
from typing import Any


MAX_EVENTS_PER_JOB = 2000

_events: dict[int, deque[dict[str, Any]]] = defaultdict(lambda: deque(maxlen=MAX_EVENTS_PER_JOB))
_last_sequence: dict[int, int] = defaultdict(int)
_lock = Lock()


def clear_scan_events(job_id: int) -> None:
    """Clear old buffered events for a scan job."""
    with _lock:
        _events.pop(job_id, None)
        _last_sequence[job_id] = 0


def record_scan_event(
    job_id: int,
    message: str,
    *,
    event_type: str = "info",
    current_file: str | None = None,
    scanned_files: int | None = None,
) -> dict[str, Any]:
    """Record a progress event that frontend polling can consume without gaps."""
    with _lock:
        _last_sequence[job_id] += 1
        event = {
            "sequence": _last_sequence[job_id],
            "type": event_type,
            "message": message,
            "current_file": current_file,
            "scanned_files": scanned_files,
            "created_at": datetime.now(UTC),
        }
        _events[job_id].append(event)
        return event


def get_scan_events(job_id: int, after: int = 0) -> list[dict[str, Any]]:
    """Return buffered scan events newer than a sequence number."""
    with _lock:
        return [event.copy() for event in _events.get(job_id, ()) if event["sequence"] > after]
