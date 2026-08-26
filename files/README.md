# URL Shortener API

A REST API that shortens long URLs, redirects short codes to their original
destination, and tracks click counts — with a custom base62 encoder and a
sliding-window rate limiter.

## Stack
- Python + Flask
- SQLite (via Python's built-in `sqlite3`)
- No external frameworks for the core logic — base62 encoding and rate
  limiting are both implemented from scratch

## Endpoints

| Method | Path             | Description                              |
|--------|------------------|-------------------------------------------|
| GET    | `/`              | Health check                              |
| POST   | `/shorten`       | Body: `{"url": "https://..."}` → returns a short code |
| GET    | `/<short_code>`  | Redirects to the original long URL        |
| GET    | `/stats/<code>`  | Returns click count and metadata          |

## Run it locally

```bash
pip install -r requirements.txt
python app.py
```

Then:

```bash
curl -X POST http://localhost:5000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

## How the short codes work

Each submitted URL is stored as a new row in SQLite with an
auto-incrementing integer ID. That ID is converted into a base62 string
(digits 0-9, lowercase a-z, uppercase A-Z — 62 characters total), which
keeps codes short even as the ID grows into the millions. The encoder/
decoder is hand-written in `base62.py`, not a library.

## Rate limiting

`rate_limiter.py` implements a sliding-window limiter per client IP
(default: 5 requests per 60 seconds) using an in-memory dictionary of
timestamps. In production with multiple server instances, this would be
backed by Redis so all instances share the same counters.
