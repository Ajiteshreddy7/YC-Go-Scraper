#
# Job Scraper Engine - Automated Job Discovery System
# This script automatically finds new job postings from multiple career websites
# and saves them to your Supabase database.
#

import os
import json
import time
import random
import requests
from bs4 import BeautifulSoup
import pandas as pd
import google.generativeai as genai
from supabase import create_client, Client
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin, urlparse
import re

# --- CONFIGURATION ---
try:
    # Gemini AI Configuration
    google_api_key = os.environ.get("GOOGLE_API_KEY")
    if not google_api_key:
        raise KeyError("GOOGLE_API_KEY")
    genai.configure(api_key=google_api_key)
    
    # Supabase Configuration
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url:
        raise KeyError("SUPABASE_URL")
    if not supabase_key:
        raise KeyError("SUPABASE_KEY")
        
    supabase: Client = create_client(supabase_url, supabase_key)
    
except KeyError as e:
    print("="*60)
    print("ERROR: Missing required environment variable!")
    print(f"Missing: {e}")
    print("="*60)
    print("Please set the following environment variables:")
    print("GOOGLE_API_KEY, SUPABASE_URL, SUPABASE_KEY")
    print("="*60)
    exit()

# Load configuration from JSON file
def load_config():
    """Load configuration from scraper_config.json"""
    try:
        with open('config/scraper_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ config/scraper_config.json not found. Using default configuration.")
        return {
            "job_search": {
                "keywords": ["data engineer", "software engineer", "python developer"],
                "locations": ["San Francisco", "New York", "Remote"],
                "max_jobs_per_search": 10,
                "delay_between_requests": 2
            },
            "career_sites": {
                "linkedin": {"enabled": True, "priority": 1, "max_pages": 2},
                "indeed": {"enabled": True, "priority": 2, "max_pages": 2},
                "glassdoor": {"enabled": True, "priority": 3, "max_pages": 1}
            },
            "company_career_pages": [],
            "targeting": {
                "exclude_keywords": [],
                "include_keywords": [],
                "locations": []
            }
        }

# Job search configuration (legacy - will be replaced by config file)
JOB_SEARCH_CONFIG = {
    'keywords': ['data engineer', 'software engineer', 'python developer', 'machine learning engineer'],
    'locations': ['San Francisco', 'New York', 'Remote', 'Seattle', 'Austin'],
    'max_jobs_per_search': 10,  # Limit to avoid overwhelming the system
    'delay_between_requests': 2,  # Seconds between requests to be respectful
}

# Career websites to scrape (legacy - will be replaced by config file)
CAREER_SITES = {
    'linkedin': {
        'base_url': 'https://www.linkedin.com/jobs/search/',
        'search_params': {
            'keywords': '{keywords}',
            'location': '{location}',
            'f_TPR': 'r86400',  # Last 24 hours
            'position': 1,
            'pageNum': 0
        }
    },
    'indeed': {
        'base_url': 'https://www.indeed.com/jobs',
        'search_params': {
            'q': '{keywords}',
            'l': '{location}',
            'fromage': '1'  # Last 24 hours
        }
    },
    'glassdoor': {
        'base_url': 'https://www.glassdoor.com/Job/',
        'search_params': {
            'sc.keyword': '{keywords}',
            'locT': 'C',
            'locId': '1147401',  # San Francisco
            'jobType': '',
            'fromAge': '1'
        }
    }
}

def get_existing_job_urls():
    """Get all existing job URLs from the database to avoid duplicates."""
    try:
        response = supabase.table('job_applications').select('URL').execute()
        existing_urls = [job['URL'] for job in response.data]
        print(f"Found {len(existing_urls)} existing jobs in database")
        return set(existing_urls)
    except Exception as e:
        print(f"Error fetching existing URLs: {e}")
        return set()

def check_if_job_exists(url):
    """Check if a job URL already exists in the database."""
    try:
        response = supabase.table('job_applications').select('URL').eq('URL', url).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error checking if job exists: {e}")
        return False

def get_page_text(url):
    """Get page text content using trafilatura for better text extraction."""
    try:
        import trafilatura
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded, include_links=True, include_images=True)
            return text
        return None
    except ImportError:
        # Fallback to requests if trafilatura is not available
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.get_text()
        except Exception as e:
            print(f"Error getting page text for {url}: {e}")
            return None

