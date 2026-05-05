# Authentication

JARL uses **JWT (HS256)** to protect all API endpoints. Tokens are obtained via `/api/auth/login` and must be included in subsequent requests.

---

## Public vs Protected Endpoints

| Endpoint | Method | Auth Required |
|---|---|---|
| `/api/auth/login` | POST | No — returns token |
| `/api/auth/me` | GET | No — validates token |
| `/api/health` | GET | No |
| `/` | GET | No |
| `/api/roms/*` | ALL | **Yes** |
| `/api/platforms/*` | ALL | **Yes** |
| `/api/scan/*` | ALL | **Yes** |
| `/api/scrape/*` | ALL | **Yes** |

---

## Getting a Token

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"
```

Response:
```json
{"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "token_type": "bearer"}
```

---

## Using the Token

Include the token in the `Authorization` header of every protected request:

```bash
curl -X POST http://localhost:8000/api/scan/start \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Token Expiry

Tokens expire after `AUTH__TOKEN_EXPIRE_MINUTES` (default: 1440 = 24 hours). After expiry, `/api/auth/me` returns 401 — at which point the client should re-authenticate via `/api/auth/login`.

---

## Credential Setup

Set credentials via environment variables:

```bash
AUTH__USERNAME=admin
AUTH__PASSWORD=your_secure_password
AUTH__TOKEN_EXPIRE_MINUTES=1440
SECRET_KEY=your-very-long-random-secret-key
```

> **Default credentials (`admin`/`admin`) must be changed in production.** Anyone with the default credentials can access all ROM data and trigger scans.

---

## Frontend Auth (Pinia Store)

The frontend stores the JWT in `localStorage` under `jarl_token`. The `useAuthStore` (`frontend/src/stores/auth.ts`) manages login/logout and automatically attaches the token to all API requests via Axios interceptors.

On app start, `checkAuth()` validates the stored token via `GET /api/auth/me`. If validation fails, the user is logged out.
