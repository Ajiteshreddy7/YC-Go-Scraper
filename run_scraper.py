#!/usr/bin/env python3
"""
Main entry point for the Job Scraper Engine - Platform-First Approach
"""

import sys
import os
import json
import time

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import scrapers
from scrapers.job_scraper_engine import main as run_legacy_scraper
from scrapers.greenhouse_scraper import scrape_all_greenhouse_companies

def load_config():
    """Load configuration from JSON file"""
    try:
        with open('config/scraper_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ config/scraper_config.json not found.")
        return {}

def run_platform_scrapers(config):
    """Run platform-based scrapers (Greenhouse, Lever, Workday, etc.)"""
    print("🏢 PHASE 1: Platform-Based Scraping")
    print("=" * 50)
    
    platforms = config.get("target_platforms", {})
    total_processed = 0
    
    # Greenhouse Platform
    if "greenhouse" in platforms:
        print("\n🌱 GREENHOUSE PLATFORM")
        print("-" * 30)
        greenhouse_companies = platforms["greenhouse"]
        processed = scrape_all_greenhouse_companies(greenhouse_companies)
        total_processed += processed
    
    # TODO: Add Lever Platform
    if "lever" in platforms:
        print("\n🔗 LEVER PLATFORM (Coming Soon)")
        print("-" * 30)
        lever_companies = platforms["lever"]
        print(f"   Found {len(lever_companies)} Lever companies to process")
        print("   ⚠️ Lever scraper not yet implemented")
    
    # TODO: Add Workday Platform
    if "workday" in platforms:
        print("\n💼 WORKDAY PLATFORM (Coming Soon)")
        print("-" * 30)
        workday_companies = platforms["workday"]
        print(f"   Found {len(workday_companies)} Workday companies to process")
        print("   ⚠️ Workday scraper not yet implemented")
    
    return total_processed

def run_company_career_pages(config):
    """Run company-specific career page scrapers (Google, etc.)"""
    print("\n🏢 PHASE 2: Company Career Pages")
    print("=" * 50)
    
    # Run the legacy scraper for company career pages
    return run_legacy_scraper()

def main():
    """Main function to run the full scraper engine."""
    print("🚀 Starting Job Scraper Engine - Platform-First Approach")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    if not config:
        print("❌ Failed to load configuration. Exiting.")
        return
    
    total_processed = 0
    
    # Phase 1: Platform-based scraping (Greenhouse, Lever, Workday)
    platform_jobs = run_platform_scrapers(config)
    total_processed += platform_jobs
    
    # Phase 2: Company-specific career pages (Google, etc.)
    career_page_jobs = run_company_career_pages(config)
    total_processed += career_page_jobs or 0
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 SCRAPING COMPLETE!")
    print(f"📊 Total jobs processed: {total_processed}")
    print("💾 All jobs saved to Supabase database")
    print("=" * 60)

if __name__ == '__main__':
    main() 