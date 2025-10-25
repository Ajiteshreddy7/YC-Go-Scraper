# Deployment Guide

## Push to GitHub

From your local repository:

```powershell
# Check current git status
git status

# Add all files
git add .

# Commit
git commit -m "feat: Complete Go migration with interactive dashboard and filters"

# Push to GitHub
git push origin main
```

## Recommended: Render (web) + Neon (DB) + GitHub Actions (scraper)

This combo is the most “free-and-stable” setup:

- Render (free) hosts the Go dashboard as a web service.
- Neon (free) provides a managed Postgres with persistent storage.
- GitHub Actions (free) runs the scraper on a schedule.

### 1) Create a Neon Postgres database (free)

1. Go to https://neon.tech and sign in.
2. Create a new project → copy the connection string (e.g., postgres://user:pass@host/db?sslmode=require).
3. Add an IP allow rule if required by your Neon project.

You’ll use this as `POSTGRES_URL` in both Render and GitHub Actions.

### 2) Deploy dashboard to Render (free)

1. Go to https://render.com and sign in with GitHub.
2. Click “New” → “Blueprint” → select this repo.
3. Render will detect `render.yaml` and create:
    - Web service: yc-go-dashboard (Dockerfile.dashboard)
    - Cron job: yc-go-scraper-cron (Dockerfile)
4. After services are created, open each service → Environment → set variables:
    - `POSTGRES_URL` = your Neon connection string
    - `LOG_LEVEL` = INFO (optional)
5. For the web service, open Settings → Generate public URL.

Note: If Cron requires enabling, open the cron job service in Render and ensure the schedule is active.

### 3) (Option B) Use GitHub Actions scheduler instead of Render cron

If you prefer to run the scraper via GitHub Actions on a schedule:

1. In your GitHub repo, go to Settings → Secrets and variables → Actions → New repository secret:
    - Name: `POSTGRES_URL`
    - Value: your Neon connection string
2. Add a workflow `.github/workflows/scheduled-scrape.yml` with:

```yaml
name: Scheduled Scrape

on:
   schedule:
      - cron: "0 3 * * *"  # daily at 03:00 UTC
   workflow_dispatch:

jobs:
   scrape:
      runs-on: ubuntu-latest
      defaults:
         run:
            working-directory: go-scraper
      steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-go@v5
            with:
               go-version: "1.21.x"
         - name: Build scraper
            run: go build ./cmd/scraper
         - name: Run scraper
            env:
               POSTGRES_URL: ${{ secrets.POSTGRES_URL }}
               LOG_LEVEL: INFO
            run: ./scraper --config ../config/scraper_config.json --out ../data/job_applications.csv
         - name: Upload CSV artifact
            uses: actions/upload-artifact@v4
            with:
               name: job_applications.csv
               path: data/job_applications.csv
```

Due to GitHub’s workflow permissions, if you see a push error for workflow files, create this workflow via the GitHub UI (Add file → Create new file).

## Alternative: Railway (credit-based free tier)

Railway can run everything via docker-compose, but persistent Postgres may consume credits. For purely free long-term deployments, prefer Neon for DB.

## Alternative: Fly.io

For more control:

```powershell
# Install flyctl
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

# Login
fly auth login

# Launch app
fly launch

# Deploy
fly deploy
```

## Environment Variables for Production

If deploying, consider setting:

```bash
LOG_LEVEL=INFO
POSTGRES_URL=<neon_connection_string>
```

## Monitoring

Once deployed:
- Railway/Render provide built-in logs and metrics
- Dashboard accessible at public URL
- Scraper runs on schedule (or manually trigger)

## Security Notes

For production:
1. Change default Postgres password (set via platform env vars)
2. Add authentication to dashboard (basic auth or OAuth)
3. Consider rate limiting on public endpoints

## Need help?

- Railway docs: https://docs.railway.app
- Render docs: https://render.com/docs
- Fly.io docs: https://fly.io/docs
