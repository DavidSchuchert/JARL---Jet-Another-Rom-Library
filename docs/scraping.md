# Scraping

JARL enriches ROM metadata using two sources: **ScreenScraper.fr** (primary) and **IGDB** (fallback).

---

## How Scraping Works

The batch scraper processes each ROM in this order:

1. **ScreenScraper — Hash lookup**: If the ROM has a SHA1 hash, look up by hash via `jeuInfos.php`
2. **ScreenScraper — Name search**: If no hash match, search by cleaned title via `jeuRecherche.php`
3. **IGDB — Name search**: If ScreenScraper returns nothing, fall back to IGDB name search

A ROM's `scrape_status` field tracks the result:
- `pending` — never scraped
- `done` — metadata found
- `failed` — no match found in any source

---

## ScreenScraper.fr

**API**: `https://api.screenscraper.fr/api2`

**Credentials**: Free account at https://www.screenscraper.fr required for private/unverified game data. Anonymous access is limited to publicly verified games.

### Rate Limits

- Anonymous: ~1 request / 2 sec (60 req/min)
- Authenticated: Same — account is mainly for accessing private game data

### Getting Credentials

1. Register at https://www.screenscraper.fr (free)
2. Set in `docker/.env`:
   ```
   SCRAPER__USERNAME=your_username
   SCRAPER__PASSWORD=your_password
   ```

---

## IGDB (Twitch)

**API**: `https://api.igdb.com/v4`

**Important**: IGDB does **not** support ROM hash lookup. It only supports name-based search. IGDB is purely a fallback when ScreenScraper finds nothing.

### Getting Credentials

1. Go to https://dev.twitch.tv/console/apps
2. Click **New Application** — set a name and any OAuth redirect URI (e.g., `http://localhost`)
3. Copy **Client ID** and **Client Secret**
4. Add to `docker/.env`:
   ```
   SCRAPER__IGDB_CLIENT_ID=your_client_id
   SCRAPER__IGDB_CLIENT_SECRET=your_client_secret
   ```

IGDB requires a Twitch account but is free for up to 25,000 requests/day.

---

## Scraper Metadata Fields

For each ROM, the scraper populates:

| Field | Source | Notes |
|---|---|---|
| `title` | ScreenScraper / IGDB | |
| `description` | ScreenScraper / IGDB | Game summary |
| `year` | ScreenScraper / IGDB | Release year |
| `genre` | ScreenScraper / IGDB | Primary genre |
| `publisher` | ScreenScraper | |
| `developer` | ScreenScraper | |
| `players` | ScreenScraper | 1-4, co-op, etc. |
| `region` | Filename parser | USA, Europe, Japan, etc. |
| `cover_url` | ScreenScraper / IGDB | CDN URL to cover image |

---

## Batch Scraping

```bash
# All platforms, missing metadata only
curl -X POST "http://localhost:8000/api/scrape/start?only_missing=true"

# Specific platform
curl -X POST "http://localhost:8000/api/scrape/start?platform=nes&only_missing=true"

# Check progress
curl http://localhost:8000/api/scrape/status

# Cancel
curl -X POST http://localhost:8000/api/scrape/stop
```

Batch scraping is **concurrency=2** (two ROMs in parallel) and **rate-limited** per source.

---

## Resetting Scrape Status

To re-scrape a ROM that already has `scrape_status = "done"`:

```bash
# Delete the ROM — it will be re-added on next scan
curl -X DELETE http://localhost:8000/api/roms/{id}
```

Or manually reset via database:

```bash
docker exec jarl-backend python -c \
  "import sqlite3; c = sqlite3.connect('/app/data/jarl.db'); \
   c.execute('UPDATE roms SET scrape_status=\"pending\" WHERE id=42'); \
   c.commit()"
```

---

## Filename Parsing

Before scraping, the scanner parses the filename to extract:

- **Title** — game name
- **Region** — USA, Europe, Japan, World, etc.
- **Languages** — En, Fr, De, etc.
- **Version** — Rev 1, v1.0, etc.

Example:
```
Super Mario Bros. 3 (Europe) (En) (Rev 1).nes
                         ^^^^^^  ^^  ^^^^^
                         region  lang version
```

Parsed metadata improves match accuracy for name-based searches.