def extract_details_with_gemini(text_content, url):
    """Extract job details using Gemini AI."""
    # Load config to get the model version
    config = load_config()
    model_name = config.get('ai_extraction', {}).get('model', 'gemini-1.5-flash')
    
    model = genai.GenerativeModel(model_name)
    
    prompt = f"""
    You are an expert job data extraction specialist. Analyze this job posting and extract key details.

    Return ONLY a valid JSON object with these exact keys:
    {{
        "job_title": "the job title found",
        "company_name": "the company name found", 
        "location": "location information found",
        "salary_range": "salary/compensation information found (or null if none)",
        "job_type": "employment type found (or null if none)"
    }}

    Text to analyze:
    ---
    {text_content[:8000]}
    ---
    """
    
    try:
        response = model.generate_content(prompt)
        json_text = response.text.strip().replace('```json', '').replace('```', '').strip()
        
        if json_text.startswith('{') and json_text.endswith('}'):
            details = json.loads(json_text)
        else:
            start_idx = json_text.find('{')
            end_idx = json_text.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_text = json_text[start_idx:end_idx]
                details = json.loads(json_text)
            else:
                raise ValueError("No valid JSON found in response")
        
        job_details = {
            'Title': details.get('job_title'),
            'Company': details.get('company_name'),
            'Location': details.get('location'),
            'Salary': details.get('salary_range'),
            'Type': details.get('job_type'),
            'URL': url,
            'Date Added': pd.to_datetime('today').strftime('%Y-%m-%d %H:%M:%S'),
        }
        return job_details

    except Exception as e:
        print(f"Error extracting details from {url}: {e}")
        return None

def save_to_supabase(job_details):
    """Save job details to Supabase database."""
    try:
        data, count = supabase.table('job_applications').insert(job_details).execute()
        print(f"✅ Saved: {job_details.get('Title', 'Unknown')} at {job_details.get('Company', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ Error saving job: {e}")
        return False

def should_process_job(job_details, config):
    """
    Determine if a job should be processed based on targeting criteria.
    
    Args:
        job_details (dict): Job details extracted by AI
        config (dict): Configuration with targeting rules
        
    Returns:
        bool: True if job should be processed, False otherwise
    """
    if not job_details or not job_details.get('Title'):
        return False
    
    title = job_details.get('Title', '').lower()
    location = job_details.get('Location', '')
    
    # Handle None location
    if location is None:
        location = ''
    else:
        location = location.lower()
    
    # Get targeting config
    targeting = config.get('targeting', {})
    exclude_keywords = targeting.get('exclude_keywords', [])
    include_keywords = targeting.get('include_keywords', [])
    target_locations = targeting.get('locations', [])
    
    # Check for excluded keywords in title
    for exclude_word in exclude_keywords:
        if exclude_word.lower() in title:
            print(f"❌ Excluding job: '{exclude_word}' found in title")
            return False
    
    # Check for included keywords in title (at least one should match)
    has_included_keyword = False
    for include_word in include_keywords:
        if include_word.lower() in title:
            has_included_keyword = True
            break
    
    # If no include keywords match, check if it's a basic engineering role
    if not has_included_keyword:
        basic_roles = ['engineer', 'developer', 'analyst', 'specialist']
        has_basic_role = any(role in title for role in basic_roles)
        if not has_basic_role:
            print(f"❌ Excluding job: No matching keywords found in title")
            return False
    
    # Check location targeting
    if target_locations:
        location_match = False
        for target_loc in target_locations:
            if target_loc.lower() in location:
                location_match = True
                break
        
        if not location_match:
            print(f"❌ Excluding job: Location '{location}' not in target locations")
            return False
    
    print(f"✅ Job passes targeting filters: {title}")
    return True

