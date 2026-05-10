"""Scan API endpoints."""
import asyncio
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select

from app.auth import require_admin
from app.database import get_db_context
from app.models import ScanJob
from app.schemas import (
    ErrorResponse,
    ScanEventResponse,
    ScanJobResponse,
    ScanProgressResponse,
    ScanStartResponse,
)
from app.scanner.filesystem import scan_directory
from app.scanner.progress import clear_scan_events, get_scan_events, record_scan_event

router = APIRouter()

scan_lock = asyncio.Lock()
current_scan_task: Optional[asyncio.Task] = None


@router.post("/scan/start", response_model=ScanStartResponse, status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(require_admin)])
async def start_scan(full_scan: bool = False) -> ScanStartResponse:
    """
    Start a new ROM scan job.

    Args:
        full_scan: If True, re-hashes all files even if they haven't changed.
    """
    async with scan_lock:
        async with get_db_context() as session:
            existing_job = await session.execute(
                select(ScanJob).where(ScanJob.status == "running")
            )
            if existing_job.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A scan is already running",
                )

            job = ScanJob(
                status="running",
                total_files=0,
                scanned_files=0,
                errors=0,
                started_at=datetime.utcnow(),
            )
            session.add(job)
            await session.flush()

            job_id = job.id
            clear_scan_events(job_id)
            record_scan_event(job_id, "Scan job created", event_type="info")

    async def run_scan(job_id: int, full_scan_mode: bool) -> None:
        try:
            await scan_directory(job_id, full_scan_mode)
        except Exception as exc:
            record_scan_event(job_id, f"Scan failed: {exc}", event_type="error")
            async with get_db_context() as session:
                result = await session.execute(select(ScanJob).where(ScanJob.id == job_id))
                job = result.scalar_one_or_none()
                if job:
                    job.status = "failed"
                    job.errors += 1
                    job.completed_at = datetime.utcnow()

    global current_scan_task
    current_scan_task = asyncio.create_task(run_scan(job_id, full_scan))

    return ScanStartResponse(
        job_id=job_id,
        status="started",
        message=f"Scan job {job_id} started successfully",
        )


@router.get(
    "/scan/events/{job_id}",
    response_model=list[ScanEventResponse],
    responses={404: {"model": ErrorResponse}},
)
async def get_scan_job_events(
    job_id: int,
    after: int = Query(0, ge=0),
) -> list[ScanEventResponse]:
    """Get buffered live-uplink events for a scan job."""
    async with get_db_context() as session:
        result = await session.execute(select(ScanJob.id).where(ScanJob.id == job_id))
        if result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan job with id {job_id} not found",
            )

    return [ScanEventResponse(**event) for event in get_scan_events(job_id, after)]


@router.get("/scan/status/{job_id}", response_model=ScanJobResponse, responses={404: {"model": ErrorResponse}})
async def get_scan_status(job_id: int) -> ScanJobResponse:
    """
    Get the status of a scan job.

    Args:
        job_id: Scan job ID.

    Returns:
        ScanJobResponse with job details.

    Raises:
        HTTPException: If job not found.
    """
    async with get_db_context() as session:
        result = await session.execute(select(ScanJob).where(ScanJob.id == job_id))
        job = result.scalar_one_or_none()

        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scan job with id {job_id} not found",
            )

        return ScanJobResponse(
            id=job.id,
            status=job.status,
            total_files=job.total_files,
            scanned_files=job.scanned_files,
            current_file=job.current_file,
            errors=job.errors,
            started_at=job.started_at,
            completed_at=job.completed_at,
            progress_percentage=job.progress_percentage,
        )


@router.get("/scan/progress", response_model=ScanProgressResponse)
async def get_scan_progress() -> ScanProgressResponse:
    """
    Get the progress of the current scan.

    Returns:
        ScanProgressResponse with current job and stats.
    """
    async with get_db_context() as session:
        running_result = await session.execute(
            select(ScanJob).where(ScanJob.status == "running")
        )
        running_job = running_result.scalars().first()

        total_result = await session.execute(select(func.count(ScanJob.id)))
        total = total_result.scalar() or 0

        completed_result = await session.execute(
            select(func.count(ScanJob.id)).where(ScanJob.status == "completed")
        )
        completed = completed_result.scalar() or 0

        running_count = 1 if running_job else 0

        current_job_response = None
        if running_job:
            current_job_response = ScanJobResponse(
                id=running_job.id,
                status=running_job.status,
                total_files=running_job.total_files,
                scanned_files=running_job.scanned_files,
                current_file=running_job.current_file,
                errors=running_job.errors,
                started_at=running_job.started_at,
                completed_at=running_job.completed_at,
                progress_percentage=running_job.progress_percentage,
            )

        return ScanProgressResponse(
            current_job=current_job_response,
            total_jobs=total,
            running_jobs=running_count,
            completed_jobs=completed,
        )
