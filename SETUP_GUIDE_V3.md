# Universal Job Tracker v3.0 Setup Guide (with Database)

## Overview
This upgraded job tracker uses Google's Gemini AI to extract job details from any website and saves them to a **Supabase cloud database**. Version 3.0 includes duplicate detection, cloud storage, and improved content extraction.

## Prerequisites

### 1. Get a Google Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key (keep it safe!)

### 2. Set Up Supabase Database
1. Go to [Supabase](https://supabase.com) and create a free account
2. Create a new project
3. Go to SQL Editor and run this SQL to create the table:

```sql
CREATE TABLE job_applications (
    id SERIAL PRIMARY KEY,
    "Title" TEXT,
    "Company" TEXT,
    "Location" TEXT,
    "Salary" TEXT,
    "Type" TEXT,
    "URL" TEXT UNIQUE,
    "Status" TEXT DEFAULT 'Not Applied',
    "Date Added" TIMESTAMP DEFAULT NOW()
);

-- Disable Row Level Security (RLS) for this table
ALTER TABLE job_applications DISABLE ROW LEVEL SECURITY;
```

4. Get your Supabase credentials:
   - Go to Settings → API
   - Copy your Project URL
   - Copy your `anon` public key (not the service key)

### 3. Install Dependencies

**Option A: Using Conda (Recommended)**
```bash
# Create and activate the conda environment
conda env create -f environment.yml
conda activate job-tracker
```

**Option B: Using pip**
```bash
pip install -r requirements.txt
```

## Setup Steps

### Step 1: Set Your Environment Variables

**For Windows (PowerShell):**
```powershell
$env:GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
$env:SUPABASE_URL="YOUR_SUPABASE_URL"
$env:SUPABASE_KEY="YOUR_SUPABASE_ANON_KEY"
```

**For Windows (Command Prompt):**
```cmd
set GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
set SUPABASE_URL=YOUR_SUPABASE_URL
set SUPABASE_KEY=YOUR_SUPABASE_ANON_KEY
```

**For macOS/Linux:**
```bash
export GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
export SUPABASE_URL="YOUR_SUPABASE_URL"
export SUPABASE_KEY="YOUR_SUPABASE_ANON_KEY"
```

Replace the placeholder values with your actual credentials.

### Step 2: Run the Script
```bash
python job_tracker_v3.py
```

## Environment Management

### Using Conda (Recommended)

**Create the environment:**
```bash
conda env create -f environment.yml
```

**Activate the environment:**
```bash
conda activate job-tracker
```

**Deactivate when done:**
```bash
conda deactivate
```

**Remove the environment (if needed):**
```bash
conda env remove -n job-tracker
```

### Using pip (Alternative)

**Install dependencies:**
```bash
pip install -r requirements.txt
```

## How It Works

1. **Duplicate Check**: Checks if the job URL already exists in your database
2. **Smart Content Fetch**: Uses Selenium to handle JavaScript-rendered content
3. **AI-Powered Extraction**: Gemini AI analyzes the content and extracts job details
4. **Cloud Storage**: Saves data to your Supabase database instantly
5. **Real-time Access**: View your job applications in the Supabase dashboard

## Key Features in v3.0

- ✅ **Cloud Database**: All data stored in Supabase (no more CSV files!)
- ✅ **Duplicate Detection**: Prevents adding the same job twice
- ✅ **JavaScript Support**: Handles modern websites with dynamic content
- ✅ **Real-time Dashboard**: View your applications in Supabase Table Editor
- ✅ **Automatic Timestamps**: Tracks when jobs were added
- ✅ **Status Tracking**: Default status of "Not Applied" for new jobs
- ✅ **Universal Compatibility**: Works with any job posting website

## Database Schema

Your Supabase table will have these columns:
- `id` (Primary Key, auto-increment)
- `Title` (Job title)
- `Company` (Company name)
- `Location` (Job location)
- `Salary` (Salary information)
- `Type` (Job type: Full-time, Part-time, etc.)
- `URL` (Job posting URL - unique)
- `Status` (Application status - defaults to "Not Applied")
- `Date Added` (Timestamp - auto-generated)

## Troubleshooting

### "Environment variable not found"
- Make sure you set all three environment variables: `GOOGLE_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`
- Verify the values are correct (no extra spaces or quotes)

### "new row violates row-level security policy"
- This means Row Level Security (RLS) is enabled on your table
- Go to your Supabase SQL Editor and run:
  ```sql
  ALTER TABLE job_applications DISABLE ROW LEVEL SECURITY;
  ```

### "Error saving to Supabase"
- Check your Supabase URL and key are correct
- Make sure the `job_applications` table exists in your database
- Verify the table schema matches the expected structure
- Ensure RLS is disabled (see above)

### "This job is already in your database"
- This is working correctly! The duplicate detection is preventing duplicate entries
- You can view existing jobs in your Supabase dashboard

### Selenium/Chrome Issues
- The script will automatically download Chrome drivers
- If you have Chrome browser issues, the script falls back to HTTP requests

### "Error checking for existing job"
- Usually a temporary network issue
- The script will continue and try to add the job anyway

## Example Usage

```
--- Universal AI Job Tracker (v3.0) ---

Enter a job URL from any website (or type 'exit' to quit): https://www.linkedin.com/jobs/view/123456789

Step 1: Checking if job already exists in database...
Step 2: Fetching page content...
Setting up browser for JavaScript-rendered content...
Loading page: https://www.linkedin.com/jobs/view/123456789
Found job content using selector: [class*="job-description"]
Using Selenium extraction (extracted 5000 characters)
Step 3: Asking Gemini AI to extract details...
Step 4: Saving to your Supabase database...

Success! Job details saved to the database.
```

## Viewing Your Data

1. Go to your Supabase project dashboard
2. Click on "Table Editor" in the left sidebar
3. Select the "job_applications" table
4. You'll see all your job applications with real-time updates

## Security Notes

- Never commit your API keys to version control
- The script uses environment variables for secure credential management
- Supabase provides secure, encrypted cloud storage
- Your data is backed up automatically
- RLS is disabled for this personal use case - consider enabling it for production

## Next Steps

- **Update Status**: Manually update job status in Supabase dashboard
- **Export Data**: Use Supabase's export features to get CSV/JSON files
- **Build Dashboard**: Create a custom dashboard using Supabase's API
- **Add Notes**: Extend the database schema to include application notes 