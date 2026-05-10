"""Pydantic schemas for API request/response validation."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PlatformBase(BaseModel):
    """Base platform schema."""

    slug: str = Field(..., max_length=100, description="Platform slug identifier")
    name: str = Field(..., max_length=255, description="Platform display name")
    family: Optional[str] = Field(None, max_length=100, description="Platform family")
    icon: Optional[str] = Field(None, max_length=500, description="Icon URL or path")


class PlatformCreate(PlatformBase):
    """Schema for creating a platform."""

    pass


class PlatformResponse(PlatformBase):
    """Schema for platform response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    rom_count: int = 0


class RomBase(BaseModel):
    """Base ROM schema."""

    filename: str = Field(..., max_length=500, description="ROM filename")
    platform_slug: str = Field(..., max_length=100, description="Platform slug")
    title: str = Field(..., max_length=500, description="ROM title")
    region: Optional[str] = Field(None, max_length=100, description="Region")
    year: Optional[int] = Field(None, description="Release year")
    genre: Optional[str] = Field(None, max_length=100, description="Genre")
    players: Optional[str] = Field(None, max_length=50, description="Player count")
    developer: Optional[str] = Field(None, max_length=255, description="Developer")
    size: int = Field(..., ge=0, description="File size in bytes")


class RomCreate(RomBase):
    """Schema for creating a ROM."""

    path: str = Field(..., max_length=1000, description="Full file path")
    description: Optional[str] = Field(None, description="Description")
    publisher: Optional[str] = Field(None, max_length=255, description="Publisher")


class RomUpdate(BaseModel):
    """Schema for updating a ROM (manual edit)."""

    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    year: Optional[int] = None
    release_date: Optional[str] = Field(None, max_length=20)
    publisher: Optional[str] = Field(None, max_length=255)
    developer: Optional[str] = Field(None, max_length=255)
    genre: Optional[str] = Field(None, max_length=100)
    players: Optional[str] = Field(None, max_length=50)
    region: Optional[str] = Field(None, max_length=100)
    cover_url: Optional[str] = Field(None, max_length=1000)
    rating: Optional[float] = Field(None, ge=0, le=100)
    scrape_status: Optional[str] = Field(None, max_length=20)


class RomResponse(RomBase):
    """Schema for ROM response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    path: str
    description: Optional[str] = None
    publisher: Optional[str] = None
    hash_sha1: Optional[str] = None
    hash_xxhash: Optional[str] = None
    cover_url: Optional[str] = None
    screenshots: Optional[str] = None   # JSON list of local paths
    rating: Optional[float] = None
    languages: Optional[str] = None     # JSON list of language names
    version: Optional[str] = None
    release_date: Optional[str] = None
    scrape_status: str
    is_multi_disc: bool = False
    disc_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class RomListResponse(BaseModel):
    """Paginated ROM list response."""

    items: list[RomResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ScanJobBase(BaseModel):
    """Base scan job schema."""

    status: str = Field(..., max_length=20)
    total_files: int = Field(default=0, ge=0)
    scanned_files: int = Field(default=0, ge=0)
    current_file: Optional[str] = Field(None, max_length=1000)
    errors: int = Field(default=0, ge=0)


class ScanJobCreate(ScanJobBase):
    """Schema for creating a scan job."""

    pass


class ScanJobResponse(ScanJobBase):
    """Schema for scan job response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    progress_percentage: float


class ScanEventResponse(BaseModel):
    """A buffered scan event for the live uplink."""

    sequence: int
    type: str
    message: str
    current_file: Optional[str] = None
    scanned_files: Optional[int] = None
    created_at: datetime


class ScanProgressResponse(BaseModel):
    """Schema for scan progress response."""

    current_job: Optional[ScanJobResponse] = None
    total_jobs: int
    running_jobs: int
    completed_jobs: int


class HealthResponse(BaseModel):
    """Schema for health check response."""

    status: str
    version: str
    database: str
    uptime: float


class ScanStartResponse(BaseModel):
    """Response schema for scan start endpoint."""

    job_id: int
    status: str
    message: str


class StatsResponse(BaseModel):
    """ROM library statistics."""
    total_roms: int
    total_platforms: int
    total_size_bytes: int
    roms_with_igdb: int
    roms_with_screenscraper: int
    last_scan: Optional[str] = None


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    detail: str
    error_code: Optional[str] = None
