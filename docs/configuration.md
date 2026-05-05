# Configuration

All configuration is via environment variables. In Docker, edit `docker/.env`. For bare metal, use a `.env` file in `backend/` or export variables directly.

---

## Core Settings

| Variable | Default | Description |
|---|---|---|
| `APP__NAME` | `JARL` | Application display name |
| `APP__VERSION` | `1.0.0` | Version string |
| `APP__DEBUG` | `false` | Enable debug mode (verbose logs) |
| `DATABASE__URL` | `sqlite+aiosqlite:///./jarl.db` | SQLite DB path (relative to `/app/data` in Docker) |

## Scanner

| Variable | Default | Description |
|---|---|---|
| `SCANNER__ROMS_PATH` | `/roms` | Mount path of ROM directory |
| `SCANNER__BATCH_SIZE` | `100` | Files processed per batch |
| `SCANNER__WORKERS` | `4` | Parallel worker count |
| `SCANNER__HASH_SIZE_LIMIT_MB` | `512` | Skip full-file hash for files larger than this (MiB). Set `0` to hash all files. |
| `SCANNER__FILE_TIMEOUT_SECONDS` | `30` | Max seconds per file before skipping |

## Scraper

| Variable | Default | Description |
|---|---|---|
| `SCRAPER__API_URL` | `https://www.screenscraper.fr/api2` | ScreenScraper endpoint |
| `SCRAPER__RATE_LIMIT` | `2.0` | Seconds between requests |
| `SCRAPER__USERNAME` | — | ScreenScraper username |
| `SCRAPER__PASSWORD` | — | ScreenScraper password |
| `SCRAPER__IGDB_CLIENT_ID` | — | IGDB OAuth client ID |
| `SCRAPER__IGDB_CLIENT_SECRET` | — | IGDB OAuth client secret |

### Getting IGDB Credentials

1. Register at https://dev.twitch.tv/console
2. Create an application — set name and OAuth redirect URI
3. Copy Client ID and Client Secret into your `.env`

### ScreenScraper Credentials

A free account at https://www.screenscraper.fr is required for private/unverified game data. Anonymous access is read-only for publicly verified games.

## CORS

| Variable | Default | Description |
|---|---|---|
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:80` | Comma-separated allowed origins |

---

## Example .env

```bash
# Paths
ROM_PATH=/home/david/roms

# Database
DATABASE__URL=sqlite+aiosqlite:///./jarl.db

# Scanner
SCANNER__ROMS_PATH=/roms
SCANNER__WORKERS=4
SCANNER__HASH_SIZE_LIMIT_MB=512

# IGDB
SCRAPER__IGDB_CLIENT_ID=your_client_id
SCRAPER__IGDB_CLIENT_SECRET=your_client_secret

# ScreenScraper
SCRAPER__USERNAME=your_username
SCRAPER__PASSWORD=your_password

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:80
```
