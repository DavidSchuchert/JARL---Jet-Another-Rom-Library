# JARL - JetAnotherRomLibrary

**Self-hosted ROM metadata manager with automatic scraping from ScreenScraper and IGDB.**

JARL scans your ROM directories, identifies games by filename, computes xxHash for deduplication, and enriches them with metadata (cover art, description, genre, year, publisher, region) using ScreenScraper.fr (primary) and IGDB (fallback).

---

## Features

- **Filesystem Scanner** — Recursively scans ROM directories, parses filenames, detects platforms, computes xxHash/SHA1 for deduplication
- **ScreenScraper Integration** — Hash-based and name-based lookup via ScreenScraper.fr API v2
- **IGDB Fallback** — Name-based search via Twitch OAuth (IGDB has no ROM hash lookup)
- **Deduplication** — xxHash (all files) + SHA1 (files ≤ hash limit) for duplicate detection
- **Smart Skipping** — Skips files unchanged since last scan (path + size + mtime check)
- **Progress Tracking** — Live scan events via polling (`/api/scan/events/{job_id}`)
- **Batch Scraping** — Background metadata enrichment with retry, concurrency, and cancellation
- **REST API** — FastAPI with Swagger/ReDoc at `/api/docs`
- **Vue.js Frontend** — Dark-themed UI with platform browser, ROM grid, and search
- **Docker-Ready** — Single `docker compose up`

---

## Architecture

```
Browser                      nginx:80
http://localhost ──────────► ────────────► frontend:80 (static)
                                        ► backend:8000 (API)
                                              │
                            ┌─────────────────┴─────────────────┐
                            │                                   │
                      SQLite DB                           /roms (read-only)
                      jarl.db                           ROM files on host
```

| Layer     | Technology                                   |
| --------- | -------------------------------------------- |
| Backend   | FastAPI 0.109, SQLAlchemy 2.0 (async), aiosqlite |
| Frontend  | Vue 3, TypeScript, Vite, Pinia, Vue Router |
| Runtime   | Python 3.11+, Node 20+                       |
| Infra     | Docker Compose, nginx:alpine                  |
| Metadata  | ScreenScraper.fr REST API v2, IGDB API v4   |

---

## Quick Start

### 1. Clone & Configure

```bash
git clone https://github.com/your-org/jarl.git
cd jarl

cp docker/.env.example docker/.env
# Edit docker/.env — set ROM_PATH to your ROMs directory
```

### 2. Start

```bash
docker compose -f docker/docker-compose.yml up -d
```

- **Frontend**: http://localhost
- **API**: http://localhost/api/docs (Swagger UI)
- **ReDoc**: http://localhost/api/redoc

### 3. Scan

```bash
curl -X POST http://localhost:8000/api/scan/start
```

Poll for events:

```bash
# Get events for job 1, after sequence 0
curl "http://localhost:8000/api/scan/events/1?after=0"
```

### 4. Scrape Metadata

```bash
# Batch scrape all ROMs with missing metadata
curl -X POST "http://localhost:8000/api/scrape/start?only_missing=true"

# Check progress
curl http://localhost:8000/api/scrape/status
```

---

## Directory Structure

JARL detects platforms from path segments — not folder names. The scanner splits the path by `/` and matches path parts against known slugs.

```
/roms/
├── nintendo/nes/
│   ├── Legend of Zelda (USA).nes
│   └── Super Mario Bros. 3 (Europe).nes
├── sony/psx/
│   ├── Final Fantasy VII (USA).bin
│   └── Metal Gear Solid (Europe).cue
└── sega/megadrive/
    └── Sonic The Hedgehog (USA, Europe).md
```

The scanner walks all subdirectories. No specific folder structure required — only the **file extension** and **path segments** matter for platform detection.

---

## Environment Variables

| Variable                        | Default            | Description                          |
| ------------------------------- | ------------------ | ------------------------------------ |
| `DATABASE__URL`                | `sqlite+aiosqlite:///./jarl.db` | Database connection     |
| `SCANNER__ROMS_PATH`           | `/roms`            | Mount path of ROM directory          |
| `SCANNER__WORKERS`             | `4`                | Scanner workers (capped at 2 for NAS) |
| `SCANNER__HASH_SIZE_LIMIT_MB`  | `512`              | Skip SHA1 for files above this (MiB). `0` = hash all |
| `SCANNER__FILE_TIMEOUT_SECONDS`| `30`               | Max seconds per file before skipping |
| `SCRAPER__USERNAME`           | —                  | ScreenScraper account username       |
| `SCRAPER__PASSWORD`           | —                  | ScreenScraper account password       |
| `SCRAPER__IGDB_CLIENT_ID`      | —                  | IGDB OAuth client ID (from dev.twitch.tv) |
| `SCRAPER__IGDB_CLIENT_SECRET`  | —                  | IGDB OAuth client secret              |
| `SCRAPER__RATE_LIMIT`         | `2.0`              | ScreenScraper: min seconds between requests |
| `CORS_ORIGINS`                 | `localhost:5173,localhost:80` | Allowed CORS origins   |

