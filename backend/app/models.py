"""SQLAlchemy database models."""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Platform(Base):
    """Platform model representing a gaming platform/system."""

    __tablename__ = "platforms"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    family: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    roms: Mapped[list["Rom"]] = relationship(back_populates="platform", lazy="selectin")

    __table_args__ = (Index("ix_platforms_family", "family"),)

    def __repr__(self) -> str:
        return f"<Platform(slug={self.slug}, name={self.name})>"


class Rom(Base):
    """Rom model representing a ROM file."""

    __tablename__ = "roms"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    path: Mapped[str] = mapped_column(String(1000), nullable=False)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    platform_slug: Mapped[str] = mapped_column(
        String(100), ForeignKey("platforms.slug", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    year: Mapped[Optional[int]] = mapped_column(nullable=True)
    genre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    players: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    developer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    publisher: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    size: Mapped[int] = mapped_column(nullable=False)
    mtime: Mapped[Optional[float]] = mapped_column(nullable=True)
    hash_sha1: Mapped[Optional[str]] = mapped_column(String(40), nullable=True, index=True)
    hash_xxhash: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    igdb_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    screenscraper_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    cover_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    screenshots: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list of local paths
    rating: Mapped[Optional[float]] = mapped_column(nullable=True)  # 0-100 scale
    languages: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list of language names
    version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    release_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # YYYY-MM-DD
    scrape_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )
    is_multi_disc: Mapped[bool] = mapped_column(nullable=False, default=False)
    disc_count: Mapped[Optional[int]] = mapped_column(nullable=True)
    is_favorite: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_played: Mapped[bool] = mapped_column(nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    platform: Mapped[Platform] = relationship(back_populates="roms", lazy="selectin")

    __table_args__ = (
        Index("ix_roms_platform_region", "platform_slug", "region"),
        Index("ix_roms_platform_year", "platform_slug", "year"),
        Index("ix_roms_platform_genre", "platform_slug", "genre"),
        Index("ix_roms_title", "title"),
        Index("ix_roms_scrape_status", "scrape_status"),
        Index("ix_roms_platform_title", "platform_slug", "title"),
    )

    def __repr__(self) -> str:
        return f"<Rom(id={self.id}, title={self.title}, platform={self.platform_slug})>"


class AppConfig(Base):
    """Key-value store for runtime configuration overrides."""

    __tablename__ = "app_config"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)


class ScanJob(Base):
    """ScanJob model representing a ROM scanning operation."""

    __tablename__ = "scan_jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="running")
    total_files: Mapped[int] = mapped_column(nullable=False, default=0)
    scanned_files: Mapped[int] = mapped_column(nullable=False, default=0)
    current_file: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    errors: Mapped[int] = mapped_column(nullable=False, default=0)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (Index("ix_scan_jobs_status", "status"),)

    def __repr__(self) -> str:
        return f"<ScanJob(id={self.id}, status={self.status}, progress={self.scanned_files}/{self.total_files})>"

    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.scanned_files / self.total_files) * 100


class User(Base):
    """User model for multi-user authentication."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="viewer")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"
