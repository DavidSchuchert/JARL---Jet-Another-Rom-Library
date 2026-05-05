# API Reference

Full interactive docs at **`/api/docs`** (Swagger UI) or **`/api/redoc`** (ReDoc).

Base URL: `http://localhost:8000/api`

---

## Authentication

All endpoints **except** the following require a valid JWT Bearer token:

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/auth/login` | POST | Get JWT token |
| `/api/auth/me` | GET | Validate current token |
| `/api/health` | GET | Health check |
| `/` | GET | API root info |

**Login:**

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=admin" \
  -d "password=admin"
```

```json
{"access_token": "eyJ...", "token_type": "bearer"}
```

Use the token in the `Authorization` header:

```bash
-H "Authorization: Bearer eyJ..."
```

---

## Endpoints

### Auth

#### `POST /api/auth/login`

```
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin
```

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### `GET /api/auth/me`

```
GET /api/auth/me
Authorization: Bearer eyJ...
```

```json
{
  "status": "authenticated",
  "username": "admin"
}
```

---

### Health

#### `GET /api/health`

```json
{
  "status": "ok",
  "version": "1.0.0",
  "database": "ok",
  "uptime": 3600.5
}
```

---

### ROMs

#### `GET /api/roms`

List ROMs with pagination and filtering.

| Parameter     | Type    | Default | Description |
| ------------ | ------- | ------- | ----------- |
| `page`       | int     | `1`     | Page number |
| `page_size`  | int     | `50`    | Items per page (max 100) |
| `platform`   | string  | —       | Filter by platform slug |
| `region`     | string  | —       | Filter by region |
| `year`       | int     | —       | Filter by release year |
| `genre`      | string  | —       | Filter by genre |
| `search`     | string  | —       | Full-text search on title |
| `missing_only` | bool   | `false` | Only ROMs with `scrape_status != "done"` |

```json
{
  "items": [
    {
      "id": 1,
      "title": "Super Mario Bros. 3",
      "platform_slug": "nes",
      "region": "Europe",
      "year": 1988,
      "genre": "Platformer",
      "publisher": "Nintendo",
      "size": 245760,
      "cover_url": null,
      "scrape_status": "pending",
      "created_at": "2026-05-01T10:00:00Z"
    }
  ],
  "total": 1337,
  "page": 1,
  "page_size": 50,
  "total_pages": 27
}
```

#### `GET /api/roms/{rom_id}`

Get a single ROM by ID.

#### `GET /api/roms/stats`

Library statistics.

```json
{
  "total_roms": 1337,
  "total_platforms": 18,
  "total_size_bytes": 536870912000,
  "roms_with_igdb": 800,
  "roms_with_screenscraper": 1200,
  "last_scan": null
}
```

#### `DELETE /api/roms/{rom_id}`

Delete a ROM.

---

### Platforms

#### `GET /api/platforms`

List all platforms that have at least one ROM, with ROM counts.

```json
[
  {
    "id": 1,
    "slug": "nes",
    "name": "Nintendo Entertainment System",
    "family": "Nintendo",
    "rom_count": 247
  }
]
```

#### `GET /api/platforms/{slug}`

Get a single platform by slug.

#### `GET /api/platforms/{slug}/roms`

Get ROMs for a specific platform (paginated).

| Parameter   | Type | Default | Description |
| ---------- | ---- | ------- | ----------- |
| `page`     | int  | `1`     | Page number |
| `page_size` | int  | `50`    | Items per page |

---

### Scan

#### `POST /api/scan/start`

Trigger a new filesystem scan.

| Query Param  | Type  | Default | Description |
| ----------- | ----- | ------- | ----------- |
| `full_scan` | bool | `false` | Re-hash all files even if unchanged |

```json
{
  "job_id": 5,
  "status": "started",
  "message": "Scan job 5 started successfully"
}
```

#### `GET /api/scan/events/{job_id}?after=N`

Poll scan events for a job. Returns all events with `sequence > after`.

```json
[
  {
    "sequence": 1,
    "type": "info",
    "message": "Found 247 ROM files",
    "current_file": null,
    "scanned_files": 0,
    "created_at": "2026-05-01T14:00:00Z"
  },
  {
    "sequence": 2,
    "type": "file",
    "message": "Super Mario Bros. 3 (Europe).nes",
    "current_file": "nintendo/nes/Super Mario Bros. 3 (Europe).nes",
    "scanned_files": 1,
    "created_at": "2026-05-01T14:00:01Z"
  }
]
```

Event `type` values: `info`, `file`, `error`, `success`.

#### `GET /api/scan/status/{job_id}`

Get detailed status of a specific scan job.

```json
{
  "id": 1,
  "status": "completed",
  "total_files": 247,
  "scanned_files": 247,
  "current_file": null,
  "errors": 0,
  "started_at": "2026-05-01T14:00:00Z",
  "completed_at": "2026-05-01T14:03:22Z",
  "progress_percentage": 100.0
}
```

#### `GET /api/scan/progress`

Get progress of the currently running scan job (if any).

---

### Scrape

#### `POST /api/scrape/start`

Start a batch scrape job.

| Query Param    | Type   | Default | Description |
| ------------- | ------ | ------- | ----------- |
| `platform`     | string | —       | Filter to a specific platform |
| `only_missing` | bool   | `true`  | Only scrape ROMs with `scrape_status != "done"` |

```json
{
  "status": "started",
  "message": "Started scraping 120 ROMs",
  "total": 120
}
```

#### `POST /api/scrape/rom/{rom_id}`

Force re-scrape of a single ROM.

#### `GET /api/scrape/status`

Get current batch scrape progress.

```json
{
  "status": "running",
  "total": 120,
  "done": 47,
  "success": 44,
  "failed": 3,
  "skipped": 0,
  "current_file": "zelda.nes",
  "percent": 39.17,
  "errors": ["bad rom.zip: Not found"]
}
```

#### `POST /api/scrape/stop`

Cancel the running batch scrape job.

#### `GET /api/scrape/test-auth`

Test ScreenScraper and IGDB credentials.
