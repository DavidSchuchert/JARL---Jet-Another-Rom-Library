# Scraper

JARL can enrich ROM metadata using two data sources: **IGDB** and **ScreenScraper**.

---

## Data Sources Compared

| | IGDB | ScreenScraper |
|---|---|---|
| **Coverage** | Commercial, major titles | Homebrew, obscure, ROM hacks |
| **Credentials** | OAuth (free, dev.twitch.tv) | Free account (screenscraper.fr) |
| **Rate limit** | 4 requests/sec (OAuth) | ~1 request/2 sec (anonymous) |
| **Data** | Title, year, genre, summary, cover | + region, players, publisher, developer |
| **Best for** | Mainstream Western releases | Japanese/European exclusives |

JARL tries **IGDB first**, then falls back to **ScreenScraper** if IGDB returns no match.

---

## Getting Credentials

### IGDB (Recommended)

1. Go to https://dev.twitch.tv/console/apps
2. Click **New Application**
3. Set a name and an OAuth redirect URI (e.g., `http://localhost`)
4. Copy **Client ID** and **Client Secret**
5. Add to `docker/.env`:
   ```
   SCRAPER__IGDB_CLIENT_ID=your_client_id
   SCRAPER__IGDB_CLIENT_SECRET=your_client_secret
   ```

IGDB requires a Twitch account but is free for up to 25,000 requests/day.

### ScreenScraper

1. Register at https://www.screenscraper.fr (free)
2. Set credentials in `docker/.env`:
   ```
   SCRAPER__USERNAME=your_username
   SCRAPER__PASSWORD=your_password
   ```

Without credentials, ScreenScraper only returns publicly verified game data. Private/unverified games require an account.

---

## Scrape Fields

For each ROM, the scraper attempts to populate:

| Field | Source | Notes |
|---|---|---|
| `title` | IGDB / ScreenScraper | |
| `description` | IGDB / ScreenScraper | Game summary |
| `year` | IGDB / ScreenScraper | Release year |
| `genre` | IGDB / ScreenScraper | Primary genre |
| `publisher` | ScreenScraper | |
| `developer` | ScreenScraper | |
| `players` | ScreenScraper | 1-4, co-op, etc. |
| `region` | Filename parser | USA, Europe, Japan, etc. |
| `cover_url` | IGDB / ScreenScraper | CDN URL to cover image |

---

## Batch Scraping

To fill in missing metadata for all ROMs:

```bash
# All platforms, missing only
curl -X POST "http://localhost:8000/api/scrape/batch?missing_only=true"

# Specific platform
curl -X POST "http://localhost:8000/api/scrape/batch?platform=nes"

# Prefer ScreenScraper first
curl -X POST "http://localhost:8000/api/scrape/batch?platform=snes&priority=screenscraper"
```

Batch scraping is **rate-limited** per source to avoid being blocked.

---

## Cache

Scrape results are stored in the SQLite database. A ROM with `scrape_status = "done"` is not re-scraped unless you manually reset it:

```bash
# Reset a single ROM to pending
curl -X PATCH http://localhost:8000/api/roms/42 \
  -H "Content-Type: application/json" \
  -d '{"scrape_status": "pending"}'
```

---

## Filename Parsing

Before scraping, JARL parses the filename to extract:

- **Title** — game name
- **Region** — USA, Europe, Japan, World, etc.
- **Year** — 4-digit year if present
- **Revision/Version** — Rev 1, v1.0, etc.

Example:
```
Super Mario Bros. 3 (Europe) (Rev 1).nes
                         ^^^^^^^
                         region
```

This parsed data is used to improve scraper match accuracy.