def scrape_google_careers(url):
    """
    Scrapes job listings directly from the Google Careers page.
    
    Args:
        url (str): The URL of the Google Careers search results page.
        
    Returns:
        list: A list of URLs for individual job postings found on the page.
    """
    print(f"🔍 Scraping Google Careers page: {url}")
    job_links = []
    
    # Setup Selenium to use a Chrome browser
    options = Options()
    options.add_argument('--headless')  # Run in headless mode (no browser window opens)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        try:
            driver.get(url)
            
            # Give the page a moment to load its JavaScript content
            time.sleep(5)
            
            # Scroll down to load more content
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            print("🔍 Looking for Google Careers job links...")
            
            # Method 1: Find job elements and extract links from them
            job_elements = driver.find_elements(By.CSS_SELECTOR, "div.sMn82b")
            print(f"Found {len(job_elements)} job elements")
            
            for i, job_element in enumerate(job_elements):
                try:
                    # Find links within each job element
                    links = job_element.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        href = link.get_attribute('href')
                        if href:
                            # Check for both URL patterns we discovered
                            if ('google.com/about/careers/applications/jobs/results/' in href or 
                                'careers.google.com/jobs/results/' in href):
                                if href != url:  # Don't include the search page itself
                                    job_links.append(href)
                                    print(f"✅ Found job link {i+1}: {href}")
                except Exception as e:
                    print(f"❌ Error processing job element {i+1}: {e}")
                    continue
            
            # Method 2: If no links found, try alternative selectors
            if not job_links:
                print("🔍 Trying alternative selectors...")
                selectors_to_try = [
                    "div.sMn82b a",
                    "[data-job-id] a", 
                    ".job-card a",
                    "[role='listitem'] a",
                    ".job-listing a",
                    "div[class*='job'] a"
                ]
                
                for selector in selectors_to_try:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            print(f"✅ Found {len(elements)} elements with selector: {selector}")
                            for element in elements:
                                try:
                                    href = element.get_attribute('href')
                                    if href and ('google.com/about/careers/applications/jobs/results/' in href or 
                                                'careers.google.com/jobs/results/' in href):
                                        if href != url:  # Don't include the search page itself
                                            job_links.append(href)
                                            print(f"✅ Found job link: {href}")
                                except:
                                    continue
                            if job_links:
                                break
                    except Exception as e:
                        continue
            
            # Method 3: Look for URLs in page source with the correct pattern
            if not job_links:
                print("🔍 Looking for URLs in page source...")
                try:
                    page_source = driver.page_source
                    import re
                    # Look for both URL patterns
                    url_patterns = [
                        r'https://www\.google\.com/about/careers/applications/jobs/results/[^"\s]+',
                        r'https://careers\.google\.com/jobs/results/[^"\s]+'
                    ]
                    
                    for pattern in url_patterns:
                        found_urls = re.findall(pattern, page_source)
                        for found_url in found_urls:
                            if found_url != url and found_url not in job_links:
                                job_links.append(found_url)
                                print(f"✅ Found job link via regex: {found_url}")
                except Exception as e:
                    print(f"❌ Error in regex search: {e}")
                    
        finally:
            driver.quit()  # Always close the browser
            
    except Exception as e:
        print(f"❌ An error occurred while scraping Google Careers: {e}")
        
    # Remove duplicate links just in case
    unique_links = list(set(job_links))
    print(f"✅ Found {len(unique_links)} unique job links from Google Careers")
    
    # Show first few links for debugging
    if unique_links:
        print("📋 Sample job links found:")
        for i, link in enumerate(unique_links[:3]):
            print(f"   {i+1}. {link}")
    
    return unique_links

def scrape_company_career_pages(config):
    """
    Scrape job listings from direct company career pages.
    
    Args:
        config (dict): Configuration dictionary containing company_career_pages list
        
    Returns:
        list: A list of URLs for individual job postings found across all company pages
    """
    all_job_urls = []
    
    if "company_career_pages" not in config or not config["company_career_pages"]:
        print("ℹ️ No company career pages configured")
        return all_job_urls
    
    print(f"\n🏢 Scraping {len(config['company_career_pages'])} company career pages...")
    
    for company_url in config["company_career_pages"]:
        if "careers.google.com" in company_url:
            # We found a Google URL, so we call our specialized function
            google_jobs = scrape_google_careers(company_url)
            all_job_urls.extend(google_jobs)
        # You can add more 'elif' blocks here for other companies in the future
        # elif "amazon.jobs" in company_url:
        #     amazon_jobs = scrape_amazon_jobs(company_url)
        #     all_job_urls.extend(amazon_jobs)
        # elif "careers.meta.com" in company_url:
        #     meta_jobs = scrape_meta_jobs(company_url)
        #     all_job_urls.extend(meta_jobs)
        else:
            print(f"⚠️ No specialized scraper found for: {company_url}")
    
    return all_job_urls

