# Universal Job Tracker Setup Guide

## Overview
This upgraded job tracker uses Google's Gemini AI to extract job details from any website, making it much more flexible than traditional web scraping methods. **Version 2.0 includes improved text extraction and enhanced AI prompts for better accuracy.**

## Prerequisites

### 1. Get a Google Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key (keep it safe!)

### 2. Install Dependencies (Recommended: Conda Environment)

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

### Step 1: Set Your API Key Environment Variable

**For Windows (PowerShell):**
```powershell
$env:GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```

**For Windows (Command Prompt):**
```cmd
set GOOGLE_API_KEY=YOUR_API_KEY_HERE
```

**For macOS/Linux:**
```bash
export GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```

Replace `YOUR_API_KEY_HERE` with your actual API key from Google AI Studio.

### Step 2: Run the Script
```bash
python job_tracker_v2.py
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

**List all environments:**
```bash
conda env list
```

### Using pip (Alternative)

**Install dependencies:**
```bash
pip install -r requirements.txt
```

## How It Works

1. **Smart Content Fetch**: Uses `trafilatura` to extract only the main content, filtering out navigation, footers, and boilerplate
2. **AI-Powered Extraction**: Gemini AI analyzes the clean text and extracts key job details with enhanced accuracy
3. **Structured Output**: Data is returned in JSON format and saved to CSV
4. **Universal Compatibility**: Works with LinkedIn, Indeed, Google Careers, and any other job board

## Key Improvements in v2.0

- ✅ **Better Text Extraction**: Uses `trafilatura` library to focus on main content only
- ✅ **Enhanced AI Prompt**: More detailed instructions for better accuracy
- ✅ **Improved Error Handling**: Better handling of edge cases
- ✅ **Salary Detection**: Better extraction of salary information from various formats
- ✅ **Job Type Recognition**: More accurate identification of employment types

## Features

- ✅ Works with any job posting website
- ✅ Extracts job title, company, location, salary, and job type
- ✅ Saves data to CSV for easy tracking
- ✅ Handles errors gracefully
- ✅ Secure API key management
- ✅ Isolated conda environment
- ✅ Smart content filtering (removes boilerplate)

## Troubleshooting

### "GOOGLE_API_KEY environment variable not found"
- Make sure you set the environment variable in the same terminal session where you run the script
- Double-check that your API key is correct

### "Error fetching URL"
- Check your internet connection
- Some websites may block automated requests
- Try a different job posting URL

### "An error occurred with the Gemini API"
- Verify your API key is valid
- Check your internet connection
- The free tier has rate limits - wait a moment and try again

### "Trafilatura could not extract main content"
- Some websites may have complex layouts
- Try a different job posting URL
- The script will still attempt to process with available content

### Conda Environment Issues
- Make sure conda is installed on your system
- Try `conda update conda` if you have issues
- Use `conda env list` to see available environments

## Example Usage

```
--- Universal AI Job Tracker (v2.0) ---

Enter a job URL from any website (or type 'exit' to quit): https://www.linkedin.com/jobs/view/123456789

Step 1: Fetching page content...
Step 2: Asking Gemini AI to extract details...
Step 3: Saving to your spreadsheet...

Success! Job details appended to 'job_applications.csv'.
```

## CSV Output Format

The script creates a `job_applications.csv` file with these columns:
- Date Added
- Company
- Title
- Location
- Salary
- Type
- Status
- URL

## Security Notes

- Never commit your API key to version control
- The script reads the key from environment variables for security
- Google's free tier is generous and suitable for personal use 