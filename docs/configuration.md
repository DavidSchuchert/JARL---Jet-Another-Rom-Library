# Configuration

All configuration is via environment variables. In Docker, edit `docker/.env`. For bare metal, use a `.env` file in `backend/` or export variables directly.

JARL uses `pydantic-settings` with double-underscore (`__`) as the nested delimiter. The format is `SECTION__KEY`.

---

## Core

| Variable | Default | Description |
|---|---|---|
| `DATABASE__URL` | `sqlite+aiosqlite:///./jarl.db` | SQLite DB path (relative to `/app/data` in Docker) |

## Scanner

| Variable | Default | Description |
|---|---|---|
| `SCANNER__ROMS_PATH` | `/roms` | Mount path of ROM directory |
| `SCANNER__WORKERS` | `4` | Parallel workers (capped at 2 when scanning NAS/network storage) |
| `SCANNER__HASH_SIZE_LIMIT_MB` | `512` | Skip SHA1 for files above this size in MiB. Set `0` to always hash all files. |
| `SCANNER__FILE_TIMEOUT_SECONDS` | `30` | Max seconds per file before skipping it |

## Scraper

| Variable | Default | Description |
|---|---|---|
| `SCRAPER__RATE_LIMIT` | `2.0` | Minimum seconds between ScreenScraper requests |
| `SCRAPER__USERNAME` | — | ScreenScraper account username |
| `SCRAPER__PASSWORD` | — | ScreenScraper account password |
| `SCRAPER__IGDB_CLIENT_ID` | — | IGDB OAuth client ID (from dev.twitch.tv) |
| `SCRAPER__IGDB_CLIENT_SECRET` | — | IGDB OAuth client secret |

## CORS

| Variable | Default | Description |
|---|---|---|
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:80` | Comma-separated list of allowed origins |

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
SCANNER__FILE_TIMEOUT_SECONDS=30

# IGDB (https://dev.twitch.tv/console/apps)
SCRAPER__IGDB_CLIENT_ID=your_client_id
SCRAPER__IGDB_CLIENT_SECRET=your_client_secret

# ScreenScraper (https://www.screenscraper.fr)
SCRAPER__USERNAME=your_username
SCRAPER__PASSWORD=your_password

# Rate limit (seconds between requests)
SCRAPER__RATE_LIMIT=2.0

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:80
```