def extract_job_urls_from_page(html_content, site_name):
    """Extract job URLs from a career site's search results page."""
    soup = BeautifulSoup(html_content, 'html.parser')
    job_urls = []
    
    if site_name == 'linkedin':
        # LinkedIn job URL patterns
        job_links = soup.find_all('a', href=re.compile(r'/jobs/view/'))
        for link in job_links:
            href = link.get('href')
            if href:
                full_url = urljoin('https://www.linkedin.com', href)
                job_urls.append(full_url)
    
    elif site_name == 'indeed':
        # Indeed job URL patterns
        job_links = soup.find_all('a', href=re.compile(r'/rc/clk'))
        for link in job_links:
            href = link.get('href')
            if href:
                full_url = urljoin('https://www.indeed.com', href)
                job_urls.append(full_url)
    
    elif site_name == 'glassdoor':
        # Glassdoor job URL patterns
        job_links = soup.find_all('a', href=re.compile(r'/partner/'))
        for link in job_links:
            href = link.get('href')
            if href:
                full_url = urljoin('https://www.glassdoor.com', href)
                job_urls.append(full_url)
    
    return list(set(job_urls))  # Remove duplicates

def get_page_content_with_selenium(url):
    """Get page content using Selenium for JavaScript-rendered sites."""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)
            return driver.page_source
        finally:
            driver.quit()
    except Exception as e:
        print(f"Selenium error for {url}: {e}")
        return None

