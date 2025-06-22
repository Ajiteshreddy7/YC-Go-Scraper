# Job Scraper Engine

An intelligent job scraping system that automatically finds and filters job postings from company career pages and job boards.

## 🏗️ Project Structure

```
flight-code/
├── src/
│   ├── scrapers/           # Job scraping modules
│   │   ├── job_scraper_engine.py      # Main scraper engine
│   │   ├── debug_google_careers.py    # Google Careers debug tool
│   │   └── test_enhanced_scraper.py   # Scraper testing utility
│   ├── dashboard/          # Dashboard and tracking modules
│   │   ├── dashboard_generator.py     # Dashboard generator
│   │   ├── job_tracker_v2.py         # Job tracking v2
│   │   └── job_tracker_v3.py         # Job tracking v3
│   └── utils/              # Utility scripts
│       └── clear_db.py     # Database clearing utility
├── config/                 # Configuration files
│   └── scraper_config.json # Main scraper configuration
├── docs/                   # Documentation
│   ├── README.md
│   ├── SCRAPER_SETUP.md
│   ├── DASHBOARD_SETUP.md
│   ├── SETUP_GUIDE.md
│   └── SETUP_GUIDE_V3.md
├── data/                   # Data files and exports
│   ├── job_applications.csv
│   └── google_careers_debug.html
├── scripts/                # Additional scripts
├── requirements.txt        # Python dependencies
├── environment.yml         # Conda environment
├── index.html              # Dashboard HTML
├── run_scraper.py          # Main scraper entry point
└── run_dashboard.py        # Main dashboard entry point
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
export GOOGLE_API_KEY="your_google_api_key"
export SUPABASE_URL="your_supabase_url"
export SUPABASE_KEY="your_supabase_key"
```

### 3. Configure the Scraper
Edit `config/scraper_config.json` to customize:
- Job keywords and locations
- Company career pages to scrape
- Targeting filters (experience level, location, etc.)

### 4. Run the Scraper
```bash
python run_scraper.py
```

### 5. View the Dashboard
```bash
python run_dashboard.py
```

## 🎯 Features

### Intelligent Job Targeting
- **Location Filtering**: US locations only
- **Experience Level**: Entry-level, intern, new grad positions
- **Smart Keywords**: Excludes senior/lead roles, includes entry-level terms
- **Company-Specific Scrapers**: Specialized scrapers for Google Careers

### Multi-Source Scraping
- **Company Career Pages**: Direct scraping from Google Careers
- **Job Boards**: LinkedIn, Indeed, Glassdoor (configurable)
- **AI-Powered Extraction**: Uses Gemini AI for job detail extraction

### Database Integration
- **Supabase Integration**: Automatic job storage and deduplication
- **Real-time Updates**: Check for existing jobs before processing
- **Structured Data**: Consistent job data format

## 📁 Folder Descriptions

### `src/scrapers/`
Contains all job scraping logic:
- **job_scraper_engine.py**: Main scraper with company career page support
- **debug_google_careers.py**: Debug tool for Google Careers page structure
- **test_enhanced_scraper.py**: Testing utility for scraper functionality

### `src/dashboard/`
Dashboard and job tracking modules:
- **dashboard_generator.py**: Generates HTML dashboard from database
- **job_tracker_v2.py**: Job tracking system v2
- **job_tracker_v3.py**: Job tracking system v3

### `src/utils/`
Utility scripts:
- **clear_db.py**: Database clearing utility

### `config/`
Configuration files:
- **scraper_config.json**: Main configuration with targeting rules

### `docs/`
All documentation and setup guides

### `data/`
Data files and exports:
- **job_applications.csv**: Exported job data
- **google_careers_debug.html**: Debug output from Google Careers

## ⚙️ Configuration

The main configuration file `config/scraper_config.json` controls:

### Job Search Parameters
```json
{
  "job_search": {
    "keywords": ["data engineer", "software engineer", "product manager"],
    "locations": ["San Francisco", "Charlotte", "Atlanta", "New York", "Remote"],
    "max_jobs_per_search": 5
  }
}
```

### Targeting Filters
```json
{
  "targeting": {
    "locations": ["United States", "Remote"],
    "experience_levels": ["ENTRY_LEVEL", "INTERN", "NEW_GRAD"],
    "exclude_keywords": ["senior", "lead", "principal", "director"],
    "include_keywords": ["entry", "junior", "new grad", "intern", "associate"]
  }
}
```

### Company Career Pages
```json
{
  "company_career_pages": [
    "https://careers.google.com/jobs/results/?location=United%20States&employment_type=FULL_TIME&experience_level=ENTRY_LEVEL"
  ]
}
```

## 🔧 Utilities

### Clear Database
```bash
python src/utils/clear_db.py
```

### Debug Google Careers
```bash
python src/scrapers/debug_google_careers.py
```

### Test Scraper
```bash
python src/scrapers/test_enhanced_scraper.py
```

## 📊 Dashboard

Generate and view the job dashboard:
```bash
python run_dashboard.py
```

Then open `index.html` in your browser to view the dashboard.

## 🤝 Contributing

1. Follow the folder structure
2. Add new scrapers to `src/scrapers/`
3. Update configuration in `config/`
4. Document changes in `docs/`

## 📝 License

This project is for educational and personal use. 