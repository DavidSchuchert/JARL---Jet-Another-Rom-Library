# JARL - JetAnotherRomLibrary

**Self-hosted ROM metadata manager with automatic scraping from IGDB and ScreenScraper.**

JARL scans your ROM directories, identifies games, and enriches them with metadata (cover art, description, genre, year, publisher, region) using the IGDB and ScreenScraper APIs.

---

## Features

- **Filesystem Scanner** — Recursively scans ROM directories, parses filenames, detects platforms, computes xxHash/SHA1 for deduplication
- **IGDB Integration** — Official game database via Twitch OAuth (no credentials needed for basic use)
- **ScreenScraper Integration** — Community-driven ROM database (free account required)
- **Deduplication** — Detects duplicates via file hash, skips already-processed files
- **Progress Tracking** — Live scan progress via SSE (Server-Sent Events)
- **REST API** — FastAPI backend with Swagger/ReDoc docs at `/api/docs`
- **Vue.js Frontend** — Dark-themed UI with platform browser, ROM grid, and search
- **Docker-Ready** — Single `docker compose up` to run everything

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Vue.js)                      │
│                   localhost:5173 (dev) /80                   │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP /api
┌──────────────────────────▼──────────────────────────────────┐
│                     Backend (FastAPI)                        │
│              localhost:8000 /api/docs (Swagger)              │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │  ROMs    │  │  Scan    │  │ Platform │  │  Scrape    │  │
│  │  CRUD    │  │  Engine  │  │  Mgmt    │  │  IGDB+SS   │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              SQLite (aiosqlite)                       │   │
│  │         platforms | roms | scan_jobs                 │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │ read-only mount
                    ┌──────▼──────┐
                    │  /roms      │
                    │  (ROM files)│
                    └─────────────┘
```

**Tech Stack**

| Layer      | Technology                          |
| ---------- | ----------------------------------- |
| Backend    | FastAPI 0.109, SQLAlchemy 2.0 (async), aiosqlite |
| Frontend   | Vue 3, TypeScript, Vite, Pinia, Vue Router |
| Runtime    | Python 3.11+, Node 20+              |
| Infra      | Docker Compose, nginx:alpine         |
| Metadata   | IGDB (OAuth), ScreenScraper REST API |

---

## Quick Start

### 1. Clone & Configure

```bash
git clone https://github.com/your-org/jarl.git
cd jarl
```

Copy and edit the environment file:

```bash
cp docker/.env.example docker/.env
# Edit docker/.env and set your ROM_PATH
```

### 2. Start

```bash
docker compose -f docker/docker-compose.yml up -d
```

Services:
- **Frontend**: http://localhost
- **API**: http://localhost/api/docs (Swagger UI)
- **ReDoc**: http://localhost/api/redoc

### 3. Scan Your Roms

```bash
# Trigger a scan via the UI or API
curl -X POST http://localhost:8000/api/scan/start \
  -H "Content-Type: application/json"
```

---

## Environment Variables

| Variable                     | Default                            | Description                        |
| ---------------------------- | ---------------------------------- | ---------------------------------- |
| `DATABASE__URL`              | `sqlite+aiosqlite:///./jarl.db`   | Database connection string         |
| `SCANNER__ROMS_PATH`         | `/roms`                            | Mount path of ROM directory        |
| `SCANNER__BATCH_SIZE`        | `100`                              | Files processed per batch          |
| `SCANNER__WORKERS`           | `4`                                | Parallel scanner workers            |
| `SCANNER__HASH_SIZE_LIMIT_MB`| `512`                              | Skip full hash for files above this size (MiB). `0` to disable. |
| `SCRAPER__USERNAME`          | —                                  | ScreenScraper username             |
| `SCRAPER__PASSWORD`          | —                                  | ScreenScraper password             |
| `SCRAPER__IGDB_CLIENT_ID`    | —                                  | IGDB OAuth client ID                |
| `SCRAPER__IGDB_CLIENT_SECRET`| —                                  | IGDB OAuth client secret            |
| `CORS_ORIGINS`               | `localhost:5173,localhost:80`      | Allowed CORS origins (comma-separated) |

---

## API Reference

### Health

```
GET /api/health
```

### ROMs

```
GET  /api/roms?page=1&page_size=50&platform=nes&search=zelda
GET  /api/roms/{id}
PATCH /api/roms/{id}
```

### Platforms

```
GET  /api/platforms
POST /api/platforms
```

### Scan

```
POST /api/scan/start              # Start scan job
GET  /api/scan/progress           # Live progress (SSE)
GET  /api/scan/jobs               # All jobs
DELETE /api/scan/jobs/{id}        # Cancel job
```

### Scrape

```
POST /api/scrape/rom/{id}         # Scrape single ROM
POST /api/scrape/batch?platform=nes&missing_only=true   # Batch scrape
```

Full docs at `/api/docs` (Swagger UI).

---

## Development

### Backend

```bash
cd backend

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run with hot-reload
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Dev server with hot-reload
npm run dev

# Production build
npm run build
```

### Build Docker Images

```bash
docker compose -f docker/docker-compose.yml build
```

---

## Project Structure

```
jarl/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI route modules (health, roms, scan, platforms, scrape)
│   │   ├── models.py      # SQLAlchemy ORM models
│   │   ├── schemas.py     # Pydantic request/response schemas
│   │   ├── config.py      # pydantic-settings configuration
│   │   ├── database.py    # Async SQLite setup
│   │   ├── scanner/
│   │   │   ├── filesystem.py  # ROM directory scanner
│   │   │   ├── parser.py      # Filename parser (region, year, title)
│   │   │   ├── dedup.py       # Hash-based deduplication
│   │   │   └── platforms.py  # Platform registry & mapping
│   │   └── scraper/
│   │       ├── base.py        # Abstract scraper base class
│   │       ├── igdb.py        # IGDB API client
│   │       ├── screenscraper.py # ScreenScraper API client
│   │       └── batch.py       # Batch scraping with rate limiting
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── views/        # Page components
│   │   ├── components/   # Reusable UI components
│   │   ├── stores/       # Pinia state stores
│   │   ├── api/          # Backend API client
│   │   └── router/       # Vue Router routes
│   └── dist/             # Built assets (served by nginx)
├── docker/
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── nginx.conf
│   └── .env.example
├── docs/                 # Wiki documentation
└── README.md
```

---

## Platform Support

JARL auto-detects platforms from directory structure and filenames. See [docs/platforms.md](docs/platforms.md) for the full platform list and mapping.

---

## License

MIT
