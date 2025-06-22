# 🚀 Automated Dashboard Setup Guide

## Overview
This guide will help you set up an **automated job application dashboard** that updates daily and displays all your job applications in a beautiful, public web interface.

## What We're Building

✅ **Automated Dashboard**: Updates daily with fresh data from your Supabase database  
✅ **Beautiful UI**: Professional-looking table with statistics and status tracking  
✅ **Public Access**: Anyone can view your dashboard via GitHub Pages  
✅ **Real-time Data**: Pulls directly from your Supabase database  

## Files Created

- `dashboard_generator.py` - Script that fetches data and generates HTML
- `.github/workflows/update-dashboard.yml` - GitHub Actions automation
- `DASHBOARD_SETUP.md` - This setup guide

## Step 1: Test the Dashboard Generator Locally

First, let's test that the dashboard generator works with your current setup:

```bash
python dashboard_generator.py
```

This should create an `index.html` file in your project folder. Open it in your browser to see your dashboard!

## Step 2: Push Files to GitHub

Commit and push the new files to your GitHub repository:

```bash
git add dashboard_generator.py .github/workflows/update-dashboard.yml DASHBOARD_SETUP.md
git commit -m "feat: add automated dashboard system"
git push
```

## Step 3: Configure GitHub Secrets

Your GitHub Action needs access to your Supabase credentials, but we can't put them directly in the code. We use GitHub's encrypted secrets:

### 3.1 Go to Your Repository Settings
1. Go to your GitHub repository
2. Click on **"Settings"** tab
3. In the left sidebar, click **"Secrets and variables"** → **"Actions"**

### 3.2 Add Supabase URL Secret
1. Click **"New repository secret"**
2. **Name**: `SUPABASE_URL`
3. **Value**: Your Supabase project URL (e.g., `https://your-project.supabase.co`)
4. Click **"Add secret"**

### 3.3 Add Supabase Key Secret
1. Click **"New repository secret"** again
2. **Name**: `SUPABASE_KEY`
3. **Value**: Your Supabase `anon` public key (NOT the service key)
4. Click **"Add secret"**

## Step 4: Enable GitHub Pages

### 4.1 Configure Pages
1. In your repository **"Settings"**, scroll down to **"Pages"**
2. Under **"Build and deployment"**:
   - **Source**: Select **"Deploy from a branch"**
   - **Branch**: Select `main` (or `master`)
   - **Folder**: Select `/ (root)`
3. Click **"Save"**

### 4.2 Get Your Dashboard URL
After saving, GitHub will show you a URL like:
`https://your-username.github.io/your-repo-name/`

This is your live dashboard URL! (It may take a few minutes to become active)

## Step 5: Test the Automation

### 5.1 Manual Test
1. Go to your repository's **"Actions"** tab
2. Click **"Update Job Dashboard"** in the sidebar
3. Click **"Run workflow"** button
4. Watch the action run - it will:
   - Set up Python environment
   - Install dependencies
   - Run your dashboard generator
   - Commit the updated `index.html` file

### 5.2 Check Results
1. Wait for the action to complete (green checkmark)
2. Visit your GitHub Pages URL
3. You should see your beautiful dashboard with all your job applications!

## Step 6: Automatic Updates

The dashboard will now automatically update **every day at 4 AM UTC**. You can also:

- **Manual Updates**: Run the workflow manually anytime from the Actions tab
- **Change Schedule**: Edit the cron schedule in `.github/workflows/update-dashboard.yml`

## Dashboard Features

### 📊 Statistics Cards
- Total Jobs
- Not Applied
- Applied
- Interviewed

### 🎨 Status Color Coding
- **Red**: Not Applied
- **Green**: Applied
- **Yellow**: Interviewed
- **Blue**: Offer

### 🔗 Clickable Links
- Direct "Apply" links to job postings
- Opens in new tab

### 📱 Responsive Design
- Works on desktop, tablet, and mobile
- Clean, professional styling

## Troubleshooting

### "Action failed" in GitHub Actions
- Check that your Supabase secrets are correct
- Verify your Supabase URL and key are valid
- Check the action logs for specific error messages

### Dashboard not updating
- Ensure the workflow completed successfully
- Check that `index.html` was committed to the repository
- Verify GitHub Pages is enabled and configured correctly

### "Page not found" error
- GitHub Pages may take 5-10 minutes to deploy
- Check that the branch and folder settings are correct
- Ensure the repository is public (or you have GitHub Pro for private repos)

### Local dashboard generator fails
- Check your environment variables are set
- Verify your Supabase connection
- Ensure all required packages are installed

## Customization Options

### Change Update Schedule
Edit the cron schedule in `.github/workflows/update-dashboard.yml`:
```yaml
schedule:
  - cron: '0 4 * * *'  # Daily at 4 AM UTC
  # Other options:
  # '0 */6 * * *'     # Every 6 hours
  # '0 12 * * 1'      # Every Monday at noon
```

### Modify Dashboard Styling
Edit the `html_style` variable in `dashboard_generator.py` to change colors, fonts, layout, etc.

### Add More Statistics
Modify the statistics calculation section in `generate_html_dashboard()` to add more metrics.

## Security Notes

- Your Supabase credentials are encrypted in GitHub secrets
- The dashboard is public, but only shows job data (no sensitive credentials)
- Consider making your repository private if you prefer

## Next Steps

1. **Add More Jobs**: Use your job tracker to add more applications
2. **Update Status**: Manually update job status in Supabase dashboard
3. **Customize**: Modify the dashboard styling and features
4. **Share**: Share your dashboard URL with recruiters or for portfolio

## Congratulations! 🎉

You now have a **fully automated, professional job application dashboard** that:
- Updates automatically every day
- Displays all your job applications beautifully
- Provides real-time statistics
- Is accessible from anywhere via the web

This is a powerful tool that demonstrates your technical skills and organization abilities to potential employers! 