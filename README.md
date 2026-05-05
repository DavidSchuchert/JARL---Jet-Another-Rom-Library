<p align="center">
  <img src="frontend/src/assets/JARL_Logo.svg" alt="JARL Logo" width="200">
</p>

# JARL - JetAnotherRomLibrary

**Self-hosted ROM metadata manager with automatic scraping from ScreenScraper and IGDB. JWT-protected API.**

JARL scans your ROM directories, identifies games by filename, computes xxHash for deduplication, and enriches them with metadata (cover art, description, genre, year, publisher, region) using ScreenScraper.fr (primary) and IGDB (fallback).

---

## Features

- **Filesystem Scanner** — Recursively scans ROM directories, parses filenames, detects platforms, computes xxHash/SHA1 for deduplication
- **ScreenScraper Integration** — Hash-based and name-based lookup via ScreenScraper.fr API v2
- **IGDB Fallback** — Name-based search via Twitch OAuth (IGDB has no ROM hash lookup)
- **Deduplication** — xxHash (all files) + SHA1 (files ≤ hash limit) for duplicate detection
- **Smart Skipping** — Skips files unchanged since last scan (path + size + mtime check)
- **Progress Tracking** — Live scan events via polling (`GET /api/scan/events/{job_id}`)
- **Batch Scraping** — Background metadata enrichment with retry, concurrency, and cancellation
- **JWT Authentication** — All API endpoints (except `/auth/*` and `/health`) require a valid Bearer token
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
| Auth      | JWT (HS256) — all protected endpoints        |

---

## Quick Start

### 1. Clone & Configure

```bash
git clone https://github.com/your-org/jarl.git
cd jarl

cp docker/.env.example docker/.env
# Edit docker/.env — set ROM_PATH, AUTH__USERNAME, AUTH__PASSWORD
```

### 2. Start

```bash
docker compose -f docker/docker-compose.yml up -d
```

- **Frontend**: http://localhost
- **API**: http://localhost/api/docs (Swagger UI)
- **ReDoc**: http://localhost/api/redoc

### 3. Login

JARL requires authentication for all API endpoints (except `/auth/login`, `/auth/me`, `/health`).

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=admin" \
  -d "password=your_password"
```

Response:
```json
{"access_token": "eyJ...", "token_type": "bearer"}
```

Use the token in subsequent requests:

```bash
curl -X POST http://localhost:8000/api/scan/start \
  -H "Authorization: Bearer eyJ..."
```

### 4. Scan

```bash
curl -X POST http://localhost:8000/api/scan/start \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Poll for events:

```bash
curl "http://localhost:8000/api/scan/events/1?after=0" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Scrape Metadata

```bash
# Batch scrape all ROMs with missing metadata
curl -X POST "http://localhost:8000/api/scrape/start?only_missing=true" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check progress
curl http://localhost:8000/api/scrape/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Authentication

JARL uses **JWT (HS256)** for API authentication. All endpoints except the following are protected:

| Endpoint | Method | Protected |
|---|---|---|
| `/api/auth/login` | POST | No — returns JWT |
| `/api/auth/me` | GET | No — validates token |
| `/api/health` | GET | No |
| `/` | GET | No |

Default credentials: `admin` / `admin`. **Change these in production!**

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

The scanner walks all subdirectories. Only the **file extension** and **path segments** matter for platform detection.

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
| `AUTH__USERNAME`              | `admin`            | API login username                   |
| `AUTH__PASSWORD`              | `admin`            | API login password                   |
| `AUTH__TOKEN_EXPIRE_MINUTES`  | `1440`             | JWT token expiration (minutes)       |
| `SECRET_KEY`                  | `change-this-in-production` | JWT signing secret — **must change in production** |
| `CORS_ORIGINS`                 | `localhost:5173,localhost:80` | Allowed CORS origins   |

---

## API Reference

Base URL: `http://localhost:8000/api`

> **All endpoints except `/auth/*`, `/health`, and `/` require a `Bearer` token.**

### Auth

```
POST /api/auth/login    # Get JWT token
GET  /api/auth/me      # Validate token
```

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
POST /api/scan/start
POST /api/scan/start?full_scan=true
GET  /api/scan/events/{job_id}?after=0
GET  /api/scan/status/{job_id}
GET  /api/scan/progress
```

### Scrape

```
POST /api/scrape/start?only_missing=true
POST /api/scrape/rom/{rom_id}
GET  /api/scrape/status
POST /api/scrape/stop
GET  /api/scrape/test-auth
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
│   │   │   ├── auth.py       # Login / me
│   │   │   ├── health.py
│   │   │   ├── roms.py
│   │   │   ├── platforms.py
│   │   │   ├── scan.py
│   │   │   └── scrape.py
│   │   ├── auth.py          # JWT utilities (verify, create_token)
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── config.py        # pydantic-settings
│   │   ├── database.py       # Async SQLite
│   │   ├── scanner/
│   │   │   ├── filesystem.py
│   │   │   ├── parser.py
│   │   │   ├── dedup.py
│   │   │   ├── platforms.py
│   │   │   └── progress.py
│   │   └── scraper/
│   │       ├── base.py
│   │       ├── screenscraper.py
│   │       ├── igdb.py
│   │       └── batch.py
│   └── tests/
├── frontend/
│   └── src/
│       ├── views/
│       ├── components/
│       ├── stores/        # Pinia (includes auth.ts)
│       └── api/
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

| Slug                | Name                          | Family    |
| ------------------- | ---------------------------- | --------- |
| `nes`              | Nintendo Entertainment System | Nintendo |
| `snes`             | Super Nintendo               | Nintendo |
| `n64`             | Nintendo 64                  | Nintendo |
| `gamecube`         | Nintendo GameCube            | Nintendo |
| `wii`             | Nintendo Wii                | Nintendo |
| `switch`           | Nintendo Switch              | Nintendo |
| `psx`             | PlayStation                 | Sony      |
| `ps2`             | PlayStation 2               | Sony      |
| `ps3`             | PlayStation 3               | Sony      |
| `psp`             | PlayStation Portable         | Sony      |
| `megadrive`        | Mega Drive / Genesis        | Sega      |
| `saturn`           | Sega Saturn                | Sega      |
| `dreamcast`        | Sega Dreamcast             | Sega      |
| `atari2600`        | Atari 2600                | Atari     |
| `gameboy`          | Game Boy                  | Nintendo  |
| `gameboyadvance`   | Game Boy Advance          | Nintendo  |
| `nds`             | Nintendo DS               | Nintendo  |
| `3ds`             | Nintendo 3DS              | Nintendo  |

See [docs/platforms.md](docs/platforms.md) for the full list.

---

## License

MIT