---

## API Reference

Base URL: `http://localhost:8000/api`

### Health

```
GET /api/health
```

### ROMs

```
GET  /api/roms?page=1&page_size=50&platform=nes&search=zelda
GET  /api/roms/{id}
GET  /api/roms/stats
DELETE /api/roms/{id}
```

### Platforms

```
GET  /api/platforms
GET  /api/platforms/{slug}
GET  /api/platforms/{slug}/roms?page=1&page_size=50
```

### Scan

```
POST /api/scan/start                    # Start scan (full_scan=false)
POST /api/scan/start?full_scan=true   # Full rescan (re-hash all)
GET  /api/scan/events/{job_id}?after=0 # Poll scan events (polling)
GET  /api/scan/status/{job_id}         # Get job details
GET  /api/scan/progress                # Current scan stats
```

### Scrape

```
POST /api/scrape/start?only_missing=true   # Batch scrape
POST /api/scrape/rom/{rom_id}             # Single ROM rescrape
GET  /api/scrape/status                    # Batch progress
POST /api/scrape/stop                     # Cancel running batch
GET  /api/scrape/test-auth                # Test credentials
```

Full docs at `/api/docs` (Swagger UI).

---

## Development

### Backend

```bash
cd backend
uv sync
uv run pytest -v
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev      # Development server
npm run build    # Production build
```

---

## Project Structure

```
jarl/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI routes
│   │   │   ├── health.py
│   │   │   ├── roms.py
│   │   │   ├── platforms.py
│   │   │   ├── scan.py
│   │   │   └── scrape.py
│   │   ├── models.py      # SQLAlchemy models
│   │   ├── schemas.py     # Pydantic schemas
│   │   ├── config.py      # pydantic-settings
│   │   ├── database.py    # Async SQLite
│   │   ├── scanner/
│   │   │   ├── filesystem.py   # ROM directory scanner
│   │   │   ├── parser.py       # Filename → title/region/year
│   │   │   ├── dedup.py        # xxHash/SHA1 deduplication
│   │   │   ├── platforms.py    # Platform registry (80+ platforms)
│   │   │   └── progress.py     # Scan event buffering
│   │   └── scraper/
│   │       ├── base.py         # Abstract scraper class
│   │       ├── screenscraper.py # ScreenScraper API v2
│   │       ├── igdb.py         # IGDB API v4 (Twitch OAuth)
│   │       └── batch.py        # Batch scraping engine
│   └── tests/
├── frontend/
│   └── src/
│       ├── views/         # HomeView, ScanView, PlatformsView, RomDetailView, ScraperTestView
│       ├── components/    # RomCard, RomGrid, ScanProgress, FilterBar, SearchBar, PlatformBadge
│       ├── stores/        # Pinia stores
│       └── api/           # API client
├── docker/
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── nginx.conf
│   └── .env.example
└── docs/
```

---

## Supported Platforms

JARL supports 80+ platforms. Key slugs:

| Slug              | Name                        | Family    |
| ----------------- | --------------------------- | --------- |
| `nes`             | Nintendo Entertainment System | Nintendo |
| `snes`            | Super Nintendo              | Nintendo |
| `n64`             | Nintendo 64                | Nintendo |
| `gamecube`        | Nintendo GameCube          | Nintendo |
| `wii`             | Nintendo Wii               | Nintendo |
| `switch`          | Nintendo Switch            | Nintendo |
| `psx`             | PlayStation                | Sony      |
| `ps2`             | PlayStation 2              | Sony      |
| `ps3`             | PlayStation 3              | Sony      |
| `psp`             | PlayStation Portable       | Sony      |
| `megadrive`       | Mega Drive / Genesis       | Sega      |
| `saturn`          | Sega Saturn               | Sega      |
| `dreamcast`       | Sega Dreamcast            | Sega      |
| `atari2600`       | Atari 2600                | Atari     |
| `gameboy`         | Game Boy                  | Nintendo  |
| `gameboyadvance`   | Game Boy Advance          | Nintendo  |
| `nds`             | Nintendo DS               | Nintendo  |
| `3ds`             | Nintendo 3DS              | Nintendo  |

See [docs/platforms.md](docs/platforms.md) for the full list.

---

## License

MIT
