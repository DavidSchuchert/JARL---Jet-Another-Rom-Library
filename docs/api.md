# API Reference

Full interactive docs at **`/api/docs`** (Swagger UI) or **`/api/redoc`** (ReDoc).

---

## Base URL

```
http://localhost:8000/api
```

---

## Authentication

Currently **no authentication** — JARL is designed for local/private network use. Add a reverse-proxy auth layer (nginx Basic Auth, Cloudflare Access, etc.) if exposed publicly.

---

## Endpoints

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

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | int | `1` | Page number |
| `page_size` | int | `50` | Items per page (max 200) |
| `platform` | string | — | Filter by platform slug |
| `search` | string | — | Full-text search on title |
| `region` | string | — | Filter by region |
| `genre` | string | — | Filter by genre |
| `missing_only` | bool | `false` | Only ROMs without metadata |

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

#### `GET /api/roms/{id}`

Get a single ROM by ID.

#### `PATCH /api/roms/{id}`

Update ROM metadata manually.

```json
{
  "title": "New Title",
  "region": "USA",
  "year": 1990
}
```

---

### Platforms

#### `GET /api/platforms`

List all platforms with ROM counts.

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

#### `POST /api/platforms`

Create a new platform entry.

```json
{
  "slug": "nes",
  "name": "Nintendo Entertainment System",
  "family": "Nintendo"
}
```

---

### Scan

#### `POST /api/scan/start`

Trigger a new filesystem scan.

```json
{
  "job_id": 5,
  "status": "running",
  "message": "Scan job started"
}
```

#### `GET /api/scan/progress`

**Server-Sent Events** — live scan progress stream.

```
Accept: text/event-stream

event: progress
data: {"sequence":1,"type":"info","message":"Scanning nintendo/nes/","scanned_files":0}

event: progress
data: {"sequence":2,"type":"file","current_file":"Super Mario Bros. 3 (Europe).nes","scanned_files":1}

event: progress
data: {"sequence":3,"type":"complete","message":"Scan complete","scanned_files":247}
```

#### `GET /api/scan/jobs`

List all scan jobs.

#### `DELETE /api/scan/jobs/{id}`

Cancel a running scan job.

---

### Scrape

#### `POST /api/scrape/rom/{id}`

Scrape metadata for a single ROM.

```json
{
  "success": true,
  "title": "Super Mario Bros. 3",
  "description": "...",
  "cover_url": "https://...",
  "year": 1988,
  "genre": "Platformer",
  "publisher": "Nintendo"
}
```

#### `POST /api/scrape/batch`

Batch scrape ROMs.

| Parameter | Type | Description |
|---|---|---|
| `platform` | string | Filter to a specific platform |
| `missing_only` | bool | Only scrape ROMs with `scrape_status = "pending"` |
| `priority` | string | `igdb` or `screenscraper` (which source to try first) |

```json
{
  "queued": 120,
  "message": "Batch scrape started"
}
```

---

### Stats

#### `GET /api/stats`

Library statistics.

```json
{
  "total_roms": 1337,
  "total_platforms": 18,
  "total_size_bytes": 536870912000,
  "roms_with_igdb": 800,
  "roms_with_screenscraper": 1200,
  "last_scan": "2026-05-01T14:30:00Z"
}
```
