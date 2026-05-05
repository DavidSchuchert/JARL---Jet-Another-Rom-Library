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
| `AUTH__USERNAME` | **Yes** | API login username — **change from default** |
| `AUTH__PASSWORD` | **Yes** | API login password — **change from default** |
| `SECRET_KEY` | **Yes** | JWT signing secret — use a long random string in production |
| `SCRAPER__IGDB_CLIENT_ID` | No | IGDB OAuth client ID |
| `SCRAPER__IGDB_CLIENT_SECRET` | No | IGDB OAuth client secret |
| `SCRAPER__USERNAME` | No | ScreenScraper account (required for private game data) |
| `SCRAPER__PASSWORD` | No | ScreenScraper password |

### 3. Start

```bash
docker compose -f docker/docker-compose.yml up -d
```

JARL will be available at:

- **Frontend**: http://localhost
- **API**: http://localhost/api/docs (Swagger UI)
- **ReDoc**: http://localhost/api/redoc

### 4. Login

All API endpoints require authentication. Get a token:

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=admin" \
  -d "password=your_password"
```

Response:
```json
{"access_token": "eyJ...", "token_type": "bearer"}
```

### 5. Run your first scan

```bash
curl -X POST http://localhost:8000/api/scan/start \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Poll scan events for progress:

```bash
curl "http://localhost:8000/api/scan/events/1?after=0" \
  -H "Authorization: Bearer YOUR_TOKEN"
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
npm run build # Production (served from frontend/dist/)
```

Configure a reverse proxy (nginx) to route `/api` → `localhost:8000` and `/` → `frontend/dist`.

---

## Volumes & Data

| Host path | Container path | Purpose |
|---|---|---|
| `${ROM_PATH}` | `/roms:ro` | Your ROM files (read-only mount) |
| `jarl-data` (Docker volume) | `/app/data` | SQLite database, cached data |

The ROMs mount is **read-only** — JARL never writes to your ROM files.

To inspect the database:

```bash
docker exec jarl-backend python -c \
  "import sqlite3; c = sqlite3.connect('/app/data/jarl.db'); \
   print('ROMs:', c.execute('SELECT COUNT(*) FROM roms').fetchone()[0])"
```
