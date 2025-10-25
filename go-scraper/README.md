# Go Job Scraper

A complete rewrite of the Python job scraper in Go, featuring:
- PostgreSQL persistence instead of Supabase
- CSV export for local data analysis
- Structured logging with levels
- Web dashboard for viewing jobs
- Docker Compose for easy deployment
- Greenhouse API scraper with smart filtering

## Architecture

```
go-scraper/
├── cmd/
│   ├── scraper/        # CLI scraper (batch job processor)
│   └── dashboard/      # Web dashboard server
├── internal/
│   ├── db/            # PostgreSQL connection and queries
│   ├── exporter/      # CSV export functionality
│   ├── logger/        # Structured logging
│   └── scraper/       # Job scraping logic (Greenhouse)
└── Dockerfile*        # Docker build configs
```

## Features

### ✅ Completed

1. **Greenhouse Scraper**: Scrapes 40+ companies via Greenhouse API
2. **Smart Filtering**: 
   - Early career roles only (intern, new grad, associate, junior)
   - Excludes senior/lead/principal positions
   - US locations only
3. **PostgreSQL Storage**: Local database with deduplication
4. **CSV Export**: Exports all jobs to `data/job_applications.csv`
5. **Structured Logging**: Timestamped logs with levels (INFO, WARN, ERROR)
6. **Web Dashboard**: Real-time job viewing at http://localhost:8080
7. **Docker Compose**: One command deployment
8. **Unit Tests**: Test coverage for scraper logic

## Quick Start

### Option 1: Docker Compose (Recommended)

```powershell
# Start everything (Postgres + Scraper + Dashboard)
docker compose up -d

# View logs
docker logs yc-go-scraper-scraper-1 -f

# Access dashboard
# Open browser to: http://localhost:8080

# Stop all services
docker compose down
```

### Option 2: Local Development

```powershell
# Start just Postgres
docker compose up -d db

# Set environment variable
$env:POSTGRES_URL='postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable'

# Build scraper
cd go-scraper
go build ./cmd/scraper

# Run scraper
./scraper.exe --config ../config/scraper_config.json --out ../data/jobs.csv

# Build and run dashboard
go build ./cmd/dashboard
./dashboard.exe --port 8080
```

## CLI Options

### Scraper
```powershell
./scraper.exe --config <path> --out <path>
```
- `--config`: Path to config JSON (default: `config/scraper_config.json`)
- `--out`: Path to output CSV (default: `data/job_applications.csv`)

### Dashboard
```powershell
./dashboard.exe --port <port>
```
- `--port`: Port to run on (default: `8080`)

## Configuration

Edit `config/scraper_config.json` to customize:

```json
{
  "target_platforms": {
    "greenhouse": [
      "stripe",
      "airbnb",
      "coinbase",
      ...
    ]
  }
}
```

## Database Schema

```sql
CREATE TABLE job_applications (
    id SERIAL PRIMARY KEY,
    title TEXT,
    company TEXT,
    location TEXT,
    salary TEXT,
    type TEXT,
    url TEXT UNIQUE,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Not Applied'
);
```

## Testing

```powershell
# Run all tests
go test ./...

# Run with verbose output
go test ./internal/scraper -v

# Run with coverage
go test ./... -cover
```

## Logs

Structured logging with timestamps and levels:

```
[INFO]  2025-10-25 15:30:03 - Starting Go Job Scraper
[INFO]  2025-10-25 15:30:03 - Found 40 greenhouse companies to scrape
[INFO]  2025-10-25 15:30:03 - [1/40] scraping stripe
[WARN]  2025-10-25 15:30:08 - error scraping uber: status 404
[INFO]  2025-10-25 15:30:45 - Processed 382 greenhouse jobs
[INFO]  2025-10/25 15:30:45 - Exported CSV to data/job_applications.csv
```

## Deployment

### Docker Compose Services

- **db**: PostgreSQL 15 on port 5432
- **scraper**: Batch job that runs once and exits
- **dashboard**: Web server on port 8080

### Environment Variables

- `POSTGRES_URL`: Database connection string
  - Default: `postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable`

### Volumes

- `./data`: Mounted for CSV exports
- `./config`: Mounted for configuration
- `pgdata`: PostgreSQL persistent storage

## Performance

- Scrapes 40 companies in ~2 minutes
- Respectful 2-second delay between companies
- Processes 300-400 jobs per run
- CSV export completes in <1 second

## Migration from Python

| Python | Go | Status |
|--------|-----|--------|
| Supabase | PostgreSQL Docker | ✅ Complete |
| greenhouse_scraper.py | internal/scraper/greenhouse.go | ✅ Complete |
| job_scraper_engine.py | cmd/scraper/main.go | ✅ Complete |
| dashboard_generator.py | cmd/dashboard/main.go | ✅ Complete |
| CSV export | internal/exporter | ✅ Complete |
| Standard logging | Structured logger | ✅ Complete |
| Google Careers scraper | - | ⏳ Future |
| Lever/Workday scrapers | - | ⏳ Future |

## Next Steps

- [ ] Port Google Careers scraper (requires chromedp for JS rendering)
- [ ] Add Lever and Workday platform scrapers
- [ ] Implement retry logic with exponential backoff
- [ ] Add metrics and monitoring
- [ ] Create systemd service file for Linux deployments
- [ ] Add Windows Task Scheduler setup guide
- [ ] Implement webhook notifications (Slack/Discord)

## Troubleshooting

### Port 5432 already in use
```powershell
# Stop conflicting Postgres
docker ps | findstr postgres
docker stop <container_id>
```

### Dashboard shows no data
```powershell
# Check if scraper ran successfully
docker logs yc-go-scraper-scraper-1

# Verify database has data
docker exec -it yc-go-scraper-db-1 psql -U postgres -d postgres -c "SELECT COUNT(*) FROM job_applications;"
```

### CSV file not generated
```powershell
# Check data directory exists and is writable
mkdir data -Force

# Check scraper logs for errors
docker logs yc-go-scraper-scraper-1 | Select-String "ERROR"
```

## Development

### Adding a New Scraper

1. Create `internal/scraper/<platform>.go`
2. Implement scraping logic returning `[]scraper.Job`
3. Add platform to config JSON
4. Update `cmd/scraper/main.go` to call new scraper
5. Add unit tests in `*_test.go`

### Building

```powershell
# Build all packages
go build ./...

# Build specific command
go build ./cmd/scraper
go build ./cmd/dashboard

# Build with optimizations
go build -ldflags="-s -w" ./cmd/scraper
```

## License

MIT - See parent directory for details
