<p align="center">
  <img src="frontend/src/assets/Logo_white.svg" alt="JARL Logo" width="200">
</p>

# JARL - JetAnotherRomLibrary

**Self-hosted ROM metadata manager with automatic scraping from ScreenScraper and IGDB. JWT-protected API.**

JARL scans your ROM directories, identifies games by filename, computes xxHash for deduplication, and enriches them with metadata (cover art, description, genre, year, publisher, region) using ScreenScraper.fr (primary) and IGDB (fallback).

---

## Features

- **Filesystem Scanner** — Recursively scans ROM directories, parses filenames, detects platforms, computes xxHash/SHA1 for deduplication
- **Multi-Disc Support** — Automatic grouping of .cue/.m3u multi-disc games (PS1, Saturn, Sega CD)
- **ScreenScraper Integration** — Hash-based and name-based lookup via ScreenScraper.fr API v2
- **IGDB Fallback** — Name-based search via Twitch OAuth (IGDB has no ROM hash lookup)
- **Local Media Storage** — Cover art and screenshots downloaded and served locally (no broken external links)
- **Rich Metadata** — Rating (0–100), genre, region, publisher, developer, languages, release date, version
- **Favorites & Played** — Mark games as favorite (♥) or played (✓) with one click, filter by status
- **Statistics Dashboard** — Library overview widget with total size, scrape coverage, top platforms chart
- **Multi-User Support** — Multiple users with admin/viewer roles, password management, role-based access control
- **Deduplication** — xxHash (all files) + SHA1 (files ≤ hash limit) for duplicate detection
- **Smart Skipping** — Skips files unchanged since last scan (path + size + mtime check)
- **Orphan Cleanup** — Automatically removes DB entries for ROMs deleted from disk
- **Progress Tracking** — Live scan events via polling (`GET /api/scan/events/{job_id}`)
- **Live Scrape Preview** — Real-time cover thumbnail and title during batch scraping
- **Batch Scraping** — Background metadata enrichment with retry, concurrency, and cancellation
- **Manual Metadata Edit** — PATCH any ROM's metadata via API or the built-in edit modal
- **Sort & Filter** — Sort by title, year, rating, size; filter by platform, region, favorites, played status
- **Skeleton Loading** — Smooth loading states with animated placeholder cards
- **JWT Authentication** — All API endpoints (except `/auth/*` and `/health`) require a valid Bearer token
- **REST API** — FastAPI with Swagger/ReDoc at `/api/docs`
- **Vue.js Frontend** — Retro-arcade dark UI with platform browser, ROM grid, detail pages, and search
- **Mobile-Ready** — Responsive layout with bottom tab bar and hamburger menu
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
| Auth      | JWT (HS256) + RBAC (admin / viewer roles)     |

> **SQLite note:** JARL uses SQLite with WAL mode, which handles multiple concurrent readers well. Concurrent heavy writes (e.g. running a full scan and batch scrape simultaneously) may cause brief lock contention — this is handled with retries internally. For high-concurrency environments, PostgreSQL support can be added by swapping the `DATABASE__URL`.

---

## Quick Start

### 1. Clone & Configure

```bash
git clone https://github.com/DavidSchuchert/JARL---Jet-Another-Rom-Library.git
cd JARL---Jet-Another-Rom-Library

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

## Authentication & Users

JARL uses **JWT (HS256)** with **role-based access control**. Two roles exist:

| Role | Permissions |
|---|---|
| **admin** | Full access — scan, scrape, manage users, edit/delete ROMs |
| **viewer** | Read-only — browse, search, filter, mark favorites/played |

On first startup, an admin user is created from `AUTH__USERNAME` / `AUTH__PASSWORD` env vars. Additional users can be created via the Settings page or API.

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
| `SCRAPER__SS_DEV_ID`          | `Greenfreeze`      | ScreenScraper developer ID (optional) |
| `SCRAPER__SS_DEV_PASSWORD`    | —                  | ScreenScraper developer password (optional) |
| `SCRAPER__SS_SOFTNAME`        | `jarl`             | ScreenScraper softname               |
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
POST  /api/auth/login      # Get JWT token
GET   /api/auth/me         # Validate token + role
PATCH /api/auth/password   # Change own password
```

### Users (admin only)

```
GET    /api/users          # List all users
POST   /api/users          # Create user (username, password, role)
DELETE /api/users/{id}     # Delete user (cannot delete self)
```

### Health

```
GET /api/health
```

### ROMs

```
GET    /api/roms?page=1&page_size=50&platform=nes&search=zelda&sort_by=title&sort_dir=asc&favorites=true&played=false
GET    /api/roms/{id}
GET    /api/roms/stats         # Library stats (total, size, coverage, top platforms)
PATCH  /api/roms/{id}          # Update metadata (title, description, year, rating, …)
PATCH  /api/roms/{id}/favorite # Toggle favorite status
PATCH  /api/roms/{id}/played   # Toggle played status
DELETE /api/roms/{id}          # Also deletes local cover / screenshot files
```

### Platforms

```
GET  /api/platforms
GET  /api/platforms/{slug}
GET  /api/platforms/{slug}/roms?page=1&page_size=50
```

### Scan

```
POST /api/scan/start               # Admin only
POST /api/scan/start?full_scan=true # Admin only
GET  /api/scan/events/{job_id}?after=0
GET  /api/scan/status/{job_id}
GET  /api/scan/progress
```

### Scrape

```
POST /api/scrape/start?only_missing=true  # Admin only
POST /api/scrape/rom/{rom_id}             # Admin only
GET  /api/scrape/status
POST /api/scrape/stop                     # Admin only
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
│   │   │   ├── auth.py       # Login / me / password
│   │   │   ├── health.py
│   │   │   ├── roms.py       # CRUD, stats, favorites, played
│   │   │   ├── platforms.py
│   │   │   ├── scan.py
│   │   │   ├── scrape.py
│   │   │   └── users.py      # User management (admin)
│   │   ├── auth.py          # JWT utilities, RBAC (get_current_user, require_admin)
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

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for local dev setup, project structure, and contribution guidelines.

Bug reports and feature requests → [GitHub Issues](https://github.com/DavidSchuchert/JARL---Jet-Another-Rom-Library/issues).

---

## License

[MIT](LICENSE) © 2024 David Schuchert
