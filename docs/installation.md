# Installation

JARL runs as a Docker stack (recommended) or bare metal.

---

## Docker (Recommended)

### 1. Clone the repository

```bash
git clone https://github.com/your-org/jarl.git
cd jarl
```

### 2. Configure environment

```bash
cp docker/.env.example docker/.env
```

Edit `docker/.env`:

| Variable | Required | Description |
|---|---|---|
| `ROM_PATH` | **Yes** | Absolute path to your ROMs directory on the host |
| `SCRAPER__IGDB_CLIENT_ID` | No | IGDB OAuth client ID |
| `SCRAPER__IGDB_CLIENT_SECRET` | No | IGDB OAuth client secret |
| `SCRAPER__USERNAME` | No | ScreenScraper account (needed for private games) |
| `SCRAPER__PASSWORD` | No | ScreenScraper password |

### 3. Start

```bash
docker compose -f docker/docker-compose.yml up -d
```

JARL will be available at:

- **Frontend**: http://localhost
- **API**: http://localhost/api/docs
- **ReDoc**: http://localhost/api/redoc

### 4. Initial scan

Point your browser to the frontend and trigger a scan, or use the API:

```bash
curl -X POST http://localhost:8000/api/scan/start
```

---

## Bare Metal

### Prerequisites

- Python 3.11+
- Node.js 20+
- ROMs directory accessible locally

### Backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev   # Development
npm run build # Production (serves from frontend/dist/)
```

Configure a reverse proxy (nginx) to route `/api` → `localhost:8000` and `/` → `frontend/dist`.

---

## Volumes & Data

| Host path | Container path | Purpose |
|---|---|---|
| `${ROM_PATH}` | `/roms:ro` | Your ROM files (read-only) |
| `jarl-data` (Docker volume) | `/app/data` | SQLite database, cached covers |

The ROMs mount is **read-only** — JARL never writes to your ROM files.

To inspect the database from the host:

```bash
docker exec jarl-backend python -c \
  "import sqlite3; c = sqlite3.connect('/app/data/jarl.db'); print(c.execute('SELECT COUNT(*) FROM roms').fetchone()[0])"
```
