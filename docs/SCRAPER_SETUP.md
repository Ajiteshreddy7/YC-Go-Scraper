# 🚀 Job Scraper Engine Setup Guide

## Overview
This guide will help you set up an **automated job scraper engine** that continuously discovers new job postings from multiple career websites and saves them to your Supabase database.

## What We're Building

✅ **Automated Discovery**: Finds new jobs every 30 minutes during business hours  
✅ **Multi-Source Scraping**: LinkedIn, Indeed, Glassdoor, and more  
✅ **AI-Powered Extraction**: Uses Gemini AI to extract job details accurately  
✅ **Duplicate Prevention**: Avoids adding the same job twice  
✅ **Respectful Scraping**: Built-in delays and rate limiting  
✅ **Cloud Automation**: Runs on GitHub Actions with zero maintenance  

## Files Created

- `job_scraper_engine.py` - Main scraper engine script
- `.github/workflows/job-scraper.yml` - GitHub Actions automation
- `scraper_config.json` - Configuration file for customization
- `SCRAPER_SETUP.md` - This setup guide

## How It Works

1. **Scheduled Execution**: Runs every 30 minutes during business hours (9 AM - 6 PM UTC, Mon-Fri)
2. **Multi-Site Search**: Searches LinkedIn, Indeed, and Glassdoor simultaneously
3. **Keyword Matching**: Uses your configured keywords and locations
4. **AI Extraction**: Gemini AI extracts job details from each posting
5. **Database Storage**: Saves new jobs to your Supabase database
6. **Duplicate Check**: Prevents adding jobs that already exist

## Step 1: Test the Scraper Locally

First, let's test that the scraper works with your current setup:

```bash
python job_scraper_engine.py
```

This will:
- Connect to your Supabase database
- Search for jobs using the default configuration
- Extract and save new job postings
- Show you real-time progress

## Step 2: Customize Your Search

Edit `scraper_config.json` to customize your job search:

### Keywords
Add or modify job titles you're interested in:
```json
"keywords": [
  "data engineer",
  "software engineer", 
  "python developer",
  "machine learning engineer",
  "your custom keyword"
]
```

### Locations
Add cities or regions you want to search:
```json
"locations": [
  "San Francisco",
  "New York", 
  "Remote",
  "your preferred location"
]
```

### Search Limits
Control how many jobs to find per run:
```json
"max_jobs_per_search": 15,
"delay_between_requests": 3
```

## Step 3: Push to GitHub

Commit and push the new files:

```bash
git add job_scraper_engine.py .github/workflows/job-scraper.yml scraper_config.json SCRAPER_SETUP.md
git commit -m "feat: add automated job scraper engine"
git push
```

## Step 4: Configure GitHub Secrets

Your GitHub Action needs access to your API keys. Add these secrets in your repository:

### 4.1 Go to Repository Settings
1. Go to your GitHub repository
2. Click **"Settings"** tab
3. Click **"Secrets and variables"** → **"Actions"**

### 4.2 Add Required Secrets
1. **GOOGLE_API_KEY**: Your Gemini AI API key
2. **SUPABASE_URL**: Your Supabase project URL
3. **SUPABASE_KEY**: Your Supabase `anon` public key

## Step 5: Test the Automation

### 5.1 Manual Test
1. Go to your repository's **"Actions"** tab
2. Click **"Job Scraper Engine"** in the sidebar
3. Click **"Run workflow"** button
4. Watch the action run and check the logs

### 5.2 Check Results
1. Wait for the action to complete
2. Check your Supabase database for new job postings
3. Verify that jobs are being added correctly

## Step 6: Monitor and Optimize

### 6.1 Check Action Logs
- Go to Actions tab to see run history
- Check for any errors or warnings
- Monitor how many jobs are being found

### 6.2 Adjust Configuration
Based on results, you can:
- Add more keywords if not finding enough jobs
- Remove keywords if finding too many irrelevant jobs
- Adjust locations based on your preferences
- Change the schedule if needed

## Configuration Options

### Schedule Customization
Edit the cron schedule in `.github/workflows/job-scraper.yml`:

```yaml
schedule:
  # Current: Every 30 minutes, 9 AM - 6 PM UTC, Mon-Fri
  - cron: '0,30 9-18 * * 1-5'
  
  # Other options:
  # '0 */2 * * *'     # Every 2 hours
  # '0 9,12,15,18 * * 1-5'  # 4 times per day
  # '0 9 * * 1-5'     # Once per day at 9 AM
```

### Site Configuration
Enable/disable specific career sites in `scraper_config.json`:

```json
"career_sites": {
  "linkedin": {
    "enabled": true,
    "priority": 1
  },
  "indeed": {
    "enabled": false,  // Disable Indeed
    "priority": 2
  }
}
```

### AI Extraction Settings
Customize the AI extraction behavior:

```json
"ai_extraction": {
  "model": "gemini-1.5-flash",
  "max_content_length": 8000,
  "confidence_threshold": 0.7
}
```

## Troubleshooting

### "Action failed" in GitHub Actions
- Check that all three secrets are set correctly
- Verify your API keys are valid and have sufficient quota
- Check the action logs for specific error messages

### "No jobs found"
- Verify your keywords are common job titles
- Check that locations are spelled correctly
- Try running manually to see detailed logs
- Consider adding more keywords or locations

### "Rate limited" errors
- The scraper includes built-in delays to be respectful
- If you get rate limited, increase the `delay_between_requests` value
- Consider reducing `max_jobs_per_search`

### "Chrome installation failed"
- The workflow automatically installs Chrome
- If it fails, check the action logs for specific errors
- This is rare but can happen on GitHub's runners

## Best Practices

### 1. Be Respectful
- The scraper includes delays between requests
- Don't reduce delays below 2-3 seconds
- Monitor for rate limiting and adjust if needed

### 2. Start Conservative
- Begin with fewer keywords and locations
- Gradually expand based on results
- Monitor your API usage

### 3. Regular Monitoring
- Check your Supabase database regularly
- Review the quality of extracted job details
- Adjust keywords based on relevance

### 4. Backup Your Data
- Your Supabase database is automatically backed up
- Consider exporting data periodically
- Keep your configuration files in version control

## Advanced Features

### Custom Career Sites
You can add more career sites by modifying the `CAREER_SITES` dictionary in the script.

### Advanced Filtering
Add more sophisticated filtering logic based on job requirements, company size, etc.

### Email Notifications
Integrate with email services to get notified of new job postings.

### Webhook Integration
Send job data to other services via webhooks.

## Security Notes

- API keys are encrypted in GitHub secrets
- The scraper only reads public job postings
- No sensitive data is exposed
- Consider making your repository private

## Next Steps

1. **Deploy**: Push your changes and let the automation run
2. **Monitor**: Check your database for new job postings
3. **Optimize**: Adjust keywords and locations based on results
4. **Scale**: Add more career sites or advanced features
5. **Integrate**: Connect with your existing job tracking workflow

## Congratulations! 🎉

You now have a **fully automated job discovery system** that:
- Runs continuously without manual intervention
- Discovers new job postings from multiple sources
- Uses AI to extract accurate job details
- Saves everything to your cloud database
- Prevents duplicates automatically

This is a powerful tool that will help you stay on top of new job opportunities automatically! 