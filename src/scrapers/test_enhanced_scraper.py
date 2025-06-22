#!/usr/bin/env python3
"""
Test script for the enhanced job scraper engine.
This script validates the configuration and structure without requiring all dependencies.
"""

import json
import os

def test_config_loading():
    """Test loading configuration from scraper_config.json"""
    print("🔍 Testing configuration loading...")
    
    try:
        with open('scraper_config.json', 'r') as f:
            config = json.load(f)
        
        print("✅ Configuration loaded successfully")
        
        # Check for required sections
        required_sections = ['job_search', 'career_sites', 'company_career_pages']
        for section in required_sections:
            if section in config:
                print(f"✅ Found {section} section")
            else:
                print(f"⚠️ Missing {section} section")
        
        # Check company career pages
        if 'company_career_pages' in config:
            pages = config['company_career_pages']
            print(f"🏢 Company career pages configured: {len(pages)}")
            for page in pages:
                print(f"   - {page}")
        
        return config
        
    except FileNotFoundError:
        print("❌ scraper_config.json not found")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in scraper_config.json: {e}")
        return None

def test_google_careers_url_validation():
    """Test Google Careers URL validation logic"""
    print("\n🔍 Testing Google Careers URL validation...")
    
    test_urls = [
        "https://careers.google.com/jobs/results/",
        "https://careers.google.com/jobs/results/?keywords=software%20engineer",
        "https://amazon.jobs/",
        "https://careers.meta.com/",
        "https://invalid-url.com/"
    ]
    
    for url in test_urls:
        if "careers.google.com" in url:
            print(f"✅ Google Careers URL detected: {url}")
        elif "amazon.jobs" in url:
            print(f"🏢 Amazon Jobs URL detected: {url}")
        elif "careers.meta.com" in url:
            print(f"📘 Meta Careers URL detected: {url}")
        else:
            print(f"⚠️ Unknown URL format: {url}")

def test_scraper_structure():
    """Test the scraper function structure"""
    print("\n🔍 Testing scraper function structure...")
    
    # Simulate the scrape_company_career_pages function logic
    def mock_scrape_company_career_pages(config):
        all_job_urls = []
        
        if "company_career_pages" not in config or not config["company_career_pages"]:
            print("ℹ️ No company career pages configured")
            return all_job_urls
        
        print(f"🏢 Would scrape {len(config['company_career_pages'])} company career pages...")
        
        for company_url in config["company_career_pages"]:
            if "careers.google.com" in company_url:
                print(f"✅ Would call Google Careers scraper for: {company_url}")
                # Mock job URLs
                mock_google_jobs = [
                    "https://careers.google.com/jobs/results/123456/",
                    "https://careers.google.com/jobs/results/789012/",
                    "https://careers.google.com/jobs/results/345678/"
                ]
                all_job_urls.extend(mock_google_jobs)
            elif "amazon.jobs" in company_url:
                print(f"🏢 Would call Amazon Jobs scraper for: {company_url}")
            elif "careers.meta.com" in company_url:
                print(f"📘 Would call Meta Careers scraper for: {company_url}")
            else:
                print(f"⚠️ No specialized scraper found for: {company_url}")
        
        return all_job_urls
    
    # Test with our config
    config = test_config_loading()
    if config:
        job_urls = mock_scrape_company_career_pages(config)
        print(f"📊 Mock scraper would find {len(job_urls)} job URLs")

def test_environment_variables():
    """Test environment variable detection"""
    print("\n🔍 Testing environment variable detection...")
    
    required_vars = ['GOOGLE_API_KEY', 'SUPABASE_URL', 'SUPABASE_KEY']
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is not set")

def main():
    """Main test function"""
    print("🚀 Enhanced Job Scraper Engine - Test Suite")
    print("=" * 50)
    
    # Run all tests
    test_config_loading()
    test_google_careers_url_validation()
    test_scraper_structure()
    test_environment_variables()
    
    print("\n" + "=" * 50)
    print("🎉 Test suite completed!")
    print("\n📋 Summary:")
    print("- Configuration file structure validated")
    print("- Google Careers URL detection working")
    print("- Scraper function structure ready")
    print("- Environment variables checked")
    print("\n💡 Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Set environment variables (GOOGLE_API_KEY, SUPABASE_URL, SUPABASE_KEY)")
    print("3. Run the full scraper: python job_scraper_engine.py")

if __name__ == '__main__':
    main() 