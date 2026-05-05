from pathlib import Path
from types import SimpleNamespace

import pytest

from app.scanner import filesystem
from app.scanner.filesystem import list_directory_entries, process_rom_file, walk_directory
from app.scanner.progress import clear_scan_events, get_scan_events, record_scan_event


@pytest.mark.asyncio
async def test_walk_directory_does_not_follow_symlink_directories(tmp_path: Path) -> None:
    roms = tmp_path / "roms"
    roms.mkdir()
    nes = roms / "nes"
    nes.mkdir()

    (nes / "real-game.nes").write_bytes(b"rom")

    linked = tmp_path / "linked"
    linked.mkdir()
    (linked / "linked-game.nes").write_bytes(b"rom")
    (roms / "linked").symlink_to(linked, target_is_directory=True)

    found = []
    async for batch in walk_directory(roms):
        found.extend(path.relative_to(roms) for path in batch)

    assert found == [Path("nes/real-game.nes")]


def test_list_directory_entries_marks_symlink_directories(tmp_path: Path) -> None:
    real_dir = tmp_path / "real"
    real_dir.mkdir()
    symlink_dir = tmp_path / "symlink"
    symlink_dir.symlink_to(real_dir, target_is_directory=True)

    entries = {
        path.name: (is_dir, is_symlink_dir)
        for path, is_dir, is_symlink_dir in list_directory_entries(tmp_path)
    }

    assert entries["real"] == (True, False)
    assert entries["symlink"] == (False, True)


def test_scan_events_can_be_read_incrementally() -> None:
    job_id = 12345
    clear_scan_events(job_id)

    first = record_scan_event(job_id, "one")
    second = record_scan_event(job_id, "two", event_type="file", scanned_files=2)

    assert [event["message"] for event in get_scan_events(job_id)] == ["one", "two"]
    assert get_scan_events(job_id, after=first["sequence"]) == [second]


@pytest.mark.asyncio
async def test_large_files_are_indexed_without_full_hash(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    roms = tmp_path / "roms"
    switch = roms / "switch"
    switch.mkdir(parents=True)
    rom = switch / "large-game.nsp"
    rom.write_bytes(b"0" * 2048)

    async def fail_if_hash_is_called(file_path: Path) -> tuple[str, str]:
        raise AssertionError(f"hashing should be skipped for {file_path}")

    monkeypatch.setattr(
        filesystem,
        "get_settings",
        lambda: SimpleNamespace(scanner=SimpleNamespace(hash_size_limit_mb=0.001)),
    )
    monkeypatch.setattr(filesystem, "compute_file_hashes", fail_if_hash_is_called)

    indexed = await process_rom_file(rom, job_id=1, full_scan=True)

    assert indexed is not None
    assert indexed.path == str(rom)
    assert indexed.platform_slug == "switch"
    assert indexed.hash_sha1 is None
    assert indexed.hash_xxhash is None
