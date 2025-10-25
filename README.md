# YC-Go-Scraper (Go-only)

An intelligent job scraper written in Go that discovers early‑career roles from Greenhouse boards, stores them in Postgres, exports CSV, and serves a simple web dashboard.

## Features

- Smart scraping via Greenhouse API
- Early‑career filtering (intern, new grad, junior) and US‑location bias
- PostgreSQL storage with de‑duplication on URL
- CSV export to `data/job_applications.csv`
- Web dashboard on http://localhost:8080
- Docker Compose for Postgres, scraper, and dashboard
- Structured logging with configurable level (LOG_LEVEL)
- JSON API: `/api/jobs` with pagination and status filter

## Quick start (Docker)

```powershell
# From repo root
docker compose up -d

# View scraper logs
docker logs yc-go-scraper-scraper-1 -f

# Open dashboard
start http://localhost:8080
```

CSV is written to `data/job_applications.csv` on the host.

## Configuration

Edit `config/scraper_config.json`:

```json
{
  "target_platforms": {
    "greenhouse": ["stripe", "airbnb", "coinbase", "databricks"]
  }
}
```

Environment variables:

- `POSTGRES_URL` (optional) override for database connection; defaults to local.
- `LOG_LEVEL` one of `DEBUG, INFO, WARN, ERROR` (default `INFO`).

## JSON API

The dashboard service also exposes a JSON endpoint for integrations:

- GET `/api/jobs?page=1&page_size=50&status=Applied|Not%20Applied`

Response shape:

```json
{
  "page": 1,
  "page_size": 50,
  "total": 382,
  "total_pages": 8,
  "items": [
    {
      "ID": 123,
      "Title": "Software Engineer",
      "Company": "Stripe",
      "Location": "San Francisco, CA, United States",
      "Type": "Engineering",
      "URL": "https://boards.greenhouse.io/...",
      "DateAdded": "2025-10-25T12:34:56Z",
      "Status": "Not Applied"
    }
  ]
}
```

## Local development

```powershell
# Start only Postgres
docker compose up -d db

# Run scraper (inside module)
cd go-scraper
go run ./cmd/scraper --config ../config/scraper_config.json

# Run dashboard
go run ./cmd/dashboard --port 8080

# Tests
go test ./...
```

## Project structure

```
YC-Go-Scraper/
├─ go-scraper/
│  ├─ cmd/
│  │  ├─ scraper/     # CLI scraper entrypoint
│  │  └─ dashboard/   # Web dashboard entrypoint
│  ├─ internal/
│  │  ├─ db/          # Postgres layer
│  │  ├─ scraper/     # Greenhouse scraper and filters
│  │  ├─ exporter/    # CSV exporter
│  │  └─ logger/      # Structured logging
│  ├─ Dockerfile
│  └─ Dockerfile.dashboard
├─ config/
│  └─ scraper_config.json
├─ data/               # CSV output folder
└─ docker-compose.yml
```

## License

MIT