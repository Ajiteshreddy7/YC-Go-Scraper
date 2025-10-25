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

## Deploy on Railway.app (Free & Easy)

Railway automatically detects Docker Compose and deploys all services.

### Steps:

1. **Sign up**: Go to [railway.app](https://railway.app) and sign in with GitHub

2. **New Project**: Click "New Project" → "Deploy from GitHub repo"

3. **Select repo**: Choose `YC-Go-Scraper`

4. **Railway auto-detects** your `docker-compose.yml` and creates:
   - Postgres service (db)
   - Scraper service
   - Dashboard service (publicly accessible)

5. **Set environment variables** (Railway dashboard → service → Variables):
   - `LOG_LEVEL`: `INFO` (optional)
   - Railway automatically handles `POSTGRES_URL` between services

6. **Get public URL**:
   - Click on the dashboard service
   - Under "Settings" → "Networking" → "Generate Domain"
   - Your dashboard will be live at `https://your-app.up.railway.app`

### Cost:
- **Free tier**: $5 credit/month (enough for this app)
- Postgres included

## Alternative: Render.com (Also Free)

Similar process to Railway:

1. Go to [render.com](https://render.com) → Sign in with GitHub
2. "New" → "Blueprint" → Select your repo
3. Render reads `docker-compose.yml` automatically
4. Deploy takes ~5-10 minutes
5. Dashboard URL: `https://your-app.onrender.com`

### Free tier:
- Postgres: Free 90 days, then $7/month
- Web services: Free (sleeps after 15min inactivity)

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
POSTGRES_URL=<provided-by-platform>
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
