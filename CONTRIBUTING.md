# Contributing to JARL

Thank you for your interest in contributing! This guide gets you up and running locally in minutes.

## Prerequisites

- Python 3.11+
- Node 20+
- [uv](https://docs.astral.sh/uv/) (`pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Docker & Docker Compose (optional, for the full stack)

## Local Development Setup

### 1. Clone & Branch

```bash
git clone https://github.com/DavidSchuchert/JARL---Jet-Another-Rom-Library.git
cd JARL---Jet-Another-Rom-Library
git checkout -b feat/your-feature
```

### 2. Backend

```bash
cd backend
uv sync                              # installs deps from pyproject.toml
cp ../.env.example .env              # configure (see .env.example)
uv run uvicorn app.main:app --reload --port 8000
```

The API is available at http://localhost:8000/api/docs.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev      # Vite dev server at http://localhost:5173
```

The Vite dev server proxies `/api` and `/media` to the backend on port 8000.

### 4. Run Tests

```bash
cd backend
uv run pytest -v
```

```bash
cd frontend
npm run type-check   # vue-tsc
```

## Docker (Full Stack)

```bash
cp docker/.env.example docker/.env
# Edit docker/.env
docker compose -f docker/docker-compose.yml up --build
```

## Project Structure

```
backend/app/
  api/          # FastAPI route modules
  scanner/      # Filesystem scanner & parser
  scraper/      # ScreenScraper + IGDB integration
  utils/        # Image download utilities
  models.py     # SQLAlchemy models
  schemas.py    # Pydantic schemas
  config.py     # pydantic-settings

frontend/src/
  api/          # Typed API client
  stores/       # Pinia stores (auth)
  views/        # Page components
  components/   # Shared UI components
```

## Guidelines

- **Backend**: follow PEP 8, use type hints, write async code for all I/O.
- **Frontend**: use TypeScript strictly, prefer Composition API (`<script setup>`).
- **Tests**: add a test for any new backend logic in `backend/tests/`.
- **Commits**: use conventional commit prefixes (`feat:`, `fix:`, `docs:`, `refactor:`).
- **PRs**: keep them focused — one feature or fix per PR.

## Reporting Issues

Use the [GitHub issue tracker](https://github.com/DavidSchuchert/JARL---Jet-Another-Rom-Library/issues).
Bug reports and feature requests both have templates to fill in.
