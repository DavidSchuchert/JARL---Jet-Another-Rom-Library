# Quick Start

Get JARL running and your first ROMs scanned in 5 minutes.

---

## 1. Prerequisites

- Docker & Docker Compose installed
- ROMs directory on your host

## 2. Start JARL

```bash
git clone https://github.com/your-org/jarl.git
cd jarl

cp docker/.env.example docker/.env
# Edit docker/.env — set ROM_PATH to your ROMs directory
```

Example `.env` excerpt:

```bash
ROM_PATH=/home/david/roms
```

Then:

```bash
docker compose -f docker/docker-compose.yml up -d
```

## 3. Open the UI

```
http://localhost
```

You should see an empty library with your platforms listed.

## 4. Scan

Click **"Scan Library"** in the UI, or:

```bash
curl -X POST http://localhost:8000/api/scan/start
```

Watch live progress via SSE:

```bash
curl -N http://localhost:8000/api/scan/progress
```

## 5. Scrape Metadata

Once scanned, enrich your ROMs:

```bash
# Scrape all missing metadata
curl -X POST "http://localhost:8000/api/scrape/batch?missing_only=true"
```

Or click **"Scrape All"** in the UI.

## 6. Browse

Navigate by platform in the sidebar. Use the search bar to find games by title.

---

## Next Steps

- [Configure IGDB credentials](scraper.md#getting-credentials) for better Western game coverage
- [Add ScreenScraper credentials](scraper.md#getting-credentials) for Japanese/European exclusives
- [Configure CORS](configuration.md#cors) if accessing from a different hostname
- [Set up a reverse proxy](https://github.com/nginx-proxy/nginx-proxy) with HTTPS for network access
