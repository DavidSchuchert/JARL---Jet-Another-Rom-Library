# Development Setup

Run JARL locally for development with hot-reload on both frontend and backend.

---

## Backend

```bash
cd backend

# Install dependencies (uv handles Python version + virtualenv)
uv sync

# Run tests
uv run pytest -v

# Run with hot-reload
uv run uvicorn app.main:app --reload --port 8000
```

Swagger docs: http://localhost:8000/api/docs

### Environment

The backend reads `.env` from `backend/`. Copy from the Docker example:

```bash
cp ../docker/.env.example .env
# Edit .env — especially SCANNER__ROMS_PATH and SCRAPER__* vars
```

### Database

SQLite database at `backend/jarl.db` (or wherever `DATABASE__URL` points).

To reset:

```bash
rm backend/jarl.db
uv run uvicorn app.main:app --reload --port 8000
# JARL re-initializes automatically on startup
```

---

## Frontend

```bash
cd frontend

npm install

# Dev server — proxies /api to :8000
npm run dev

# Production build
npm run build
```

Frontend dev server: http://localhost:5173

---

## Running Both Simultaneously

**Terminal 1 — Backend:**

```bash
cd backend && uv run uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**

```bash
cd frontend && npm run dev
```

Or use Docker for backend + local Vite:

```bash
docker compose -f docker/docker-compose.yml up backend nginx
cd frontend && npm run dev
```

---

## Testing

```bash
cd backend

# All tests
uv run pytest -v

# With coverage
uv run pytest --cov=app --cov-report=term-missing

# Specific test file
uv run pytest tests/test_scanner_filesystem.py -v
uv run pytest tests/test_parser.py -v
uv run pytest tests/test_platforms.py -v
```

Test files in `backend/tests/`:
- `test_parser.py` — filename parser (region, year, title extraction)
- `test_platforms.py` — platform registry (slug lookup, extension mapping)
- `test_scanner_filesystem.py` — filesystem scanner (walk, batch save)

---

## Code Quality

```bash
cd backend

# Lint
uv run ruff check .

# Format
uv run ruff format .

# Type check
uv run mypy app/
```

---

## Docker Build (for testing)

```bash
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml up -d
```