def get_page_content_with_requests(url):
    """Get page content using requests for simple sites."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Request error for {url}: {e}")
        return None

def save_job_to_database(job_details):
    """Save job details to Supabase database."""
    try:
        data, count = supabase.table('job_applications').insert(job_details).execute()
        print(f"✅ Saved: {job_details.get('Title', 'Unknown')} at {job_details.get('Company', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ Error saving job: {e}")
        return False

def scrape_career_site(site_name, site_config, keywords, locations):
    """Scrape a specific career site for new job postings."""
    print(f"\n🔍 Scraping {site_name.upper()}...")
    
    existing_urls = get_existing_job_urls()
    new_jobs_found = 0
    
    # Handle both new config format and legacy format
    if isinstance(site_config, dict) and 'enabled' in site_config:
        # New config format - skip if disabled
        if not site_config.get('enabled', True):
            print(f"  ⏭️ {site_name} is disabled in configuration")
            return 0
        
        # For new config format, we need to use the legacy CAREER_SITES structure
        if site_name in CAREER_SITES:
            legacy_config = CAREER_SITES[site_name]
        else:
            print(f"  ❌ No legacy configuration found for {site_name}")
            return 0
    else:
        # Legacy config format
        legacy_config = site_config
    
    for keyword in keywords:
        for location in locations:
            if new_jobs_found >= JOB_SEARCH_CONFIG['max_jobs_per_search']:
                break
                
            print(f"  Searching: {keyword} in {location}")
            
            # Build search URL using legacy config structure
            search_params = legacy_config['search_params'].copy()
            search_params = {k: v.format(keywords=keyword, location=location) for k, v in search_params.items()}
            
            search_url = legacy_config['base_url']
            if site_name == 'linkedin':
                search_url = f"{search_url}?{'&'.join([f'{k}={v}' for k, v in search_params.items()])}"
            else:
                search_url = f"{search_url}?{'&'.join([f'{k}={v}' for k, v in search_params.items()])}"
            
            # Get search results page
            if site_name in ['linkedin', 'glassdoor']:
                page_content = get_page_content_with_selenium(search_url)
            else:
                page_content = get_page_content_with_requests(search_url)
            
            if not page_content:
                continue
            
            # Extract job URLs
            job_urls = extract_job_urls_from_page(page_content, site_name)
            print(f"    Found {len(job_urls)} job URLs")
            
            # Process each job URL
            for job_url in job_urls[:5]:  # Limit to 5 jobs per search to be respectful
                if job_url in existing_urls:
                    continue
                
                print(f"    Processing: {job_url}")
                
                # Get job details page
                job_page_content = get_page_content_with_selenium(job_url)
                if not job_page_content:
                    continue
                
                # Extract job details
                job_details = extract_details_with_gemini(job_page_content, job_url)
                if job_details and job_details.get('Title'):
                    if should_process_job(job_details, config):
                        if save_job_to_database(job_details):
                            new_jobs_found += 1
                            existing_urls.add(job_url)
                
                # Be respectful with delays
                time.sleep(JOB_SEARCH_CONFIG['delay_between_requests'])
            
            time.sleep(JOB_SEARCH_CONFIG['delay_between_requests'])
    
    return new_jobs_found

def main():
    """Main function to run the full scraper engine."""
    print("🚀 Starting Job Scraper Engine")
    print("="*50)
    
    # Load configuration from the JSON file
    config = load_config()
    
    # --- This is where we'll store all the job URLs we find ---
    all_new_job_urls = []
    
    # Part 1: Scrape direct company career pages
    # ==========================================
    print("\n🏢 PHASE 1: Scraping Company Career Pages")
    print("-" * 40)
    company_job_urls = scrape_company_career_pages(config)
    all_new_job_urls.extend(company_job_urls)
    
    # Part 2: Scrape Job Boards (legacy support)
    # ==========================================
    print("\n📋 PHASE 2: Scraping Job Boards")
    print("-" * 40)
    
    # Use config if available, otherwise fall back to legacy configuration
    if "career_sites" in config:
        career_sites_config = config["career_sites"]
        job_search_config = config["job_search"]
    else:
        career_sites_config = CAREER_SITES
        job_search_config = JOB_SEARCH_CONFIG
    
    total_new_jobs = 0
    
    # Scrape each career site
    for site_name, site_config in career_sites_config.items():
        if isinstance(site_config, dict) and site_config.get('enabled', True):
            try:
                new_jobs = scrape_career_site(
                    site_name, 
                    site_config, 
                    job_search_config['keywords'], 
                    job_search_config['locations']
                )
                total_new_jobs += new_jobs
                print(f"✅ {site_name.upper()}: Found {new_jobs} new jobs")
            except Exception as e:
                print(f"❌ Error scraping {site_name}: {e}")
    
    print(f"\n📊 Found a total of {len(all_new_job_urls)} new job URLs across all sources.")
    
    # Part 3: Process each unique URL from company career pages
    # ========================================================
    processed_count = 0  # Initialize the variable
    
    if all_new_job_urls:
        print("\n🔍 PHASE 3: Processing Company Career Page Jobs")
        print("-" * 40)
        
        unique_urls = list(set(all_new_job_urls))  # Use set to process each URL only once
        
        for url in unique_urls:
            print("-" * 40)
            print(f"Processing URL: {url}")
            try:
                if check_if_job_exists(url):
                    print("Job already exists in the database. Skipping.")
                    continue
                page_text = get_page_text(url)  # This function uses trafilatura
                if page_text:
                    job_details = extract_details_with_gemini(page_text, url)  # Gemini does the hard work
                    if job_details:
                        # Apply targeting filters before saving
                        if should_process_job(job_details, config):
                            if save_to_supabase(job_details):
                                processed_count += 1
                            time.sleep(2)  # Be respectful and add a small delay
                        else:
                            print(f"⏭️ Skipping job due to targeting filters")
                    else:
                        print(f"❌ Could not extract job details from {url}")
                else:
                    print(f"❌ Could not extract text from {url}")
            except Exception as e:
                print(f"❌ Unexpected error processing {url}: {e}")
    
    print(f"\n🎉 Scraping Complete!")
    print(f"📈 Total new jobs found from job boards: {total_new_jobs}")
    print(f"🏢 Total new jobs processed from company pages: {processed_count}")
    print(f"💾 All jobs saved to Supabase database")

if __name__ == '__main__':
    main() 