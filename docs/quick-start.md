# Quick Start

Get JARL running and your first ROMs scanned in 5 minutes.

---

## 1. Prerequisites

- Docker & Docker Compose installed
- ROMs directory on your host

## 2. Configure & Start

```bash
git clone https://github.com/your-org/jarl.git
cd jarl

cp docker/.env.example docker/.env
# Set ROM_PATH to your ROMs directory in docker/.env

docker compose -f docker/docker-compose.yml up -d
```

## 3. Open the UI

```
http://localhost
```

## 4. Scan

Click **"Scan Library"** in the UI, or:

```bash
curl -X POST http://localhost:8000/api/scan/start
```

Poll for live progress:

```bash
curl "http://localhost:8000/api/scan/events/1?after=0"
```

## 5. Scrape Metadata

Once scanned, enrich your ROMs with metadata:

```bash
# Scrape all ROMs missing metadata
curl -X POST "http://localhost:8000/api/scrape/start?only_missing=true"

# Check progress
curl http://localhost:8000/api/scrape/status

# Cancel if needed
curl -X POST http://localhost:8000/api/scrape/stop
```

Or click **"Scrape All"** in the UI.

## 6. Browse

Navigate platforms in the sidebar. Search by title with the search bar.

---

## Next Steps

- [Add ScreenScraper credentials](scraping.md#screenscraper) — required for private/unverified games
- [Add IGDB credentials](scraping.md#igdb) — improves coverage for Western commercial titles
- [Configure hash size limit](configuration.md#scanner) — set to `0` to always compute SHA1 for deduplication
- [Browse all platforms](platforms.md)
