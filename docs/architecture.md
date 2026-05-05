# Architecture

---

## System Overview

```
Browser
http://localhost ──────► nginx:80
                              │
                    ┌─────────┴─────────┐
                    │                   │
               frontend:80          backend:8000
               (Vue.js static)       (FastAPI)
                                        │
                               ┌────────┴────────┐
                               │                  │
                          SQLite DB          /roms (RO mount)
                          jarl.db           ROM files on host
```

---

## Authentication

All API routes (except `/auth/*`, `/health`, `/`) are protected via JWT Bearer token dependency injection using FastAPI's `Depends(get_current_user)`.

```
Unprotected:  POST /auth/login, GET /auth/me, GET /health, GET /
Protected:   all /roms/*, /platforms/*, /scan/*, /scrape/*
```

JWT is signed with HS256 using `settings.secret_key`. Tokens expire after `AUTH__TOKEN_EXPIRE_MINUTES` (default 24h).

---

## Backend

Located in `backend/app/`.

### API Routes (`app/api/`)

| Module | Responsibility |
|---|---|
| `auth.py` | Login (`/auth/login`), token validation (`/auth/me`) |
| `health.py` | Health check, version, uptime |
| `roms.py` | ROM CRUD, pagination, filtering, stats |
| `platforms.py` | Platform registry, per-platform ROM listing |
| `scan.py` | Scan job management, event polling |
| `scrape.py` | Batch scraping, auth testing |

### Auth (`app/auth.py`)

JWT utilities: `create_access_token()`, `verify_password()`, `get_password_hash()`, `get_current_user` (FastAPI dependency).

### Data Layer

| File | Responsibility |
|---|---|
| `models.py` | SQLAlchemy ORM models (Platform, Rom, ScanJob) |
| `schemas.py` | Pydantic v2 schemas (request/response validation) |
| `database.py` | Async SQLite session factory via `get_db_context()` |
| `config.py` | pydantic-settings — env binding with `__` delimiter |

### Scanner (`app/scanner/`)

| File | Responsibility |
|---|---|
| `filesystem.py` | Directory walker, file discovery, batch processing |
| `parser.py` | Filename → (title, region, year, languages, version) |
| `dedup.py` | xxHash/SHA1 deduplication checks |
| `platforms.py` | Platform registry — 80+ platforms with extensions and path patterns |
| `progress.py` | In-memory scan event buffer |

### Scraper (`app/scraper/`)

| File | Responsibility |
|---|---|
| `base.py` | Abstract `BaseScraper` class, `ScraperResult` dataclass |
| `screenscraper.py` | ScreenScraper.fr API v2 — hash + name lookup |
| `igdb.py` | IGDB API v4 via Twitch OAuth — name search only |
| `batch.py` | Batch scraping engine — concurrency, retry, progress tracking |

---

## Frontend

Located in `frontend/src/`. Vue 3 + TypeScript + Vite + Pinia + Vue Router.

```
src/
├── views/
│   ├── HomeView.vue       # ROM grid with filter bar
│   ├── ScanView.vue       # Scan trigger + live progress
│   ├── PlatformsView.vue  # Platform listing
│   ├── RomDetailView.vue  # Single ROM detail
│   └── ScraperTestView.vue # Scraper auth testing
├── components/
│   ├── RomCard.vue, RomGrid.vue, ScanProgress.vue
│   ├── FilterBar.vue, SearchBar.vue, PlatformBadge.vue
├── stores/
│   ├── auth.ts           # JWT login/logout, token in localStorage
│   └── ...
└── api/
```

Routes:
- `/` — HomeView
- `/roms/:id` — RomDetailView
- `/platforms` — PlatformsView
- `/scan` — ScanView
- `/scraper-test` — ScraperTestView

---

## Data Model

```
Platform
├── id (PK)
├── slug (unique, indexed)
├── name
├── family
└── icon

Rom
├── id (PK)
├── path (unique)
├── filename
├── platform_slug (FK → Platform.slug)
├── title, description, year, genre
├── publisher, developer, players
├── region
├── size, mtime
├── hash_sha1 (indexed), hash_xxhash (indexed)
├── igdb_id, screenscraper_id
├── cover_url
├── scrape_status  -- "pending" | "done" | "failed"
├── created_at, updated_at

ScanJob
├── id (PK)
├── status          -- "running" | "completed" | "failed"
├── total_files, scanned_files, errors
├── current_file
├── started_at, completed_at
```

---

## Scan Flow

```
POST /api/scan/start
       │
       ▼
┌──────────────────────────────────┐
│ 1. Create ScanJob (DB)           │
│ 2. Count total ROM files          │
│ 3. Return job_id=5, status=started│
└──────────────┬───────────────────┘
              │ async background task
              ▼
┌──────────────────────────────────┐
│ walk_directory()                  │
│   AsyncDirectoryWalker queue       │
│   Yields batches of BATCH_SIZE=100│
│                                    │
│ For each file:                    │
│   a) Skip if path+size+mtime      │
│      matches existing DB entry     │
│   b) Compute xxhash (always)      │
│   c) Compute sha1 if size <= limit│
│   d) Check dedup via xxhash       │
│   e) Detect platform from path    │
│   f) Parse filename               │
│   g) Record scan event            │
│   h) Save batch to DB every 100   │
└──────────────┬───────────────────┘
              │
              ▼
┌──────────────────────────────────┐
│ Mark job completed                 │
│ Record "success" scan event        │
└──────────────────────────────────┘
```

---

## Deduplication

Two files are considered duplicates if they share the same `hash_xxhash`.

- **xxhash**: computed for **all** files (fast, streaming)
- **SHA1**: computed only for files ≤ `SCANNER__HASH_SIZE_LIMIT_MB` (default 512 MiB). Set to `0` to always compute SHA1.

---

## Smart Skipping

If `full_scan=false` (default), the scanner skips any file where **all three** match an existing DB entry:
- `path` equals stored path
- `size` equals stored size
- `mtime` equals stored mtime

---

## Scan Events (Polling)

Scan progress uses **polling** via `GET /api/scan/events/{job_id}?after=N`. Events are stored in an in-memory circular buffer in `progress.py` (per job, sequence-numbered).
