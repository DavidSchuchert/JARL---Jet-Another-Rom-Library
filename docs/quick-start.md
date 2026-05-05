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
# Set ROM_PATH, AUTH__USERNAME, AUTH__PASSWORD in docker/.env

docker compose -f docker/docker-compose.yml up -d
```

## 3. Login

All API endpoints require authentication:

```bash
# Get a JWT token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -d "username=admin" \
  -d "password=admin" | jq -r '.access_token')

echo $TOKEN
```

## 4. Scan

```bash
curl -X POST http://localhost:8000/api/scan/start \
  -H "Authorization: Bearer $TOKEN"
```

Poll for live progress:

```bash
curl "http://localhost:8000/api/scan/events/1?after=0" \
  -H "Authorization: Bearer $TOKEN"
```

## 5. Scrape Metadata

Once scanned, enrich your ROMs with metadata:

```bash
# Scrape all ROMs missing metadata
curl -X POST "http://localhost:8000/api/scrape/start?only_missing=true" \
  -H "Authorization: Bearer $TOKEN"

# Check progress
curl http://localhost:8000/api/scrape/status \
  -H "Authorization: Bearer $TOKEN"

# Cancel if needed
curl -X POST http://localhost:8000/api/scrape/stop \
  -H "Authorization: Bearer $TOKEN"
```

## 6. Open the UI

Navigate to **http://localhost** and log in with the same credentials. The frontend handles token storage automatically.

## 7. Browse

Navigate platforms in the sidebar. Search by title with the search bar.

---

## Next Steps

- [Change default credentials](authentication.md#credential-setup) — default `admin`/`admin` is insecure
- [Add ScreenScraper credentials](scraping.md#screenscraper) — required for private/unverified games
- [Add IGDB credentials](scraping.md#igdb) — improves coverage for Western commercial titles
- [Browse all platforms](platforms.md)
