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

Backend reads `.env` from `backend/` directory. Create one if needed:

```bash
cd backend
cp ../docker/.env.example .env
# Edit .env with your paths
```

### Database

The SQLite database is at `backend/jarl.db` (or wherever `DATABASE__URL` points).

To reset:

```bash
rm backend/jarl.db
uv run uvicorn app.main:app --reload --port 8000
# JARL will re-initialize on startup
```

---

## Frontend

```bash
cd frontend

npm install

# Dev server (proxies /api to :8000)
npm run dev

# Production build
npm run build
```

Frontend dev server: http://localhost:5173

### Pinia Stores

State lives in `src/stores/`:

```typescript
// Example: fetch ROMs
import { useRomsStore } from '@/stores/roms'
const romsStore = useRomsStore()
await romsStore.fetchRoms({ platform: 'nes', page: 1 })
```

### API Client

Backend calls go through `src/api/index.ts` which wraps `fetch()` with the base URL.

---

## Running Both Simultaneously

In two terminals:

```bash
# Terminal 1 — Backend
cd backend && uv run uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend && npm run dev
```

Or use Docker for backend + local Vite:

```bash
docker compose -f docker/docker-compose.yml up backend nginx
npm run dev  # from frontend/
```

---

## Testing

```bash
cd backend

# Unit tests
uv run pytest

# With coverage
uv run pytest --cov=app --cov-report=term-missing

# Specific test file
uv run pytest tests/test_scanner_filesystem.py -v
```

Test files live in `backend/tests/`:
- `test_parser.py` — filename parser
- `test_platforms.py` — platform registry
- `test_scanner_filesystem.py` — filesystem scanner

---

## Code Quality

```bash
cd backend

# Lint (ruff)
uv run ruff check .

# Format (ruff)
uv run ruff format .

# Type check (mypy)
uv run mypy app/
```

---

## Docker Build (for testing)

```bash
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml up -d
```
