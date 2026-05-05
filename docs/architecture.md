# Architecture

---

## System Overview

JARL is split into two services:

```
┌──────────────────────────────────────────────────────────┐
│  Browser                                                  │
│  http://localhost                                         │
└─────────────────────┬────────────────────────────────────┘
                      │ HTTP (REST + SSE)
         ┌────────────▼────────────┐
         │  nginx :80              │
         │  Reverse proxy          │
         └────────────┬────────────┘
                      │
       ┌──────────────┴──────────────┐
       │                             │
  ┌────▼─────────┐           ┌──────▼──────┐
  │  Frontend    │           │   Backend   │
  │  Vue 3        │           │  FastAPI    │
  │  localhost    │           │  localhost   │
  │  :5173        │           │  :8000       │
  │  (static)     │           │              │
  └───────────────┘           └──────┬──────┘
                                      │
                               ┌──────▼──────┐
                               │  SQLite      │
                               │  aiosqlite  │
                               └─────────────┘
```

---

## Backend

Located in `backend/app/`.

### Entry Point

`main.py` — FastAPI app factory. Initializes CORS, registers routers, manages lifespan (startup/shutdown).

### API Routes (`app/api/`)

| Module | Responsibility |
|---|---|
| `health.py` | Health check, uptime |
| `roms.py` | ROM CRUD, pagination, filtering |
| `platforms.py` | Platform registry |
| `scan.py` | Scan job management, SSE progress |
| `scrape.py` | Metadata scraping orchestration |

### Data Layer

| File | Responsibility |
|---|---|
| `models.py` | SQLAlchemy ORM models (Platform, Rom, ScanJob) |
| `schemas.py` | Pydantic v2 schemas (request/response validation) |
| `database.py` | Async SQLite session factory, `get_db_context()` |
| `config.py` | pydantic-settings, environment variable binding |

### Scanner (`app/scanner/`)

| File | Responsibility |
|---|---|
| `filesystem.py` | Directory walker, file discovery, metadata extraction |
| `parser.py` | Filename → (title, region, year) parser using regex |
| `dedup.py` | xxHash/SHA1 deduplication checks |
| `platforms.py` | Platform slug registry, extension mappings |
| `progress.py` | SSE event buffering for live progress |

### Scraper (`app/scraper/`)

| File | Responsibility |
|---|---|
| `base.py` | Abstract `Scraper` class, rate limiting |
| `igdb.py` | IGDB API client via Twitch OAuth |
| `screenscraper.py` | ScreenScraper REST API client |
| `batch.py` | Batch scrape queue with retry logic |

---

## Frontend

Located in `frontend/src/`. Vue 3 with TypeScript, Vite, Pinia (stores), Vue Router.

```
src/
├── main.ts           # App bootstrap
├── App.vue           # Root component
├── views/            # Page-level components
│   ├── HomeView.vue
│   └── PlatformView.vue
├── components/       # Reusable UI components
│   ├── RomCard.vue
│   ├── PlatformBadge.vue
│   └── ScanProgress.vue
├── stores/           # Pinia state stores
│   ├── roms.ts
│   └── scan.ts
├── api/              # Backend API client
│   └── index.ts
└── router/
    └── index.ts
```

---

## Data Model

```
┌──────────────┐       ┌──────────────────────┐
│  Platform    │  1:N  │        Rom           │
│──────────────│◄──────│──────────────────────│
│ id (PK)      │       │ id (PK)              │
│ slug (unique)│       │ path                 │
│ name         │       │ platform_slug (FK)   │
│ family       │       │ title                │
│ icon         │       │ description          │
└──────────────┘       │ year, genre, region │
                       │ publisher, developer│
                       │ size, mtime         │
                       │ hash_sha1, hash_xx │
                       │ cover_url           │
                       │ scrape_status       │
                       │ created_at, updated_at│
                       └──────────────────────┘

┌──────────────────────────┐
│       ScanJob            │
│──────────────────────────│
│ id (PK)                  │
│ status (pending/running/ │
│           completed/failed│
│ total_files              │
│ scanned_files            │
│ errors                   │
│ started_at, completed_at │
└──────────────────────────┘
```

---

## Scan Flow

```
POST /api/scan/start
       │
       ▼
┌─────────────────────────┐
│ 1. Create ScanJob (DB)  │
│ 2. Return job_id        │
└──────────┬──────────────┘
           │ async background task
           ▼
┌─────────────────────────┐
│ 3. Walk /roms/          │
│    (filesystem.py)      │
│                         │
│    For each file:       │
│    a) Parse filename    │
│    b) Detect platform   │
│    c) Compute hash       │
│    d) Check dedup        │
│    e) Insert/update ROM │
│    f) Emit SSE event    │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ 4. Mark job completed   │
│ 5. SSE "complete" event │
└─────────────────────────┘
```

---

## Deduplication

Two ROMs are considered duplicates if they share the same `hash_xxhash` (fast) **or** `hash_sha1` (full file).

The scanner computes `xxhash` for all files regardless of size. SHA1 is computed only for files below `SCANNER__HASH_SIZE_LIMIT_MB` (default 512 MiB). Larger files get `hash_sha1 = null`.

When a duplicate is found:
- If the existing ROM has more metadata, skip the new file
- If the new file has more metadata, update the existing entry
- If equal, keep the first-seen entry
